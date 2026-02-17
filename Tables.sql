-- ===========================
-- TEAM-LEVEL TABLES
-- ===========================

CREATE TABLE team_offense (
    id              serial PRIMARY KEY,   -- unique row identifier
    season          integer,              -- season year

    rk              integer,              -- rank
    tm              varchar(64),          -- team name
    g               integer,              -- games played
    pf              integer,              -- points for
    yds             integer,              -- total yards gained
    ply             integer,              -- total plays run
    ypp             numeric(5,2),         -- yards per play
    turnovers       integer,              -- total turnovers
    fl              integer,              -- fumbles lost
    firstd_total    integer,              -- total first downs
    cmp             integer,              -- pass completions
    att_pass        integer,              -- pass attempts
    yds_pass        integer,              -- passing yards
    td_pass         integer,              -- passing touchdowns
    ints            integer,              -- interceptions thrown
    nypa            numeric(5,2),         -- net yards per pass attempt
    firstd_pass     integer,              -- first downs via passing
    att_rush        integer,              -- rushing attempts
    yds_rush        integer,              -- rushing yards
    td_rush         integer,              -- rushing touchdowns
    ypa             numeric(5,2),         -- yards per rush attempt
    firstd_rush     integer,              -- first downs via rushing
    pen             integer,              -- penalties committed
    yds_pen         integer,              -- penalty yards
    firstpy         integer,              -- first downs via penalty
    sc_pct          numeric(5,2),         -- scoring percentage of drives
    to_pct          numeric(5,2),         -- turnover percentage of drives
    opea            numeric(8,2),         -- expected points added (EPA)

    UNIQUE (tm, season)
);

CREATE TABLE team_defense (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    tm              varchar(64),          -- team name
    g               integer,              -- games played
    pa              integer,              -- points allowed
    yds             integer,              -- yards allowed
    ply             integer,              -- plays faced
    ypp             numeric(5,2),         -- yards per play allowed
    turnovers       integer,              -- takeaways
    fl              integer,              -- fumbles recovered
    firstd_total    integer,              -- first downs allowed
    cmp             integer,              -- completions allowed
    att_pass        integer,              -- pass attempts faced
    yds_pass        integer,              -- passing yards allowed
    td_pass         integer,              -- passing TDs allowed
    ints            integer,              -- interceptions made
    nypa            numeric(5,2),         -- net yards per pass attempt allowed
    firstd_pass     integer,              -- first downs allowed via pass
    att_rush        integer,              -- rush attempts faced
    yds_rush        integer,              -- rushing yards allowed
    td_rush         integer,              -- rushing TDs allowed
    ypa             numeric(5,2),         -- yards per rush allowed
    firstd_rush     integer,              -- first downs allowed via rush
    pen             integer,              -- penalties committed by defense
    yds_pen         integer,              -- penalty yards against defense
    firstpy         integer,              -- first downs allowed via penalty
    sc_pct          numeric(5,2),         -- scoring percentage allowed
    to_pct          numeric(5,2),         -- turnover percentage forced
    depa            numeric(8,2),         -- expected points allowed

    UNIQUE (tm, season)
);

CREATE TABLE returns (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    tm              varchar(64),          -- team name
    g               integer,              -- games played
    ret_punt        integer,              -- punt returns
    yds_punt        integer,              -- punt return yards
    td_punt         integer,              -- punt return TDs
    lng_punt        integer,              -- longest punt return
    ypr_punt        numeric(5,2),         -- yards per punt return
    ret_kick        integer,              -- kickoff returns
    yds_kick        integer,              -- kickoff return yards
    td_kick         integer,              -- kickoff return TDs
    lng_kick        integer,              -- longest kickoff return
    ypr_kick        numeric(5,2),         -- yards per kickoff return
    apyd            integer,              -- all-purpose yards

    UNIQUE (tm, season)
);

