import streamlit as st
from supabase import create_client
from curriculum import CURRICULUM, MONTHS

st.set_page_config(
    page_title="StudyBae — Study together. Grow together.",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap');

:root {
  --berry:#8f263e; --rose:#d95f70; --coral:#f18b91; --pink:#f6b5b6;
  --blush:#fbe2dc; --cream:#fff6ed; --paper:#fffaf5; --ink:#43252b;
  --muted:#896c6c; --line:#efc9c1; --white:#fffdfb;
}
html, body, [data-testid="stAppViewContainer"] {
  background:var(--coral) !important; color:var(--ink);
  font-family:'DM Sans',sans-serif;
}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stToolbar"] {right:1rem;}
[data-testid="stDecoration"] {display:none;}
.block-container {max-width:1180px; padding:1.2rem 2.2rem 4rem;}

/* Hide the default sidebar: this is a full-width editorial layout. */
section[data-testid="stSidebar"] {display:none;}
div[data-testid="stVerticalBlock"] {gap:.85rem;}
h1,h2,h3 {color:var(--berry)!important; font-family:'Playfair Display',serif!important; letter-spacing:-.025em;}
h1 {font-size:clamp(2.25rem,5vw,4.4rem)!important; line-height:1.03!important;}
h2 {font-size:clamp(1.55rem,3vw,2.3rem)!important;}
h3 {font-size:1.28rem!important;}
p, label, li, .stMarkdown {color:var(--ink);}
small, .muted {color:var(--muted)!important;}
/* Brand masthead */
.brandbar {
 display:flex; align-items:center; justify-content:space-between; gap:1rem;
 padding:1rem 1.4rem; margin:0 0 1.1rem; border:1.5px solid #8f263e;
 border-radius:18px; background:var(--cream); box-shadow:0 5px 0 rgba(143,38,62,.16);
}
.brandmark {font-family:'Playfair Display',serif; font-size:1.55rem; font-weight:800;color:var(--berry);}
.brandmark span {color:var(--rose);}
.brandtag {font-size:.78rem; letter-spacing:.08em; text-transform:uppercase;color:var(--muted);}
.hero {
 position:relative; overflow:hidden; padding:clamp(1.5rem,5vw,4.5rem);
 border:2px solid var(--berry); border-radius:24px;
 background:var(--blush);
 box-shadow:0 9px 0 rgba(143,38,62,.22);
}
.hero:before,.hero:after {position:absolute; font-size:clamp(3rem,8vw,7rem); opacity:.20; pointer-events:none;}
.hero:before {content:"♥  ✿"; right:4%; top:5%; transform:rotate(12deg);}
.hero:after {content:"♡  ✦"; right:9%; bottom:3%; transform:rotate(-12deg);}
.eyebrow {font-size:.72rem; text-transform:uppercase; letter-spacing:.18em; font-weight:700;color:var(--rose);margin-bottom:.7rem;}
.hero-copy {max-width:690px; position:relative; z-index:1;}
.hero-copy p {font-size:1.05rem; line-height:1.7; max-width:570px;color:#71444b;}
.hero-note {display:inline-block;margin-top:1rem;padding:.55rem .9rem;border-radius:99px;background:#f4c1b7;color:var(--berry);font-size:.82rem;font-weight:700;}
/* Navigation tabs */
div[data-testid="stTabs"] > div:first-child {border-bottom:1px solid #a94255; margin:1.2rem 0 1.5rem;}
div[data-testid="stTabs"] button[role="tab"] {border-radius:999px!important;padding:.65rem 1.15rem!important;color:#672c3b!important;font-weight:700!important;}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {background:var(--berry)!important;color:#fff!important;}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {display:none;}
/* Cream paper surfaces */
.paper {
 background:var(--paper); border:1.5px solid var(--line); border-radius:18px;
 padding:1.25rem 1.35rem; box-shadow:0 4px 0 rgba(143,38,62,.10);
}
.paper-soft {background:var(--cream);border:1px solid var(--line);border-radius:16px;padding:1rem 1.1rem;}
.section-kicker {font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;color:var(--rose);font-weight:800;}
.metric-card {background:var(--paper);border:1.5px solid var(--line);border-radius:16px;padding:1rem 1.1rem;min-height:110px;}
.metric-value {font-family:'Playfair Display',serif;font-size:2rem;font-weight:800;color:var(--berry);}
.metric-label {font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);}
.month-card {background:var(--paper);border:1.5px solid var(--line);border-radius:16px;padding:1rem 1.1rem;margin-bottom:.2rem;}
.month-number {font-family:'Playfair Display',serif;font-size:1.5rem;color:var(--rose);font-weight:800;}
/* Inputs and buttons */
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"] > div {
 background:#fffdfb!important;border:1px solid #dfaaa5!important;border-radius:12px!important;color:var(--ink)!important;
}
.stButton button,.stFormSubmitButton button {
 background:var(--berry)!important;color:white!important;border:0!important;border-radius:999px!important;
 padding:.62rem 1.2rem!important;font-weight:700!important;min-height:44px;
}
.stButton button:hover,.stFormSubmitButton button:hover {background:#6e1d31!important;border:0!important;}
.stProgress > div > div {background:#ed9b9a!important;border-radius:99px;}
.stProgress > div {background:#f3d4ca!important;border-radius:99px;}
div[data-testid="stExpander"] {background:var(--paper);border:1px solid var(--line);border-radius:14px;overflow:hidden;}
div[data-testid="stExpander"] summary {font-weight:700;color:var(--berry);}
.stCheckbox label {line-height:1.45;}
div[data-testid="stAlert"] {border-radius:14px;}
hr {border-color:#e8b7ae!important;}
.footer {text-align:center;color:#754650;font-size:.8rem;padding:2rem .5rem 0;}
/* Mobile / iPhone-width treatment */
@media(max-width:768px) {
 .block-container {padding:.65rem .75rem 2.5rem!important;}
 .brandbar {padding:.8rem 1rem;border-radius:14px;margin-bottom:.7rem;}
 .brandmark {font-size:1.3rem;}
 .brandtag {font-size:.62rem;}
 .hero {padding:1.5rem 1.15rem;border-radius:18px;}
 .hero-copy p {font-size:.94rem;}
 div[data-testid="stTabs"] > div:first-child {overflow-x:auto; white-space:nowrap;}
 div[data-testid="stTabs"] button[role="tab"] {padding:.55rem .8rem!important;font-size:.82rem!important;}
 .paper,.month-card {padding:1rem;border-radius:14px;}
 .metric-card {min-height:90px;padding:.8rem;}
 .metric-value {font-size:1.55rem;}
 .stButton button,.stFormSubmitButton button {width:100%;}
 h1 {font-size:2.3rem!important;}
}
@media(prefers-reduced-motion:reduce) { * {scroll-behavior:auto!important;transition:none!important; } }
</style>
""", unsafe_allow_html=True)

def brandbar():
    st.markdown("""
    <div class="brandbar">
      <div><div class="brandmark">Study<span>Bae</span> ♥</div>
      <div class="brandtag">Study together. Grow together.</div></div>
      <div class="brandtag">A little progress, every day ✿</div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, note=""):
    st.markdown(f"""<div class="metric-card"><div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div><div class="muted" style="font-size:.78rem">{note}</div></div>""",
    unsafe_allow_html=True)

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
    st.title("Welcome to StudyBae ♥")
    st.caption("Sign in to your own space. Your progress, notes and evidence stay private to your account.")
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
    try:
        profile = load_profile(client)
    except Exception:
        profile = {}

    try:
        progress = load_progress(client)
    except Exception as exc:
        st.error(f"Could not load your cloud progress: {exc}")
        st.info("Check the Supabase SQL setup and app secrets.")
        st.stop()

    topics = flatten_topics()
    total_weight = sum(t["weight"] for t in topics)
    overall = sum(t["weight"] * topic_progress(t, progress) for t in topics) / total_weight if total_weight else 0
    done_topics = sum(topic_progress(t, progress) == 1 for t in topics)
    done_tasks = sum(bool(row.get("done")) for row in progress.values())
    total_tasks = sum(len(t["tasks"]) for t in topics)
    next_topic = next((t for t in topics if topic_progress(t, progress) < 1), None)
    name = profile.get("display_name", "").strip()
    target = profile.get("target_role", "AI Engineer")

    brandbar()
    st.markdown(f"""
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">Your shared little corner of ambition</div>
        <h1>Big dreams.<br>Small daily wins.</h1>
        <p>{'Welcome back, ' + name + '!' if name else 'A space to learn, build and keep each other going.'}
        Your path to becoming an <b>{target}</b> starts with one focused session at a time.</p>
        <div class="hero-note">♡ Learn it · Build it · Ship it ♡</div>
      </div>
    </section>
    """, unsafe_allow_html=True)

    st.write("")
    m1,m2,m3 = st.columns(3)
    with m1: metric_card("Your progress", f"{overall:.0%}", "Across the full roadmap")
    with m2: metric_card("Topics finished", f"{done_topics}/{len(topics)}", "One step at a time")
    with m3: metric_card("Practice checks", f"{done_tasks}/{total_tasks}", "Proof beats plans")

    st.progress(overall)
    tab_home, tab_plan, tab_project, tab_us = st.tabs(["♡ Our space", "✿ Learning plan", "⌘ Our project", "♥ Our rules"])

    with tab_home:
        st.markdown('<div class="section-kicker">The next chapter</div>', unsafe_allow_html=True)
        st.subheader("A little progress goes a long way.")
        if next_topic:
            st.markdown(f"""
            <div class="paper">
              <div class="section-kicker">Up next · Month {next_topic['month']}</div>
              <h2 style="margin:.35rem 0">{next_topic['title']}</h2>
              <p>{next_topic['why']}</p>
              <div class="paper-soft"><b>Try building this:</b><br>{next_topic['example']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("Every roadmap topic is complete. Time to polish the portfolio and interview stories.")
        st.write("")
        st.markdown('<div class="section-kicker">The six-month story</div>', unsafe_allow_html=True)
        for month in MONTHS:
            mt = [t for t in topics if t["month"] == month["number"]]
            weight = sum(t["weight"] for t in mt)
            pct = sum(t["weight"] * topic_progress(t, progress) for t in mt) / weight if weight else 0
            with st.container():
                st.markdown(f"""
                <div class="month-card">
                  <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center">
                    <div><div class="section-kicker">Chapter {month['number']}</div>
                    <div style="font-family:'Playfair Display',serif;font-size:1.25rem;font-weight:800;color:#8f263e">{month['name']}</div></div>
                    <div class="month-number">{pct:.0%}</div>
                  </div><p style="margin:.45rem 0;color:#76565b">{month['outcome']}</p>
                  <div style="font-size:.82rem;color:#896c6c">✦ {' · '.join(month['deliverables'])}</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(pct)

    with tab_plan:
        st.markdown('<div class="section-kicker">Your roadmap, one week at a time</div>', unsafe_allow_html=True)
        st.subheader("The learning library")
        st.caption("A week is a target, not a timer. Finish the work properly before moving on.")
        month_filter = st.selectbox("Browse by chapter", ["All chapters"] + [f"Chapter {m['number']} — {m['name']}" for m in MONTHS])
        for week in CURRICULUM:
            if month_filter != "All chapters" and not month_filter.startswith(f"Chapter {week['month']} "):
                continue
            week_topics = week["topics"]
            w = sum(t["weight"] for t in week_topics)
            pct = sum(t["weight"] * topic_progress(t, progress) for t in week_topics) / w if w else 0
            with st.expander(f"Week {week['week']}  ·  {week['title']}  ·  {pct:.0%}", expanded=False):
                st.markdown(f"**The outcome:** {week['outcome']}")
                for topic in week_topics:
                    tp = topic_progress(topic, progress)
                    st.markdown(f"---\n### {topic['title']}  ·  {tp:.0%}")
                    st.caption(topic["why"])
                    st.markdown(f"**Build this:** {topic['example']}")
                    for i, task in enumerate(topic["tasks"]):
                        task_id = f"{topic['id']}::{i}"
                        existing = progress.get(task_id, {})
                        checked = st.checkbox(task, value=bool(existing.get("done")), key=f"check_{task_id}")
                        if checked != bool(existing.get("done")):
                            try:
                                save_row(client, task_id, done=checked)
                                progress[task_id] = {**existing, "done": checked}
                            except Exception as exc:
                                st.error(f"Save failed: {exc}")
                    with st.form(f"evidence_{topic['id']}"):
                        existing_meta = progress.get(f"{topic['id']}::meta", {})
                        evidence = st.text_input("GitHub commit / PR / repo URL", value=existing_meta.get("evidence_url", ""), key=f"url_{topic['id']}")
                        notes = st.text_area("What can you now explain or implement?", value=existing_meta.get("notes", ""), key=f"notes_{topic['id']}", height=80)
                        save = st.form_submit_button("Save my evidence")
                    if save:
                        try:
                            save_row(client, f"{topic['id']}::meta", notes=notes, evidence_url=evidence)
                            progress[f"{topic['id']}::meta"] = {"notes": notes, "evidence_url": evidence}
                            st.success("Saved to your account ♡")
                        except Exception as exc:
                            st.error(f"Save failed: {exc}")

    with tab_project:
        st.markdown('<div class="section-kicker">One project. Six chapters.</div>', unsafe_allow_html=True)
        st.subheader("Applied AI Engineering Lab")
        st.markdown('<div class="paper-soft">A living engineering project that grows with the syllabus. Every milestone should demonstrate real learning — not another tutorial clone.</div>', unsafe_allow_html=True)
        milestones = [
            ("01", "Reliable API foundation", "FastAPI service, typed schemas, PostgreSQL, migrations, validation, tests, logging and clean configuration.", "A tested API with a README, API examples and architecture sketch."),
            ("02", "LLM service layer", "Provider abstraction, prompt/version management, structured outputs, tool calling, streaming, retries and token/cost tracking.", "A small service that accepts a task and returns validated structured output."),
            ("03", "Document intelligence / RAG", "Ingestion, parsing, chunking, embeddings, hybrid retrieval, reranking, citations and retrieval evaluation.", "A document Q&A API with a small evaluation dataset and measured results."),
            ("04", "Workflow and agent layer", "A bounded tool-using workflow with state, persistence, approval gates, retries, idempotency and audit trail.", "One reliable workflow; use an agent only where tool choice or branching is genuinely needed."),
            ("05", "Production readiness", "Docker, cloud deployment, background jobs, caching, monitoring, security controls, rate limits and cost/latency analysis.", "A deployed system with health checks, logs, metrics and a short operational runbook."),
            ("06", "Architecture case study", "Capacity assumptions, component choices, failure modes, scaling plan, threat model, cost model and trade-off decisions.", "A concise architecture document and a demo you can confidently defend in an interview."),
        ]
        for num,title,scope,evidence in milestones:
            st.markdown(f"""<div class="month-card"><div class="section-kicker">Milestone {num}</div>
            <h3>{title}</h3><p>{scope}</p><div class="paper-soft"><b>Publishable proof:</b> {evidence}</div></div>""", unsafe_allow_html=True)
        st.markdown("### Tiny habits that make the project credible")
        st.markdown("- Small commits with clear messages; commit working increments, not just final code.\n- README: problem, architecture, setup, example request/response, limitations.\n- Tests for the behavior you claim works.\n- One short LinkedIn post per meaningful milestone: problem → engineering decision → demo/result → what you learned.\n- Be ready to explain every dependency and design choice.")
        st.info("Keep the project repository separate from this tracker repository. The tracker records evidence links; the project repo contains the actual engineering work.")

    with tab_us:
        st.markdown('<div class="section-kicker">A few promises to future us</div>', unsafe_allow_html=True)
        st.subheader("Rules that protect our time")
        rules = [
            ("Read-only concepts", "If a concept is low-weight and can be understood from a good explanation plus notes, give it a focused session. Do not manufacture a coding project for it."),
            ("High-weight concepts", "For core topics, implement a realistic example, test edge cases, and explain trade-offs before marking complete."),
            ("No tool collecting", "Choose one primary tool for a job. Learn alternatives only when a real requirement forces a comparison."),
            ("No tutorial dependency", "Use docs and examples as references. Build from a small requirement and write the implementation yourself."),
            ("DSA stays bounded", "Revise patterns and practice interview questions. Do not restart a giant problem-count challenge."),
            ("GitHub is evidence", "Commit meaningful work consistently. A green contribution graph is not a substitute for a useful repository."),
            ("Interview readiness matters", "For every important topic, explain what it is, when to use it, alternatives, failure modes and one implementation."),
        ]
        for title,body in rules:
            st.markdown(f'<div class="month-card"><b style="color:#8f263e">{title}</b><p style="margin:.35rem 0 0">{body}</p></div>', unsafe_allow_html=True)

    with st.expander("Your profile & account", expanded=False):
        with st.form("profile_form"):
            roles = ["AI Engineer", "Applied AI Engineer", "AI Solution Architect", "ML Engineer", "Other"]
            display_name = st.text_input("Your name / nickname", value=profile.get("display_name", ""))
            saved_role = profile.get("target_role", "AI Engineer")
            target_role = st.selectbox("Target role", roles, index=roles.index(saved_role) if saved_role in roles else 0)
            journey_notes = st.text_area("Personal goals / context", value=profile.get("journey_notes", ""), placeholder="Your goals, milestones or constraints")
            profile_saved = st.form_submit_button("Save my journey")
        if profile_saved:
            try:
                save_profile(client, display_name, target_role, journey_notes)
                st.success("Your journey is saved ♡")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save profile: {exc}")
    st.markdown('<div class="footer">Made with a little love and a lot of consistency · StudyBae ♥</div>', unsafe_allow_html=True)
    if st.button("Sign out", key="signout_bottom"):
        logout()

if "user_id" not in st.session_state:
    brandbar()
    st.markdown("""
    <section class="hero"><div class="hero-copy">
      <div class="eyebrow">Welcome to your little study corner</div>
      <h1>Two minds.<br>One beautiful journey.</h1>
      <p>Build skills, keep promises to yourselves, and celebrate every tiny win. Your progress stays private to your account.</p>
      <div class="hero-note">♡ Study together. Grow together. ♡</div>
    </div></section>
    """, unsafe_allow_html=True)
    st.write("")
    auth_screen(get_client())
else:
    main()
