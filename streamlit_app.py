import streamlit as st
from supabase import create_client
from curriculum import CURRICULUM, MONTHS

st.set_page_config(page_title="AI Engineering Roadmap", page_icon="🧭", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1150px;}
[data-testid="stMetric"] {background: rgba(120,120,120,.07); padding: 12px; border-radius: 10px;}
.small-muted {color: #888; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

def get_client():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
    except Exception:
        st.error("Supabase credentials are missing. Add SUPABASE_URL and SUPABASE_ANON_KEY to .streamlit/secrets.toml.")
        st.stop()
    return create_client(url, key)


def current_user_id():
    return st.session_state.get("user_id")


def load_progress(client):
    result = client.table("progress").select("task_id, done, notes, evidence_url").execute()
    return {row["task_id"]: row for row in (result.data or [])}


def save_row(client, task_id, done=None, notes=None, evidence_url=None):
    payload = {"task_id": task_id}
    if done is not None:
        payload["done"] = done
    if notes is not None:
        payload["notes"] = notes
    if evidence_url is not None:
        payload["evidence_url"] = evidence_url
    client.table("progress").upsert(payload, on_conflict="user_id,task_id").execute()


def load_profile(client):
    result = (
        client.table("profiles")
        .select("display_name, target_role, journey_notes")
        .limit(1)
        .execute()
    )

    rows = result.data or []

    if not rows:
        return {}

    return rows[0]


def save_profile(client, display_name, target_role, journey_notes):
    client.table("profiles").upsert({
        "user_id": current_user_id(),
        "display_name": display_name.strip(),
        "target_role": target_role,
        "journey_notes": journey_notes.strip(),
    }, on_conflict="user_id").execute()


def logout():
    try:
        st.session_state.client.auth.sign_out()
    except Exception:
        pass
    for key in ["client", "user_id", "email"]:
        st.session_state.pop(key, None)
    st.rerun()


def auth_screen(client):
    st.title("🧭 AI Engineering Roadmap")
    st.caption("Create your own account. Your progress, notes and evidence stay separate from everyone else.")
    tab1, tab2 = st.tabs(["Sign in", "Create account"])
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)
        if submitted:
            try:
                response = client.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.client = client
                st.session_state.user_id = response.user.id
                st.session_state.email = response.user.email
                st.rerun()
            except Exception as exc:
                st.error(f"Could not sign in: {exc}")
    with tab2:
        with st.form("signup"):
            email = st.text_input("Email address", key="signup_email")
            password = st.text_input("Password (at least 8 characters)", type="password", key="signup_password")
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            try:
                response = client.auth.sign_up({"email": email, "password": password})
                if response.session:
                    st.session_state.client = client
                    st.session_state.user_id = response.user.id
                    st.session_state.email = response.user.email
                    st.rerun()
                else:
                    st.success("Account created. Check your email for the confirmation link, then sign in.")
            except Exception as exc:
                st.error(f"Could not create account: {exc}")


def flatten_topics():
    return [topic for week in CURRICULUM for topic in week["topics"]]


def topic_progress(topic, progress):
    tasks = topic["tasks"]
    complete = sum(bool(progress.get(f"{topic['id']}::{i}", {}).get("done")) for i in range(len(tasks)))
    return complete / len(tasks) if tasks else 0