CREATE TABLE kicking (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    tm              varchar(64),          -- team name
    g               integer,              -- games played

    fga_0_19        integer,              -- FG attempts 0-19 yards
    fgm_0_19        integer,              -- FG made 0-19 yards
    fga_20_29       integer,              -- FG attempts 20-29 yards
    fgm_20_29       integer,              -- FG made 20-29 yards
    fga_30_39       integer,              -- FG attempts 30-39 yards
    fgm_30_39       integer,              -- FG made 30-39 yards
    fga_40_49       integer,              -- FG attempts 40-49 yards
    fgm_40_49       integer,              -- FG made 40-49 yards
    fga_50_plus     integer,              -- FG attempts 50+ yards
    fgm_50_plus     integer,              -- FG made 50+ yards

    fga             integer,              -- total FG attempts
    fgm             integer,              -- total FG made

    lng             integer,              -- longest FG
    fg_pct          numeric(5,2),         -- FG percentage
    xpa             integer,              -- XP attempts
    xpm             integer,              -- XP made
    xp_pct          numeric(5,2),         -- XP percentage

    ko              integer,              -- kickoffs
    ko_yds          integer,              -- kickoff yards
    tb              integer,              -- touchbacks
    tb_pct          numeric(5,2),         -- touchback percentage
    ko_avg          numeric(5,2),         -- average yards per kickoff

    UNIQUE (tm, season)
);

CREATE TABLE punting (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    tm              varchar(64),          -- team name
    g               integer,              -- games played
    pnt             integer,              -- punts
    yds             integer,              -- total punt yards
    ypp             numeric(5,2),         -- yards per punt
    retyds          integer,              -- return yards allowed
    net             integer,              -- net punting yards
    nyp             numeric(5,2),         -- net yards per punt
    lng             integer,              -- longest punt
    tb              integer,              -- touchbacks
    tb_pct          numeric(5,2),         -- touchback percentage
    in20            integer,              -- punts inside 20
    in20_pct        numeric(5,2),         -- percentage inside 20
    blck            integer,              -- punts blocked

    UNIQUE (tm, season)
);

-- ===========================
-- PLAYER-LEVEL TABLES
-- ===========================

CREATE TABLE passing_stats (
    id              serial PRIMARY KEY,   -- unique row identifier
    season          integer,              -- season year

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started
    qb_rec          varchar(16),          -- QB record (W-L-T)
    cmp             integer,              -- completions
    att             integer,              -- pass attempts
    cmp_pct         numeric(5,2),         -- completion percentage
    yds             integer,              -- passing yards
    td              integer,              -- passing touchdowns
    td_pct          numeric(5,2),         -- touchdown percentage
    ints            integer,              -- interceptions
    int_pct         numeric(5,2),         -- interception percentage
    first_downs     integer,              -- first downs via passing (1D)
    succ_pct        numeric(5,2),         -- success percentage (Succ%)
    lng             integer,              -- longest pass
    ypa             numeric(5,2),         -- yards per attempt (Y/A)
    ay_pa           numeric(5,2),         -- adjusted yards per attempt (AY/A)
    ypc             numeric(5,2),         -- yards per completion (Y/C)
    ypg             numeric(6,2),         -- passing yards per game (Y/G)
    rate            numeric(6,2),         -- passer rating
    qbr             numeric(6,2),         -- QBR
    sk              integer,              -- sacks taken
    yds_sack        integer,              -- yards lost due to sacks
    sk_pct          numeric(6,3),         -- sack percentage
    ny_pa           numeric(6,2),         -- net yards per attempt (NY/A)
    any_pa          numeric(6,2),         -- adjusted net yards per attempt (ANY/A)
    four_qc         integer,              -- 4th quarter comebacks (4QC)
    gwd             integer,              -- game-winning drives (GWD)

    UNIQUE (player_name, season, tm)
);

