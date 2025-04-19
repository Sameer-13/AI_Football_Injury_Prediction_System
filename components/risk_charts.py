import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

def display_risk_charts(player_df):
    """
    Display enhanced risk distribution charts using Plotly
    
    Args:
        player_df: DataFrame containing player data with risk assessments
    """
    if len(player_df) == 0:
        st.warning("No player data available to display risk charts.")
        return
    
    # Create position distribution data
    position_risk = player_df.groupby(['Position', 'Injury Risk']).size().reset_index(name='Count')
    
    # Create a pivot table for easier plotting
    pivot_df = position_risk.pivot(index='Position', columns='Injury Risk', values='Count').fillna(0)
    
    # Ensure all columns exist
    if 'High Risk' not in pivot_df.columns:
        pivot_df['High Risk'] = 0
    if 'Low Risk' not in pivot_df.columns:
        pivot_df['Low Risk'] = 0
    
    # Calculate percentages for annotations
    pivot_df['Total'] = pivot_df['High Risk'] + pivot_df['Low Risk']
    pivot_df['High Risk %'] = (pivot_df['High Risk'] / pivot_df['Total'] * 100).round(1)
    
    # Get positions in order
    positions = pivot_df.index.tolist()
    
    # Create color map for positions
    position_colors = {
        "Goalkeeper": "#F1C40F",
        "Defender": "#3498DB",
        "Midfielder": "#9B59B6",
        "Forward": "#E74C3C",
        "Not Specified": "#95A5A6"
    }
    
    # 1. Create stacked bar chart for risk distribution by position
    fig1 = go.Figure()
    
    # Add bars for High Risk
    fig1.add_trace(go.Bar(
        x=positions,
        y=pivot_df['High Risk'],
        name='High Risk',
        marker_color='#E74C3C',
        hovertemplate='Position: %{x}<br>Count: %{y}<br>Percentage: %{customdata}%<extra></extra>',
        customdata=pivot_df['High Risk %']
    ))
    
    # Add bars for Low Risk
    fig1.add_trace(go.Bar(
        x=positions,
        y=pivot_df['Low Risk'],
        name='Low Risk',
        marker_color='#5DB85C',
        hovertemplate='Position: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Update layout
    fig1.update_layout(
        barmode='stack',
        title={
            'text': 'Risk Distribution by Position',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': 'white', 'size': 16}
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={'size': 10}
        ),
        xaxis=dict(
            title='',
            showgrid=False,
            tickfont={'size': 12}
        ),
        yaxis=dict(
            title='Number of Players',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            tickfont={'size': 10}
        ),
        height=200,
    )
    
    # Display the stacked bar chart
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    
    # 2. Create a row with metrics and small donut charts for each position
    cols = st.columns(len(positions))
    
    for i, position in enumerate(positions):
        with cols[i]:
            # Calculate high risk percentage for this position
            high_risk_count = pivot_df.loc[position, 'High Risk']
            total_count = pivot_df.loc[position, 'Total']
            high_risk_pct = pivot_df.loc[position, 'High Risk %']
            
            # Create mini donut chart
            fig = go.Figure()
            
            # Add the donut chart
            fig.add_trace(go.Pie(
                labels=['High Risk', 'Low Risk'],
                values=[high_risk_count, total_count - high_risk_count],
                hole=0.7,
                marker=dict(colors=['#E74C3C', '#5DB85C']),
                textinfo='none',
                hoverinfo='label+percent',
                showlegend=False
            ))
            
            # Update layout
            fig.update_layout(
                annotations=[dict(
                    text=f"{high_risk_pct}%",
                    x=0.5, y=0.5,
                    font_size=14,
                    font_color='white',
                    showarrow=False
                )],
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
                height=120,
                width=120
            )
            
            # Display the position name with colored badge
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style= 
                              display: inline-block; padding: 3px 8px; border-radius: 5px; 
                              margin-bottom: 5px; color: white; font-size: 12px;">
                        {position}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display donut chart
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 3. Find and display highest risk position
    highest_risk_position = pivot_df.sort_values('High Risk %', ascending=False).index[0]
    highest_risk_pct = pivot_df.loc[highest_risk_position, 'High Risk %']
    
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 10px;">
            <div style="color: #b0b0b0; font-size: 14px;">Highest injury risk position:</div>
            <div style="font-size: 16px; color: white; font-weight: 600;">
                {highest_risk_position} ({highest_risk_pct}%)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )