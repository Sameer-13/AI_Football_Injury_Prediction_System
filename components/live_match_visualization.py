import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from collections import defaultdict

def display_live_match_visualization(live_data):
    """
    Display live match injury risk visualization
    
    Args:
        live_data: DataFrame containing live match risk data with columns:
                  minute, player_name, risk_score, rank
    """
    if live_data is None or live_data.empty:
        st.warning("No live match data available.")
        return
    
    # Ensure we have the required columns
    required_columns = ['minute', 'player_name', 'risk_score', 'rank']
    for col in required_columns:
        if col not in live_data.columns:
            st.error(f"Required column '{col}' missing from live match data.")
            return
    
    # Get the latest data timestamp
    latest_minute = live_data['minute'].max()
    latest_data = live_data[live_data['minute'] == latest_minute]
    
    # Sort by risk score (descending)
    latest_data = latest_data.sort_values('risk_score', ascending=False)
    
    # Display current risk rankings
    st.markdown("<h3>Current Injury Risk Rankings</h3>", unsafe_allow_html=True)
    
    # Create two columns layout for the table
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # First half of players (top 5 or half of the list)
        half_count = min(5, len(latest_data) // 2 + len(latest_data) % 2)
        first_half = latest_data.iloc[:half_count].copy()
        display_player_ranks(first_half)
        
    with col2:
        # Second half of players (rest of the list)
        second_half = latest_data.iloc[half_count:min(10, len(latest_data))].copy()
        if not second_half.empty:
            display_player_ranks(second_half)
    
    # Create the trend visualization
    create_trend_visualization(live_data)

def display_player_ranks(player_data):
    """
    Display player rankings in a styled table
    
    Args:
        player_data: DataFrame containing player data to display
    """
    # Copy the data to avoid modifying the original and drop the risk_score column from display
    display_df = player_data[['player_name', 'rank']].copy()
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'player_name': 'Player Name',
        'rank': 'Rank'
    })
    
    # Style and display the DataFrame
    styled_df = display_df.style.applymap(
        lambda x: 'background-color: rgba(231, 76, 60, 0.8); color: white; font-weight: bold; text-align: center;' 
        if x <= 3 else '', 
        subset=['Rank']
    )
    
    # Set table styles with larger font and improved spacing
    styled_df = styled_df.set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#1E2130'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('border', 'none'),
            ('padding', '10px'),
            ('font-size', '24px')
        ]},
        {'selector': 'tr:hover', 'props': [
            ('background-color', '#3b3f5c')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '12px'),
            ('text-align', 'center'),
            ('font-size', '20px'),
            ('border-bottom', '1px solid rgba(255,255,255,0.1)')
        ]}
    ])
    
    # Display the dataframe with auto height
    st.dataframe(styled_df, use_container_width=True, height=None)

def create_trend_visualization(live_data):
    """
    Create trend visualization for risk rankings over time
    
    Args:
        live_data: DataFrame containing live match risk data with timestamps
    """
    st.markdown("<h3>Injury Risk Trend Over Match Time</h3>", unsafe_allow_html=True)
    
    # Get unique timestamps and players
    timestamps = sorted(live_data['minute'].unique())
    
    # If we have only one timestamp, we can't show trends
    if len(timestamps) <= 1:
        st.info("Trend visualization will be available after multiple data points are collected during the match.")
        return
    
    # Get top 10 players based on latest risk rankings
    latest_minute = max(timestamps)
    latest_data = live_data[live_data['minute'] == latest_minute]
    top_players = latest_data.sort_values('risk_score', ascending=False).head(10)['player_name'].tolist()
    
    # Filter data for top players only
    player_data = live_data[live_data['player_name'].isin(top_players)]
    
    # Create a color dictionary for consistent player colors
    colors = px.colors.qualitative.Plotly
    player_colors = {player: colors[i % len(colors)] for i, player in enumerate(top_players)}
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for each player
    for player in top_players:
        player_df = player_data[player_data['player_name'] == player]
        
        if not player_df.empty:
            # Sort by minute
            player_df = player_df.sort_values('minute')
            
            # Add line trace for player trend
            fig.add_trace(go.Scatter(
                x=player_df['minute'],
                y=player_df['rank'],
                mode='lines+markers',
                name=player,
                line=dict(color=player_colors[player], width=2),
                marker=dict(size=10, color=player_colors[player]),
                hovertemplate='Player: %{text}<br>Minute: %{x}<br>Rank: %{y}<br>Risk Score: %{customdata:.1%}<extra></extra>',
                text=[player] * len(player_df),
                customdata=player_df['risk_score']
            ))
    
    # Update layout with legend on right side
    fig.update_layout(
        title=dict(
            text="Player Risk Ranking Trends",
            font=dict(size=18, color="white"),
            x=0.5,
            y=0.98
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="v",  # Vertical orientation
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,  # Position slightly outside the plot area
            font=dict(color="white", size=12),
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            bgcolor="rgba(30,33,48,0.7)"  # Semi-transparent background
        ),
        xaxis=dict(
            title="Match Minute",
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),
        yaxis=dict(
            title="Risk Ranking",
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color="white"),
            title_font=dict(color="white"),
            autorange="reversed",  # Higher rank = lower number (1 is highest risk)
            dtick=1  # Integer ticks for ranks
        ),
        margin=dict(l=50, r=120, t=60, b=50),  # Increased right margin for legend
        height=550
    )
    
    # Add markers for high-risk threshold (top 3)
    fig.add_shape(
        type="rect",
        x0=min(timestamps),
        x1=max(timestamps),
        y0=0.5,
        y1=3.5,
        fillcolor="rgba(231, 76, 60, 0.2)",
        line=dict(width=0),
        layer="below"
    )
    
    # Add annotation for high-risk zone
    fig.add_annotation(
        x=min(timestamps) + 2,  # Move slightly to the right to avoid y-axis labels
        y=2,
        text="High Risk Zone",
        showarrow=False,
        font=dict(color="rgba(231, 76, 60, 1)"),
        xanchor="left"
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # # Add informational note about the visualization
    # st.markdown(
    #     """
    #     <div style="background-color: #1E2130; border-radius: 10px; padding: 1rem; margin-top: 1rem;">
    #         <h4 style="margin-top: 0; color: white;">Reading the Visualization</h4>
    #         <ul style="color: #b0b0b0;">
    #             <li>Each line represents a player's risk ranking over time</li>
    #             <li>Lower rank numbers (1, 2, 3) indicate higher risk</li>
    #             <li>The red highlighted area shows the high-risk zone (ranks 1-3)</li>
    #             <li>Hover over points to see detailed risk scores</li>
    #             <li>Watch for players moving into or out of the high-risk zone</li>
    #         </ul>
    #     </div>
    #     """,
    #     unsafe_allow_html=True
    # )