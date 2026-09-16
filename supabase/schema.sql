-- =========================================================
-- SPHOORTHY PREMIER LEAGUE
-- SUPABASE DATABASE SCHEMA
-- =========================================================

create extension if not exists "uuid-ossp";

-- =========================================================
-- ENUMS
-- =========================================================

create type user_role as enum (
    'admin',
    'franchise'
);

create type player_status as enum (
    'AVAILABLE',
    'LIVE',
    'SOLD',
    'UNSOLD'
);

create type auction_status as enum (
    'IDLE',
    'LIVE',
    'PAUSED',
    'AWAITING_SOLD',
    'SOLD',
    'UNSOLD'
);

-- =========================================================
-- PROFILES
-- =========================================================

create table profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    full_name text not null,
    role user_role not null default 'franchise',
    team_id uuid,
    created_at timestamptz not null default now()
);

-- =========================================================
-- TEAMS / FRANCHISES
-- =========================================================

create table teams (
    id uuid primary key default uuid_generate_v4(),

    name text not null unique,
    short_name text unique,

    owner_name text,
    owner_email text,

    purse_total numeric(12,2) not null default 1000000,
    purse_remaining numeric(12,2) not null default 1000000,

    max_squad_size integer not null default 15,

    logo_url text,
    jersey_color text,

    created_at timestamptz not null default now()
);

-- Add team relationship after teams exists
alter table profiles
add constraint profiles_team_id_fkey
foreign key (team_id)
references teams(id)
on delete set null;

-- =========================================================
-- PLAYERS
-- =========================================================

create table players (
    id uuid primary key default uuid_generate_v4(),

    name text not null,

    roll_number text unique,

    department text,
    year text,

    role text,
    batting_style text,
    bowling_style text,

    photo_url text,

    base_price numeric(12,2) not null default 10000,

    status player_status not null default 'AVAILABLE',

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- =========================================================
-- AUCTION SETTINGS
-- =========================================================

create table auction_settings (
    id uuid primary key default uuid_generate_v4(),

    bid_increment numeric(12,2) not null default 10000,

    initial_timer_seconds integer not null default 30,

    extension_seconds integer not null default 10,

    updated_at timestamptz not null default now()
);

-- Only one settings row
insert into auction_settings (
    bid_increment,
    initial_timer_seconds,
    extension_seconds
)
values (
    10000,
    30,
    10
);

-- =========================================================
-- CURRENT AUCTION
-- =========================================================

create table auctions (
    id uuid primary key default uuid_generate_v4(),

    player_id uuid references players(id)
        on delete set null,

    status auction_status not null default 'IDLE',

    current_bid numeric(12,2) default 0,

    highest_team_id uuid references teams(id)
        on delete set null,

    started_at timestamptz,
    ends_at timestamptz,

    updated_at timestamptz not null default now()
);

-- =========================================================
-- BIDS
-- =========================================================

create table bids (
    id uuid primary key default uuid_generate_v4(),

    auction_id uuid not null references auctions(id)
        on delete cascade,

    player_id uuid not null references players(id)
        on delete cascade,

    team_id uuid not null references teams(id)
        on delete cascade,

    amount numeric(12,2) not null,

    created_at timestamptz not null default now()
);

-- =========================================================
-- SQUADS
-- =========================================================

create table squads (
    id uuid primary key default uuid_generate_v4(),

    team_id uuid not null references teams(id)
        on delete cascade,

    player_id uuid not null references players(id)
        on delete cascade,

    purchase_price numeric(12,2) not null,

    purchased_at timestamptz not null default now(),

    unique(team_id, player_id),
    unique(player_id)
);

-- =========================================================
-- AUCTION HISTORY
-- =========================================================

create table auction_history (
    id uuid primary key default uuid_generate_v4(),

    player_id uuid not null references players(id)
        on delete cascade,

    team_id uuid references teams(id)
        on delete set null,

    result auction_status not null,

    final_price numeric(12,2),

    created_at timestamptz not null default now()
);

-- =========================================================
-- INDEXES
-- =========================================================

create index idx_players_status
on players(status);

create index idx_players_roll_number
on players(roll_number);

create index idx_bids_auction
on bids(auction_id);

create index idx_bids_team
on bids(team_id);

create index idx_squads_team
on squads(team_id);

create index idx_history_player
on auction_history(player_id);

-- =========================================================
-- ENABLE REALTIME
-- =========================================================

alter publication supabase_realtime
add table auctions;

alter publication supabase_realtime
add table bids;

alter publication supabase_realtime
add table players;

alter publication supabase_realtime
add table teams;

alter publication supabase_realtime
add table squads;

-- =========================================================
-- UPDATED_AT FUNCTION
-- =========================================================

create or replace function update_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create trigger players_updated_at
before update on players
for each row
execute function update_updated_at();

create trigger auctions_updated_at
before update on auctions
for each row
execute function update_updated_at();

create trigger settings_updated_at
before update on auction_settings
for each row
execute function update_updated_at();
