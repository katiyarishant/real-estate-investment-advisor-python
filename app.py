import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


st.set_page_config(
    page_title="Real Estate Investment Advisor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CUSTOM CSS STYLING


st.markdown("""
    <style>
    .big-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .good-box {
        background-color: #d4edda;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #28a745;
        text-align: center;
    }
    .bad-box {
        background-color: #f8d7da;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #dc3545;
        text-align: center;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #0c5460;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)



# DATA LOADING FUNCTION


@st.cache_data
def load_data():

    try:
        df = pd.read_csv('india_housing_prices.csv')

        # Create Price per Sq Ft if not present
        if 'Price_per_SqFt' not in df.columns:
            df['Price_per_SqFt'] = (df['Price_in_Lakhs'] * 100000) / df['Size_in_SqFt']

        # Create Age of Property if not present
        if 'Age_of_Property' not in df.columns:
            df['Age_of_Property'] = 2025 - df['Year_Built']

        return df
    except FileNotFoundError:
        st.error("⚠️ Error: 'india_housing_prices.csv' file not found!")
        st.info("Please place the CSV file in the same directory as this script.")
        return None
    except Exception as e:
        st.error(f"⚠️ Error loading data: {str(e)}")
        return None



# INVESTMENT SCORE CALCULATOR (RULE-BASED)


def calculate_investment_score(row, df):
    score = 0
    reasons = []

    try:
        price_per_sqft = float(row['Price_per_SqFt'])
        bhk = int(row['BHK'])
        age = float(row['Age_of_Property'])
        schools = int(row['Nearby_Schools'])
        hospitals = int(row['Nearby_Hospitals'])
        parking = int(row['Parking_Space'])
        transport = str(row['Public_Transport_Accessibility'])
        security = str(row['Security'])
        amenities = str(row['Amenities'])
        availability = str(row['Availability_Status'])
    except (ValueError, TypeError):
        return 50, ["⚠️ Unable to calculate score due to data format issues"]

    # Factor 1: Price per Sq Ft Analysis (Max 25 points)
    median_price = df['Price_per_SqFt'].median()
    if price_per_sqft <= median_price * 0.8:
        score += 25
        reasons.append("✅ Price is 20% below market median - Excellent value")
    elif price_per_sqft <= median_price:
        score += 15
        reasons.append("✅ Price is at or below market median - Good value")
    else:
        score -= 10
        reasons.append("❌ Price is above market median - Overpriced")

    # Factor 2: BHK Configuration (Max 20 points)
    if bhk >= 3:
        score += 20
        reasons.append("✅ 3+ BHK - High resale value and demand")
    elif bhk == 2:
        score += 10
        reasons.append("✅ 2 BHK - Popular configuration")

    # Factor 3: Property Age (Max 20 points)
    if age < 5:
        score += 20
        reasons.append("✅ New property (< 5 years) - Low maintenance")
    elif age < 10:
        score += 10
        reasons.append("✅ Relatively new property (< 10 years)")
    elif age > 20:
        score -= 15
        reasons.append("❌ Old property (> 20 years) - High maintenance risk")

    # Factor 4: Infrastructure Score (Max 15 points)
    infra = schools + hospitals
    if infra >= 6:
        score += 15
        reasons.append("✅ Excellent infrastructure (6+ facilities nearby)")
    elif infra >= 4:
        score += 10
        reasons.append("✅ Good infrastructure (4+ facilities nearby)")
    else:
        reasons.append("⚠️ Limited infrastructure nearby")

    # Factor 5: Public Transport (Max 10 points)
    if transport == 'High':
        score += 10
        reasons.append("✅ High public transport accessibility")
    elif transport == 'Medium':
        score += 5
        reasons.append("✅ Moderate transport accessibility")

    # Factor 6: Security (Max 5 points)
    if security == 'Yes':
        score += 5
        reasons.append("✅ Property has security features")

    # Factor 7: Amenities (Max 5 points)
    if amenities not in ['None', 'No', 'nan', '']:
        score += 5
        reasons.append("✅ Property has amenities (Gym/Pool/Club)")

    # Factor 8: Parking (Max 5 points)
    if parking >= 2:
        score += 5
        reasons.append("✅ Multiple parking spaces available")

    # Factor 9: Availability (Max 10 points)
    if availability in ['Available', 'Ready to Move']:
        score += 10
        reasons.append("✅ Ready to move - No construction delays")


    final_score = max(0, min(100, score))

    return final_score, reasons



# FUTURE PRICE CALCULATOR (RULE-BASED)


def calculate_future_price(row, df):

    base_growth_rate = 0.08

    try:
        bhk = int(row['BHK'])
        age = float(row['Age_of_Property'])
        price = float(row['Price_in_Lakhs'])
        schools = int(row['Nearby_Schools'])
        hospitals = int(row['Nearby_Hospitals'])
        transport = str(row['Public_Transport_Accessibility'])
        security = str(row['Security'])
        amenities = str(row['Amenities'])
    except (ValueError, TypeError):
        # Return default 40% growth if data issues
        return price * 1.4, 40.0, 8.0

    # Adjust growth rate based on factors
    if bhk >= 3:
        base_growth_rate += 0.01  # +1% for larger properties

    if age < 5:
        base_growth_rate += 0.01  # +1% for new properties

    if transport == 'High':
        base_growth_rate += 0.015  # +1.5% for good connectivity

    if (schools + hospitals) >= 5:
        base_growth_rate += 0.01  # +1% for good infrastructure

    if security == 'Yes' and amenities not in ['None', 'No', 'nan', '']:
        base_growth_rate += 0.005  # +0.5% for security + amenities

    if age > 20:
        base_growth_rate -= 0.02  # -2% for old properties

    # Calculate future price using compound growth
    future_price = price * ((1 + base_growth_rate) ** 5)

    # Calculate appreciation percentage
    appreciation = ((future_price - price) / price) * 100

    # Return annual growth rate as percentage
    annual_growth = base_growth_rate * 100

    return future_price, appreciation, annual_growth



# MAIN APPLICATION

def main():

    # Header
    st.markdown("<h1 class='big-title'>🏠 Real Estate Investment Advisor</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Make Smart Property Investment Decisions with Data-Driven Insights</p>",
                unsafe_allow_html=True)


    df = load_data()

    if df is None:
        st.stop()

    # Sidebar Navigation
    st.sidebar.title("🔍 Navigation Menu")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Select Page:",
        ["📊 Dashboard & EDA", "🎯 Investment Predictor"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Dataset Info:**
    - Total Properties: {len(df):,}
    - Cities: {df['City'].nunique()}
    - Property Types: {df['Property_Type'].nunique()}
    """)

    # Route to selected page
    if page == "📊 Dashboard & EDA":
        show_dashboard(df)
    else:
        show_predictor(df)


# DASHBOARD PAGE

def show_dashboard(df):

    st.header("📊 Exploratory Data Analysis Dashboard")
    st.markdown("Analyze property trends, patterns, and insights from the dataset")


    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📍 Total Properties", f"{len(df):,}")
    with col2:
        st.metric("💰 Avg Price", f"₹{df['Price_in_Lakhs'].mean():.1f}L")
    with col3:
        st.metric("📏 Avg Size", f"{df['Size_in_SqFt'].mean():.0f} sqft")
    with col4:
        st.metric("🏙️ Cities", df['City'].nunique())

    st.markdown("---")

    # Analysis Section Selector
    analysis_type = st.selectbox(
        "📋 Select Analysis Section:",
        [
            "💰 Price Analysis",
            "📏 Size Analysis",
            "📍 Location Analysis",
            "🏗️ Property Features",
            "💎 Investment & Amenities"
        ]
    )

    # Route to analysis functions
    if "Price Analysis" in analysis_type:
        show_price_analysis(df)
    elif "Size Analysis" in analysis_type:
        show_size_analysis(df)
    elif "Location Analysis" in analysis_type:
        show_location_analysis(df)
    elif "Property Features" in analysis_type:
        show_features_analysis(df)
    else:
        show_investment_analysis(df)



# PRICE ANALYSIS


def show_price_analysis(df):

    st.subheader("💰 Price Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Property Price Distribution**")
        fig = px.histogram(
            df, x='Price_in_Lakhs', nbins=30,
            title='Property Price Distribution',
            labels={'Price_in_Lakhs': 'Price (Lakhs)', 'count': 'Number of Properties'},
            color_discrete_sequence=['#3498db']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"""
        📊 **Key Insights:**
        - Average Price: ₹{df['Price_in_Lakhs'].mean():.2f} Lakhs
        - Median Price: ₹{df['Price_in_Lakhs'].median():.2f} Lakhs
        - Price Range: ₹{df['Price_in_Lakhs'].min():.1f}L - ₹{df['Price_in_Lakhs'].max():.1f}L
        """)

    with col2:
        st.markdown("**Average Price by Property Type**")
        avg_price = df.groupby('Property_Type')['Price_in_Lakhs'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=avg_price.index, y=avg_price.values,
            title='Average Price by Property Type',
            labels={'x': 'Property Type', 'y': 'Average Price (Lakhs)'},
            color=avg_price.values,
            color_continuous_scale='viridis'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        most_expensive = avg_price.index[0]
        st.info(f"""
        📊 **Key Insights:**
        - Most Expensive: {most_expensive}
        - Price: ₹{avg_price.values[0]:.2f} Lakhs
        """)

    st.markdown("**Relationship between Property Size and Price**")
    sample_df = df.sample(min(1000, len(df)))
    fig = px.scatter(
        sample_df, x='Size_in_SqFt', y='Price_in_Lakhs',
        title='Property Size vs Price (Colored by BHK)',
        labels={'Size_in_SqFt': 'Size (Sq Ft)', 'Price_in_Lakhs': 'Price (Lakhs)'},
        color='BHK',
        opacity=0.6
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    correlation = df['Size_in_SqFt'].corr(df['Price_in_Lakhs'])
    st.info(f"📊 **Correlation:** Size and Price have a correlation of {correlation:.3f}")



# SIZE ANALYSIS


def show_size_analysis(df):

    st.subheader("📏 Property Size Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Property Size Distribution**")
        fig = px.histogram(
            df, x='Size_in_SqFt', nbins=30,
            title='Property Size Distribution',
            labels={'Size_in_SqFt': 'Size (Sq Ft)', 'count': 'Number of Properties'},
            color_discrete_sequence=['#2ecc71']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"""
        📊 **Key Insights:**
        - Average Size: {df['Size_in_SqFt'].mean():.0f} Sq Ft
        - Median Size: {df['Size_in_SqFt'].median():.0f} Sq Ft
        """)

    with col2:
        st.markdown("**BHK Distribution**")
        bhk_count = df['BHK'].value_counts().sort_index()
        fig = px.bar(
            x=bhk_count.index, y=bhk_count.values,
            title='Number of Properties by BHK',
            labels={'x': 'BHK', 'y': 'Number of Properties'},
            color=bhk_count.values,
            color_continuous_scale='blues'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        most_common_bhk = bhk_count.index[0]
        st.info(f"""
        📊 **Key Insights:**
        - Most Common: {most_common_bhk} BHK
        - Count: {bhk_count.values[0]:,} properties
        """)

    st.markdown("**Price per Sq Ft Distribution (Outlier Detection)**")
    fig = px.box(
        df, y='Price_per_SqFt',
        title='Price per Sq Ft - Box Plot',
        labels={'Price_per_SqFt': 'Price per Sq Ft (₹)'},
        color_discrete_sequence=['#e74c3c']
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    Q1 = df['Price_per_SqFt'].quantile(0.25)
    Q3 = df['Price_per_SqFt'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df[(df['Price_per_SqFt'] < Q1 - 1.5 * IQR) | (df['Price_per_SqFt'] > Q3 + 1.5 * IQR)]

    st.info(f"""
    📊 **Outlier Analysis:**
    - Total Outliers: {len(outliers):,} ({len(outliers) / len(df) * 100:.2f}%)
    - These properties have unusual price per sq ft values
    """)



# LOCATION ANALYSIS


def show_location_analysis(df):

    st.subheader("📍 Location-Based Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Top 10 States by Average Price per Sq Ft**")
        state_price = df.groupby('State')['Price_per_SqFt'].mean().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=state_price.index, y=state_price.values,
            title='Top 10 States',
            labels={'x': 'State', 'y': 'Avg Price per Sq Ft (₹)'},
            color=state_price.values,
            color_continuous_scale='reds'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Top 10 Most Expensive Cities**")
        city_price = df.groupby('City')['Price_in_Lakhs'].mean().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=city_price.index, y=city_price.values,
            title='Top 10 Expensive Cities',
            labels={'x': 'City', 'y': 'Average Price (Lakhs)'},
            color=city_price.values,
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Property Age by Locality (Top 10 Oldest Localities)**")
    locality_age = df.groupby('Locality')['Age_of_Property'].median().sort_values(ascending=False).head(10)
    fig = px.bar(
        x=locality_age.index, y=locality_age.values,
        title='Oldest Localities by Median Property Age',
        labels={'x': 'Locality', 'y': 'Median Age (Years)'},
        color=locality_age.values,
        color_continuous_scale='purples'
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True)



# FEATURES ANALYSIS


def show_features_analysis(df):

    st.subheader("🏗️ Property Features Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Impact of Nearby Schools on Price per Sq Ft**")
        school_price = df.groupby('Nearby_Schools')['Price_per_SqFt'].mean()
        fig = px.line(
            x=school_price.index, y=school_price.values, markers=True,
            title='Schools vs Price per Sq Ft',
            labels={'x': 'Number of Schools', 'y': 'Avg Price per Sq Ft (₹)'}
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Impact of Nearby Hospitals on Price per Sq Ft**")
        hospital_price = df.groupby('Nearby_Hospitals')['Price_per_SqFt'].mean()
        fig = px.line(
            x=hospital_price.index, y=hospital_price.values, markers=True,
            title='Hospitals vs Price per Sq Ft',
            labels={'x': 'Number of Hospitals', 'y': 'Avg Price per Sq Ft (₹)'},
            color_discrete_sequence=['#2ecc71']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Price by Furnished Status**")
        furnished = df.groupby('Furnished_Status')['Price_in_Lakhs'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=furnished.index, y=furnished.values,
            title='Furnished Status vs Price',
            labels={'x': 'Furnished Status', 'y': 'Avg Price (Lakhs)'},
            color=furnished.values,
            color_continuous_scale='greens'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Price by Property Facing Direction**")
        facing = df.groupby('Facing')['Price_per_SqFt'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=facing.index, y=facing.values,
            title='Facing Direction vs Price',
            labels={'x': 'Facing', 'y': 'Avg Price per Sq Ft (₹)'},
            color=facing.values,
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)



# INVESTMENT ANALYSIS


def show_investment_analysis(df):

    st.subheader("💎 Investment & Amenities Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Properties by Owner Type**")
        owner = df['Owner_Type'].value_counts()
        fig = px.pie(
            values=owner.values, names=owner.index,
            title='Owner Type Distribution',
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Properties by Availability Status**")
        avail = df['Availability_Status'].value_counts()
        fig = px.pie(
            values=avail.values, names=avail.index,
            title='Availability Status Distribution',
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Parking Space Impact on Price**")
        parking = df.groupby('Parking_Space')['Price_in_Lakhs'].mean()
        fig = px.bar(
            x=parking.index, y=parking.values,
            title='Parking vs Price',
            labels={'x': 'Parking Spaces', 'y': 'Avg Price (Lakhs)'},
            color=parking.values,
            color_continuous_scale='purples'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Transport Accessibility vs Price**")
        transport = df.groupby('Public_Transport_Accessibility')['Price_per_SqFt'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=transport.index, y=transport.values,
            title='Transport vs Price',
            labels={'x': 'Transport Access', 'y': 'Avg Price per Sq Ft (₹)'},
            color=transport.values,
            color_continuous_scale='teal'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Top 10 Amenities by Price Impact**")
    amenities = df.groupby('Amenities')['Price_per_SqFt'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(
        x=amenities.index, y=amenities.values,
        title='Top 10 Amenities',
        labels={'x': 'Amenities', 'y': 'Avg Price per Sq Ft (₹)'},
        color=amenities.values,
        color_continuous_scale='burg'
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True)



# INVESTMENT PREDICTOR PAGE


def show_predictor(df):

    st.header("🎯 Property Investment Predictor")
    st.markdown("Enter property details below to get intelligent investment analysis and price forecast")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🏘️ Basic Information")
        prop_type = st.selectbox("Property Type", sorted(df['Property_Type'].unique()))
        bhk = st.number_input("BHK", min_value=1, max_value=10, value=2, step=1)
        size = st.number_input("Size (Sq Ft)", min_value=100, max_value=10000, value=1000, step=50)
        price = st.number_input("Price (Lakhs)", min_value=1.0, max_value=1000.0, value=50.0, step=1.0)
        year = st.number_input("Year Built", min_value=1950, max_value=2024, value=2015, step=1)

    with col2:
        st.subheader("🏗️ Infrastructure")
        schools = st.number_input("Nearby Schools", min_value=0, max_value=20, value=3, step=1)
        hospitals = st.number_input("Nearby Hospitals", min_value=0, max_value=20, value=2, step=1)
        transport = st.selectbox("Public Transport Access", ['High', 'Medium', 'Low'])
        parking = st.number_input("Parking Spaces", min_value=0, max_value=10, value=1, step=1)

    with col3:
        st.subheader("🎨 Features & Amenities")
        furnished = st.selectbox("Furnished Status", sorted(df['Furnished_Status'].unique()))
        security = st.selectbox("Security", ['Yes', 'No'])
        amenities = st.selectbox("Amenities", sorted(df['Amenities'].unique()))
        availability = st.selectbox("Availability Status", sorted(df['Availability_Status'].unique()))


    st.markdown("---")

    # Analyze Button

    if st.button("🔮 Analyze This Property", type="primary", use_container_width=True):

        # Create property data dictionary
        property_data = {
            'Property_Type': prop_type,
            'BHK': bhk,
            'Size_in_SqFt': size,
            'Price_in_Lakhs': price,
            'Year_Built': year,
            'Age_of_Property': 2025 - year,
            'Price_per_SqFt': (price * 100000) / size,
            'Nearby_Schools': schools,
            'Nearby_Hospitals': hospitals,
            'Public_Transport_Accessibility': transport,
            'Parking_Space': parking,
            'Furnished_Status': furnished,
            'Security': security,
            'Amenities': amenities,
            'Availability_Status': availability
        }

        # Calculate investment score and future price
        score, reasons = calculate_investment_score(property_data, df)
        future_price, appreciation, growth = calculate_future_price(property_data, df)

        st.markdown("---")

        # Display Results
        col1, col2 = st.columns(2)

        with col1:
            if score >= 60:
                st.markdown(f"""
                <div class='good-box'>
                    <h2>✅ GOOD INVESTMENT</h2>
                    <h1 style='color: #28a745;'>{score}/100</h1>
                    <p style='font-size: 1.1rem; margin-top: 1rem;'>
                        This property shows strong investment potential based on market analysis
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='bad-box'>
                    <h2>⚠️ RISKY INVESTMENT</h2>
                    <h1 style='color: #dc3545;'>{score}/100</h1>
                    <p style='font-size: 1.1rem; margin-top: 1rem;'>
                        Consider other options or negotiate the price
                    </p>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 10px; color: white; text-align: center;'>
                <h3 style='margin-bottom: 0.5rem;'>📈 Estimated Price After 5 Years</h3>
                <h1 style='font-size: 2.5rem; margin: 1rem 0;'>₹{future_price:.2f}L</h1>
                <h3 style='color: #90EE90; margin-bottom: 0.5rem;'>+{appreciation:.1f}% Total Growth</h3>
                <p style='font-size: 1rem;'>Annual Growth Rate: {growth:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Investment Score Breakdown")
            st.markdown("**Factors Contributing to the Score:**")
            for reason in reasons:
                st.markdown(f"- {reason}")

        with col2:
            st.subheader("💡 Key Property Metrics")
            st.metric("Current Price per Sq Ft", f"₹{property_data['Price_per_SqFt']:.2f}")
            st.metric("Market Median Price/SqFt", f"₹{df['Price_per_SqFt'].median():.2f}")
            st.metric("Property Age", f"{property_data['Age_of_Property']} years")
            st.metric("Infrastructure Score", f"{schools + hospitals}/40")

            if property_data['Price_per_SqFt'] < df['Price_per_SqFt'].median():
                st.success("✅ Price is below market median")
            else:
                st.warning("⚠️ Price is above market median")

        st.markdown("---")
        st.subheader("📊 Market Comparison with Similar Properties")

        # Filter similar properties
        similar = df[
            (df['BHK'] == bhk) &
            (df['Property_Type'] == prop_type) &
            (df['Size_in_SqFt'].between(size * 0.8, size * 1.2))
            ]

        if len(similar) > 0:
            col1, col2 = st.columns(2)

            with col1:
                fig = go.Figure()
                fig.add_trace(go.Box(
                    y=similar['Price_in_Lakhs'],
                    name='Market Range',
                    marker_color='lightblue'
                ))
                fig.add_trace(go.Scatter(
                    x=[0], y=[price],
                    mode='markers',
                    marker=dict(size=15, color='red', symbol='star'),
                    name='Your Property'
                ))
                fig.update_layout(
                    title='Price Comparison (Lakhs)',
                    yaxis_title='Price (Lakhs)',
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = go.Figure()
                fig.add_trace(go.Box(
                    y=similar['Price_per_SqFt'],
                    name='Market Range',
                    marker_color='lightgreen'
                ))
                fig.add_trace(go.Scatter(
                    x=[0], y=[property_data['Price_per_SqFt']],
                    mode='markers',
                    marker=dict(size=15, color='red', symbol='star'),
                    name='Your Property'
                ))
                fig.update_layout(
                    title='Price per Sq Ft Comparison',
                    yaxis_title='Price per Sq Ft (₹)',
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            st.info(f"""
            📊 **Similar Properties Found:** {len(similar):,} properties with same BHK, 
            type, and similar size (±20%)
            """)
        else:
            st.warning("⚠️ No similar properties found in the dataset for comparison")

        # Investment Recommendation
        st.markdown("---")
        st.subheader("💼 Investment Recommendation")

        if score >= 80:
            st.success("""
            🌟 **Highly Recommended!** This property shows excellent investment potential 
            with strong fundamentals and good growth prospects.
            """)
        elif score >= 60:
            st.info("""
            👍 **Recommended:** This is a good investment opportunity with decent fundamentals. 
            Consider negotiating the price for better returns.
            """)
        else:
            st.warning("""
            ⚠️ **Not Recommended:** This property has several concerns. Consider looking for 
            better alternatives or negotiate a significantly lower price.
            """)



if __name__ == "__main__":
    main()