CREATE TABLE rushing_stats (
    id              serial PRIMARY KEY,   -- unique row identifier
    season          integer,              -- season year

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started
    att             integer,              -- rush attempts
    yds             integer,              -- rushing yards
    td              integer,              -- rushing touchdowns
    first_downs     integer,              -- first downs rushing (1D)
    succ_pct        numeric(5,2),         -- success percentage (Succ%)
    lng             integer,              -- longest rush
    ypa             numeric(5,2),         -- yards per attempt (Y/A)
    ypg             numeric(6,2),         -- rushing yards per game (Y/G)
    apg             numeric(6,2),         -- attempts per game (A/G)
    fmb             integer,              -- fumbles
    awards          varchar(128),         -- awards (if any)

    UNIQUE (player_name, season, tm)
);

CREATE TABLE receiving_stats (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started
    tgt             integer,              -- targets
    rec             integer,              -- receptions
    yds             integer,              -- receiving yards
    ypr             numeric(5,2),         -- yards per reception (Y/R)
    td              integer,              -- receiving touchdowns
    first_downs     integer,              -- first downs receiving (1D)
    succ_pct        numeric(5,2),         -- success percentage (Succ%)
    lng             integer,              -- longest reception
    rpg             numeric(6,2),         -- receptions per game (R/G)
    ypg             numeric(6,2),         -- yards per game (Y/G)
    catch_pct       numeric(5,2),         -- catch percentage (Ctch%)
    ypt             numeric(5,2),         -- yards per target (Y/Tgt)
    fmb             integer,              -- fumbles

    UNIQUE (player_name, season, tm)
);

CREATE TABLE defense_stats (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team (2TM if multiple)
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started
    ints            integer,              -- interceptions
    int_yds         integer,              -- interception return yards
    int_td          integer,              -- interception TDs
    int_lng         integer,              -- longest interception return
    pd              integer,              -- passes defensed
    ff              integer,              -- forced fumbles
    fmb             integer,              -- fumbles
    fr              integer,              -- fumbles recovered
    fr_yds          integer,              -- fumble return yards
    fr_td           integer,              -- fumble return TDs
    sk              numeric(5,2),         -- sacks
    comb            integer,              -- combined tackles
    solo            integer,              -- solo tackles
    ast             integer,              -- assisted tackles
    tfl             integer,              -- tackles for loss
    qb_hits         integer,              -- QB hits
    sfty            integer,              -- safeties

    UNIQUE (player_name, season, tm)
);

CREATE TABLE kicking_stats (
    id              serial PRIMARY KEY,   -- unique row identifier
    season          integer,              -- season year

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started

    fga_0_19        integer,              -- FG attempts 0-19
    fgm_0_19        integer,              -- FG made 0-19
    fga_20_29       integer,              -- FG attempts 20-29
    fgm_20_29       integer,              -- FG made 20-29
    fga_30_39       integer,              -- FG attempts 30-39
    fgm_30_39       integer,              -- FG made 30-39
    fga_40_49       integer,              -- FG attempts 40-49
    fgm_40_49       integer,              -- FG made 40-49
    fga_50_plus     integer,              -- FG attempts 50+
    fgm_50_plus     integer,              -- FG made 50+

    fga             integer,              -- total FG attempts
    fgm             integer,              -- total FG made

    lng             integer,              -- longest FG
    fg_pct          numeric(5,2),         -- FG percentage
    xpa             integer,              -- XP attempts
    xpm             integer,              -- XP made
    xp_pct          numeric(5,2),         -- XP percentage

    ko              integer,              -- kickoffs
    ko_yds          integer,              -- kickoff yards
    tb              integer,              -- touchbacks
    tb_pct          numeric(5,2),         -- touchback percentage (TB%)
    ko_avg          numeric(5,2),         -- average yards per kickoff

    UNIQUE (player_name, season, tm)
);

CREATE TABLE punting_stats (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started
    pnt             integer,              -- punts
    yds             integer,              -- punt yards
    ypp             numeric(5,2),         -- yards per punt (Y/P)
    ret_yds         integer,              -- return yards allowed
    net_yds         integer,              -- net punting yards
    ny_pa           numeric(5,2),         -- net yards per punt (NY/P)
    lng             integer,              -- longest punt
    tb              integer,              -- touchbacks
    tb_pct          numeric(5,2),         -- touchback percentage
    pnt20           integer,              -- punts inside 20
    in20_pct        numeric(5,2),         -- percentage inside 20
    blck            integer,              -- punts blocked
    awards          varchar(128),         -- awards

    UNIQUE (player_name, season, tm)
);

