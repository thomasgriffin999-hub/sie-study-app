import streamlit as st

from db.schema import init_db

init_db()

st.set_page_config(page_title="SIE Study App", page_icon="📈", layout="wide")
st.title("SIE Exam Study App")

from db.questions import get_question_count
from core.topics import TOPICS

total = get_question_count()

if total == 0:
    st.warning(
        "No questions in the database yet. "
        "Go to the **Generate Questions** page to seed the question bank first."
    )
else:
    st.success(f"{total} questions ready in the bank.")

st.divider()
st.subheader("Question Bank by Topic")
cols = st.columns(len(TOPICS))
for col, topic in zip(cols, TOPICS):
    n = get_question_count(topic["id"])
    col.metric(
        label=f"Topic {topic['id']} ({int(topic['weight']*100)}%)",
        value=f"{n} Qs",
        help=topic["name"],
    )

st.divider()
st.subheader("Get Started")

col_a, col_b = st.columns(2)
with col_a:
    st.page_link("pages/1_practice.py", label="Practice Mode", icon="📝")
    st.caption("One question at a time, with AI explanations on demand.")
with col_b:
    st.page_link("pages/4_generate.py", label="Generate Questions", icon="🔧")
    st.caption("Seed the question bank with Claude-generated questions.")
