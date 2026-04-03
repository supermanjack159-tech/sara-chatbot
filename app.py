import streamlit as st
import anthropic

# ── Page Configuration ──────────────────────────────────────
st.set_page_config(
    page_title="ABC Coaching Assistant",
    page_icon="💬",
    layout="centered"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit's default header and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Remove default top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 700px;
    }

    /* Chat widget wrapper */
    .chat-widget {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        overflow: hidden;
        background: #ffffff;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    /* Widget header */
    .chat-header {
        padding: 14px 18px;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        gap: 10px;
        background: #ffffff;
    }

    .sara-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #EEEDFE;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        font-weight: 600;
        color: #534AB7;
    }

    /* Chat bubbles */
    .bubble-sara {
        background: #f4f4f5;
        border-radius: 16px 16px 16px 4px;
        padding: 10px 14px;
        max-width: 75%;
        font-size: 14px;
        line-height: 1.55;
        color: #1a1a1a;
        margin: 4px 0;
    }

    .bubble-user {
        background: #534AB7;
        border-radius: 16px 16px 4px 16px;
        padding: 10px 14px;
        max-width: 75%;
        font-size: 14px;
        line-height: 1.55;
        color: #ffffff;
        margin: 4px 0;
        margin-left: auto;
    }

    .message-row {
        display: flex;
        margin-bottom: 8px;
    }

    .message-row.user {
        justify-content: flex-end;
    }

    .message-row.sara {
        justify-content: flex-start;
        align-items: flex-end;
        gap: 8px;
    }

    .mini-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #EEEDFE;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 600;
        color: #534AB7;
        flex-shrink: 0;
    }

    /* Fix Streamlit chat input to look like the widget */
    .stChatInput {
        border-radius: 24px !important;
    }

    .stChatInput > div {
        border-radius: 24px !important;
        border: 1px solid #e5e7eb !important;
    }
</style>
""", unsafe_allow_html=True)

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
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception as e:
        st.error("API key not found. Check Streamlit secrets.")
        st.stop()

# ── Session State Initialization ────────────────────────────
def initialize_session():
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "sara_introduced" not in st.session_state:
        st.session_state.sara_introduced = False

# ── Core Chat Function ───────────────────────────────────────
def chat(user_input):
    client = get_client()

    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input
    })

    trimmed = st.session_state.conversation_history[-HISTORY_LIMIT:]

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SARA_SYSTEM_PROMPT,
        messages=trimmed
    )

    sara_reply = response.content[0].text
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": sara_reply
    })

    return sara_reply

# ── Render a single message bubble ──────────────────────────
def render_message(role, content):
    if role == "user":
        st.markdown(f"""
        <div class="message-row user">
            <div class="bubble-user">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message-row sara">
            <div class="mini-avatar">S</div>
            <div class="bubble-sara">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# ── UI Rendering ─────────────────────────────────────────────
def render_chat_interface():

    # Widget header
    st.markdown("""
    <div style="border: 1px solid #e5e7eb; border-radius: 16px 16px 0 0;
                padding: 14px 18px; background: #fff;
                display: flex; align-items: center; gap: 10px;
                border-bottom: 1px solid #f0f0f0;">
        <div style="width:38px; height:38px; border-radius:50%;
                    background:#EEEDFE; display:flex; align-items:center;
                    justify-content:center; font-size:15px; font-weight:600;
                    color:#534AB7;">S</div>
        <div>
            <p style="margin:0; font-size:14px; font-weight:600;
                      color:#1a1a1a;">Sara</p>
            <p style="margin:0; font-size:12px; color:#6b7280;">
                ABC Coaching Assistant</p>
        </div>
        <div style="margin-left:auto; display:flex; align-items:center;
                    gap:6px; font-size:12px; color:#6b7280;">
            <div style="width:8px; height:8px; border-radius:50%;
                        background:#1D9E75;"></div>
            Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Message area
    st.markdown('<div style="padding: 16px 18px 8px;">', unsafe_allow_html=True)

    # Opening message — shown only once
    if not st.session_state.sara_introduced:
        render_message("assistant",
            "Hi there! I'm Sara, your guide at ABC Coaching. "
            "Whether you're curious about our program or just "
            "exploring — I'm here to help. What's on your mind?"
        )
        st.session_state.sara_introduced = True

    # Render full conversation history
    for message in st.session_state.conversation_history:
        render_message(message["role"], message["content"])

    st.markdown('</div>', unsafe_allow_html=True)

# ── Input Handler ────────────────────────────────────────────
def handle_input():
    user_input = st.chat_input("Message Sara...")

    if user_input:
        render_message("user", user_input)

        with st.spinner(""):
            reply = chat(user_input)

        render_message("assistant", reply)

# ── Main ─────────────────────────────────────────────────────
def main():
    initialize_session()
    render_chat_interface()
    handle_input()

if __name__ == "__main__":
    main()