CREATE TABLE return_stats (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started

    pr              integer,              -- punt returns
    pr_yds          integer,              -- punt return yards
    pr_td           integer,              -- punt return TDs
    pr_lng          integer,              -- longest punt return
    pr_ypr          numeric(5,2),         -- yards per punt return (Y/Ret)

    kr              integer,              -- kick returns
    kr_yds          integer,              -- kick return yards
    kr_td           integer,              -- kick return TDs
    kr_lng          integer,              -- longest kick return
    kr_ypr          numeric(5,2),         -- yards per kick return (Y/Ret)

    apyd            integer,              -- all-purpose yards
    awards          varchar(128),         -- awards

    UNIQUE (player_name, season, tm)
);

CREATE TABLE scoring_stats (
    id              serial PRIMARY KEY,
    season          integer,

    rk              integer,              -- rank
    player_name     varchar(128),         -- player name
    age             integer,              -- player age
    tm              varchar(64),          -- team
    pos             varchar(16),          -- position
    g               integer,              -- games played
    gs              integer,              -- games started

    rush_td         integer,              -- rushing TDs
    rec_td          integer,              -- receiving TDs
    pr_td           integer,              -- punt return TDs
    kr_td           integer,              -- kick return TDs
    fr_td           integer,              -- fumble return TDs
    int_td          integer,              -- interception TDs
    oth_td          integer,              -- other TDs
    all_td          integer,              -- total TDs

    two_pm          integer,              -- two-point makes (2PM)
    d2p             integer,              -- defensive 2-point conversions

    xpm             integer,              -- extra points made
    xpa             integer,              -- extra points attempted
    fgm             integer,              -- field goals made
    fga             integer,              -- field goals attempted
    sfty            integer,              -- safeties
    pts             integer,              -- total points
    pts_pg          numeric(5,2),         -- points per game (Pts/G)
    awards          varchar(128),         -- awards

    UNIQUE (player_name, season, tm)
);

-- ===========================
-- STANDINGS + GAMES
-- ===========================

CREATE TABLE standings (
    id              serial PRIMARY KEY,
    season          integer,

    tm              varchar(64),          -- team
    w               integer,              -- wins
    l               integer,              -- losses
    t               integer,              -- ties
    win_pct         numeric(6,3),         -- win percentage (W-L%)
    pf              integer,              -- points for
    pa              integer,              -- points against
    pd              integer,              -- point differential
    mov             numeric(6,2),         -- margin of victory (MoV)
    sos             numeric(6,2),         -- strength of schedule (SoS)
    srs             numeric(6,2),         -- simple rating system (SRS)
    osrs            numeric(6,2),         -- offensive SRS
    dsrs            numeric(6,2),         -- defensive SRS

    UNIQUE (tm, season)
);

CREATE TABLE games (
    id              serial PRIMARY KEY,   -- unique row identifier
    season          integer,              -- season year

    week            integer,              -- week number
    game_day        varchar(16),          -- day of week (renamed from "Day")
    game_date       date,                 -- date of game
    kickoff_time    varchar(16),          -- kickoff time (renamed from "Time")
    winner          varchar(64),          -- winning team
    loser           varchar(64),          -- losing team
    boxscore        varchar(128),         -- boxscore link or identifier
    pts_w           integer,              -- points by winner
    pts_l           integer,              -- points by loser
    yds_w           integer,              -- yards by winner
    to_w            integer,              -- turnovers by winner
    yds_l           integer,              -- yards by loser
    to_l            integer,              -- turnovers by loser

    UNIQUE (season, week, winner, loser)
);

-- ===========================
-- SCRAPE METADATA
-- ===========================

