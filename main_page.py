import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fetch_data import main
from PIL import Image
import base64
import os

# Yerel placeholder görüntüyü yüklemek için fonksiyon
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Placeholder görüntü yolu - kendi dosya yolunuzu buraya yazın
PLACEHOLDER_IMAGE_PATH = "placeholder.jpeg"  # Bu dosyanın Python kodunuzla aynı dizinde olduğunu varsayıyorum

# Görüntüyü base64 formatına dönüştür (eğer dosya mevcutsa)
if os.path.exists(PLACEHOLDER_IMAGE_PATH):
    img_base64 = get_base64_encoded_image(PLACEHOLDER_IMAGE_PATH)
    PLACEHOLDER_IMAGE = f"data:image/jpeg;base64,{img_base64}"
else:
    # Dosya bulunamazsa yedek olarak online bir görsel kullan
    PLACEHOLDER_IMAGE = "https://img.freepik.com/free-vector/artificial-intelligence-ai-robot-server-room-digital-technology-banner_39422-794.jpg"
    st.warning(f"Placeholder image not found at {PLACEHOLDER_IMAGE_PATH}. Using fallback image.")

all_sources = ["The Berkeley Artificial Intelligence Research Blog","NVDIA Blog","Microsoft Research","Science Daily","META Research","OpenAI News",
               "Google DeepMind Blog","MIT News - Artificial intelligence","MIT Technology Review - Artificial intelligence","Wired: Artificial Intelligence Latest",
               "Ollama Blog","IBM - Announcements (Artificial intelligence)","deeplearning.ai"]


# Use Streamlit's built-in caching
@st.cache_data(ttl=60)  # Cache for 1 minute
def get_data():
    with st.spinner('Fetching latest AI news...'):
        return main()

def run_dashboard():
    # Başlık ve refresh butonunu aynı satıra yerleştir
    col_title, col_button = st.columns([4, 1])
    with col_title:
        st.title("Latest AI News")
    with col_button:
        # Butonu dikey olarak başlıkla hizalamak için biraz boşluk
        st.write("")
        if st.button("Refresh News"):
            st.cache_data.clear()
            st.rerun()
    
    # Add sidebar for all filters
    with st.sidebar:
        st.header("Filter Options")
    
    
    # Load data with caching
    try:
        df = get_data()
        
        # Check if df is empty
        if df.empty:
            st.error("No news data available. Please try refreshing later.")
            return
            
        # Get min and max dates
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        # Calculate default date range (last 7 days)
        default_end_date = max_date
        default_start_date = default_end_date - timedelta(days=7)
        if default_start_date < min_date:
            default_start_date = min_date
        
        # Continue with sidebar for filters
        with st.sidebar:
            # Date filter
            selected_dates = st.date_input(
                "Choose dates",
                value=(default_start_date, default_end_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Handle single date selection
            if len(selected_dates) == 1:
                start_date = selected_dates[0]
                end_date = selected_dates[0]
            else:
                start_date, end_date = selected_dates
            
            
            # Get unique sources from predefined list
            sources = sorted(all_sources)
            
            # Use multiselect without "All" option
            selected_sources = st.multiselect(
                "Choose sources",
                options=sources
            )
            
        
        # Main content area for displaying news
        # Convert dates to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filter by date range
        df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        # Handle source filtering
        if selected_sources:  # If sources are selected
            # Filter by selected sources
            df_filtered = df_filtered[df_filtered['Source'].isin(selected_sources)]
        # If no sources selected, show all (no additional filtering needed)
        
        # Display results
        if len(df_filtered) > 0:
            
            # Apply CSS styling for cards
            st.markdown("""
            <style>
            .news-card {
                border-radius: 20px;
                padding: 0;
                margin-bottom: 20px;
                background-color: #E8E8E8;
                height: 480px;
                overflow: hidden;
                position: relative;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
            }
            .news-image-container {
                width: 100%;
                height: 220px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px 10px 0 10px;
            }
            .news-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 12px;
            }
            .news-content {
                padding: 12px 15px;
            }
            .news-title {
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 10px;
                color: #000;
                line-height: 1.3;
                max-height: 105px;
                display: -webkit-box;
                -webkit-line-clamp: 4;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            .news-meta {
                display: flex;
                justify-content: space-between;
                margin-bottom: 12px;
                align-items: center;
                border-bottom: 1px solid #ddd;
                padding-bottom: 8px;
            }
            .news-source {
                color: #555;
                font-size: 12px;
                font-style: italic;
            }
            .news-date {
                color: #555;
                font-size: 12px;
                text-align: right;
                font-style: italic;
            }
            .news-description {
                color: #333;
                font-size: 13px;
                padding-bottom: 10px;
                line-height: 1.4;
                display: -webkit-box;
                -webkit-line-clamp: 5;
                -webkit-box-orient: vertical;
                overflow: hidden;
                height: 90px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create 3-column layout
            num_cols = 3
            
            # Process news items in groups of 3 for the grid
            for i in range(0, len(df_filtered), num_cols):
                cols = st.columns(num_cols)
                
                # Get the current batch of news items
                current_batch = df_filtered.iloc[i:i+num_cols]
                
                # Display each news item in its column
                for j, (_, row) in enumerate(current_batch.iterrows()):
                    if j < len(cols):  # Ensure we have a column for this item
                        with cols[j]:
                            # Eğer kaynak deeplearning.ai ise veya geçerli bir görüntü yoksa, placeholder kullan
                            if row['Source'] == "deeplearning.ai" or not pd.notna(row.get('Image')) or row.get('Image') is None:
                                image_url = PLACEHOLDER_IMAGE
                            else:
                                image_url = row['Image']
                            
                            # Format the date
                            date_str = row['date'].strftime('%d %b %Y')
                            
                            # Truncate description if it's too long
                            description = row['Description'][:150] + "..." if len(row['Description']) > 150 else row['Description']
                            
                            # Display card with HTML
                            html_content = f"""
                            <a href="{row['Link']}" target="_blank" style="text-decoration: none; color: inherit;">
                                <div class="news-card">
                                    <div class="news-image-container">
                                        <img src="{image_url}" class="news-image" onerror="this.onerror=null;this.src='{PLACEHOLDER_IMAGE}';">
                                    </div>
                                    <div class="news-content">
                                        <div class="news-title">{row['Title']}</div>
                                        <div class="news-meta">
                                            <div class="news-source">{row['Source']}</div>
                                            <div class="news-date">{date_str}</div>
                                        </div>
                                        <div class="news-description">{description}</div>
                                    </div>
                                </div>
                            </a>
                            """
                            st.markdown(html_content, unsafe_allow_html=True)
        else:
            st.warning("No news found with the selected filters. Please adjust your date range or source selection.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Try refreshing the data using the button above.")

if __name__ == '__main__':
    run_dashboard()
