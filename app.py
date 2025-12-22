import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="News Summarizer")

st.title("📰 News Summarizer")

@st.cache_resource
def load_model():
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=-1
    )

summarizer = load_model()

text = st.text_area(
    "Paste your news article here:",
    height=250
)

if st.button("Summarize"):
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
