import ast
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Personalized Career Path Recommendation with AI",
    page_icon="🎯",
    layout="wide"
)

# ---------------------------------------------------
# File path setup
# Assumes:
# repo/
# ├── app.py
# ├── result/
# │   └── career_roles_seed.csv
# ├── notebooks/
# ├── data/
# └── requirements.txt
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "result" / "career_roles_seed.csv"


@st.cache_data
def load_data(file_path: Path) -> pd.DataFrame:
    """Load the career dataset and convert list-like columns properly."""
    df = pd.read_csv(file_path)

    list_like_cols = ["required_skills", "preferred_skills", "interest_tags"]

    def parse_list_column(value):
        if isinstance(value, list):
            return value
        if pd.isna(value):
            return []
        try:
            return ast.literal_eval(value)
        except Exception:
            return [item.strip() for item in str(value).split("|") if item.strip()]

    for col in list_like_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_list_column)

    return df


def overlap_score(user_items, role_items):
    user_set = {str(x).strip().lower() for x in user_items}
    role_set = {str(x).strip().lower() for x in role_items}

    if not role_set:
        return 0.0

    return len(user_set & role_set) / len(role_set)


def experience_score(user_exp, role_exp):
    user_exp = str(user_exp).strip().lower()
    role_exp = str(role_exp).strip().lower()

    if user_exp in role_exp:
        return 1.0
    if user_exp == "entry" and role_exp == "junior":
        return 0.7
    if user_exp == "entry" and role_exp == "entry/junior":
        return 1.0
    return 0.4


def education_score(user_edu, role_edu):
    user_edu = str(user_edu).strip().lower()
    role_edu = str(role_edu).strip().lower()

    if user_edu in role_edu:
        return 1.0
    return 0.6


def missing_skills(user_skills, required_skills):
    user_set = {skill.strip().lower() for skill in user_skills}
    return [
        skill for skill in required_skills
        if skill.strip().lower() not in user_set
    ]


def matched_skills(user_skills, required_skills):
    user_set = {skill.strip().lower() for skill in user_skills}
    return [
        skill for skill in required_skills
        if skill.strip().lower() in user_set
    ]


def build_learning_roadmap(missing_required_skills):
    if not missing_required_skills:
        return [
            "Strengthen existing portfolio projects",
            "Practice interview questions for the target role",
            "Apply for relevant entry-level opportunities"
        ]

    roadmap = []
    for skill in missing_required_skills[:4]:
        roadmap.append(f"Learn or improve {skill}")
    roadmap.append("Build one portfolio project using these skills")
    roadmap.append("Update CV and LinkedIn with new evidence")
    return roadmap


def build_recommendation_explanation(row):
    matched = (
        ", ".join(row["matched_required_skills"][:3])
        if row["matched_required_skills"]
        else "some relevant skills"
    )
    missing_count = len(row["missing_required_skills"])
    fit_pct = round(row["fit_score"] * 100, 1)

    return (
        f"This role is a strong match because your profile already aligns with key skills such as "
        f"{matched}. It belongs to the {row['domain']} domain and has a current fit score of "
        f"{fit_pct}%. You would still need to strengthen {missing_count} important skill(s) "
        f"to become more competitive."
    )


