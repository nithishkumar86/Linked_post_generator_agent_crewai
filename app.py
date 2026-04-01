import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Linkedin Post Generator",
    page_icon="📝",
    layout="centered"
)

st.title("📝 AI Linkedin Post Generator with HITL")
st.caption("Generate → Review → Revise → Approve")

if "flow_id" not in st.session_state:
    st.session_state.flow_id = None
if "post_content" not in st.session_state:
    st.session_state.post_content = None
if "iteration" not in st.session_state:
    st.session_state.iteration = 0
if "approved" not in st.session_state:
    st.session_state.approved = False
if "status" not in st.session_state:
    st.session_state.status = None


# ─────────────────────────────────────────────
# Step 1 — Topic input
# ─────────────────────────────────────────────
if st.session_state.post_content is None and not st.session_state.approved:

    st.subheader("Step 1 — Enter your topic")
    topic = st.text_input("Content topic", placeholder="How AI is Transforming Healthcare in 2026")

    if st.button("🚀 Generate Post", disabled=not topic, use_container_width=True):
        with st.spinner("🤖 Crew is generating your LinkedIn post..."):
            try:
                res = requests.post(f"{API_URL}/generate", json={"topic": topic}, timeout=300)

                if res.status_code != 200:
                    st.error(f"❌ API Error: {res.status_code}\n{res.text}")
                    st.stop()

                data = res.json()

                if "content" not in data or "flow_id" not in data:
                    st.error("❌ Invalid response: missing 'content' or 'flow_id' field")
                    st.stop()

                st.session_state.flow_id = data.get("flow_id")
                st.session_state.post_content = data.get("content")
                st.session_state.iteration = data.get("iteration", 1)
                st.session_state.approved = False
                st.session_state.status = "needs_revision"
                st.rerun()

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection error. Make sure the API is running.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


# ─────────────────────────────────────────────
# Step 2 — Approved ← BEFORE review check! ✅
# ─────────────────────────────────────────────
elif st.session_state.approved:

    st.success("✅ Post Approved and Ready to Publish!")
    st.markdown("---")
    st.markdown(st.session_state.post_content)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.code(st.session_state.post_content, language="text")
            st.success("✅ Ready to copy!")

    with col2:
        if st.button("🔄 Generate New Post", use_container_width=True):
            st.session_state.flow_id = None
            st.session_state.post_content = None
            st.session_state.iteration = 0
            st.session_state.approved = False
            st.session_state.status = None
            st.rerun()


# ─────────────────────────────────────────────
# Step 3 — Review + Feedback ← LAST! ✅
# ─────────────────────────────────────────────
elif st.session_state.post_content is not None:

    st.subheader(f"Step 2 — Review LinkedIn Post (Iteration #{st.session_state.iteration})")
    st.markdown("---")
    st.markdown(st.session_state.post_content)
    st.markdown("---")

    st.subheader("Your Feedback")
    feedback = st.text_input(
        "Type 'approved' or give revision feedback:",
        placeholder="approved / make it shorter / add examples",
        key=f"feedback_{st.session_state.iteration}"
    )

    if st.button("📤 Submit", disabled=not feedback, use_container_width=True):
        with st.spinner("🔁 Processing..."):
            try:
                if not st.session_state.flow_id:
                    st.error("❌ Flow ID missing. Please generate a new post.")
                    st.stop()

                res = requests.post(
                    f"{API_URL}/feedback/{st.session_state.flow_id}",
                    json={"feedback": feedback.strip().lower()},
                    timeout=300
                )

                if res.status_code != 200:
                    st.error(f"❌ API Error: {res.status_code}\n{res.text}")
                    st.stop()

                data = res.json()

                st.session_state.post_content = data.get("content")
                st.session_state.flow_id = data.get("flow_id", st.session_state.flow_id)
                st.session_state.iteration = data.get("iteration", st.session_state.iteration + 1)
                st.session_state.status = data.get("status", "needs_revision")

                # ✅ approved check — rerun hits elif approved first!
                if st.session_state.status == "completed":
                    st.session_state.approved = data.get("approved", False)
                else:
                    st.session_state.approved = False

                st.rerun()

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection error. Make sure the API is running.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")