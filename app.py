import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="🎮 Video Game Sales Dashboard",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Video Game Sales Analysis Dashboard")
st.markdown("**Interactive Dashboard** for 16,598 Video Games | Built from your Jupyter Notebook")

# ====================== LOAD & CLEAN DATA ======================
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('vgsales.csv')
    
    # Cleaning (as in your notebook)
    df['Year'] = df['Year'].fillna(df['Year'].median()).astype(int)
    df['Publisher'] = df['Publisher'].fillna('Unknown')
    
    # Extra useful columns
    df['Platform_Family'] = df['Platform'].apply(lambda x: 
        'PlayStation' if any(p in str(x) for p in ['PS','PSP','PSV']) else
        'Xbox' if any(p in str(x) for p in ['X360','XB','XOne']) else
        'Nintendo' if any(p in str(x) for p in ['Wii','DS','3DS','NES','SNES','N64','GC','GB','GBA']) else
        'PC' if x == 'PC' else 'Other')
    
    return df

df = load_and_clean_data()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("🔍 Filters")

selected_genres = st.sidebar.multiselect(
    "Select Genres", 
    options=sorted(df['Genre'].unique()),
    default=['Action', 'Sports', 'Shooter']
)

year_range = st.sidebar.slider(
    "Year Range",
    int(df['Year'].min()),
    int(df['Year'].max()),
    (2000, 2016)
)

selected_platforms = st.sidebar.multiselect(
    "Select Platforms",
    options=sorted(df['Platform'].unique()),
    default=[]
)

# Apply filters
filtered_df = df[
    (df['Genre'].isin(selected_genres)) &
    (df['Year'].between(year_range[0], year_range[1]))
]

if selected_platforms:
    filtered_df = filtered_df[filtered_df['Platform'].isin(selected_platforms)]

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🥧 Pie Charts", "📈 Trends", "🔥 Insights"])

with tab1:
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Games", f"{len(filtered_df):,}")
    with col2:
        st.metric("Total Global Sales", f"{filtered_df['Global_Sales'].sum():.1f}M")
    with col3:
        st.metric("Average Sales/Game", f"{filtered_df['Global_Sales'].mean():.2f}M")
    with col4:
        st.metric("Top Publisher", filtered_df.groupby('Publisher')['Global_Sales'].sum().idxmax())

    st.subheader("Top 10 Best-Selling Games")
    top10 = filtered_df.nlargest(10, 'Global_Sales')[['Rank','Name','Platform','Year','Genre','Global_Sales']]
    st.dataframe(top10, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        genre_sales = filtered_df.groupby('Genre')['Global_Sales'].sum().reset_index().sort_values('Global_Sales', ascending=False)
        fig_pie = px.pie(genre_sales.head(10), names='Genre', values='Global_Sales', 
                        title="Top 10 Genres by Global Sales", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        family_sales = filtered_df.groupby('Platform_Family')['Global_Sales'].sum().reset_index()
        fig_family = px.pie(family_sales, names='Platform_Family', values='Global_Sales',
                           title="Sales by Platform Family", hole=0.4)
        st.plotly_chart(fig_family, use_container_width=True)

with tab3:
    yearly = filtered_df.groupby('Year')['Global_Sales'].sum().reset_index()
    fig_line = px.line(yearly, x='Year', y='Global_Sales', title="Sales Trend Over Time")
    st.plotly_chart(fig_line, use_container_width=True)

with tab4:
    st.subheader("Platform Family Performance")
    family_perf = filtered_df.groupby('Platform_Family').agg(
        Total_Sales=('Global_Sales', 'sum'),
        Avg_Sales=('Global_Sales', 'mean'),
        Count=('Global_Sales', 'count')
    ).round(2)
    st.dataframe(family_perf, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Built with Streamlit | Data: vgsales.csv | Ahmed's Project")