# AI Engineering Roadmap Tracker

A lightweight Streamlit tracker for a six-month, outcome-based AI Engineering roadmap. Progress is stored in Supabase and tied to the signed-in user, so it syncs across devices.

## Features
- Email/password sign-up and sign-in through Supabase Auth
- 24 weekly learning targets across six months
- Weighted topic completion (core topics count more)
- Practice checkpoints, notes and GitHub evidence links
- One evolving Applied AI Engineering Lab project
- Responsive Streamlit interface for desktop and mobile browsers

## 1. Create the Supabase backend
1. Create a Supabase project.
2. Open **SQL Editor** and run `supabase_schema.sql`.
3. In **Project Settings → API**, copy the Project URL and the publishable/anon key.
4. For a personal tracker, email confirmation can remain enabled. If enabled, confirm your email before signing in.

## 2. Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Supabase URL and anon/publishable key
streamlit run streamlit_app.py
```

Never commit `.streamlit/secrets.toml`. The anon/publishable key is intended for client-side use only when Row Level Security is correctly enabled. Never put a Supabase service-role key in this app.

## 3. Deploy free
1. Push this repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Create an app from this repository and select `streamlit_app.py` as the entrypoint.
4. In the app's **Settings → Secrets**, add the same two values from your local secrets file:

```toml
SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
```

5. Deploy. Open the resulting `*.streamlit.app` URL on your phone and computer and sign in with the same account.

## Data model and sync
Each progress record is keyed by `(user_id, task_id)`. Supabase Auth identifies the user, and Row Level Security ensures users can only read or change their own rows. The app fetches progress from the cloud when it loads and writes changes to Supabase.

## Roadmap rules
- Topic weights are relative priority scores from 1 to 5.
- High-weight topics require practical implementation and validation.
- Lower-weight concepts can be completed with focused reading plus a small check for understanding.
- A topic is complete only when its practice checkpoints are done. Save a GitHub link and a short explanation as evidence.
- The six-month plan is a sequence, not a deadline. Extend a week when the implementation is not yet understood.

## Project strategy
Keep the actual **Applied AI Engineering Lab** in a separate repository. This tracker stores links and notes; it is not the project itself. Each month adds a capability to the same modular service, with a small demo and technical write-up.


## Multi-user accounts

Each person signs up with their own email/password. Progress and profile data are isolated by Supabase Row Level Security. Each account can save a display name, target role and personal journey notes. Sign in with the same account on phone and computer to sync progress.

### Upgrade Supabase

Open Supabase Dashboard → SQL Editor, paste the updated `supabase_schema.sql`, and run it. Existing progress rows are preserved; the private `profiles` table and policies are added. Use only the project URL and publishable/anon key in Streamlit secrets. Never commit `.streamlit/secrets.toml` or use the service-role key in the app.
