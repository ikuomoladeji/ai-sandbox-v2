"""
AI-Powered TPRM System - Interactive Dashboard
Real-time vendor risk analytics and portfolio insights using Streamlit
"""
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from config import Config

# Page configuration
st.set_page_config(
    page_title="TPRM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .risk-high {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .risk-medium {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .risk-low {
        background-color: #e8f5e9;
        border-left-color: #4caf50;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_vendor_data():
    """Load and parse vendor data from JSON"""
    vendor_file = Config.VENDOR_DB_PATH

    if not vendor_file.exists():
        return pd.DataFrame()

    with open(vendor_file, 'r') as f:
        data = json.load(f)

    # Flatten the nested structure
    vendors = []
    for org_id, org_vendors in data.items():
        for vendor_name, vendor_info in org_vendors.items():
            vendor_record = {
                'Organization': org_id,
                'Vendor': vendor_name,
                'Service': vendor_info.get('service', 'N/A'),
                'Business Owner': vendor_info.get('business_owner', 'N/A'),
                'Assessment Date': vendor_info.get('assessment_date', 'N/A'),
                'Weighted Score': vendor_info.get('weighted_score', 0),
                'Risk Level': vendor_info.get('risk_level', 'Unknown'),
                'Risk Bucket': vendor_info.get('risk_bucket', 'Unknown'),
                'Likelihood': vendor_info.get('likelihood', 'Unknown'),
                'Impact': vendor_info.get('impact', 'Unknown'),
                'Regulator': vendor_info.get('regulator', 'N/A'),
                'Assessed By': vendor_info.get('assessed_by', 'N/A'),
                'Composite Score': vendor_info.get('composite_pct_score', 0)
            }

            # Add domain scores
            if 'domains' in vendor_info:
                for domain in vendor_info['domains']:
                    vendor_record[f"{domain['name']} Score"] = domain['score']

            vendors.append(vendor_record)

    return pd.DataFrame(vendors)


def render_overview_metrics(df):
    """Render key metrics overview"""
    col1, col2, col3, col4 = st.columns(4)

    total_vendors = len(df)
    high_risk = len(df[df['Risk Level'].str.lower() == 'high'])
    medium_risk = len(df[df['Risk Level'].str.lower() == 'medium'])
    low_risk = len(df[df['Risk Level'].str.lower() == 'low'])
    avg_score = df['Weighted Score'].mean() if not df.empty else 0

    with col1:
        st.metric(
            label="Total Vendors",
            value=total_vendors,
            delta=None
        )

    with col2:
        st.metric(
            label="High Risk Vendors",
            value=high_risk,
            delta=f"{(high_risk/total_vendors*100):.1f}%" if total_vendors > 0 else "0%",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            label="Medium Risk Vendors",
            value=medium_risk,
            delta=f"{(medium_risk/total_vendors*100):.1f}%" if total_vendors > 0 else "0%",
            delta_color="off"
        )

    with col4:
        st.metric(
            label="Average Risk Score",
            value=f"{avg_score:.2f}",
            delta=None
        )


def render_risk_distribution(df):
    """Render risk level distribution chart"""
    st.subheader("📊 Risk Distribution")

    if df.empty:
        st.info("No vendor data available")
        return

    # Risk level counts
    risk_counts = df['Risk Level'].value_counts().reset_index()
    risk_counts.columns = ['Risk Level', 'Count']

    # Color mapping
    color_map = {
        'Low': '#4caf50',
        'Medium': '#ff9800',
        'High': '#f44336'
    }

    fig = px.pie(
        risk_counts,
        values='Count',
        names='Risk Level',
        title='Vendor Risk Distribution',
        color='Risk Level',
        color_discrete_map=color_map,
        hole=0.4
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)


def render_risk_heatmap(df):
    """Render likelihood vs impact heatmap"""
    st.subheader("🔥 Risk Heat Map")

    if df.empty:
        st.info("No vendor data available")
        return

    # Create risk matrix data
    likelihood_order = ['low', 'medium', 'high']
    impact_order = ['low', 'medium', 'high']

    # Count vendors in each cell
    heatmap_data = []
    for likelihood in likelihood_order:
        row = []
        for impact in impact_order:
            count = len(df[(df['Likelihood'].str.lower() == likelihood) &
                          (df['Impact'].str.lower() == impact)])
            row.append(count)
        heatmap_data.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=['Low Impact', 'Medium Impact', 'High Impact'],
        y=['Low Likelihood', 'Medium Likelihood', 'High Likelihood'],
        colorscale='RdYlGn_r',
        text=heatmap_data,
        texttemplate='%{text}',
        textfont={"size": 16},
        showscale=True
    ))

    fig.update_layout(
        title='Risk Matrix: Likelihood vs Impact',
        xaxis_title='Impact',
        yaxis_title='Likelihood',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def render_domain_scores(df):
    """Render domain score comparison"""
    st.subheader("📈 Control Domain Performance")

    if df.empty:
        st.info("No vendor data available")
        return

    # Get all domain score columns
    domain_cols = [col for col in df.columns if 'Score' in col and col not in ['Weighted Score', 'Composite Score']]

    if not domain_cols:
        st.warning("No domain scores available")
        return

    # Calculate average scores per domain
    domain_avgs = []
    for col in domain_cols:
        domain_name = col.replace(' Score', '')
        avg_score = df[col].mean()
        domain_avgs.append({'Domain': domain_name, 'Average Score': avg_score})

    domain_df = pd.DataFrame(domain_avgs).sort_values('Average Score')

    fig = px.bar(
        domain_df,
        x='Average Score',
        y='Domain',
        orientation='h',
        title='Average Scores by Control Domain',
        color='Average Score',
        color_continuous_scale='RdYlGn',
        range_color=[1, 5]
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_vendor_timeline(df):
    """Render vendor assessment timeline"""
    st.subheader("📅 Assessment Timeline")

    if df.empty:
        st.info("No vendor data available")
        return

    # Convert dates and sort
    df_timeline = df.copy()
    df_timeline['Assessment Date'] = pd.to_datetime(df_timeline['Assessment Date'], errors='coerce')
    df_timeline = df_timeline.dropna(subset=['Assessment Date'])
    df_timeline = df_timeline.sort_values('Assessment Date')

    if df_timeline.empty:
        st.warning("No valid assessment dates found")
        return

    fig = px.scatter(
        df_timeline,
        x='Assessment Date',
        y='Weighted Score',
        color='Risk Level',
        size='Composite Score',
        hover_data=['Vendor', 'Organization', 'Service'],
        title='Vendor Assessments Over Time',
        color_discrete_map={'Low': '#4caf50', 'Medium': '#ff9800', 'High': '#f44336'}
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_organization_comparison(df):
    """Render organization-level comparison"""
    st.subheader("🏢 Organization Comparison")

    if df.empty:
        st.info("No vendor data available")
        return

    org_stats = df.groupby('Organization').agg({
        'Vendor': 'count',
        'Weighted Score': 'mean',
        'Risk Level': lambda x: (x.str.lower() == 'high').sum()
    }).reset_index()

    org_stats.columns = ['Organization', 'Total Vendors', 'Avg Score', 'High Risk Count']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Total Vendors',
        x=org_stats['Organization'],
        y=org_stats['Total Vendors'],
        yaxis='y',
        offsetgroup=1
    ))

    fig.add_trace(go.Bar(
        name='High Risk Vendors',
        x=org_stats['Organization'],
        y=org_stats['High Risk Count'],
        yaxis='y',
        offsetgroup=2,
        marker_color='#f44336'
    ))

    fig.update_layout(
        title='Vendor Distribution by Organization',
        xaxis_title='Organization',
        yaxis_title='Count',
        barmode='group',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def render_vendor_table(df):
    """Render detailed vendor table"""
    st.subheader("📋 Vendor Portfolio")

    if df.empty:
        st.info("No vendor data available")
        return

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        org_filter = st.multiselect(
            'Filter by Organization',
            options=df['Organization'].unique(),
            default=df['Organization'].unique()
        )

    with col2:
        risk_filter = st.multiselect(
            'Filter by Risk Level',
            options=df['Risk Level'].unique(),
            default=df['Risk Level'].unique()
        )

    with col3:
        service_filter = st.multiselect(
            'Filter by Service',
            options=df['Service'].unique(),
            default=df['Service'].unique()
        )

    # Apply filters
    filtered_df = df[
        (df['Organization'].isin(org_filter)) &
        (df['Risk Level'].isin(risk_filter)) &
        (df['Service'].isin(service_filter))
    ]

    # Display table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Weighted Score': st.column_config.ProgressColumn(
                'Risk Score',
                format='%.2f',
                min_value=0,
                max_value=5,
            ),
            'Composite Score': st.column_config.ProgressColumn(
                'Composite %',
                format='%.1f%%',
                min_value=0,
                max_value=100,
            )
        }
    )

    # Export button
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"vendor_portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def main():
    """Main dashboard application"""

    # Header
    st.title("🛡️ AI-Powered TPRM Dashboard")
    st.markdown("Real-time vendor risk analytics and portfolio insights")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")

        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # System info
        st.subheader("System Information")
        st.info(f"""
        **App Version:** {Config.VERSION}

        **Ollama URL:** {Config.OLLAMA_URL}

        **Default Model:** {Config.OLLAMA_MODEL_DEFAULT}

        **Data Path:** {Config.VENDOR_DB_PATH}
        """)

        st.divider()

        # Risk thresholds
        st.subheader("Risk Thresholds")
        st.metric("Low Risk ≥", Config.RISK_THRESHOLD_LOW)
        st.metric("Medium Risk ≥", Config.RISK_THRESHOLD_MEDIUM)

    # Load data
    try:
        df = load_vendor_data()

        if df.empty:
            st.warning("⚠️ No vendor data found. Please run vendor assessments first.")
            st.info("💡 Use the main TPRM system to add vendors: `python main.py`")
            return

        # Overview metrics
        render_overview_metrics(df)

        st.divider()

        # Charts in columns
        col1, col2 = st.columns(2)

        with col1:
            render_risk_distribution(df)

        with col2:
            render_risk_heatmap(df)

        st.divider()

        # Domain scores
        render_domain_scores(df)

        st.divider()

        # Timeline
        render_vendor_timeline(df)

        st.divider()

        # Organization comparison
        render_organization_comparison(df)

        st.divider()

        # Detailed table
        render_vendor_table(df)

    except Exception as e:
        st.error(f"❌ Error loading dashboard: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()
