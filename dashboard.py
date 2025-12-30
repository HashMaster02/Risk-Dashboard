import streamlit as st
import pandas as pd
from datetime import datetime
from data_storage import db_manager

# Page configuration
st.set_page_config(
    page_title="Investment Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .last-updated {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def format_currency(value):
    """Format number as currency"""
    return f"${value:,.2f}"

def load_data():
    """Load latest data from database"""
    data = db_manager.get_latest_data_per_symbol()
    return data

def main():
    # Header
    st.markdown('<div class="main-header">Investment Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="last-updated">TradingView Webhook Data</div>', unsafe_allow_html=True)

    # Create columns for refresh button and last updated time
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()

    # Load data
    data = load_data()

    # Display last updated time
    with col3:
        if data:
            st.markdown(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

    # Main content
    if not data:
        st.info("📊 No data available yet. Waiting for TradingView webhooks...")
        st.markdown("""
        ### How to send data:
        1. Configure your TradingView alert with webhook URL
        2. Use this JSON format:
        ```json
        {
          "symbol": "{{ticker}}",
          "price": {{close}},
          "atr": {{plot("ATR")}}
        }
        ```
        3. Data will appear here after the first webhook is received
        """)
    else:
        # Convert to DataFrame and calculate exit price
        df = pd.DataFrame(data)

        # Calculate exit price
        df['exit_price'] = df['price'] - df['atr']

        # Reorder columns
        df = df[['symbol', 'price', 'atr', 'exit_price', 'timestamp']]

        # Rename columns for display
        df.columns = ['Symbol', 'Price', 'ATR', 'Exit Price', 'Last Updated']

        # Format timestamp
        df['Last Updated'] = pd.to_datetime(df['Last Updated']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Symbols", len(df))
        with col2:
            avg_price = df['Price'].mean()
            st.metric("Avg Price", format_currency(avg_price))
        with col3:
            avg_atr = df['ATR'].mean()
            st.metric("Avg ATR", format_currency(avg_atr))

        # Display table
        st.markdown("### Investment Data")

        # Format numeric columns
        styled_df = df.copy()
        styled_df['Price'] = styled_df['Price'].apply(format_currency)
        styled_df['ATR'] = styled_df['ATR'].apply(format_currency)
        styled_df['Exit Price'] = styled_df['Exit Price'].apply(format_currency)

        # Display as interactive dataframe
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

        # Download button
        st.download_button(
            label="📥 Download CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f'investment_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
        )

        # Additional information
        with st.expander("ℹ️ About Exit Price Calculation"):
            st.markdown("""
            **Exit Price** is calculated as:
            ```
            Exit Price = Price - ATR
            ```

            This represents a potential stop-loss level based on the Average True Range (ATR),
            which measures market volatility. The exit price is one ATR below the current price.
            """)

if __name__ == "__main__":
    main()
