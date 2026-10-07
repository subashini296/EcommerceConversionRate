# E-Commerce Conversion Rate Analysis

Data analytics internship project (Task 4) using **Python, Pandas, Matplotlib and Seaborn**.
It analyses the shopping funnel **Visitors -> Product Views -> Add to Cart -> Purchases**,
calculates the conversion rate, studies monthly/weekly trends and gives business insights.

## Project Structure
```
EcommerceConversionRate/
├── ecommerce_data.csv                 # dataset (5,475 rows, year 2025)
├── generate_data.py                   # creates the dataset
├── ecommerce_analysis.py              # cleaning, analysis, charts, insights
├── insights.txt                       # auto-generated business insights
├── conversion_rate.png                # conversion by channel / device / weekday
├── monthly_conversion.png             # monthly + weekly conversion trend
├── Sales_Funnel.png                   # funnel chart with drop-off
├── ECommerce_Conversion_Report.docx   # final report
├── requirements.txt
└── README.md
```

## How to Run
```bash
pip install -r requirements.txt
python generate_data.py        # creates ecommerce_data.csv
python ecommerce_analysis.py   # creates charts + insights.txt
```

## Dataset Columns
| Column | Meaning |
|---|---|
| date | day of activity |
| channel | Organic Search, Paid Ads, Social Media, Email, Direct |
| device | Mobile, Desktop, Tablet |
| visitors | website visitors |
| product_views | visitors who viewed a product |
| add_to_cart | users who added to cart |
| purchases | completed orders |
| revenue | sales value (Rs.) |

> The data is **simulated**. To use real data, replace `ecommerce_data.csv` with your
> own file using the same columns and run `ecommerce_analysis.py`.

## Metrics
- View rate = product_views / visitors
- Add-to-cart rate = add_to_cart / product_views
- Purchase rate = purchases / add_to_cart
- **Conversion rate = purchases / visitors x 100**
- Average order value = revenue / purchases

## Key Findings
See `insights.txt` and the Word report for results, charts and recommendations.
