import streamlit as st

def display_risk_summary(player_display_df):
    """
    Display a summary of injury risk statistics
    
    Args:
        player_display_df: Processed player display DataFrame
    """
    # Calculate risk counts
    risk_count = player_display_df['Injury Prediction'].value_counts()
    high_risk = risk_count.get(1, 0)
    low_risk = risk_count.get(0, 0)
    
    # Display summary metrics
    st.markdown("### Team Injury Risk Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        high_risk_pct = f"{high_risk/len(player_display_df)*100:.1f}%" if len(player_display_df) > 0 else "0%"
        st.metric(label="High Risk Players", value=high_risk, delta=high_risk_pct)
    
    with col2:
        low_risk_pct = f"{low_risk/len(player_display_df)*100:.1f}%" if len(player_display_df) > 0 else "0%"
        st.metric(label="Low Risk Players", value=low_risk, delta=low_risk_pct)