def main():
    client = st.session_state.client
    st.sidebar.title("Your roadmap")
    st.sidebar.caption(st.session_state.get("email", ""))
    if st.sidebar.button("Sign out", use_container_width=True):
        logout()

    try:
        profile = load_profile(client)
        with st.sidebar.expander("Personalize your journey", expanded=not bool(profile)):
            roles = ["AI Engineer", "Applied AI Engineer", "AI Solution Architect", "ML Engineer", "Other"]
            with st.form("profile_form"):
                display_name = st.text_input("Your name / nickname", value=profile.get("display_name", ""))
                saved_role = profile.get("target_role", "AI Engineer")
                target_role = st.selectbox("Target role", roles, index=roles.index(saved_role) if saved_role in roles else 0)
                journey_notes = st.text_area("Personal goals / context", value=profile.get("journey_notes", ""), placeholder="Your goals, milestones or constraints")
                profile_saved = st.form_submit_button("Save my journey")
            if profile_saved:
                try:
                    save_profile(client, display_name, target_role, journey_notes)
                    st.success("Your personal journey is saved.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not save profile: {exc}")
    except Exception as exc:

        st.sidebar.error(f"Profile setup error: {exc}")

    try:
        progress = load_progress(client)
    except Exception as exc:
        st.error(f"Could not load your cloud progress: {exc}")
        st.info("Check that the SQL setup has been run in Supabase and that the app secrets are correct.")
        st.stop()

    topics = flatten_topics()
    total_weight = sum(t["weight"] for t in topics)
    overall = sum(t["weight"] * topic_progress(t, progress) for t in topics) / total_weight if total_weight else 0
    done_topics = sum(topic_progress(t, progress) == 1 for t in topics)
    done_tasks = sum(bool(row.get("done")) for row in progress.values())
    total_tasks = sum(len(t["tasks"]) for t in topics)

    st.title("🧭 AI Engineering Roadmap")
    try:
        profile = load_profile(client)
    except Exception:
        profile = {}
    greeting = f"Welcome, {profile.get('display_name')} · " if profile.get("display_name") else ""
    target = profile.get("target_role", "AI Engineer")
    st.caption(f"{greeting}Your target: {target}. Learn it → build it → validate it → publish the evidence.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Weighted progress", f"{overall:.0%}")
    c2.metric("Topics completed", f"{done_topics}/{len(topics)}")
    c3.metric("Practice checkpoints", f"{done_tasks}/{total_tasks}")
    st.progress(overall)

    tab_overview, tab_syllabus, tab_project, tab_rules = st.tabs(["Overview", "Weekly syllabus", "Project & GitHub", "How we work"])

    with tab_overview:
        st.subheader("Six-month roadmap")
        for month in MONTHS:
            month_topics = [t for t in topics if t["month"] == month["number"]]
            weight = sum(t["weight"] for t in month_topics)
            pct = sum(t["weight"] * topic_progress(t, progress) for t in month_topics) / weight if weight else 0
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(f"**Month {month['number']}: {month['name']}**")
                left.caption(month["outcome"])
                right.metric("Progress", f"{pct:.0%}")
                st.progress(pct)
                st.caption(" · ".join(month["deliverables"]))
        st.subheader("Current focus")
        next_topic = next((t for t in topics if topic_progress(t, progress) < 1), None)
        if next_topic:
            st.info(f"**{next_topic['title']}** — {next_topic['why']}\n\nSuggested practice: {next_topic['example']}")
        else:
            st.success("All roadmap topics are complete. Time to polish the portfolio and interview stories.")

    with tab_syllabus:
        st.subheader("Weekly targets")
        st.caption("A week is a target, not a timer. If a topic needs more practice, finish it properly before moving on.")
        month_filter = st.selectbox("Filter by month", ["All months"] + [f"Month {m['number']} — {m['name']}" for m in MONTHS])
        for week in CURRICULUM:
            if month_filter != "All months" and not month_filter.startswith(f"Month {week['month']} "):
                continue
            week_topics = week["topics"]
            w = sum(t["weight"] for t in week_topics)
            pct = sum(t["weight"] * topic_progress(t, progress) for t in week_topics) / w if w else 0
            with st.expander(f"Week {week['week']}: {week['title']}  ·  {pct:.0%}", expanded=(pct < 1 and week['week'] == next((x['week'] for x in CURRICULUM if any(topic_progress(t, progress) < 1 for t in x['topics'])), -1))):
                st.markdown(f"**Outcome:** {week['outcome']}")
                for topic in week_topics:
                    tp = topic_progress(topic, progress)
                    st.markdown(f"---\n#### {topic['title']}  ·  Weight {topic['weight']}/5  ·  {tp:.0%}")
                    st.caption(topic["why"])
                    st.markdown(f"**Practice example:** {topic['example']}")
                    for i, task in enumerate(topic["tasks"]):
                        task_id = f"{topic['id']}::{i}"
                        existing = progress.get(task_id, {})
                        key = f"check_{task_id}"
                        checked = st.checkbox(task, value=bool(existing.get("done")), key=key)
                        if checked != bool(existing.get("done")):
                            try:
                                save_row(client, task_id, done=checked)
                                progress[task_id] = {**existing, "done": checked}
                            except Exception as exc:
                                st.error(f"Save failed: {exc}")
                    with st.form(f"evidence_{topic['id']}"):
                        existing_meta = progress.get(f"{topic['id']}::meta", {})
                        evidence = st.text_input("GitHub commit / PR / repo URL", value=existing_meta.get("evidence_url", ""), key=f"url_{topic['id']}")
                        notes = st.text_area("What can you now explain or implement?", value=existing_meta.get("notes", ""), key=f"notes_{topic['id']}", height=70)
                        save = st.form_submit_button("Save topic evidence")
                    if save:
                        try:
                            save_row(client, f"{topic['id']}::meta", notes=notes, evidence_url=evidence)
                            progress[f"{topic['id']}::meta"] = {"notes": notes, "evidence_url": evidence}
                            st.success("Evidence saved to your account.")
                        except Exception as exc:
                            st.error(f"Save failed: {exc}")

    with tab_project:
        st.subheader("One evolving project: Applied AI Engineering Lab")
        st.write("A small, modular engineering project that grows with the syllabus. Each milestone demonstrates the month's actual learning—not a tutorial clone.")
        milestones = [
            ("Month 1", "Reliable API foundation", "FastAPI service, typed schemas, PostgreSQL, migrations, validation, tests, logging and clean configuration.", "A tested API with a README, API examples and architecture sketch."),
            ("Month 2", "LLM service layer", "Provider abstraction, prompt/version management, structured outputs, tool calling, streaming, retries and token/cost tracking.", "A small service that accepts a task and returns validated structured output."),
            ("Month 3", "Document intelligence / RAG", "Ingestion, parsing, chunking, embeddings, hybrid retrieval, reranking, citations and retrieval evaluation.", "A document Q&A API with a small evaluation dataset and measured results."),
            ("Month 4", "Workflow and agent layer", "A bounded tool-using workflow with state, persistence, approval gates, retries, idempotency and audit trail.", "One reliable workflow; use an agent only where tool choice or branching is genuinely needed."),
            ("Month 5", "Production readiness", "Docker, cloud deployment, background jobs, caching, monitoring, security controls, rate limits and cost/latency analysis.", "A deployed system with health checks, logs, metrics and a short operational runbook."),
            ("Month 6", "Architecture case study", "Capacity assumptions, component choices, failure modes, scaling plan, threat model, cost model and trade-off decisions.", "A concise architecture document and a demo you can confidently defend in an interview."),
        ]
        for month, title, scope, evidence in milestones:
            with st.container(border=True):
                st.markdown(f"**{month} — {title}**")
                st.write(scope)
                st.caption(f"**Publishable evidence:** {evidence}")
        st.markdown("### Every meaningful GitHub milestone")
        st.markdown("- Small commits with clear messages; commit working increments, not just final code.\n- README: problem, architecture, setup, example request/response, limitations.\n- Tests for the behavior you claim works.\n- One short LinkedIn post per meaningful milestone: problem → engineering decision → demo/result → what you learned.\n- Be ready to explain every dependency and design choice. If you cannot explain it, it is not portfolio-ready.")
        st.info("Keep the project repository separate from this tracker repository. The tracker records evidence links; the project repo contains the actual engineering work.")

    with tab_rules:
        st.subheader("Rules that protect our time")
        rules = [
            ("Read-only concepts", "If a concept is low-weight and can be understood from a good explanation plus notes, give it a focused session. Do not manufacture a coding project for it."),
            ("High-weight concepts", "For core topics, implement a realistic example, test edge cases, and explain trade-offs before marking complete."),
            ("No tool collecting", "Choose one primary tool for a job. Learn alternatives only when a real requirement forces a comparison."),
            ("No tutorial dependency", "Use docs and examples as references. Build from a small requirement and write the implementation yourself."),
            ("DSA stays bounded", "Revise patterns and practice interview questions. Do not restart a giant problem-count challenge."),
            ("GitHub is evidence", "Commit meaningful work consistently. A green contribution graph is not a substitute for a useful repository."),
            ("Interview readiness matters", "For every important topic, be able to explain what it is, when to use it, alternatives, failure modes and one implementation."),
        ]
        for title, body in rules:
            st.markdown(f"**{title}**  \n{body}")
        st.caption("Suggested weekly review: choose the next unfinished high-priority topic, check blockers, and decide what evidence will prove completion.")

    st.sidebar.divider()
    st.sidebar.caption("Cloud sync is active when signed in. Changes are stored in Supabase and load on every device after sign-in.")


if "user_id" not in st.session_state:
    auth_screen(get_client())
else:
    main()
