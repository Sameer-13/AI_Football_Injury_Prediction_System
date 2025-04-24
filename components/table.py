import streamlit as st
import pandas as pd

def display_player_table(player_df):
    """
    Display a modern styled table of players with injury predictions

    Args:
        player_df: DataFrame containing player data with risk assessments

    Returns:
        DataFrame: Processed player display DataFrame
    """
    # Color function for styling
    def color_injury_prediction(val):
        if val == 'High Risk':
            return 'background-color: rgba(231, 76, 60, 0.9); color: white; font-weight: bold; border-radius: 5px; padding: 0.3rem 0.6rem; text-align: center;'
        else:
            return 'background-color: rgba(93, 184, 92, 0.9); color: white; font-weight: bold; border-radius: 5px; padding: 0.3rem 0.6rem; text-align: center;'

    # Add custom styling to position column
    def style_position(val):
        position_colors = {
            "Goalkeeper": "background-color: rgba(241, 196, 15, 0.2); border-left: 3px solid #F1C40F;",
            "Defender": "background-color: rgba(52, 152, 219, 0.2); border-left: 3px solid #3498DB;",
            "Midfielder": "background-color: rgba(155, 89, 182, 0.2); border-left: 3px solid #9B59B6;",
            "Forward": "background-color: rgba(231, 76, 60, 0.2); border-left: 3px solid #E74C3C;",
        }
        return position_colors.get(val, "")

    # Create a copy of the dataframe for display
    display_df = player_df.copy()

    # Ensure numeric columns are formatted properly
    if 'age' in display_df.columns:
        display_df['age'] = display_df['age'].apply(lambda x: f"{float(x):.0f}" if pd.notnull(x) else "N/A")

    if 'height_cm' in display_df.columns:
        display_df['height_cm'] = display_df['height_cm'].apply(lambda x: f"{float(x):.0f}" if pd.notnull(x) else "N/A")

    if 'weight_kg' in display_df.columns:
        display_df['weight_kg'] = display_df['weight_kg'].apply(lambda x: f"{float(x):.0f}" if pd.notnull(x) else "N/A")

    if 'Minutes Played' in display_df.columns:
        display_df['Minutes Played'] = display_df['Minutes Played'].apply(lambda x: f"{float(x):.0f}" if pd.notnull(x) else "N/A")

    # Style and display the DataFrame
    styled_df = (
        display_df.style
        .applymap(color_injury_prediction, subset=["Injury Risk"])
        .applymap(style_position, subset=["Position"])
        .set_properties(**{
            'text-align': 'center',
            'font-size': '14px',
            'border': 'none',
            'background-color': '#2C2F44',
            'color': 'white'
        })
        .set_table_styles([
            {'selector': 'th', 'props': [
                ('background-color', '#1E2130'),
                ('color', 'white'),
                ('font-weight', 'bold'),
                ('text-align', 'center'),
                ('border', 'none'),
                ('padding', '10px'),
                ('font-size', '14px')
            ]},
            {'selector': 'tr:hover', 'props': [
                ('background-color', '#3b3f5c')
            ]},
            {'selector': 'td', 'props': [
                ('padding', '10px')
            ]}
        ])
    )

    # Display the styled table
    st.dataframe(styled_df, use_container_width=True, height=400)

    st.markdown("</div>", unsafe_allow_html=True)

    # Add table legends/info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style= border-radius: 10px; padding: 1rem; text-align: center;">
                <span style="background-color: rgba(231, 76, 60, 0.9); color: white; font-weight: bold; border-radius: 5px; padding: 0.3rem 0.6rem;">High Risk</span>
                <span style="margin-left: 0.5rem; color: #b0b0b0;">Players requiring special attention</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div style= border-radius: 10px; padding: 1rem; text-align: center; margin: 100rem;">
                <span style="background-color: rgba(93, 184, 92, 0.9); color: white; font-weight: bold; border-radius: 5px; padding: 0.3rem 0.6rem;">Low Risk</span>
                <span style="margin-left: 0.5rem; color: #b0b0b0;">Players with normal injury risk</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div style= border-radius: 10px; padding: 1rem; text-align: center;">
                <button style="background-color: #5762D5; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; font-weight: 600;">
                    <span style="margin-right: 0.5rem;">📊</span> Export Data
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )

    return player_df


def plot_risk_dots_with_ci(df):
        df_sorted = df.sort_values("inj_probability", ascending=False).reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(10, 8))
        y_positions = range(len(df_sorted))
        
        # Plot confidence intervals as horizontal lines
        ax.hlines(y=y_positions, xmin=df_sorted["ci_lower_95"], xmax=df_sorted["ci_upper_95"],
                color="#888", alpha=0.7, linewidth=2)

        # Plot actual points
        colors = ["#EF4444" if p > 0.5 else "#10B981" for p in df_sorted["inj_probability"]]  # Tailwind red/green
        ax.scatter(df_sorted["inj_probability"], y_positions, color=colors, s=100, zorder=3)

        # Formatting
        ax.set_yticks(y_positions)
        ax.set_yticklabels(df_sorted["player_name"])
        ax.set_xlabel("Injury Probability")
        ax.set_title("Pre-match Injury Risk per Player (with Confidence Intervals)")
        ax.invert_yaxis()
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)
        ax.set_facecolor("#111827")  # Dark background
        fig.patch.set_facecolor('#111827')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        st.pyplot(fig)
