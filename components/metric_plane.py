import streamlit as st

def display_risk_summary(player_display_df):
    """
    Display a modern summary of injury risk statistics
    
    Args:
        player_display_df: Processed player display DataFrame
    """
    # Calculate risk counts
    high_risk = player_display_df[player_display_df['inj_probability'] > 0.5].shape[0]
    low_risk = player_display_df[player_display_df['inj_probability'] <= 0.5].shape[0]
    
    # Calculate percentages
    total_players = len(player_display_df)
    high_risk_pct = f"{high_risk/total_players*100:.1f}%" if total_players > 0 else "0%"
    low_risk_pct = f"{low_risk/total_players*100:.1f}%" if total_players > 0 else "0%"
    
    # Create columns for metrics
    col1, col2 = st.columns(2)
    
    # High risk metric
    with col1:
        st.markdown(
            f"""
            <div style="background-color: #1E2130; border-radius: 10px; padding: 1rem; height: 100%; border-left: 5px solid #E74C3C;">
                <div style="font-size: 0.9rem; color: #b0b0b0; margin-bottom: 0.5rem;">HIGH RISK PLAYERS</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #E74C3C;">{high_risk}</div>
                <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                    <div style="font-size: 1rem; color: #E74C3C; margin-right: 0.5rem;">▲</div>
                    <div style="font-size: 0.9rem; color: #b0b0b0;">{high_risk_pct} of squad</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Low risk metric
    with col2:
        st.markdown(
            f"""
            <div style="background-color: #1E2130; border-radius: 10px; padding: 1rem; height: 100%; border-left: 5px solid #5DB85C;">
                <div style="font-size: 0.9rem; color: #b0b0b0; margin-bottom: 0.5rem;">LOW RISK PLAYERS</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #5DB85C;">{low_risk}</div>
                <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                    <div style="font-size: 1rem; color: #5DB85C; margin-right: 0.5rem;">▲</div>
                    <div style="font-size: 0.9rem; color: #b0b0b0;">{low_risk_pct} of squad</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Add overall team risk assessment
    print("Total players",total_players)
    overall_risk = "High" if high_risk/total_players > 0.3 else "Moderate" if high_risk/total_players > 0.1 else "Low"
    risk_color = "#E74C3C" if overall_risk == "High" else "#F1C40F" if overall_risk == "Moderate" else "#5DB85C"
    
    st.markdown(
        f"""
        <div style="margin-top: 1rem; background-color: #1E2130; border-radius: 10px; padding: 1rem; text-align: center;">
            <div style="font-size: 0.9rem; color: #b0b0b0; margin-bottom: 0.5rem;">OVERALL TEAM RISK ASSESSMENT</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: {risk_color};">{overall_risk} Risk</div>
        </div>
        """,
        unsafe_allow_html=True
    )