CREATE OR REPLACE FUNCTION place_bid(
    p_auction_id UUID,
    p_team_id UUID,
    p_amount NUMERIC
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_auction auctions%ROWTYPE;
    v_team teams%ROWTYPE;
    v_settings auction_settings%ROWTYPE;
    v_squad_count INTEGER;
    v_now TIMESTAMPTZ := NOW();
    v_new_ends_at TIMESTAMPTZ;
    v_bid_id UUID;
BEGIN

    -- Lock the auction row.
    -- This prevents two bids from changing the same
    -- auction at exactly the same time.
    SELECT *
    INTO v_auction
    FROM auctions
    WHERE id = p_auction_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Auction not found';
    END IF;


    -- Auction must be live
    IF v_auction.status <> 'LIVE' THEN
        RAISE EXCEPTION 'Auction is not live';
    END IF;


    -- Check timer
    IF v_auction.ends_at IS NOT NULL
       AND v_now >= v_auction.ends_at THEN

        UPDATE auctions
        SET status = 'AWAITING_SOLD',
            updated_at = NOW()
        WHERE id = p_auction_id;

        RAISE EXCEPTION 'Auction timer has expired';
    END IF;


    -- Get team
    SELECT *
    INTO v_team
    FROM teams
    WHERE id = p_team_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Team not found';
    END IF;


    -- Count current squad
    SELECT COUNT(*)
    INTO v_squad_count
    FROM squads
    WHERE team_id = p_team_id;


    IF v_squad_count >= v_team.max_squad_size THEN
        RAISE EXCEPTION 'Team squad is already full';
    END IF;


    -- Bid must be higher than current bid
    IF p_amount <= v_auction.current_bid THEN
        RAISE EXCEPTION
            'Bid must be higher than current bid of %',
            v_auction.current_bid;
    END IF;


    -- Get auction settings
    SELECT *
    INTO v_settings
    FROM auction_settings
    ORDER BY updated_at DESC
    LIMIT 1;


    IF NOT FOUND THEN
        RAISE EXCEPTION 'Auction settings not found';
    END IF;


    -- Check minimum increment
    IF p_amount - v_auction.current_bid
       < v_settings.bid_increment THEN

        RAISE EXCEPTION
            'Minimum bid increment is %',
            v_settings.bid_increment;
    END IF;


    -- Check purse
    IF p_amount > v_team.purse_remaining THEN
        RAISE EXCEPTION 'Insufficient purse';
    END IF;


    -- Calculate timer extension.
    --
    -- If 10 seconds or less remain,
    -- add 10 seconds.
    IF v_auction.ends_at IS NOT NULL
       AND (
           EXTRACT(
               EPOCH FROM (
                   v_auction.ends_at - v_now
               )
           )
           <= v_settings.extension_seconds
       ) THEN

        v_new_ends_at =
            v_auction.ends_at
            + make_interval(
                secs => v_settings.extension_seconds
            );

    ELSE

        v_new_ends_at =
            v_auction.ends_at;

    END IF;


    -- Insert bid
    INSERT INTO bids (
        auction_id,
        player_id,
        team_id,
        amount
    )
    VALUES (
        v_auction.id,
        v_auction.player_id,
        p_team_id,
        p_amount
    )
    RETURNING id INTO v_bid_id;


    -- Update auction
    UPDATE auctions
    SET
        current_bid = p_amount,
        highest_team_id = p_team_id,
        ends_at = v_new_ends_at,
        updated_at = NOW()
    WHERE id = p_auction_id;


    RETURN json_build_object(
        'success', true,
        'bid_id', v_bid_id,
        'auction_id', p_auction_id,
        'team_id', p_team_id,
        'amount', p_amount,
        'ends_at', v_new_ends_at
    );

END;
$$;
