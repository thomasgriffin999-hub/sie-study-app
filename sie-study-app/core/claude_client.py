import anthropic
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def get_claude_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()
