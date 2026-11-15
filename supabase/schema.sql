-- Run this SQL in your Supabase project's SQL Editor.
create table if not exists public.watchlist (
    user_id uuid not null references auth.users(id) on delete cascade,
    movie_title text not null,
    created_at timestamptz not null default now(),
    primary key (user_id, movie_title)
);
alter table public.watchlist enable row level security;
drop policy if exists "Users can read their own watchlist" on public.watchlist;
drop policy if exists "Users can add to their own watchlist" on public.watchlist;
drop policy if exists "Users can remove from their own watchlist" on public.watchlist;
drop policy if exists "Users can update their own watchlist" on public.watchlist;
create policy "Users can read their own watchlist" on public.watchlist for select to authenticated using (auth.uid() = user_id);
create policy "Users can add to their own watchlist" on public.watchlist for insert to authenticated with check (auth.uid() = user_id);
create policy "Users can remove from their own watchlist" on public.watchlist for delete to authenticated using (auth.uid() = user_id);
create policy "Users can update their own watchlist" on public.watchlist for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