CREATE TABLE scraped_data_metadata (
    id              serial PRIMARY KEY,
    source_url      text NOT NULL,         -- URL that was scraped
    table_id        varchar(255) NOT NULL, -- identifier for the scraped table
    table_name      varchar(255),          -- human-readable table name
    scraped_at      timestamp NOT NULL DEFAULT NOW(), -- when the scrape occurred
    season          integer,               -- season year (optional)
    entity_type     varchar(100),          -- type of entity scraped
    table_type      varchar(100),          -- classification of table
    rows_scraped    integer,               -- number of rows scraped
    source_type     varchar(50)            -- 'visible' or 'comment'
);

-- ===========================
-- SCRAPED DATA STAGING TABLES
-- ===========================
-- Dynamically created by the scraper (excel_scraper_service.py).
-- Table names derived from HTML table id attributes on Pro-Football-Reference.
-- NOT managed by Alembic — auto-generated at scrape time.
-- Raw text columns in regular season tables; typed columns in _post tables.

-- Standings (conference-level)
CREATE TABLE scraped_afc (
    id              serial PRIMARY KEY,
    tm              text,
    w               text,
    l               text,
    w_l_            text,                  -- win-loss percentage
    pf              text,
    pa              text,
    pd              text,
    mov             text,
    sos             text,
    srs             text,
    osrs            text,
    dsrs            text,
    source_url      text,
    scraped_at      timestamp,
    season          integer,
    entity_type     text,
    table_type      text
);

CREATE TABLE scraped_nfc (
    id              serial PRIMARY KEY,
    tm              text,
    w               text,
    l               text,
    w_l_            text,
    pf              text,
    pa              text,
    pd              text,
    mov             text,
    sos             text,
    srs             text,
    osrs            text,
    dsrs            text,
    source_url      text,
    scraped_at      timestamp,
    season          integer,
    entity_type     text,
    table_type      text
);

-- Playoff standings
CREATE TABLE scraped_afc_playoff_standings (
    id              serial PRIMARY KEY,
    tm              text,
    w               integer,
    l               integer,
    t               integer,
    position        text,
    reason          text,
    source_url      text,
    scraped_at      timestamp,
    season          integer,
    entity_type     text,
    table_type      text
);

CREATE TABLE scraped_nfc_playoff_standings (
    id              serial PRIMARY KEY,
    tm              text,
    w               integer,
    l               integer,
    t               integer,
    position        text,
    reason          text,
    source_url      text,
    scraped_at      timestamp,
    season          integer,
    entity_type     text,
    table_type      text
);

-- Games
CREATE TABLE scraped_games (
    id              serial PRIMARY KEY,
    week            text,
    day             text,
    date            text,
    time            text,
    winner_tie      text,
    unnamed__5      text,                  -- home/away indicator
    loser_tie       text,
    unnamed__7      text,                  -- home/away indicator
    ptsw            text,
    ptsl            text,
    ydsw            text,
    tow             text,
    ydsl            text,
    tol             text,
    source_url      text,
    scraped_at      timestamp
);

CREATE TABLE scraped_playoff_results (
    id              serial PRIMARY KEY,
    week            text,
    day             text,
    date            text,
    winner_tie      text,
    unnamed__4      text,
    loser_tie       text,
    date_1          text,
    ptsw            integer,
    ptsl            integer,
    source_url      text,
    scraped_at      timestamp,
    season          integer,
    entity_type     text,
    table_type      text
);

CREATE TABLE scraped_preseason_games (
    id              serial PRIMARY KEY,
    week            text,
    day             text,
    date            text,
    time            text,
    vistm           text,
    pts             text,
    unnamed__6      text,
    hometm          text,
    pts_1           text,
    source_url      text,
    scraped_at      timestamp
);

