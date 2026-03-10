import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from core.generate import generate_questions
from core.topics import TOPICS
from db.questions import get_question_count, insert_question
from db.schema import init_db

init_db()

st.set_page_config(page_title="Generate Questions", page_icon="🔧")
st.title("Generate Questions")
st.caption("Admin page — use this to seed the question bank via Claude.")

# Sidebar controls
with st.sidebar:
    st.header("Generation Settings")
    topic = st.selectbox(
        "Topic",
        options=TOPICS,
        format_func=lambda t: t["name"],
    )
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
    count = st.slider("Number of questions", min_value=5, max_value=30, value=10, step=5)

st.info(
    f"**{topic['name']}** ({int(topic['weight'] * 100)}% of exam)\n\n"
    + topic["description"]
)

col1, col2, col3, col4 = st.columns(4)
for i, t in enumerate(TOPICS):
    n = get_question_count(t["id"])
    [col1, col2, col3, col4][i].metric(f"Topic {t['id']}", f"{n} Qs")

st.divider()

if st.button(f"Generate {count} {difficulty} questions for Topic {topic['id']}", type="primary"):
    with st.spinner(f"Asking Claude to generate {count} questions..."):
        try:
            questions = generate_questions(
                topic_id=topic["id"],
                topic_name=topic["name"],
                topic_description=topic["description"],
                difficulty=difficulty,
                count=count,
            )
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

    if not questions:
        st.warning("No valid questions were returned. Try again.")
        st.stop()

    st.success(f"Generated {len(questions)} questions. Review below before saving.")

    st.session_state["pending_questions"] = questions
    st.session_state["pending_topic"] = topic
    st.session_state["pending_difficulty"] = difficulty

if "pending_questions" in st.session_state:
    questions = st.session_state["pending_questions"]
    topic_meta = st.session_state["pending_topic"]
    diff = st.session_state["pending_difficulty"]

    for i, q in enumerate(questions, 1):
        with st.expander(f"Q{i}: {q['stem'][:80]}...", expanded=(i == 1)):
            st.write(f"**Question:** {q['stem']}")
            for letter, text in q["options"].items():
                marker = " ✓" if letter == q["correct"] else ""
                st.write(f"**{letter})** {text}{marker}")
            st.info(f"**Explanation:** {q['explanation']}")

    st.divider()
    col_save, col_discard = st.columns([1, 4])

    if col_save.button("Save all to database", type="primary"):
        saved = 0
        for q in questions:
            insert_question(
                topic_id=topic_meta["id"],
                topic_name=topic_meta["name"],
                stem=q["stem"],
                option_a=q["options"]["A"],
                option_b=q["options"]["B"],
                option_c=q["options"]["C"],
                option_d=q["options"]["D"],
                correct_option=q["correct"],
                explanation=q["explanation"],
                difficulty=diff,
            )
            saved += 1
        del st.session_state["pending_questions"]
        del st.session_state["pending_topic"]
        del st.session_state["pending_difficulty"]
        st.success(f"Saved {saved} questions to the database.")
        st.rerun()

    if col_discard.button("Discard"):
        del st.session_state["pending_questions"]
        del st.session_state["pending_topic"]
        del st.session_state["pending_difficulty"]
        st.rerun()
