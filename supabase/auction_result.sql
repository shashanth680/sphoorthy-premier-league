CREATE OR REPLACE FUNCTION mark_auction_sold(
    p_auction_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_auction auctions%ROWTYPE;
    v_team teams%ROWTYPE;
    v_player players%ROWTYPE;
    v_squad_count INTEGER;
    v_squad_id UUID;
BEGIN

    -- Lock auction
    SELECT *
    INTO v_auction
    FROM auctions
    WHERE id = p_auction_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Auction not found';
    END IF;

    IF v_auction.status <> 'LIVE'
       AND v_auction.status <> 'AWAITING_SOLD'
    THEN
        RAISE EXCEPTION 'Auction cannot be marked sold';
    END IF;

    -- A team must have placed a bid
    IF v_auction.highest_team_id IS NULL THEN
        RAISE EXCEPTION 'No team has placed a bid';
    END IF;

    -- Lock player
    SELECT *
    INTO v_player
    FROM players
    WHERE id = v_auction.player_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Player not found';
    END IF;

    -- Lock team
    SELECT *
    INTO v_team
    FROM teams
    WHERE id = v_auction.highest_team_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Team not found';
    END IF;

    -- Check squad size
    SELECT COUNT(*)
    INTO v_squad_count
    FROM squads
    WHERE team_id = v_team.id;

    IF v_squad_count >= v_team.max_squad_size THEN
        RAISE EXCEPTION 'Team squad is already full';
    END IF;

    -- Check purse again before final sale
    IF v_auction.current_bid > v_team.purse_remaining THEN
        RAISE EXCEPTION 'Team has insufficient purse';
    END IF;

    -- Add player to squad
    INSERT INTO squads (
        team_id,
        player_id,
        purchase_price
    )
    VALUES (
        v_team.id,
        v_player.id,
        v_auction.current_bid
    )
    RETURNING id INTO v_squad_id;

    -- Deduct purse
    UPDATE teams
    SET
        purse_remaining =
            purse_remaining - v_auction.current_bid
    WHERE id = v_team.id;

    -- Mark player SOLD
    UPDATE players
    SET
        status = 'SOLD',
        updated_at = NOW()
    WHERE id = v_player.id;

    -- Mark auction SOLD
    UPDATE auctions
    SET
        status = 'SOLD',
        updated_at = NOW()
    WHERE id = p_auction_id;

    -- Save auction history
    INSERT INTO auction_history (
        player_id,
        team_id,
        result,
        final_price
    )
    VALUES (
        v_player.id,
        v_team.id,
        'SOLD',
        v_auction.current_bid
    );

    RETURN jsonb_build_object(
        'success', true,
        'result', 'SOLD',
        'auction_id', p_auction_id,
        'player_id', v_player.id,
        'player_name', v_player.name,
        'team_id', v_team.id,
        'team_name', v_team.name,
        'final_price', v_auction.current_bid,
        'squad_id', v_squad_id,
        'purse_remaining',
            v_team.purse_remaining
            - v_auction.current_bid
    );

END;
$$;


CREATE OR REPLACE FUNCTION mark_auction_unsold(
    p_auction_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_auction auctions%ROWTYPE;
    v_player players%ROWTYPE;
BEGIN

    -- Lock auction
    SELECT *
    INTO v_auction
    FROM auctions
    WHERE id = p_auction_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Auction not found';
    END IF;

    IF v_auction.status <> 'LIVE'
       AND v_auction.status <> 'AWAITING_SOLD'
    THEN
        RAISE EXCEPTION 'Auction cannot be marked unsold';
    END IF;

    -- Lock player
    SELECT *
    INTO v_player
    FROM players
    WHERE id = v_auction.player_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Player not found';
    END IF;

    -- Mark player UNSOLD
    UPDATE players
    SET
        status = 'UNSOLD',
        updated_at = NOW()
    WHERE id = v_player.id;

    -- Mark auction UNSOLD
    UPDATE auctions
    SET
        status = 'UNSOLD',
        updated_at = NOW()
    WHERE id = p_auction_id;

    -- Save history
    INSERT INTO auction_history (
        player_id,
        team_id,
        result,
        final_price
    )
    VALUES (
        v_player.id,
        NULL,
        'UNSOLD',
        NULL
    );

    RETURN jsonb_build_object(
        'success', true,
        'result', 'UNSOLD',
        'auction_id', p_auction_id,
        'player_id', v_player.id,
        'player_name', v_player.name
    );

END;
$$;


-- Prevent normal users from calling these functions directly
REVOKE EXECUTE ON FUNCTION mark_auction_sold(UUID)
FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION mark_auction_sold(UUID)
FROM anon;

REVOKE EXECUTE ON FUNCTION mark_auction_sold(UUID)
FROM authenticated;

REVOKE EXECUTE ON FUNCTION mark_auction_unsold(UUID)
FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION mark_auction_unsold(UUID)
FROM anon;

REVOKE EXECUTE ON FUNCTION mark_auction_unsold(UUID)
FROM authenticated;

-- Backend service role can execute them
GRANT EXECUTE ON FUNCTION mark_auction_sold(UUID)
TO service_role;

GRANT EXECUTE ON FUNCTION mark_auction_unsold(UUID)
TO service_role;