def score_roles(df, user_profile):
    scored_df = df.copy()

    scored_df["required_skill_score"] = scored_df["required_skills"].apply(
        lambda x: overlap_score(user_profile["current_skills"], x)
    )
    scored_df["preferred_skill_score"] = scored_df["preferred_skills"].apply(
        lambda x: overlap_score(user_profile["current_skills"], x)
    )
    scored_df["interest_score"] = scored_df["interest_tags"].apply(
        lambda x: overlap_score(user_profile["interests"], x)
    )
    scored_df["experience_score"] = scored_df["experience_level"].apply(
        lambda x: experience_score(user_profile["experience_level"], x)
    )
    scored_df["education_score"] = scored_df["education_level"].apply(
        lambda x: education_score(user_profile["education_level"], x)
    )

    scored_df["fit_score"] = (
        0.45 * scored_df["required_skill_score"] +
        0.15 * scored_df["preferred_skill_score"] +
        0.20 * scored_df["interest_score"] +
        0.10 * scored_df["experience_score"] +
        0.10 * scored_df["education_score"]
    )

    scored_df["missing_required_skills"] = scored_df["required_skills"].apply(
        lambda x: missing_skills(user_profile["current_skills"], x)
    )
    scored_df["matched_required_skills"] = scored_df["required_skills"].apply(
        lambda x: matched_skills(user_profile["current_skills"], x)
    )
    scored_df["learning_roadmap"] = scored_df["missing_required_skills"].apply(
        build_learning_roadmap
    )
    scored_df["recommendation_explanation"] = scored_df.apply(
        build_recommendation_explanation,
        axis=1
    )

    return scored_df.sort_values(by="fit_score", ascending=False).reset_index(drop=True)


# ---------------------------------------------------
# Load data safely
# ---------------------------------------------------
if not DATA_FILE.exists():
    st.error(f"Data file not found: {DATA_FILE}")
    st.stop()

df = load_data(DATA_FILE)

all_skills = sorted(
    {
        skill
        for col in ["required_skills", "preferred_skills"]
        for skills_list in df[col]
        for skill in skills_list
    }
)

all_interests = sorted(
    {
        tag
        for tags in df["interest_tags"]
        for tag in tags
    }
)

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.title("Personalized Career Path Recommendation with AI")
st.markdown(
    "Get career recommendations based on your skills, interests, education, and experience level."
)

with st.sidebar:
    st.header("Your Profile")

    education_level = st.selectbox(
        "Education Level",
        ["Bachelor", "MSc", "PhD"]
    )

    experience_level = st.selectbox(
        "Experience Level",
        ["Entry", "Junior", "Mid"]
    )

    current_skills = st.multiselect(
        "Current Skills",
        options=all_skills,
        default=["Python", "SQL", "Statistics", "Data Visualization"]
    )

    interests = st.multiselect(
        "Interests",
        options=all_interests,
        default=["AI", "Analytics", "Problem Solving"]
    )

    top_n = st.slider(
        "Number of Recommendations",
        min_value=3,
        max_value=10,
        value=5
    )

user_profile = {
    "education_level": education_level,
    "experience_level": experience_level,
    "current_skills": current_skills,
    "interests": interests
}

if st.button("Generate Career Recommendations"):
    results_df = score_roles(df, user_profile)
    top_results = results_df.head(top_n)

    st.subheader("Top Career Recommendations")

    for idx, row in top_results.iterrows():
        with st.container():
            st.markdown(f"### {idx + 1}. {row['role_title']}")
            st.write(f"**Domain:** {row['domain']}")
            st.write(f"**Fit Score:** {round(row['fit_score'] * 100, 1)}%")
            st.progress(float(row["fit_score"]))

            st.write("**Why this role fits:**")
            st.write(row["recommendation_explanation"])

            st.write("**Matched Required Skills:**")
            if row["matched_required_skills"]:
                st.write(", ".join(row["matched_required_skills"]))
            else:
                st.write("No matched required skills yet.")

            st.write("**Missing Required Skills:**")
            if row["missing_required_skills"]:
                st.write(", ".join(row["missing_required_skills"]))
            else:
                st.write("No major required skill gaps detected.")

            st.write("**Suggested Learning Roadmap:**")
            for step_no, step in enumerate(row["learning_roadmap"], start=1):
                st.write(f"{step_no}. {step}")

            st.markdown("---")

    export_df = top_results[
        [
            "role_title",
            "domain",
            "fit_score",
            "matched_required_skills",
            "missing_required_skills",
            "recommendation_explanation",
            "learning_roadmap"
        ]
    ].copy()

    st.download_button(
        label="Download Recommendations as CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="career_recommendations.csv",
        mime="text/csv"
    )
else:
    st.info("Fill in your profile in the sidebar, then click 'Generate Career Recommendations'.")