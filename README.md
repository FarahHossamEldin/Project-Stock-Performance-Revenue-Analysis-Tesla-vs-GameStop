# Stock-Performance-Revenue-Analysis-Tesla-vs-GameStop-Project
A Python-based analysis comparing the historical stock performance and revenue trends of Tesla and GameStop using data analysis, web scraping, and interactive visualizations.

## Project Overview

This project analyzes and compares the historical stock performance and revenue trends of Tesla and GameStop.

The analysis combines financial data collection, data cleaning, exploratory data analysis, revenue growth analysis, stock price comparison, and interactive visualizations.

The goal is to explore how the two companies' revenue and stock prices changed over time and identify notable trends in their financial performance.

---

## Project Preview

### Revenue Growth Comparison

![Revenue Growth Comparison](images/revenue_growth_comparison.png)

### Stock Price Comparison

![Stock Price Comparison](images/stock_price_comparison.png)

### Interactive Revenue Comparison

![Interactive Revenue Comparison](images/revenue_comparison.png)

> Interactive Plotly visualizations are available in the project notebook.

---

## Objectives

- Analyze historical stock price trends for Tesla and GameStop.
- Examine historical revenue trends.
- Compare revenue growth between the two companies.
- Compare historical stock price movements.
- Identify notable trends and changes in financial performance.
- Create interactive visualizations using Plotly.

---

## Tools & Technologies

- Python
- Pandas
- Matplotlib
- Plotly
- yfinance
- BeautifulSoup
- Requests
- Jupyter Notebook

---

## Data Collection

### Stock Data

Historical stock data for Tesla and GameStop was collected using the `yfinance` Python library.

The stock datasets include information such as:

- Date
- Open price
- High price
- Low price
- Closing price
- Trading volume

### Revenue Data

Historical revenue data was collected through web scraping using:

- Requests
- BeautifulSoup
- Pandas

The scraped revenue data was then cleaned and converted into appropriate data types for analysis.

---

## Analysis & Methodology

The project follows these main steps:

### 1. Data Collection

Stock data was obtained using `yfinance`, while historical revenue data was collected through web scraping.

### 2. Data Cleaning

The datasets were inspected and cleaned by:

- Checking data types
- Converting dates into datetime format
- Converting revenue values into numeric values
- Preparing the datasets for analysis

### 3. Exploratory Data Analysis

Historical stock prices and revenue trends were visualized using Matplotlib.

### 4. Revenue Growth Analysis

Year-over-year revenue growth was calculated using the `pct_change()` method.

The revenue growth of Tesla and GameStop was then compared during their overlapping period.

### 5. Stock Price Comparison

Historical closing prices were compared over their common trading period.

### 6. Interactive Visualization

Plotly was used to create interactive visualizations that allow users to explore the data through hover, zoom, and other interactive features.

---

## Key Insights

- Tesla demonstrated stronger and more consistent revenue growth than GameStop during the overlapping period (2009–2020).
- Tesla's revenue increased substantially over the analyzed period, while GameStop experienced several periods of negative revenue growth.
- Tesla generally traded at a higher stock price than GameStop and showed greater price fluctuations.
- GameStop experienced a sharp increase in stock price around 2021, while Tesla's stock price also increased noticeably around 2020.

---

## Conclusion

This project demonstrates how financial data can be collected, cleaned, analyzed, and visualized using Python.

It combines data collection through financial APIs and web scraping with exploratory analysis, revenue growth analysis, stock price comparison, and interactive visualization.

The project provided practical experience in using Python-based data analysis tools to explore real-world financial data.

---

## How to Run

1. Clone this repository.

2. Install the required libraries:

```bash
pip install pandas matplotlib plotly yfinance beautifulsoup4 requests
