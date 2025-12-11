import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Aircraft Crashes Dashboard",
    layout="wide",
    page_icon="✈️"
)

# --------------------------------------------------------
# DARK THEME CSS
# --------------------------------------------------------
st.markdown("""
    <style>
    .reportview-container, .main, .block-container {
        background-color: black !important;
        color: white !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #111 !important;
        color: white !important;
    }
    .st-bf, .st-c1, .stMarkdown {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------
df = pd.read_csv("aircrahesFullDataUpdated_2024.csv")
df.columns = df.columns.str.strip()
df["Country/Region"] = df["Country/Region"].fillna("Unknown")
df["Month"] = df["Month"].fillna("Unknown")
df["Aboard"] = df["Aboard"].fillna(0)
df["Fatalities (air)"] = df["Fatalities (air)"].fillna(0)

# --------------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------------
st.sidebar.header("FILTERS")
country_filter = st.sidebar.multiselect("Select Country", df["Country/Region"].unique())
manufacturer_filter = st.sidebar.multiselect("Select Manufacturer", df["Aircraft Manufacturer"].unique())
month_filter = st.sidebar.multiselect("Select Month", df["Month"].unique())
year_filter = st.sidebar.slider(
    "Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (int(df["Year"].min()), int(df["Year"].max()))
)

# --------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------
filtered_df = df.copy()
if country_filter:
    filtered_df = filtered_df[filtered_df["Country/Region"].isin(country_filter)]
if manufacturer_filter:
    filtered_df = filtered_df[filtered_df["Aircraft Manufacturer"].isin(manufacturer_filter)]
if month_filter:
    filtered_df = filtered_df[filtered_df["Month"].isin(month_filter)]

filtered_df = filtered_df[(filtered_df["Year"] >= year_filter[0]) & (filtered_df["Year"] <= year_filter[1])]

# --------------------------------------------------------
# KPIs
# --------------------------------------------------------
st.markdown("### ✈️ Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_crashes = len(filtered_df)
total_fatalities = filtered_df["Fatalities (air)"].sum()
avg_fatalities = filtered_df["Fatalities (air)"].mean()
most_dangerous_country = filtered_df.groupby("Country/Region")["Fatalities (air)"].sum().idxmax()

col1.metric("Total Crashes", total_crashes)
col2.metric("Total Fatalities", total_fatalities)
col3.metric("Average Fatalities per Crash", f"{avg_fatalities:.1f}")
col4.metric("Most Dangerous Country", most_dangerous_country)

# --------------------------------------------------------
# INTERACTIVE PLOTLY CHARTS
# --------------------------------------------------------

# Crashes per Year
st.subheader("📈 Crashes per Year")
crashes_per_year = filtered_df.groupby("Year").size().reset_index(name="Crashes")
fig_year = px.line(crashes_per_year, x="Year", y="Crashes", markers=True, 
                   title="Crashes Over Time", template="plotly_dark")
st.plotly_chart(fig_year, use_container_width=True)

# Top 10 Countries
st.subheader("🌍 Top 10 Countries by Crashes")
top_countries = filtered_df["Country/Region"].value_counts().head(10).reset_index()
top_countries.columns = ["Country", "Crashes"]
fig_country = px.bar(top_countries, x="Crashes", y="Country", orientation='h', 
                     title="Top 10 Countries", template="plotly_dark")
st.plotly_chart(fig_country, use_container_width=True)

# Top 10 Manufacturers
st.subheader("🏭 Top 10 Manufacturers")
top_manufacturers = filtered_df["Aircraft Manufacturer"].value_counts().head(10).reset_index()
top_manufacturers.columns = ["Manufacturer", "Crashes"]
fig_manufacturer = px.bar(top_manufacturers, x="Crashes", y="Manufacturer", orientation='h', 
                          title="Top 10 Manufacturers", template="plotly_dark")
st.plotly_chart(fig_manufacturer, use_container_width=True)

# Fatalities vs Aboard
st.subheader("💥 Fatalities vs People Aboard")
fig_scatter = px.scatter(filtered_df, x="Aboard", y="Fatalities (air)", 
                         hover_data=["Aircraft", "Operator", "Location", "Year"], 
                         title="Fatalities vs People Aboard", template="plotly_dark")
st.plotly_chart(fig_scatter, use_container_width=True)

# Survival Rate Distribution
st.subheader("🟢 Survival Rate Distribution")
filtered_df["Survival Rate"] = ((filtered_df["Aboard"] - filtered_df["Fatalities (air)"]) / 
                                filtered_df["Aboard"].replace(0,1)) * 100
fig_survival = px.histogram(filtered_df, x="Survival Rate", nbins=30, title="Survival Rate Distribution", template="plotly_dark")
st.plotly_chart(fig_survival, use_container_width=True)

# Crashes by Month
st.subheader("📅 Crashes by Month")
crashes_by_month = filtered_df["Month"].value_counts().reset_index()
crashes_by_month.columns = ["Month", "Crashes"]
fig_month = px.bar(crashes_by_month, x="Month", y="Crashes", title="Crashes by Month", template="plotly_dark")
st.plotly_chart(fig_month, use_container_width=True)

# Crashes per Decade
st.subheader("📊 Crashes per Decade")
filtered_df["Decade"] = (filtered_df["Year"] // 10) * 10
crashes_per_decade = filtered_df["Decade"].value_counts().sort_index().reset_index()
crashes_per_decade.columns = ["Decade", "Crashes"]
fig_decade = px.bar(crashes_per_decade, x="Decade", y="Crashes", title="Crashes per Decade", template="plotly_dark")
st.plotly_chart(fig_decade, use_container_width=True)

# Top 10 Deadliest Crashes Table
st.subheader("🔥 Top 10 Deadliest Crashes")
deadliest = filtered_df.sort_values("Fatalities (air)", ascending=False).head(10)
st.dataframe(deadliest[["Year","Aircraft","Operator","Location","Fatalities (air)"]])