-- Defense (regular season = text, post = typed)
CREATE TABLE scraped_defense (
    id              serial PRIMARY KEY,
    rk              text,
    player          text,
    age             text,
    team            text,
    pos             text,
    g               text,
    gs              text,
    def_interceptions_int   text,
    def_interceptions_yds   text,
    def_interceptions_inttd text,
    def_interceptions_lng   text,
    def_interceptions_pd    text,
    fumbles_ff      text,
    fumbles_fmb     text,
    fumbles_fr      text,
    fumbles_yds     text,
    fumbles_frtd    text,
    sk              text,
    tackles_comb    text,
    tackles_solo    text,
    tackles_ast     text,
    tackles_tfl     text,
    tackles_qbhits  text,
    sfty            text,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

CREATE TABLE scraped_defense_post (
    id              serial PRIMARY KEY,
    rk              integer,
    player          text,
    age             integer,
    team            text,
    pos             text,
    g               integer,
    gs              integer,
    def_interceptions_int   integer,
    def_interceptions_yds   integer,
    def_interceptions_inttd integer,
    def_interceptions_lng   integer,
    def_interceptions_pd    integer,
    fumbles_ff      integer,
    fumbles_fmb     integer,
    fumbles_fr      integer,
    fumbles_yds     integer,
    fumbles_frtd    integer,
    sk              double precision,
    tackles_comb    integer,
    tackles_solo    integer,
    tackles_ast     integer,
    tackles_tfl     integer,
    tackles_qbhits  integer,
    sfty            integer,
    awards          double precision,
    source_url      text,
    scraped_at      timestamp
);

-- Punting (regular season = float, post = float)
CREATE TABLE scraped_punting (
    id              serial PRIMARY KEY,
    rk              double precision,
    player          text,
    age             double precision,
    team            text,
    pos             text,
    g               double precision,
    gs              double precision,
    punting_pnt     double precision,
    punting_yds     double precision,
    punting_y_p     double precision,
    punting_retyds  double precision,
    punting_netyds  double precision,
    punting_ny_p    double precision,
    punting_lng     double precision,
    punting_tb      double precision,
    punting_tb_     double precision,
    punting_pnt20   double precision,
    punting_in20_   double precision,
    punting_blck    double precision,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

CREATE TABLE scraped_punting_post (
    id              serial PRIMARY KEY,
    rk              double precision,
    player          text,
    age             double precision,
    team            text,
    pos             text,
    g               double precision,
    gs              double precision,
    punting_pnt     double precision,
    punting_yds     double precision,
    punting_y_p     double precision,
    punting_retyds  double precision,
    punting_netyds  double precision,
    punting_ny_p    double precision,
    punting_lng     double precision,
    punting_tb      double precision,
    punting_tb_     double precision,
    punting_pnt20   double precision,
    punting_in20_   double precision,
    punting_blck    double precision,
    awards          double precision,
    source_url      text,
    scraped_at      timestamp
);

-- Receiving (regular season = text, post = float)
CREATE TABLE scraped_receiving (
    id              serial PRIMARY KEY,
    rk              text,
    player          text,
    age             text,
    team            text,
    pos             text,
    g               text,
    gs              text,
    receiving_tgt   text,
    receiving_rec   text,
    receiving_yds   text,
    receiving_y_r   text,
    receiving_td    text,
    receiving_1d    text,
    receiving_succ_ text,
    receiving_lng   text,
    receiving_r_g   text,
    receiving_y_g   text,
    receiving_ctch_ text,
    receiving_y_tgt text,
    fmb             text,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

CREATE TABLE scraped_receiving_post (
    id              serial PRIMARY KEY,
    rk              double precision,
    player          text,
    age             double precision,
    team            text,
    pos             text,
    g               double precision,
    gs              double precision,
    receiving_tgt   double precision,
    receiving_rec   double precision,
    receiving_yds   double precision,
    receiving_y_r   double precision,
    receiving_td    double precision,
    receiving_1d    double precision,
    receiving_succ_ double precision,
    receiving_lng   double precision,
    receiving_r_g   double precision,
    receiving_y_g   double precision,
    receiving_ctch_ double precision,
    receiving_y_tgt double precision,
    fmb             double precision,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

-- Returns (regular season = text, post = float)
CREATE TABLE scraped_returns (
    id              serial PRIMARY KEY,
    rk              text,
    player          text,
    age             text,
    team            text,
    pos             text,
    g               text,
    gs              text,
    punt_returns_ret    text,
    punt_returns_yds    text,
    punt_returns_prtd   text,
    punt_returns_lng    text,
    punt_returns_y_ret  text,
    kick_returns_ret    text,
    kick_returns_yds    text,
    kick_returns_krtd   text,
    kick_returns_lng    text,
    kick_returns_y_ret  text,
    apyd            text,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

CREATE TABLE scraped_returns_post (
    id              serial PRIMARY KEY,
    rk              double precision,
    player          text,
    age             double precision,
    team            text,
    pos             text,
    g               double precision,
    gs              double precision,
    punt_returns_ret    double precision,
    punt_returns_yds    double precision,
    punt_returns_prtd   double precision,
    punt_returns_lng    double precision,
    punt_returns_y_ret  double precision,
    kick_returns_ret    double precision,
    kick_returns_yds    double precision,
    kick_returns_krtd   double precision,
    kick_returns_lng    double precision,
    kick_returns_y_ret  double precision,
    apyd            double precision,
    awards          double precision,
    source_url      text,
    scraped_at      timestamp
);

-- Rushing (regular season = text, post = float)
CREATE TABLE scraped_rushing (
    id              serial PRIMARY KEY,
    rk              text,
    player          text,
    age             text,
    team            text,
    pos             text,
    g               text,
    gs              text,
    rushing_att     text,
    rushing_yds     text,
    rushing_td      text,
    rushing_1d      text,
    rushing_succ_   text,
    rushing_lng     text,
    rushing_y_a     text,
    rushing_y_g     text,
    rushing_a_g     text,
    fmb             text,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

CREATE TABLE scraped_rushing_post (
    id              serial PRIMARY KEY,
    rk              double precision,
    player          text,
    age             double precision,
    team            text,
    pos             text,
    g               double precision,
    gs              double precision,
    rushing_att     double precision,
    rushing_yds     double precision,
    rushing_td      double precision,
    rushing_1d      double precision,
    rushing_succ_   double precision,
    rushing_lng     double precision,
    rushing_y_a     double precision,
    rushing_y_g     double precision,
    rushing_a_g     double precision,
    fmb             double precision,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

-- Scoring (regular season = text, post = typed)
CREATE TABLE scraped_scoring (
    id              serial PRIMARY KEY,
    rk              text,
    player          text,
    age             text,
    team            text,
    pos             text,
    g               text,
    gs              text,
    touchdowns_rshtd    text,
    touchdowns_rectd    text,
    touchdowns_prtd     text,
    touchdowns_krtd     text,
    touchdowns_frtd     text,
    touchdowns_inttd    text,
    touchdowns_othtd    text,
    touchdowns_alltd    text,
    touchdowns_2pm      text,
    d2p             text,
    pat_xpm         text,
    pat_xpa         text,
    fg_fgm          text,
    fg_fga          text,
    sfty            text,
    pts             text,
    pts_g           text,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);

CREATE TABLE scraped_scoring_post (
    id              serial PRIMARY KEY,
    rk              integer,
    player          text,
    age             integer,
    team            text,
    pos             text,
    g               integer,
    gs              integer,
    touchdowns_rshtd    integer,
    touchdowns_rectd    integer,
    touchdowns_prtd     integer,
    touchdowns_krtd     integer,
    touchdowns_frtd     integer,
    touchdowns_inttd    integer,
    touchdowns_othtd    integer,
    touchdowns_alltd    integer,
    touchdowns_2pm      integer,
    d2p             integer,
    pat_xpm         integer,
    pat_xpa         integer,
    fg_fgm          integer,
    fg_fga          integer,
    sfty            integer,
    pts             integer,
    pts_g           double precision,
    awards          text,
    source_url      text,
    scraped_at      timestamp
);
