import streamlit as st
from agent import app  # Your compiled LangGraph workflow
from image_analyzer import analyze_all_images
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Constants ---
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Page Config ---
st.set_page_config(
    page_title="Zocket Ad Optimizer", 
    page_icon="🚀",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Zocket+Logo", width=150)
    st.title("Settings")
    
    # 1. Multi-File Upload with Drag-and-Drop
    uploaded_files = st.file_uploader(
        "📤 Upload Ad Creatives",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Upload up to 10 images at once"
    )
    
    # 2. Ad Copy Generator
    with st.expander("✍️ Ad Copy Suggestions"):
        ad_text = st.text_area(
            "Ad Text", 
            "50% Off Summer Sale!",
            height=100
        )
        if st.button("✨ Generate Variants"):
            with st.spinner("Generating..."):
                # Call your text_optimizer here
                st.session_state.variants = ["Hurry! 50% Off", "Summer Sale!", "Limited Time Offer"]
    
    # 3. Performance Weighting
    st.subheader("⚖️ Optimization Rules")
    text_weight = st.slider("Text Importance", 0.0, 1.0, 0.6)
    visual_weight = st.slider("Visual Importance", 0.0, 1.0, 0.4)
    
    # 4. Platform Targeting
    platforms = st.multiselect(
        "Target Platforms",
        ["Facebook", "Instagram", "Google Ads", "LinkedIn"],
        default=["Facebook", "Instagram"]
    )

# --- Main Dashboard ---
tab1, tab2, tab3 = st.tabs(["Optimizer", "History", "API Docs"])

with tab1:
    # 1. Real-Time Processing
    if uploaded_files and st.button("🚀 Optimize Now", type="primary"):
        with st.spinner("Analyzing..."):
            # Save uploaded files
            for file in uploaded_files:
                with open(f"data/{file.name}", "wb") as f:
                    f.write(file.getbuffer())
            
            # Run analysis
            results = app.invoke({
                "text": ad_text,
                "image_analyses": analyze_all_images(),
                "weights": {"text": text_weight, "visual": visual_weight}
            })
            
            # Save to history
            st.session_state.history.append({
                "timestamp": datetime.now().isoformat(),
                "results": results
            })
            
            # 2. Interactive Results Grid
            cols = st.columns(3)
            for idx, ad in enumerate(results["ranked_ads"][:3]):
                with cols[idx]:
                    st.image(f"data/{ad['image']}", use_column_width=True)
                    st.metric("Score", f"{ad['text_coverage']*100:.1f}%")
                    st.caption(f"Brightness: {ad['brightness']:.1f}")
            
            # 3. Performance Visualization
            st.plotly_chart(
                px.bar(
                    pd.DataFrame(results["ranked_ads"]),
                    x="image",
                    y="text_coverage",
                    title="Ad Performance Ranking"
                ),
                use_container_width=True
            )
            
            # 4. Download Options
            st.download_button(
                label="📥 Export Full Report (JSON)",
                data=json.dumps(results, indent=2),
                file_name=f"ad_report_{datetime.now().strftime('%Y%m%d')}.json"
            )

with tab2:
    # 5. Analysis History
    st.subheader("📅 Previous Runs")
    for i, entry in enumerate(st.session_state.history[::-1]):
        with st.expander(f"Run {i+1} - {entry['timestamp']}"):
            st.json(entry["results"], expanded=False)

with tab3:
    # 6. API Documentation (For Engineers)
    st.subheader("🛠️ Integration Guide")
    st.markdown("""
    ```python
    # Sample API Request
    import requests
    
    response = requests.post(
        "https://your-api-endpoint/optimize",
        json={
            "text": "50% Off Sale!",
            "images": ["ad1.jpg", "ad2.png"]
        }
    )
    ```
    """)

# --- Hidden Features ---
# 7. Performance Monitoring (Mock)
with st.expander("🔧 Developer Tools", False):
    st.line_chart(pd.DataFrame({
        "Memory Usage": [70, 72, 68, 65],
        "Processing Time": [1.2, 1.1, 1.3, 1.0]
    }))

# 8. Error Handling
if 'error' in st.session_state:
    st.error(st.session_state.error)