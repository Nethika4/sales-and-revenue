import io
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Sales & Revenue Dashboard", layout="wide")

st.title("Sales & Revenue Analysis Dashboard")
st.markdown("Use this dashboard to import sales data from Excel, CSV, or a SQLite database, then analyze revenue trends, top products, and key business metrics.")

@st.cache_data
def load_data_from_csv(uploaded_file):
    return pd.read_csv(uploaded_file)

@st.cache_data
def load_data_from_excel(uploaded_file):
    return pd.read_excel(uploaded_file, engine="openpyxl")

@st.cache_data
def load_data_from_sqlite(file_path, table_name="sales"):
    from sqlalchemy import create_engine
    engine = create_engine(f"sqlite:///{file_path}")
    return pd.read_sql_table(table_name, engine)

@st.cache_data
def prepare_data(df):
    df = df.copy()
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    if "sales" in df.columns:
        df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    if "revenue" in df.columns:
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    return df


def show_file_import():
    st.sidebar.header("Import Data")
    import_source = st.sidebar.selectbox("Choose data source", ["CSV", "Excel", "SQLite database"])
    df = None
    if import_source == "CSV":
        uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
        if uploaded_file is not None:
            df = load_data_from_csv(uploaded_file)
    elif import_source == "Excel":
        uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xls", "xlsx"])
        if uploaded_file is not None:
            df = load_data_from_excel(uploaded_file)
    else:
        db_file = st.sidebar.file_uploader("Upload a SQLite database file", type=["db", "sqlite", "sqlite3"])
        if db_file is not None:
            table_name = st.sidebar.text_input("Table name", value="sales")
            if table_name:
                try:
                    df = load_data_from_sqlite(db_file, table_name)
                except Exception as exc:
                    st.sidebar.error(f"Unable to load table: {exc}")
    return df


def apply_filters(df):
    st.sidebar.header("Filters")
    date_col = "order_date" if "order_date" in df.columns else None
    prod_col = next((c for c in ["product", "product_name", "item"] if c in df.columns), None)
    region_col = next((c for c in ["region", "territory", "market"] if c in df.columns), None)

    if date_col:
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        date_range = st.sidebar.date_input("Date range", [min_date, max_date])
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[df[date_col].between(pd.to_datetime(start_date), pd.to_datetime(end_date))]

    if prod_col:
        selected_products = st.sidebar.multiselect("Product", sorted(df[prod_col].dropna().unique()), default=sorted(df[prod_col].dropna().unique())[:5])
        if selected_products:
            df = df[df[prod_col].isin(selected_products)]

    if region_col:
        selected_regions = st.sidebar.multiselect("Region", sorted(df[region_col].dropna().unique()), default=sorted(df[region_col].dropna().unique())[:3])
        if selected_regions:
            df = df[df[region_col].isin(selected_regions)]

    return df


def render_metrics(df):
    sales_col = "sales" if "sales" in df.columns else "revenue" if "revenue" in df.columns else None
    revenue_col = "revenue" if "revenue" in df.columns else sales_col

    total_sales = df[sales_col].sum() if sales_col is not None else None
    total_revenue = df[revenue_col].sum() if revenue_col is not None else None
    avg_order = df[revenue_col].mean() if revenue_col is not None else None
    orders = len(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Orders", f"{orders:,}")
    col2.metric("Total Revenue", f"${total_revenue:,.2f}" if total_revenue is not None else "N/A")
    col3.metric("Total Sales", f"{total_sales:,.0f}" if total_sales is not None else "N/A")
    col4.metric("Avg Revenue", f"${avg_order:,.2f}" if avg_order is not None else "N/A")

    return sales_col, revenue_col


def render_charts(df, revenue_col):
    date_col = "order_date" if "order_date" in df.columns else None
    prod_col = next((c for c in ["product", "product_name", "item"] if c in df.columns), None)
    category_col = next((c for c in ["category", "segment", "product_category"] if c in df.columns), None)

    if date_col and revenue_col is not None:
        trend = df.groupby(pd.Grouper(key=date_col, freq="W"))[revenue_col].sum().reset_index()
        fig = px.line(trend, x=date_col, y=revenue_col, title="Revenue Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    if prod_col and revenue_col is not None:
        top_products = df.groupby(prod_col)[revenue_col].sum().nlargest(10).reset_index()
        fig = px.bar(top_products, x=revenue_col, y=prod_col, orientation="h", title="Top Performing Products", labels={revenue_col: "Revenue", prod_col: "Product"})
        st.plotly_chart(fig, use_container_width=True)

    if category_col and revenue_col is not None:
        category_perf = df.groupby(category_col)[revenue_col].sum().reset_index().sort_values(revenue_col, ascending=False)
        fig = px.pie(category_perf, names=category_col, values=revenue_col, title="Revenue by Category")
        st.plotly_chart(fig, use_container_width=True)

    if "profit" in df.columns and revenue_col is not None:
        profit_trend = df.groupby(pd.Grouper(key=date_col, freq="ME"))["profit"].sum().reset_index()
        fig = px.area(profit_trend, x=date_col, y="profit", title="Profit Trend")
        st.plotly_chart(fig, use_container_width=True)


def show_data_table(df):
    st.subheader("Data Preview")
    st.dataframe(df.head(200), use_container_width=True)
    with st.expander("Download cleaned data"):
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="sales_data_cleaned.csv", mime="text/csv")


def render_sample_data_instructions():
    st.sidebar.markdown("---")
    st.sidebar.write("Need sample data? Download the sample CSV from this project and upload it.")
    st.sidebar.write("The sample includes columns: order_date, product, category, region, sales, revenue, profit.")


def main():
    df = show_file_import()
    render_sample_data_instructions()

    if df is None:
        st.warning("Upload a CSV/Excel file or SQLite database to begin analysis. A sample data file is included in this project.")
        return

    df = prepare_data(df)
    if df.empty:
        st.error("The imported file contains no data after parsing. Check the file format and available columns.")
        return

    df = apply_filters(df)
    sales_col, revenue_col = render_metrics(df)
    render_charts(df, revenue_col)
    show_data_table(df)

if __name__ == "__main__":
    main()
