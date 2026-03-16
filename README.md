\# AI Career Path Recommender



An AI-powered career recommendation system that matches users to suitable roles based on their skills, interests, education, and experience level, then identifies skill gaps and generates personalized learning roadmaps.



\## Overview



Choosing a career path can be difficult, especially for students and early-career professionals who may have transferable skills but are unsure which roles are the best fit.



This project builds a simple and explainable AI-driven recommendation system that:



\- recommends suitable career roles

\- ranks roles using a weighted fit score

\- identifies matched and missing required skills

\- generates personalized next-step learning roadmaps

\- provides an interactive Streamlit interface for real-time recommendations



The system is designed to be interpretable, practical, and portfolio-ready.



\## Problem Statement



Many people struggle to connect their current skills and interests to realistic career opportunities.



Traditional career advice is often too generic, while job descriptions are usually fragmented and difficult to compare.



This project addresses that problem by creating a structured role dataset and a recommendation engine that evaluates user profiles against career paths in a transparent and actionable way.



\## Objectives



The main goals of this project are to:



\- recommend top-fit career roles based on user profile inputs

\- compare user skills against required and preferred role skills

\- highlight skill gaps that need improvement

\- generate a practical learning roadmap for career growth

\- present the recommendations in an accessible web app



\## Features



\- Career role recommendation engine

\- Weighted fit scoring system

\- Skill overlap analysis

\- Missing skill detection

\- Personalized recommendation explanations

\- Learning roadmap generation

\- Interactive Streamlit application

\- Exportable recommendation results



\## How It Works



The user provides a profile containing:



\- education level

\- experience level

\- current skills

\- career interests



The system then compares the profile against a curated career-role dataset and calculates:



\- required skill match score

\- preferred skill match score

\- interest alignment score

\- experience alignment score

\- education alignment score



These components are combined into a final career fit score used to rank roles.



\## Scoring Logic



The current fit score is calculated as:



```python

fit\_score = (

&#x20;   0.45 \* required\_skill\_score +

&#x20;   0.15 \* preferred\_skill\_score +

&#x20;   0.20 \* interest\_score +

&#x20;   0.10 \* experience\_score +

&#x20;   0.10 \* education\_score

)

```



Project Structure

```python

ai-career-path-recommender/

│

├── data/

│

├── notebooks/

│   ├── 01\_data\_loading\_and\_preparation.ipynb

│   └── 02\_recommendation\_summary\_and\_roadmap.ipynb

│

├── app.py

│   

├── result/

│   ├── career\_recommendation\_results.xlsx

│   └── career\_recommendation\_summary.xlsx

│

├── requirements.txt

└── README.md

```





