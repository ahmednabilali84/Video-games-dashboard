import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="🎮 Video Game Sales Dashboard", layout="wide")
st.title("🎮 Video Game Sales Analysis Dashboard")
st.markdown("**Interactive Dashboard** - 16,598 Games")

# ====================== LOAD DATA ======================
@st.cache_data
def load_data():
    df = pd.read_csv('vgsales.csv')
    df['Year'] = df['Year'].fillna(df['Year'].median()).astype(int)
    df['Publisher'] = df['Publisher'].fillna('Unknown')
    
    def get_family(p):
        if any(x in str(p) for x in ['PS', 'PSP', 'PSV']): return 'PlayStation'
        if any(x in str(p) for x in ['X360', 'XB', 'XOne']): return 'Xbox'
        if any(x in str(p) for x in ['Wii', 'DS', '3DS', 'NES', 'SNES', 'N64', 'GC', 'GB', 'GBA']): return 'Nintendo'
        if p == 'PC': return 'PC'
        return 'Other'
    
    df['Platform_Family'] = df['Platform'].apply(get_family)
    return df

df = load_data()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("🔍 Filters")

genres = st.sidebar.multiselect("Genre", options=sorted(df['Genre'].unique()), 
                               default=['Action', 'Sports', 'Shooter'])

year_range = st.sidebar.slider("Year Range", 
                              int(df['Year'].min()), int(df['Year'].max()), (2000, 2016))

platforms = st.sidebar.multiselect("Platform", options=sorted(df['Platform'].unique()), default=[])

st.sidebar.header("🌍 Region Filter")
na_filter = st.sidebar.checkbox("North America (NA)", value=True)
eu_filter = st.sidebar.checkbox("Europe (EU)", value=True)
jp_filter = st.sidebar.checkbox("Japan (JP)", value=True)
other_filter = st.sidebar.checkbox("Other Regions", value=True)

# ====================== APPLY FILTERS ======================
filtered_df = df[
    (df['Genre'].isin(genres)) &
    (df['Year'].between(year_range[0], year_range[1]))
]

if platforms:
    filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]

# Region mask
region_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
if na_filter:    region_mask |= (filtered_df['NA_Sales'] > 0)
if eu_filter:    region_mask |= (filtered_df['EU_Sales'] > 0)
if jp_filter:    region_mask |= (filtered_df['JP_Sales'] > 0)
if other_filter: region_mask |= (filtered_df['Other_Sales'] > 0)

filtered_df = filtered_df[region_mask]

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📊 Distributions", 
    "📈 Trends", 
    "🔥 Insights", 
    "📍 Regional Analysis"
])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Games", f"{len(filtered_df):,}")
    with col2: st.metric("Total Global Sales", f"{filtered_df['Global_Sales'].sum():.1f}M")
    with col3: st.metric("Avg Sales/Game", f"{filtered_df['Global_Sales'].mean():.2f}M")
    with col4: st.metric("Top Genre", filtered_df.groupby('Genre')['Global_Sales'].sum().idxmax() if not filtered_df.empty else "N/A")

    st.subheader("Top 10 Best Selling Games")
    top10 = filtered_df.nlargest(10, 'Global_Sales')[['Name', 'Platform', 'Year', 'Genre', 'Global_Sales']]
    st.dataframe(top10, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        genre_sales = filtered_df.groupby('Genre')['Global_Sales'].sum().reset_index().sort_values('Global_Sales', ascending=False)
        st.plotly_chart(px.pie(genre_sales.head(10), names='Genre', values='Global_Sales', 
                             title="Top 10 Genres by Global Sales", hole=0.4), use_container_width=True)
    with col2:
        family_sales = filtered_df.groupby('Platform_Family')['Global_Sales'].sum().reset_index()
        st.plotly_chart(px.pie(family_sales, names='Platform_Family', values='Global_Sales',
                             title="Sales by Platform Family", hole=0.4), use_container_width=True)

with tab3:
    st.subheader("📈 Sales Trends Over Years")
    
    # Prepare yearly data
    yearly = filtered_df.groupby('Year').agg({
        'Global_Sales': 'sum',
        'NA_Sales': 'sum',
        'EU_Sales': 'sum',
        'JP_Sales': 'sum',
        'Other_Sales': 'sum'
    }).reset_index()
    
    # 1. Global Sales - Separate Chart
    fig_global = px.line(yearly, x='Year', y='Global_Sales', title="Global Sales Trend",markers=True, line_shape="spline")
    fig_global.update_layout(xaxis_title="Year", yaxis_title="Sales (Millions)")
    st.plotly_chart(fig_global, use_container_width=True)
    
    # 2. Regional Trends
    st.subheader("Regional Sales Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(px.line(yearly, x='Year', y='NA_Sales', title="North America Sales Trend", markers=True), use_container_width=True)
        st.plotly_chart(px.line(yearly, x='Year', y='EU_Sales', title="Europe Sales Trend", markers=True), use_container_width=True)
    
    with col2:
        st.plotly_chart(px.line(yearly, x='Year', y='JP_Sales', title="Japan Sales Trend", markers=True), use_container_width=True)
        st.plotly_chart(px.line(yearly, x='Year', y='Other_Sales', title="Other Regions Sales Trend", markers=True), use_container_width=True)
        
with tab4:
    st.subheader("Platform Family Performance")
    family_perf = filtered_df.groupby('Platform_Family').agg(
        Total_Sales=('Global_Sales', 'sum'),
        Avg_Sales=('Global_Sales', 'mean'),
        Games=('Global_Sales', 'count')
    ).round(2)
    st.dataframe(family_perf, use_container_width=True)

with tab5:
    st.subheader("Regional Sales Breakdown")
    region_data = pd.DataFrame({
        'Region': ['North America', 'Europe', 'Japan', 'Other'],
        'Sales': [filtered_df['NA_Sales'].sum(), filtered_df['EU_Sales'].sum(),
                 filtered_df['JP_Sales'].sum(), filtered_df['Other_Sales'].sum()]
    })
    st.plotly_chart(px.pie(region_data, names='Region', values='Sales', 
                          title="Sales Distribution by Region", hole=0.4), use_container_width=True)

st.caption("Built by Ahmed Nabil | Built with Streamlit")
