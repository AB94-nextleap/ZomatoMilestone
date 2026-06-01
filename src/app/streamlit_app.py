import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path so we can import src modules
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.recommendation_service import RecommendationService, RecommendationServiceError

# Page Configuration
st.set_page_config(
    page_title="Zomato AI - Restaurant Advisor",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Premium Styling (Dark Mode / Glassmorphism theme)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,600;1,400&display=swap');
    
    /* Global Styles */
    .reportview-container {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Custom Title */
    .title-container {
        background: linear-gradient(135deg, #FF4B60 0%, #1A0D10 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(255, 75, 96, 0.2);
        margin-bottom: 30px;
        text-align: center;
        border: 1px solid rgba(255, 75, 96, 0.2);
    }
    .title-main {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 3.5rem;
        color: #ffffff;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .title-sub {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        color: #ffcbd1;
        margin-top: 10px;
        font-weight: 300;
    }
    
    /* Glassmorphism Cards */
    .restaurant-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
    }
    .restaurant-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px 0 rgba(255, 75, 96, 0.25);
        border-color: rgba(255, 75, 96, 0.5);
    }
    .restaurant-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 12px;
        margin-bottom: 16px;
    }
    .restaurant-title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0;
    }
    .restaurant-rank-badge {
        background: linear-gradient(135deg, #FF4B60 0%, #d82b40 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(255, 75, 96, 0.4);
    }
    .rating-badge {
        background: rgba(255, 193, 7, 0.15);
        color: #ffc107;
        border: 1px solid rgba(255, 193, 7, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Tags and Details */
    .restaurant-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.08);
        color: #e0e0e0;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .restaurant-cost {
        font-weight: 600;
        color: #52c41a;
        font-size: 1.1rem;
        margin: 10px 0;
    }
    
    /* AI Rationale Block */
    .rationale-block {
        background: rgba(255, 75, 96, 0.08);
        border-left: 4px solid #FF4B60;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin-top: 16px;
        font-style: italic;
        color: #f0f0f0;
        line-height: 1.5;
    }
    .rationale-header {
        font-weight: 600;
        color: #FF4B60;
        font-style: normal;
        margin-bottom: 4px;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Highlights */
    .highlight-pill {
        display: inline-block;
        background: rgba(82, 196, 26, 0.12);
        color: #52c41a;
        border: 1px solid rgba(82, 196, 26, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        text-transform: uppercase;
    }
    
    /* Summary Block */
    .summary-block {
        background: rgba(255, 255, 255, 0.03);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 30px;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #e0e0e0;
    }
    
    /* Empty State Banner */
    .suggestion-box {
        background: rgba(24, 144, 255, 0.08);
        border-left: 4px solid #1890ff;
        border-radius: 0 12px 12px 0;
        padding: 20px;
        margin-bottom: 25px;
        color: #e6f7ff;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Recommendation Service
# Programmatic auto-ingestion if data file is missing (essential for cloud deployment)
from src.config.loader import get_settings
data_path = Path(get_settings().get("data_path", "data/restaurants.parquet"))
if not data_path.is_absolute():
    data_path = PROJECT_ROOT / data_path

if not data_path.exists():
    with st.spinner("📦 Restaurant database not found. Ingesting Zomato dataset from Hugging Face..."):
        try:
            import subprocess
            ingest_script = PROJECT_ROOT / "scripts" / "ingest.py"
            subprocess.run([sys.executable, str(ingest_script)], check=True)
            st.toast("✅ Data ingestion completed successfully!")
        except Exception as ingest_err:
            st.error(f"Failed to automatically ingest Zomato dataset: {ingest_err}")
            st.info("💡 Make sure you run the ingestion step locally first: `python scripts/ingest.py`")
            st.stop()

@st.cache_resource
def get_service() -> RecommendationService:
    return RecommendationService.from_defaults()

try:
    service = get_service()
    store = service.store
except Exception as e:
    st.error(f"Error loading the recommendation engine database: {e}")
    st.stop()

# Helper lists for forms
cities = store.list_cities()
all_cuisines = sorted(list({c for r in store.query_all() for c in r.cuisines if c}))

# --- Header Section ---
st.markdown(
    """
    <div class="title-container">
        <h1 class="title-main">Zomato AI Advisor</h1>
        <p class="title-sub">Hyper-Personalized & Grounded Restaurant Recommendations</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar Inputs ---
with st.sidebar:
    st.markdown("### 🔍 Your Preferences")
    
    # Location input
    location = st.selectbox(
        "Location / Area",
        options=[""] + cities,
        index=0,
        help="Select a supported city or neighborhood",
    )
    
    # Budget input
    budget = st.selectbox(
        "Budget Level",
        options=["low", "medium", "high"],
        index=1,
        format_func=lambda x: {
            "low": "Low (Under ₹500 for two)",
            "medium": "Medium (₹500 - ₹1500 for two)",
            "high": "High (Above ₹1500 for two)"
        }[x],
        help="Price range matching estimated cost for two people",
    )
    
    # Cuisine input (combobox-like selector)
    cuisine = st.selectbox(
        "Cuisine",
        options=[""] + all_cuisines,
        index=0,
        help="Cuisine you are craving",
    )
    
    # Rating slider
    min_rating = st.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=5.0,
        value=3.5,
        step=0.1,
        format="%.1f ⭐",
    )
    
    # Additional preferences (tags / free text)
    additional_input = st.text_area(
        "Additional Preferences",
        placeholder="e.g. outdoor seating, family-friendly, quiet, live music, quick service",
        help="Comma-separated special requests or attributes",
    )
    
    # Top K slider
    top_k = st.slider(
        "Number of recommendations",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )
    
    st.markdown("---")
    submit = st.button("Generate Recommendations 🚀", use_container_width=True)

# --- Main Results View ---
if submit:
    # 1. Validate mandatory location
    if not location:
        st.error("🚨 Location is required. Please select a city/area in the sidebar.")
        st.stop()
        
    # Prepare preferences payload
    preferences_payload = {
        "location": location,
        "budget": budget,
        "cuisine": cuisine if cuisine else None,
        "min_rating": min_rating,
        "additional_preferences": [tag.strip() for tag in additional_input.split(",") if tag.strip()] if additional_input else [],
    }
    
    # Use selected top_k configuration dynamically
    service.top_k = top_k
    
    with st.spinner("✨ Fetching matching candidates and generating AI explanations..."):
        try:
            # 2. Get recommendations
            response = service.recommend(preferences_payload)
        except RecommendationServiceError as exc:
            st.error(f"Validation / Configuration Error: {exc.message}")
            if exc.suggestions:
                st.info("💡 Suggestions:\n" + "\n".join([f"- {s}" for s in exc.suggestions]))
            st.stop()
        except Exception as exc:
            st.error(f"An unexpected internal error occurred: {exc}")
            st.stop()
            
    # 3. Check for empty candidate sets
    if not response.recommendations:
        st.markdown(
            f"""
            <div class="suggestion-box">
                <h4>🔍 No matching restaurants found!</h4>
                <p>We couldn't find any restaurants in <b>{location}</b> matching all your strict filters.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if response.suggestions:
            st.markdown("### 💡 Try adjusting your preferences:")
            for sugg in response.suggestions:
                st.markdown(f"- {sugg}")
        st.stop()
        
    # 4. Display AI Summary if present
    if response.summary:
        st.markdown(
            f"""
            <div class="summary-block">
                <b>🤖 AI Advisor Summary:</b><br/>
                {response.summary}
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    # 5. Display Recommendations Cards
    st.markdown(f"### 🍽️ Top Recommendations ({len(response.recommendations)} matches)")
    
    for rec in response.recommendations:
        rest = rec.restaurant
        
        # Format Cuisines
        cuisine_badges = "".join([f'<span class="restaurant-tag">{c}</span>' for c in rest.cuisines])
        
        # Format Highlights/Matches if any
        highlight_badges = ""
        if rec.highlights:
            highlight_badges = "".join([f'<span class="highlight-pill">{h}</span>' for h in rec.highlights])
            
        # Cost formatting
        cost_str = f"₹{int(rest.estimated_cost_for_two):,}" if rest.estimated_cost_for_two else "N/A"
        
        # Construct Card HTML (left-aligned to prevent markdown parser from treating indentation as a code block)
        card_html = f"""<div class="restaurant-card">
<div class="restaurant-header">
<div>
<h2 class="restaurant-title">{rest.name}</h2>
<p style="margin: 4px 0 0 0; color: #a0a0a0; font-size: 0.95rem;">
📍 {rest.location}
</p>
</div>
<div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
<span class="restaurant-rank-badge">RANK #{rec.rank}</span>
<span class="rating-badge">⭐ {rest.rating:.1f} / 5.0</span>
</div>
</div>
<div style="margin-bottom: 12px;">
{cuisine_badges}
</div>
<div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px;">
<div class="restaurant-cost">
💰 Cost for two: {cost_str} ({rest.budget_band.upper()} budget)
</div>
<div>
{highlight_badges}
</div>
</div>
<div class="rationale-block">
<div class="rationale-header">AI Explanation</div>
"{rec.explanation}"
</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)
else:
    # Initial landing screen design
    st.markdown(
        """
        <div style="text-align: center; padding: 60px 20px; opacity: 0.85;">
            <span style="font-size: 4rem;">🍜</span>
            <h3 style="margin-top: 20px; font-weight: 600;">Welcome to Zomato AI Advisor</h3>
            <p style="max-width: 600px; margin: 10px auto; color: #b0b0b0;">
                To get started, select your location, budget, and cravings in the sidebar on the left and click <b>Generate Recommendations</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
