import streamlit as st
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path and import logger
sys.path.append('src')
try:
    from utils.logger import logger
except ImportError:
    # Create a simple logger if the main one isn't available
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('hedgelab')

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="HedgeLab - Investment Learning Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for simple styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .nav-button {
        width: 100%;
        padding: 0.75rem;
        margin: 0.25rem 0;
        border: none;
        border-radius: 8px;
        background: #f8fafc;
        color: #1e293b;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    .nav-button:hover {
        background: #e2e8f0;
        transform: translateY(-1px);
    }
    .nav-button.active {
        background: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Log application start
    logger.info("HedgeLab application started")
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0; text-align: center;">
            📈 HedgeLab - Investment Learning Tool
        </h1>
        <p style="color: #d1d5db; text-align: center; margin: 0.5rem 0 0 0;">
            Basic stock analysis • Simple opportunity detection • Portfolio tracking
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    with st.sidebar:
        st.markdown("### Navigation")
        
        # Initialize session state for page selection
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'Macro View'
        
        # Navigation buttons
        pages = {
            'Macro View': '🌍',
            'Opportunities': '🔍', 
            'Portfolio': '💼',
            'Reports': '📊',
            'Logs': '📋'
        }
        
        for page_name, icon in pages.items():
            if st.button(f"{icon} {page_name}", key=page_name):
                st.session_state.current_page = page_name
                st.rerun()
    
    # Page routing
    current_page = st.session_state.current_page
    logger.user_action("page_navigation", f"Navigated to {current_page}")
    
    try:
        if current_page == 'Macro View':
            logger.info("Loading Macro View module")
            from src.macro.macro_view import MacroView
            MacroView().render()
        elif current_page == 'Opportunities':
            logger.info("Loading Opportunities module")
            from src.opportunities.opportunity_detector import OpportunityDetector
            OpportunityDetector().render()
        elif current_page == 'Portfolio':
            logger.info("Loading Portfolio module")
            from src.portfolio.portfolio_manager import PortfolioManager
            PortfolioManager().render()
        elif current_page == 'Reports':
            logger.info("Loading Reports module")
            from src.portfolio.reports import ReportGenerator
            ReportGenerator().render()
        elif current_page == 'Logs':
            logger.info("Loading Logs module")
            from src.ui.log_viewer import LogViewer
            LogViewer().render()
    except ImportError as e:
        logger.error(f"Module not found: {e}")
        st.error(f"Module not found: {e}")
        st.info("Some modules are still being implemented. Please check back shortly.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error(f"An error occurred: {e}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main() 