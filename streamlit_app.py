import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment, on July 14th")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ("ME")
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq="ME")).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## Your additions")

# Overall margin across all products/categories, used as the baseline for the delta in (5)
overall_margin = df["Profit"].sum() / df["Sales"].sum() * 100

st.write("### (1) Category")
category = st.selectbox("Category", df["Category"].unique())

st.write("### (2) Sub_Category")
sub_options = df[df["Category"] == category]["Sub_Category"].unique()
subs = st.multiselect("Sub_Category", sub_options)

filtered = df[(df["Category"] == category) & (df["Sub_Category"].isin(subs))]

if filtered.empty:
    st.info("Select at least one Sub_Category to see the chart and metrics.")
else:
    st.write("### (3) Sales for the selected items")
    
    # One column per selected Sub_Category (monthly sales), plus a Total column
    monthly_sales = (
        filtered.groupby([pd.Grouper(freq="ME"), "Sub_Category"])["Sales"]
        .sum()
        .unstack("Sub_Category", fill_value=0)
    )
    monthly_sales["Total"] = monthly_sales.sum(axis=1)
    st.line_chart(monthly_sales)

    st.write("### (4) Metrics for the selected items")
    total_sales = filtered["Sales"].sum()
    total_profit = filtered["Profit"].sum()
    margin = total_profit / total_sales * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    # (5) delta: selected margin minus the overall margin
    col3.metric("Overall Profit Margin", f"{margin:.2f}%", delta=f"{margin - overall_margin:.2f}%")
