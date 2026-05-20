# Sales & Revenue Analysis Dashboard

This project includes a Streamlit dashboard for importing, analyzing, and visualizing sales and revenue data.

## Features

- Import data from CSV, Excel, or SQLite database
- Interactive KPI cards for orders, total revenue, total sales, and average revenue
- Revenue trend and top-performing products charts
- Filters for date range, product, and region
- Data preview and download of cleaned output

## Getting Started

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Run the dashboard:

```bash
streamlit run app.py
```

3. Upload your own dataset or use the included `sample_data.csv`.

## Expected Data Columns

The app works best with columns such as:

- `order_date`
- `product`
- `category`
- `region`
- `sales`
- `revenue`
- `profit`
