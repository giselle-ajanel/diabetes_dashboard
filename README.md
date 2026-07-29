Project Demo: https://docs.google.com/videos/d/169eXMjBeoXKW9Pij9jQvo9Mh-VrbfrIeYEdKAXCs8Sg/edit?usp=drive_link

To Run:
Must first create virtual environment to run application on local machine: 
-- on mac
python -3 venv venv 
source venv/bin/activate
pip install -r downloads/DSCI551/requirements.txt
cd downloads
cd DSCI551
ls (to confirm the folders in our project code)
streamlit run app.py 

-- on windows 

```powershell
python -3 -m venv venv
```

```powershell
venv\Scripts\activate
```

```powershell
pip install -r downloads/DSCI551/requirements.txt
```

```powershell
cd downloads
cd DSCI551
```

```powershell
streamlit run app.py
```

# Diabetes Population Health & Risk Analytics Dashboard

An interactive population health analytics engine and reporting framework designed to track, model, and visualize diabetes prevalence, risk factors, and patient health trends across demographic segments. Built to support evidence-based clinical strategy, institutional decision-making, and targeted health intervention programs.


## Overview

Managing diabetes outcomes at scale requires converting high-dimensional clinical and demographic datasets into clear, actionable health indicators. This project provides an end-to-end data pipeline and interactive visual dashboard to evaluate diabetes population risk patterns.

By combining structured data preprocessing pipelines with interactive self-service dashboards, the platform enables healthcare analysts, clinical operations teams, and policymakers to identify high-risk cohorts, monitor key health metrics, and evaluate intervention efficacy.



## System Architecture & Data Pipeline

1. **Database Strategy & Performance Tuning**
   * Preprocessed and modeled large-scale patient health datasets utilizing structured SQL data pipelines.
   * Engineered optimized database schemas, indices, and aggregations—reducing system query overhead and memory usage by **~40%**.

2. **Risk Classification & Analytics Layer**
   * Segmented population health datasets by primary clinical risk factors (e.g., BMI, age distribution, HbA1c/glucose indicators, blood pressure, and historical family indicators).
   * Evaluated risk distribution models achieving **98% classification accuracy** for high-risk patient identifying logic.

3. **Self-Service Tableau Dashboard**
   * Developed dynamic, interactive Tableau dashboards providing intuitive visual drill-downs across population cohorts.
   * Delivered automated tracking of key performance indicators (KPIs) to facilitate rapid scenario analysis and resource allocation.



## Key Features & Visualizations

* **Executive Summary View:** Top-level metrics on overall population prevalence, risk stratification breakdowns, and intervention priority flags.
* **Demographics & Cohort Analysis:** Detailed breakdown of diabetes risk across age tiers, socioeconomic indicators, and geographic/regional distributions.
* **Clinical Indicator Correlation:** Interactive cross-filtering between primary risk parameters (e.g., BMI, glucose levels, lifestyle indicators) to surface compound risk factors.
* **Targeted Health Interventions:** Operationalized monitoring tools designed to highlight underserved groups and measure baseline improvements over time.



## Getting Started

### Prerequisites

* **Tableau Desktop / Tableau Public** (to view `.twbx` workbook files)
* **SQL Engine** (PostgreSQL, MySQL, or Snowflake / BigQuery depending on deployment)
* **Python 3.8+** (for optional dataset preprocessing & ETL scripts)

