import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Sales Dashboard",
    layout="wide",
    page_icon="📊"
)


st.title("📊 Sales Data Analysis Dashboard")

def database_connection():
    return sqlite3.connect('sales_dashboard.db')

@st.cache_data
def fetch_data(query):
    conn=database_connection()
    df=pd.read_sql(query,conn)
    conn.close()
    return df

def download_csv(dataframe,filename):
    """
        function to let the users download the dataframe as csv
    """
    buffer=BytesIO()
    dataframe.to_csv(buffer,index=False)
    buffer.seek(0)
    return buffer

st.subheader("👤 Customer Data")

#payment method selectbox
payment_method_filter=st.selectbox("Filter by Payment method:",options=['All','Credit Card', 'Debit Card', 'Cash'])
customer_query='SELECT * FROM Customers'

if payment_method_filter!='All':
    customer_query+=f" WHERE payment_method like '%{payment_method_filter}%'"

customers_df=fetch_data(customer_query)
st.dataframe(customers_df)

#Download the Csv
if not customers_df.empty:
    csv_buffer=download_csv(customers_df,'customer_data.csv')
    st.download_button(
        label='⬇️ Download Customer Data',
        data=csv_buffer,
        file_name='customer_data.csv',
        mime='text/csv'
    )

# ----- Sales Analysis ------

sales_query='SELECT * FROM Sales'

sales_df=fetch_data(sales_query)

# Convert invoice_date to datetime format
sales_df["invoice_date"] = pd.to_datetime(sales_df["invoice_date"], format="%d-%m-%Y")

with st.expander("🔍 Filter Data", expanded=False):
    categories = sales_df["category"].unique().tolist()
    selected_category = st.selectbox("Select Product Category", ["All"] + categories)

    malls = sales_df["shopping_mall"].unique().tolist()
    selected_mall = st.multiselect("Select Shopping Mall", malls, default=malls)

# Apply filters
filtered_df = sales_df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if selected_mall:
    filtered_df = filtered_df[filtered_df["shopping_mall"].isin(selected_mall)]

# ---- Dashboard Layout ----
st.title("📊 Sales Dashboard")

# Summary Metrics
st.subheader("📈 Key Performance Indicators")
col1, col2, col3 = st.columns(3)
total_sales = filtered_df["Total Sales"].sum()
total_transactions = filtered_df.shape[0]
avg_sale = total_sales / total_transactions if total_transactions else 0

col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
col2.metric("🛒 Total Transactions", total_transactions)
col3.metric("📉 Avg. Sale Value", f"${avg_sale:,.2f}")

tab1, tab2, tab3 = st.tabs(["📦 Category Analysis", "🏬 Shopping Malls", "📆 Sales Trends"])

# Tab 1: Category Analysis
with tab1:
    st.subheader("🏆 Top 5 Best-Selling Categories")
    top_categories = (
        sales_df.groupby("category")["Total Sales"].sum().reset_index().nlargest(5, "Total Sales")
    )
    fig_top_categories = px.bar(top_categories, x="category", y="Total Sales", title="Top 5 Best-Selling Categories")
    st.plotly_chart(fig_top_categories)

    st.subheader("📊 Category Sales Breakdown")
    category_sales = filtered_df.groupby("category")["Total Sales"].sum().reset_index()
    fig_category_pie = px.pie(category_sales, names="category", values="Total Sales", title="Category Sales Distribution")
    st.plotly_chart(fig_category_pie)

# Tab 2: Shopping Malls
with tab2:
    st.subheader("🏬 Sales by Shopping Mall")
    sales_by_mall = filtered_df.groupby("shopping_mall")["Total Sales"].sum().reset_index()
    fig_mall = px.bar(sales_by_mall, x="shopping_mall", y="Total Sales", title="Sales by Shopping Mall", color="shopping_mall")
    st.plotly_chart(fig_mall)

    st.subheader("🏪 Shopping Mall Sales Distribution")
    fig_mall_pie = px.pie(sales_by_mall, names="shopping_mall", values="Total Sales", title="Shopping Mall Sales Share")
    st.plotly_chart(fig_mall_pie)

# Tab 3: Sales Trends
with tab3:
    st.subheader("📆 Sales Over Time")
    sales_trend = filtered_df.groupby("invoice_date")["Total Sales"].sum().reset_index()
    fig_trend = px.line(sales_trend, x="invoice_date", y="Total Sales", title="Sales Over Time")
    st.plotly_chart(fig_trend)

# Display Filtered Data Table
st.subheader("📜 Filtered Sales Data")
st.dataframe(filtered_df)

# ---- Export Data ----
st.subheader("📥 Download Filtered Data")

# Convert filtered data to CSV
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

# Download button
st.download_button(
    label="📂 Download as CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)

st.success("Dashboard Updated ✅")
