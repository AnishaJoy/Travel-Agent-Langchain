import streamlit as st
from agent import TravelAgent

st.set_page_config(page_title="AI Travel Agent", page_icon="✈️", layout="wide")

# Custom CSS for a premium feel
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f0f2f6;
        color: #1a1c23;
    }
    
    /* Header styling */
    h1 {
        color: #1e3a8a;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        text-align: center;
        padding-top: 50px;
        margin-bottom: 10px;
    }

    /* Subtitle/Markdown text */
    .stMarkdown p {
        color: #4b5563;
        font-size: 1.1rem;
        text-align: center;
    }

    /* Chat message containers */
    .stChatMessage {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Input area */
    .stChatInputContainer {
        padding-bottom: 20px;
    }

    /* Hide the default streamlit decoration line at the top */
    header {visibility: hidden;}
    
    /* Custom button styling if any exists */
    .stButton > button {
        border-radius: 8px;
        background-color: #1e3a8a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Welcome screen (only shown when no messages exist)
if not st.session_state.get("messages"):
    st.title("✈️ AI Travel Agent")
    st.markdown("Your personal AI travel planner. Ask me to plan a trip, check flights, or find hotels!")

# Initialize Agent
if "agent" not in st.session_state:
    try:
        st.session_state.agent = TravelAgent()
    except Exception as e:
        st.error(f"Failed to initialize Agent. Please check .env file. Error: {e}")
        st.stop()

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask me anything about travel!"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # We pass ONLY the conversation history (system prompt is handled internally by agent class logic mostly, 
        # but strictly speaking `agent.run` creates a new context. 
        # To persist context correctly, we should pass the full history. 
        # The agent.py logic currently prepends system prompt every time. This is fine for stateless REST API style.
        
        # Get the response
        try:
            # Convert streamlit history to LangChain format (AIMessage/HumanMessage)
            from langchain_core.messages import HumanMessage, AIMessage
            
            lc_history = []
            for m in st.session_state.messages[:-1]: # Exclude the just-added user message
                if m["role"] == "user":
                    lc_history.append(HumanMessage(content=m["content"]))
                else:
                    lc_history.append(AIMessage(content=m["content"]))
            
            # Run the agent
            raw_response = st.session_state.agent.run(prompt, history=lc_history)
            
            # Handle structured output (fixing the JSON display issue)
            if isinstance(raw_response, list) and len(raw_response) > 0 and isinstance(raw_response[0], dict):
                 full_response = raw_response[0].get("text", str(raw_response))
            else:
                 full_response = str(raw_response)
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "I encountered an error. Please try again."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
