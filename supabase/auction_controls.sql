CREATE OR REPLACE FUNCTION pause_auction(
    p_auction_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_auction auctions%ROWTYPE;
BEGIN

    SELECT *
    INTO v_auction
    FROM auctions
    WHERE id = p_auction_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Auction not found';
    END IF;

    IF v_auction.status <> 'LIVE' THEN
        RAISE EXCEPTION 'Only a live auction can be paused';
    END IF;

    UPDATE auctions
    SET
        status = 'PAUSED',
        updated_at = NOW()
    WHERE id = p_auction_id;

    RETURN jsonb_build_object(
        'success', true,
        'status', 'PAUSED',
        'auction_id', p_auction_id
    );
END;
$$;


CREATE OR REPLACE FUNCTION resume_auction(
    p_auction_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_auction auctions%ROWTYPE;
BEGIN

    SELECT *
    INTO v_auction
    FROM auctions
    WHERE id = p_auction_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Auction not found';
    END IF;

    IF v_auction.status <> 'PAUSED' THEN
        RAISE EXCEPTION 'Only a paused auction can be resumed';
    END IF;

    UPDATE auctions
    SET
        status = 'LIVE',
        updated_at = NOW()
    WHERE id = p_auction_id;

    RETURN jsonb_build_object(
        'success', true,
        'status', 'LIVE',
        'auction_id', p_auction_id
    );
END;
$$;


REVOKE EXECUTE ON FUNCTION pause_auction(UUID)
FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION pause_auction(UUID)
FROM anon;

REVOKE EXECUTE ON FUNCTION pause_auction(UUID)
FROM authenticated;

REVOKE EXECUTE ON FUNCTION resume_auction(UUID)
FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION resume_auction(UUID)
FROM anon;

REVOKE EXECUTE ON FUNCTION resume_auction(UUID)
FROM authenticated;

GRANT EXECUTE ON FUNCTION pause_auction(UUID)
TO service_role;

GRANT EXECUTE ON FUNCTION resume_auction(UUID)
TO service_role;
