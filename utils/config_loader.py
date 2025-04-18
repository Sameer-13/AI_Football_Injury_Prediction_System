import os
import yaml
import streamlit as st

@st.cache_data
def load_config():
    """
    Load configuration from config.yaml file
    
    Returns:
        dict: Configuration dictionary
    """
    try:
        # Determine the config file path relative to the current file
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
        
        # Load the config file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Convert relative paths to absolute if needed
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if config.get('paths'):
            for key, path in config['paths'].items():
                if not os.path.isabs(path):
                    config['paths'][key] = os.path.join(base_dir, path)
        
        return config
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        # Return default config if there's an error
        return {
            'paths': {
                'data': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cleaned_data.csv'),
                'logo': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'whiteLogo.png')
            }
        }