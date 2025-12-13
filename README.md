# 🏠 Real Estate Investment Advisor  

A data-driven real estate analysis and investment advisory system that helps users evaluate property investment potential using exploratory data analysis and rule-based prediction.

---

## Overview  
This project is an end-to-end **Data Analytics + Streamlit** application designed to analyze housing market data and assist users in making smarter real estate investment decisions.  
It combines **data preprocessing, feature engineering, rule-based scoring, and interactive visualizations** to provide both market insights and property-level investment recommendations.  
The project demonstrates how analytical thinking and business logic can be applied to real-world real estate problems.

---

## Problem Statement  
Real estate investment decisions are often based on incomplete information or intuition.  
With multiple factors such as price, size, location, infrastructure, and amenities influencing property value, it becomes difficult to objectively evaluate an investment.  

The goal of this project is to:
- Analyze housing market trends  
- Compare properties using meaningful metrics  
- Provide a clear, explainable investment recommendation for a given property  

---

## Dataset  
- **File Used:**  
  - `india_housing_prices.csv`  
- **Dataset Size:** 250000 rows and 23 columns 
- **Key Features Used:**  
  `Price_in_Lakhs`, `Size_in_SqFt`, `BHK`, `City`, `State`, `Year_Built`,  
  `Nearby_Schools`, `Nearby_Hospitals`, `Parking_Space`,  
  `Public_Transport_Accessibility`, `Security`, `Amenities`, `Availability_Status`

---

## Tools and Technologies  

| Category | Tools |
|--------|-------|
| Language | Python |
| Libraries | pandas, numpy |
| Visualization | Plotly |
| Framework | Streamlit |
| IDEs | Jupyter Notebook (EDA & Feature Engineering) / PyCharm (App Development) |

---

## Methods  

### 1. Data Cleaning & Preparation  
- Loaded housing dataset and handled missing or inconsistent values  
- Converted price units from lakhs to rupees where required  
- Created derived features such as **Price per Sq Ft** and **Age of Property**

### 2. Feature Engineering  
- Calculated `Price_per_SqFt` for fair comparison across properties  
- Derived `Age_of_Property` from year built  
- Used infrastructure and amenity-related features to enrich analysis  

### 3. Exploratory Data Analysis (EDA)  
- Analyzed price and size distributions  
- Studied location-based trends (State, City, Locality)  
- Identified outliers using box plots and IQR  
- Explored relationships between price and features like BHK, parking, transport, and amenities  

### 4. Investment Score Calculation (Rule-Based)  
- Designed a transparent scoring system (0–100) based on:
  - Price per Sq Ft vs market median  
  - Property size and BHK configuration  
  - Property age  
  - Nearby schools and hospitals  
  - Public transport accessibility  
  - Security, amenities, and parking availability  
- Returned both **score and clear reasons** for explainability  

### 5. Future Price Estimation  
- Estimated property price after 5 years using compound annual growth  
- Adjusted growth rate based on property features and infrastructure  
- Calculated total appreciation percentage and annual growth rate  

### 6. Frontend (Streamlit App)  
- Built an interactive dashboard for EDA  
- Added a property investment predictor with user inputs  
- Displayed investment recommendation (Good / Risky) with visual indicators  
- Compared the user-selected property with similar properties from the dataset  

---

## 💡 Key Insights  
- Price per sq. Ft is a strong indicator for comparing properties across locations  
- Infrastructure and transport accessibility significantly impact property value  
- Rule-based systems provide better transparency than black-box models for business decisions  
- Interactive dashboards improve understanding of market trends and patterns  

---

## Author and Contact  
**Author:** Ishant Katiyar  
**Email:** ishantkatiyar68@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/ishantkatiyar/
