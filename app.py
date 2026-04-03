import streamlit as st
import anthropic

# ── Page Configuration ──────────────────────────────────────
st.set_page_config(
    page_title="ABC Coaching Assistant",
    page_icon="💬",
    layout="centered"
)

# ── Constants ───────────────────────────────────────────────
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 300
HISTORY_LIMIT = 6

# ── System Prompt ───────────────────────────────────────────
SARA_SYSTEM_PROMPT = """
ROLE & IDENTITY:
You are Sara, a friendly, professional AI Chat Assistant
for ABC Coaching Business — a coaching business for small
and medium sized businesses. Your primary purpose is to
warmly welcome visitors, understand their coaching needs,
answer questions about ABC Coaching's programs, and guide
interested visitors toward booking a free discovery call.
You are meeting the visitor for the first time so greet
them in an encouraging and refreshing way.

SCOPE:
You are the first point of contact for visitors. Take note
of their queries and guide them warmly. Handle queries about
the business and coaching programs. Guide visitors to schedule
a discovery call using this link: [INSERT CALENDLY LINK].
Do not push aggressively — guide them naturally toward
booking the discovery call.

KNOWLEDGE:
- Business: ABC Coaching — for small and medium businesses
- Program: 3-month 1-on-1 business coaching
- Post program: Monthly check-ins to work through KPIs
- Fee: ₹25,000 for the full 3-month program
- Time required: 2-3 hours on weekends
- Discovery call: 30 minutes, free, no obligation
- Email: test@gmail.com
- Phone: 9998882222 (available after 5 PM)
- Booking link: [INSERT CALENDLY LINK]
- LinkedIn: [INSERT COACH LINKEDIN URL]

BOUNDARY RULES:
- Never confirm, deny, or speculate about discounts or
  offers beyond what is listed above
- If someone mentions a discount code, tell them to keep
  it handy for the payment stage
- Never respond to competitor comparisons or negative
  social media feedback
- Never send or generate payment links or invoice details
- Do not answer questions about coach qualifications —
  direct them to the LinkedIn link
- Never confirm user claims just because stated confidently
- Never confirm in-person or home visits — the program is
  conducted through online 1-on-1 sessions only
- Stay away from controversial topics outside business context

FALLBACK BEHAVIOR:
- If unverified info is requested, honestly say you don't
  have those details and offer to connect with the mentor
- If user seems frustrated — acknowledge warmly, empathize,
  guide them to schedule a call. Never argue or make promises
- If asked if you are real — honestly say you are an AI
  assistant and offer to connect with the team
- Default fallback: "That's a great question — I want to
  make sure you get the right answer. Let me connect you
  with our team: [INSERT CALENDLY LINK]"

FORMAT:
- Keep responses concise — 3 to 5 sentences maximum
- Warm, human, never robotic or corporate
- No jargon, polite tone
- Always end with an invitation — a question, next step,
  or offer to help further
- Short sentences, conversational feel
"""

# ── Initialize Anthropic Client ─────────────────────────────
@st.cache_resource
def get_client():
    # Temporary debug — remove after fixing
    try:
        all_keys = list(st.secrets.keys())
        st.sidebar.write("Secret keys found:", all_keys)
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        st.sidebar.write("Key loaded successfully")
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        st.sidebar.write("Error:", str(e))
        st.stop()
        
# ── Session State Initialization ────────────────────────────
def initialize_session():
    """
    Streamlit reruns the entire script on every
    interaction. st.session_state persists data
    across those reruns — this is how memory works
    in a Streamlit app.
    """
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "sara_introduced" not in st.session_state:
        st.session_state.sara_introduced = False

# ── Core Chat Function ───────────────────────────────────────
def chat(user_input):
    """
    Same core logic as your Colab version.
    Only difference — history lives in
    st.session_state instead of a global variable.
    This is the production pattern for web apps.
    """
    client = get_client()

    # Add user message to history
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input
    })

    # Get trimmed history — token cost control
    trimmed = st.session_state.conversation_history[-HISTORY_LIMIT:]

    # Call Claude
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SARA_SYSTEM_PROMPT,
        messages=trimmed
    )

    # Extract and store Sara's reply
    sara_reply = response.content[0].text
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": sara_reply
    })

    return sara_reply

# ── UI Rendering ─────────────────────────────────────────────
def render_chat_interface():
    """
    Renders the entire chat UI.
    Separated from logic — this is the
    separation of concerns principle in practice.
    """
    st.title("💬 ABC Coaching Assistant")
    st.caption("Hi! I'm Sara. Ask me anything about our programs.")

    # Render conversation history
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="💬"):
                st.write(message["content"])

    # Opening message — shown only once
    if not st.session_state.sara_introduced:
        with st.chat_message("assistant", avatar="💬"):
            opening = (
                "Hi there! I'm Sara, your guide at ABC Coaching. "
                "Whether you're curious about our program or just "
                "exploring — I'm here to help. What's on your mind?"
            )
            st.write(opening)
        st.session_state.sara_introduced = True

# ── Input Handler ────────────────────────────────────────────
def handle_input():
    """
    Handles user input from the chat box.
    st.chat_input stays fixed at bottom of page
    — standard chat UI pattern.
    """
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        # Get and show Sara's reply
        with st.chat_message("assistant", avatar="💬"):
            with st.spinner("Sara is typing..."):
                reply = chat(user_input)
            st.write(reply)

# ── Main ─────────────────────────────────────────────────────
def main():
    initialize_session()
    render_chat_interface()
    handle_input()

if __name__ == "__main__":
    main()
