import streamlit as st
import time

# Page Configuration
st.set_page_config(
    page_title="Study Note Flashcard & Quiz Generator Agent",
    page_icon="📚",
    layout="wide"
)

# Custom CSS styling for a cleaner look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .card-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("📚 Agentic Study Assistant")
st.markdown("Transform your dense lecture notes into active-recall flashcards and practice quizzes using an automated multi-agent pipeline.")

# Sidebar for Agent Configuration
st.sidebar.header("🤖 Agent Configuration")
selected_agents = st.sidebar.multiselect(
    "Active Agents in Pipeline",
    ["Planner Agent", "Executor (Content) Agent", "Critic Agent"],
    default=["Planner Agent", "Executor (Content) Agent", "Critic Agent"]
)
difficulty = st.sidebar.selectbox("Quiz Difficulty", ["Beginner", "Intermediate", "Advanced"])
num_questions = st.sidebar.slider("Number of Practice Questions", 2, 6, 3)

# Main Input Section
st.subheader("1. Input Your Study Notes")
notes_input = st.text_area(
    "Paste your lecture notes, article text, or summary chapters here:",
    height=200,
    placeholder="Example: Photosynthesis is the process used by plants to convert light energy into chemical energy..."
)

# Simulated Agentic Pipeline Functions (Easily replaceable with real LLM / LangChain calls)
def run_planner_agent(text):
    time.sleep(1)
    # Splits text into thematic chunks
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    chunks = sentences if sentences else [text.strip()]
    return chunks

def run_executor_agent(chunks, count):
    time.sleep(1.5)
    flashcards = []
    quizzes = []
    effective_chunks = chunks if len(chunks) >= count else (chunks * ((count // len(chunks)) + 1))
    for i, chunk in enumerate(effective_chunks[:count]):
        flashcards.append({
            "front": f"Core Concept {i+1} from notes",
            "back": f"Summary: {chunk}"
        })
        quizzes.append({
            "question": f"Based on the notes, which statement best aligns with: '{chunk}'",
            "options": [
                "It describes the primary foundational mechanism.",
                "It is an unrelated historical footnote.",
                "It contradicts the core premise.",
                "It applies only under rare edge cases."
            ],
            "answer": "It describes the primary foundational mechanism."
        })
    return flashcards, quizzes

def run_critic_agent(flashcards, quizzes):
    time.sleep(1)
    # Validates and cleans output formatting
    validated_flashcards = [fc for fc in flashcards if len(fc['back']) > 10]
    validated_quizzes = [q for q in quizzes if len(q['options']) == 4]
    return validated_flashcards, validated_quizzes

# Execution Trigger Button
if st.button("🚀 Run Agentic Workflow"):
    if not notes_input.strip():
        st.warning("Please paste some study notes before running the agents.")
    else:
        # Progress status container to showcase agent collaboration
        status_container = st.status("Agent Pipeline in Progress...", expanded=True)
        
        chunks = []
        flashcards = []
        quizzes = []

        try:
            if "Planner Agent" in selected_agents:
                status_container.write("🧠 **Planner Agent:** Analyzing notes and chunking text into core topics...")
                chunks = run_planner_agent(notes_input)
            else:
                chunks = [notes_input]

            if "Executor (Content) Agent" in selected_agents:
                status_container.write("⚡ **Executor Agent:** Generating structured flashcards and MCQs...")
                flashcards, quizzes = run_executor_agent(chunks, num_questions)

            if "Critic Agent" in selected_agents:
                status_container.write("🔍 **Critic Agent:** Reviewing outputs for accuracy and formatting quality...")
                flashcards, quizzes = run_critic_agent(flashcards, quizzes)

            status_container.update(label="✅ Agentic Workflow Completed Successfully!", state="complete", expanded=True)
            
            # Save generated data to session state so it persists across UI interactions
            st.session_state['flashcards'] = flashcards
            st.session_state['quizzes'] = quizzes

        except Exception as e:
            status_container.update(label="❌ Error during execution", state="error")
            st.error(f"An error occurred: {e}")

# Display Results if Available in Session State
if 'flashcards' in st.session_state and 'quizzes' in st.session_state:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📌 Generated Flashcards", "📝 Practice Quiz"])

    with tab1:
        st.subheader("Active-Recall Flashcards")
        for idx, fc in enumerate(st.session_state['flashcards']):
            with st.container():
                st.markdown(f"""
                <div class="card-box">
                    <b>Flashcard {idx+1}</b><br><br>
                    <b>Question:</b> What is the significance of <i>{fc['front']}</i>?<br><br>
                    <details open>
                        <summary style='color: #ff4b4b; cursor: pointer;'><b>Reveal Answer</b></summary>
                        <p style='margin-top: 10px; white-space: pre-wrap; word-break: break-word;'>{fc['back']}</p>
                    </details>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.subheader("Interactive Knowledge Check")
        score = 0
        for idx, q in enumerate(st.session_state['quizzes']):
            st.markdown(f"**Question {idx+1}:** {q['question']}")
            user_choice = st.radio(
                f"Select your answer for Q{idx+1}:", 
                q['options'], 
                key=f"q_{idx}"
            )
            if user_choice == q['answer']:
                st.success("Correct!")
            else:
                st.info(f"Correct Answer: {q['answer']}")
            st.markdown("---")
