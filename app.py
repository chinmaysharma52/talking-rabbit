import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import anthropic
import json

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Talking Rabbitt", page_icon="🐰", layout="wide")

st.title("🐰 Talking Rabbitt – Conversational Data Analytics")
st.caption("Upload a CSV and ask questions in plain English. Powered by Claude AI.")

# ── API Key input ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.markdown("[Get your API key →](https://console.anthropic.com/)")
    st.divider()
    st.markdown("**Sample questions to try:**")
    st.markdown("- Which region had the highest revenue?")
    st.markdown("- Show me revenue by product")
    st.markdown("- Who is the top salesperson?")
    st.markdown("- What is the monthly revenue trend?")
    st.markdown("- Compare Q1 vs Q4 revenue")

# ── File upload ───────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Dataset Preview")
    st.dataframe(df, width='stretch')

    st.divider()

    question = st.text_input("💬 Ask a question about your data", placeholder="e.g. Which region had the highest revenue in Q1?")

    if question:
        if not api_key:
            st.error("Please enter your Anthropic API key in the sidebar.")
            st.stop()

        with st.spinner("🐰 Thinking..."):

            # Build prompt
            system_prompt = """You are Talking Rabbitt, an expert data analyst AI.
The user has uploaded a CSV. Answer their question using the data provided.

Respond ONLY in valid JSON with this exact structure:
{
  "answer": "A clear, accurate text answer to the question",
  "chart_type": "bar" | "line" | "pie" | "none",
  "chart_title": "Title for the chart",
  "chart_data": {"labels": [...], "values": [...]} or null,
  "insight": "One key business insight from the data"
}

Rules:
- Be precise with numbers from the actual data
- chart_data must have parallel "labels" and "values" arrays
- If no chart is needed, set chart_type to "none" and chart_data to null
- No markdown, no explanation outside the JSON"""

            user_prompt = f"""CSV Columns: {list(df.columns)}

Full Data:
{df.to_string(index=False)}

Question: {question}"""

            try:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )

                raw = message.content[0].text.strip()

                # Parse JSON response
                try:
                    result = json.loads(raw)
                except json.JSONDecodeError:
                    # Strip markdown fences if present
                    clean = raw.replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                # ── Display Answer ────────────────────────────────────
                st.success(f"**Answer:** {result['answer']}")

                # ── Display Chart ─────────────────────────────────────
                if result.get("chart_type") != "none" and result.get("chart_data"):
                    labels = result["chart_data"]["labels"]
                    values = result["chart_data"]["values"]

                    fig, ax = plt.subplots(figsize=(10, 5))
                    fig.patch.set_facecolor("#0d0d14")
                    ax.set_facecolor("#0d0d14")

                    colors = ["#FF6B35", "#F7C59F", "#1A936F", "#004E89", "#C3423F", "#88D498", "#EFEFD0"]

                    if result["chart_type"] == "bar":
                        bars = ax.bar(labels, values, color=colors[:len(labels)], edgecolor="none", width=0.6)
                        for bar, val in zip(bars, values):
                            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                                    f"{val:,.0f}", ha="center", va="bottom", color="white", fontsize=10)

                    elif result["chart_type"] == "line":
                        ax.plot(labels, values, color="#FF6B35", linewidth=2.5, marker="o",
                                markersize=7, markerfacecolor="#FF6B35")
                        ax.fill_between(range(len(labels)), values, alpha=0.15, color="#FF6B35")
                        ax.set_xticks(range(len(labels)))
                        ax.set_xticklabels(labels, rotation=45, ha="right")

                    elif result["chart_type"] == "pie":
                        wedges, texts, autotexts = ax.pie(
                            values, labels=labels, colors=colors[:len(labels)],
                            autopct="%1.1f%%", startangle=90,
                            textprops={"color": "white"}
                        )
                        for t in autotexts:
                            t.set_color("white")

                    ax.set_title(result.get("chart_title", ""), color="white", fontsize=14, pad=15)
                    ax.tick_params(colors="white")
                    for spine in ax.spines.values():
                        spine.set_edgecolor("#333")
                    ax.yaxis.set_tick_params(labelcolor="white")
                    ax.xaxis.set_tick_params(labelcolor="white")

                    st.pyplot(fig)

                # ── Display Insight ───────────────────────────────────
                if result.get("insight"):
                    st.info(f"💡 **Insight:** {result['insight']}")

            except json.JSONDecodeError:
                st.error("Claude returned an unexpected response. Try rephrasing your question.")
                st.code(raw)
            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your Anthropic API key in the sidebar.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

else:
    st.info("👆 Upload a CSV file to get started.")
