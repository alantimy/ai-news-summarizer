import streamlit as st
import requests
from transformers import pipeline
import os

# Page config with custom theme
st.set_page_config(
    page_title="Dynamic News Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io/',
        'Report a bug': "https://github.com/streamlit/streamlit/issues",
        'About': "# Dynamic News Summarizer\nPowered by AI and NewsAPI."
    }
)

# Custom CSS for styling
st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background-color: #f4f4f4;
    color: #000000 !important;
    font-family: 'Lato', sans-serif;
}

/* Headings */
h1, h2, h3 {
    color: #000000 !important;
    font-weight: 700;
}

/* Widget labels */
[data-testid="stWidgetLabel"] {
    color: #000000 !important;
    font-weight: 500;
}

/* ===== SELECTBOX FIX (BIGGEST ISSUE) ===== */
div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border-radius: 6px !important;
}

div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
}

div[data-baseweb="select"] span {
    color: #000000 !important;
}

div[data-baseweb="select"] svg {
    fill: #000000 !important;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
}

section[data-testid="stSidebar"] * {
    color: #000000 !important;
}

/* ===== TEXTAREA ===== */
textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 8px !important;
}

/* ===== INPUT BOXES ===== */
input {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* ===== SLIDER ===== */
[data-testid="stSlider"] span {
    color: #000000 !important;
}

/* ===== BUTTONS ===== */
.stButton>button {
    background-color: #ffcc00 !important;
    color: #1a1a1a !important;
    border-radius: 6px;
    border: none;
    font-weight: 700;
    transition: 0.25s ease;
}

.stButton>button:hover {
    background-color: #e6b800 !important;
    transform: translateY(-1px);
}

/* ===== CARDS ===== */
.card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 18px;
    margin: 18px 0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)






# Load API key
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY") or os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    st.error("NewsAPI key not found. Set it in Streamlit secrets or environment variables.")
    st.stop()

# Cached model loader
@st.cache_resource
def load_model():
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn",  # Or "sshleifer/distilbart-cnn-12-6" for speed
        device=-1
    )

summarizer = load_model()

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Simple login credentials (hardcoded for demo; hash in production)
VALID_USERNAME = "user"
VALID_PASSWORD = "pass"

# Login page
def login_page():
    st.title("🔐 Login to News Summarizer")
    st.markdown("Enter your credentials to access the app.")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# Main app
def main_app():
    # Sidebar for navigation and logout
    with st.sidebar:
        st.header(f"👋 Welcome, {st.session_state.username}!")
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        st.markdown("### Settings")
        theme = st.selectbox("Theme", ["Light", "Dark"], index=0)
        # Note: Theme switching requires more code; for now, it's placeholder
    
    # Main content
    st.title("📰 Dynamic News Summarizer")
    st.info("⚡ Select a category, fetch the latest news, and get AI-powered summaries!")
    
    # User selections
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox(
            "Choose a news category:",
            ["general", "business", "technology", "sports", "health", "science"],
            index=0
        )
    with col2:
        num_articles = st.slider("Number of articles to fetch:", 1, 10, 5)
    
    # Fetch news function
    @st.cache_data(ttl=3600)
    def fetch_news(category, num_articles):
        url = f"https://newsapi.org/v2/top-headlines?category={category}&pageSize={num_articles}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("articles", [])
        else:
            st.error(f"Failed to fetch news: {response.status_code}")
            return []
    
    # Fetch and display
    if st.button("🚀 Fetch & Summarize Latest News"):
        with st.spinner("Fetching news..."):
            articles = fetch_news(category, num_articles)
        
        if not articles:
            st.warning("No articles found. Try a different category.")
        else:
            st.success(f"✅ Fetched {len(articles)} articles!")
            progress_bar = st.progress(0)
            
            for i, article in enumerate(articles):
                title = article.get("title", "No title")
                content = article.get("content", article.get("description", "No content"))
                url = article.get("url", "#")
                
                # Card-like layout
                st.markdown(f"""
                    <div class="card">
                        <div class="title">{title}</div>
                        <p><strong>Source:</strong> {article.get('source', {}).get('name', 'Unknown')}</p>
                        <p><strong>Published:</strong> {article.get('publishedAt', 'Unknown')}</p>
                        <p><a href="{url}" target="_blank">Read Full Article</a></p>
                        <p>{content[:300]}...</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Summarize button
                if st.button(f"📝 Summarize Article {i+1}", key=f"summarize_{i}"):
                    if content and len(content.split()) > 10:
                        with st.spinner("Summarizing..."):
                            input_len = len(content.split())
                            summary = summarizer(
                                content,
                                max_length=max(30, input_len // 2),
                                min_length=10,
                                do_sample=False
                            )
                        st.markdown(f"<div class='summary'>{summary[0]['summary_text']}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Not enough content to summarize.")
                
                progress_bar.progress((i + 1) / len(articles))
    
    # Manual input section
    st.markdown("---")
    st.subheader("✏️ Or Summarize Your Own Text")
    text = st.text_area("Paste custom news text here:", height=150)
    if st.button("Summarize Custom Text"):
        if text.strip() == "":
            st.warning("Please enter some text.")
        else:
            with st.spinner("Summarizing..."):
                input_len = len(text.split())
                summary = summarizer(
                    text,
                    max_length=max(30, input_len // 2),
                    min_length=20,
                    do_sample=False
                )
            st.subheader("Summary")
            st.write(summary[0]["summary_text"])

# App logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
