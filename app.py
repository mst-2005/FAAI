import streamlit as st
import os
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="Study Note Flashcard & Quiz Generator Agent",
    page_icon="📚",
    layout="wide"
)

# Custom CSS styling
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
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("📚 Agentic Study Assistant (Powered by Gemini)")
st.markdown("Transform your dense lecture notes into active-recall flashcards and practice quizzes using an automated multi-agent pipeline.")

# Sidebar for Configuration & API Key
st.sidebar.header("🤖 Agent & API Configuration")

# Secure API Key Input
api_key_input = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Get your key from Google AI Studio")

# If user provided a key via sidebar, set it in environment or use it directly
if api_key_input:
    os.environ["GEMINI_API_KEY"] = api_key_input

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

# Real Agentic Pipeline Functions using Gemini API
def run_planner_agent(client, text):
    # Planner Agent: Chunks and categorizes text
    prompt = f"Analyze the following study notes and break them down into {num_questions} core thematic sub-topics or conceptual sections:\n\n{text}"
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

def run_executor_agent(client, plan_text):
    # Executor Agent: Generates Flashcards and Quizzes based on the plan
    prompt = f"""
    Based on the following sub-topics/plan, generate:
    1. {num_questions} Flashcards (Front/Question and Back/Answer format).
    2. {num_questions} Multiple Choice Questions (MCQs) with 4 options each and the correct answer explicitly marked.
    
    Plan / Context:
    {plan_text}
    
    Format the output clearly separating Flashcards and Quizzes so it can be parsed easily.
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

def run_critic_agent(client, raw_content):
    # Critic Agent: Reviews and validates output quality
    prompt = f"""
    Review the following generated study materials. Clean up any formatting errors, ensure all quiz options are accurate, and format the output neatly into JSON-like or clearly structured blocks for display:
    
    {raw_content}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

# Execution Trigger Button
if st.button("🚀 Run Agentic Workflow"):
    # Check if API key is available
    active_api_key = os.environ.get("GEMINI_API_KEY")
    if not active_api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar to run the agents.")
    elif not notes_input.strip():
        st.warning("Please paste some study notes before running the agents.")
    else:
        try:
            # Initialize the Gemini client using the modern google-genai SDK
            client = genai.Client(api_key=active_api_key)
            
            # Progress status container to showcase agent collaboration
            status_container = st.status("Agent Pipeline in Progress...", expanded=True)
            
            plan_result = ""
            executor_result = ""
            final_output = ""

            if "Planner Agent" in selected_agents:
                status_container.write("🧠 **Planner Agent:** Analyzing notes and chunking text into core topics...")
                plan_result = run_planner_agent(client, notes_input)
            else:
                plan_result = notes_input

            if "Executor (Content) Agent" in selected_agents:
                status_container.write("⚡ **Executor Agent:** Generating structured flashcards and MCQs...")
                executor_result = run_executor_agent(client, plan_result)
            else:
                executor_result = plan_result

            if "Critic Agent" in selected_agents:
                status_container.write("🔍 **Critic Agent:** Reviewing outputs for accuracy and formatting quality...")
                final_output = run_critic_agent(client, executor_result)
            else:
                final_output = executor_result

            status_container.update(label="✅ Agentic Workflow Completed Successfully!", state="complete", expanded=False)
            
            # Save generated raw response to session state
            st.session_state['final_output'] = final_output

        except Exception as e:
            st.error(f"An error occurred during API execution: {e}")

# Display Results if Available in Session State
if 'final_output' in st.session_state:
    st.markdown("---")
    st.subheader("🎯 Generated Study Suite (Gemini Output)")
    
    # Display the structured output returned by the agent pipeline
    st.markdown(st.session_state['final_output'])
