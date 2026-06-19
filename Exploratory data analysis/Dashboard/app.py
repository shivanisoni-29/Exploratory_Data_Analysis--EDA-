
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Amazon Sales Dashboard", page_icon="🛒", layout="wide")

st.markdown("""
<style>
.main {background-color:#f7f9fc;}
h1 {color:#0F4C81;}
div[data-testid="stMetric"]{
    background:#ffffff;
    padding:15px;
    border-radius:10px;
    border:1px solid #ddd;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "Amazon Sale Report.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    if "New" in df.columns:
        df.drop(columns=["New"], inplace=True)
    if "PendingS" in df.columns:
        df.drop(columns=["PendingS"], inplace=True)

    df = df.dropna(subset=["Amount"])
    df["fulfilled-by"] = df["fulfilled-by"].fillna("Merchant")

    df.dropna(subset=[
        "ship-city",
        "ship-state",
        "ship-postal-code",
        "ship-country"
    ], inplace=True)

    df["Date"] = pd.to_datetime(df["Date"])

    df["Month"] = df["Date"].dt.month_name()
    df["Year"] = df["Date"].dt.year

    return df

df = load_data()

st.sidebar.title("🔎 Filters")

months = sorted(df["Month"].unique())
states = sorted(df["ship-state"].unique())
categories = sorted(df["Category"].unique())
statuses = sorted(df["Status"].unique())

selected_month = st.sidebar.multiselect("Month", months, default=months)
selected_state = st.sidebar.multiselect("State", states, default=states)
selected_category = st.sidebar.multiselect("Category", categories, default=categories)
selected_status = st.sidebar.multiselect("Status", statuses, default=statuses)

filtered_df = df[
    (df["Month"].isin(selected_month)) &
    (df["ship-state"].isin(selected_state)) &
    (df["Category"].isin(selected_category)) &
    (df["Status"].isin(selected_status))
]

st.title("Amazon Sales Dashboard")
st.caption("Interactive dashboard built using Streamlit and Plotly")

c1,c2,c3,c4 = st.columns(4)

c1.metric("💰 Revenue", f"₹{filtered_df['Amount'].sum():,.0f}")
c2.metric("📦 Orders", f"{len(filtered_df):,}")
c3.metric("🛍 Quantity", f"{filtered_df['Qty'].sum():,}")
avg = filtered_df["Amount"].mean() if len(filtered_df) else 0
c4.metric("⭐ Avg Order", f"₹{avg:,.2f}")

st.divider()

left,right = st.columns(2)

with left:
    cat = filtered_df.groupby("Category",as_index=False)["Amount"].sum().sort_values("Amount",ascending=False)
    fig = px.bar(cat,x="Category",y="Amount",color="Category",title="Revenue by Category")
    st.plotly_chart(fig,use_container_width=True)

with right:
    month_order=["January","February","March","April","May","June","July","August","September","October","November","December"]
    ms = filtered_df.groupby("Month",as_index=False)["Amount"].sum()
    ms["Month"]=pd.Categorical(ms["Month"],categories=month_order,ordered=True)
    ms=ms.sort_values("Month")
    fig=px.line(ms,x="Month",y="Amount",markers=True,title="Monthly Sales Trend")
    st.plotly_chart(fig,use_container_width=True)

left,right = st.columns(2)

with left:
    state = filtered_df.groupby("ship-state",as_index=False)["Amount"].sum().sort_values("Amount",ascending=False).head(10)
    fig=px.bar(state,x="Amount",y="ship-state",orientation="h",title="Top 10 States by Revenue")
    st.plotly_chart(fig,use_container_width=True)

with right:
    city = filtered_df["ship-city"].value_counts().head(10).reset_index()
    city.columns=["City","Orders"]
    fig=px.bar(city,x="Orders",y="City",orientation="h",title="Top 10 Cities by Orders")
    st.plotly_chart(fig,use_container_width=True)

left,right = st.columns(2)

with left:
    status = filtered_df["Status"].value_counts().reset_index()
    status.columns=["Status","Orders"]
    fig=px.pie(status,names="Status",values="Orders",title="Order Status")
    st.plotly_chart(fig,use_container_width=True)

with right:
    b2b = filtered_df["B2B"].replace({True:"B2B",False:"B2C"}).value_counts().reset_index()
    b2b.columns=["Type","Orders"]
    fig=px.pie(b2b,names="Type",values="Orders",title="B2B vs B2C")
    st.plotly_chart(fig,use_container_width=True)

st.divider()
st.subheader(" Dynamic Business Insights")

if not filtered_df.empty:

    # Top Performers
    top_category = filtered_df.groupby("Category")["Amount"].sum().idxmax()
    top_state = filtered_df.groupby("ship-state")["Amount"].sum().idxmax()
    top_city = filtered_df["ship-city"].value_counts().idxmax()
    top_size = filtered_df["Size"].value_counts().idxmax()
    top_fulfilment = filtered_df["Fulfilment"].value_counts().idxmax()

    # Revenue Metrics
    total_revenue = filtered_df["Amount"].sum()
    avg_order = filtered_df["Amount"].mean()
    total_orders = len(filtered_df)
    total_quantity = filtered_df["Qty"].sum()

    # Order Status
    cancelled_orders = filtered_df["Status"].str.contains(
        "Cancelled", case=False, na=False
    ).sum()

    shipped_orders = filtered_df["Status"].str.contains(
        "Shipped", case=False, na=False
    ).sum()

    cancellation_rate = (cancelled_orders / total_orders) * 100
    shipped_rate = (shipped_orders / total_orders) * 100

    # B2B & B2C
    b2b_orders = filtered_df["B2B"].sum()
    b2c_orders = total_orders - b2b_orders

    # Highest Revenue Month
    top_month = (
        filtered_df.groupby("Month")["Amount"]
        .sum()
        .idxmax()
    )

    # Highest Revenue Category Value
    highest_category_revenue = (
        filtered_df.groupby("Category")["Amount"]
        .sum()
        .max()
    )

    # Insights
    st.success(f" Highest Revenue Category: **{top_category}**")
    st.success(f" Top Revenue State: **{top_state}**")
    st.success(f" City with Most Orders: **{top_city}**")

    st.info(f"📅 Highest Revenue Month: **{top_month}**")
    st.info(f" Most Purchased Size: **{top_size}**")
    st.info(f" Most Used Fulfilment Method: **{top_fulfilment}**")
    st.warning(f" Cancellation Rate: {cancellation_rate:.2f}%")
    st.success(f" Shipped Orders: {shipped_rate:.2f}%")
    st.info(f" Total Revenue: ₹{filtered_df['Amount'].sum():,.0f}")
    st.info(f" Average Order Value: ₹{filtered_df['Amount'].mean():.2f}")
    st.info(f" B2B Orders: {b2b_orders:,}")
    st.info(f" B2C Orders: {b2c_orders:,}")

    st.info(f" Highest Category Revenue: ₹{highest_category_revenue:,.0f}")

else:
    st.warning("No data available for selected filters.")

st.divider()

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.subheader(" Top 5 Revenue Generating Categories")

top5 = (
    filtered_df.groupby("Category")["Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

top5["Revenue Contribution (%)"] = (
    top5["Amount"] / total_revenue * 100
).round(2)

st.dataframe(top5, use_container_width=True)

st.download_button(
    "📥 Download Filtered Dataset",
    csv,
    "filtered_amazon_sales.csv",
    "text/csv"
)

with st.expander("View Filtered Dataset"):
    st.dataframe(filtered_df, use_container_width=True)
