-- Run once in Supabase Dashboard -> SQL Editor. Existing progress is preserved.
create table if not exists public.progress (
    user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
    task_id text not null,
    done boolean not null default false,
    notes text not null default '',
    evidence_url text not null default '',
    updated_at timestamptz not null default now(),
    primary key (user_id, task_id)
);
alter table public.progress enable row level security;
drop policy if exists "Users can read their own progress" on public.progress;
create policy "Users can read their own progress" on public.progress for select using (auth.uid() = user_id);
drop policy if exists "Users can insert their own progress" on public.progress;
create policy "Users can insert their own progress" on public.progress for insert with check (auth.uid() = user_id);
drop policy if exists "Users can update their own progress" on public.progress;
create policy "Users can update their own progress" on public.progress for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Private profile: one row per authenticated user.
create table if not exists public.profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    display_name text not null default '',
    target_role text not null default 'AI Engineer',
    journey_notes text not null default '',
    updated_at timestamptz not null default now()
);
alter table public.profiles enable row level security;
drop policy if exists "Users can read their own profile" on public.profiles;
create policy "Users can read their own profile" on public.profiles for select using (auth.uid() = user_id);
drop policy if exists "Users can insert their own profile" on public.profiles;
create policy "Users can insert their own profile" on public.profiles for insert with check (auth.uid() = user_id);
drop policy if exists "Users can update their own profile" on public.profiles;
create policy "Users can update their own profile" on public.profiles for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
