import streamlit as st
import pandas as pd
import altair as alt

def display_risk_charts(player_df):
    """
    Display risk distribution charts
    
    Args:
        player_df: DataFrame containing player data with risk assessments
    """
    # Add altair charts for risk visualization
    
    # Create position distribution data
    position_risk = player_df.groupby(['Position', 'Injury Risk']).size().reset_index(name='Count')
    
    # Create the chart for position risk distribution
    position_chart = alt.Chart(position_risk).mark_bar().encode(
        x=alt.X('Position:N', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Count:Q'),
        color=alt.Color('Injury Risk:N', 
                      scale=alt.Scale(domain=['High Risk', 'Low Risk'],
                                     range=['#E74C3C', '#5DB85C'])),
        tooltip=['Position', 'Injury Risk', 'Count']
    ).properties(
        height=200
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(position_chart, use_container_width=True)
    
    # Additional information
    if 'Position' in player_df.columns:
        high_risk_by_position = player_df[player_df['Injury Prediction'] == 1].groupby('Position').size()
        total_by_position = player_df.groupby('Position').size()
        
        # Calculate percentages
        position_percentages = {}
        for position in total_by_position.index:
            high_risk_count = high_risk_by_position.get(position, 0)
            total_count = total_by_position.get(position, 0)
            percentage = (high_risk_count / total_count * 100) if total_count > 0 else 0
            position_percentages[position] = percentage
        
        # Find highest risk position
        if position_percentages:
            highest_risk_position = max(position_percentages.items(), key=lambda x: x[1])
            
            st.markdown(
                f"""
                <div style="margin-top: 1rem; text-align: center;">
                    <div style="color: #b0b0b0;">Highest risk position:</div>
                    <div style="font-size: 1.2rem; color: white; font-weight: 600;">
                        {highest_risk_position[0]} ({highest_risk_position[1]:.1f}%)
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )