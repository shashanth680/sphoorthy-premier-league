import { useEffect, useState } from "react";


const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


function FranchiseDashboard({
  user,
  onLogout
}) {

  const [auction, setAuction] =
    useState(null);

  const [team, setTeam] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [bidding, setBidding] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [timeLeft, setTimeLeft] =
    useState(0);


  const token =
    localStorage.getItem(
      "spl_access_token"
    );


  async function apiRequest(
    url,
    options = {}
  ) {

    const response = await fetch(
      `${API_URL}${url}`,
      {
        ...options,

        headers: {
          "Content-Type":
            "application/json",

          Authorization:
            `Bearer ${token}`,

          ...(options.headers || {})
        }
      }
    );

    const data =
      await response.json();

    if (!response.ok) {

      throw new Error(
        data.detail ||
        "Request failed"
      );
    }

    return data;
  }


  async function loadData() {

    try {

      const [
        auctionData,
        teamData
      ] = await Promise.all([

        apiRequest(
          "/api/auction/current"
        ),

        apiRequest(
          `/api/teams/${user.team_id}`
        )

      ]);

      setAuction(
        auctionData.auction || null
      );

      setTeam(
        teamData.team || null
      );

    } catch (error) {

      setMessage(
        error.message
      );

    } finally {

      setLoading(false);

    }
  }


 useEffect(() => {

  loadData();


  const channel =
    supabase
      .channel("spl-auction-live")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "auctions"
        },
        () => {
          loadData();
        }
      )
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "bids"
        },
        () => {
          loadData();
        }
      )
      .subscribe();


  return () => {

    supabase.removeChannel(
      channel
    );

  };

}, []);

  useEffect(() => {

    if (
      !auction ||
      !auction.ends_at ||
      auction.status !== "LIVE"
    ) {

      setTimeLeft(0);

      return;
    }


    function updateTimer() {

      const end =
        new Date(
          auction.ends_at
        ).getTime();

      const now =
        Date.now();

      const remaining =
        Math.max(
          0,
          Math.ceil(
            (end - now) / 1000
          )
        );

      setTimeLeft(
        remaining
      );
    }


    updateTimer();

    const interval =
      setInterval(
        updateTimer,
        250
      );

    return () =>
      clearInterval(interval);

  }, [
    auction?.ends_at,
    auction?.status
  ]);


  async function placeBid() {

    if (
      !auction ||
      auction.status !== "LIVE" ||
      !team
    ) {
      return;
    }


    const increment =
      10000;


    const nextBid =
      Number(
        auction.current_bid
      ) + increment;


    if (
      nextBid >
      Number(
        team.purse_remaining
      )
    ) {

      setMessage(
        "Insufficient purse"
      );

      return;
    }


    try {

      setBidding(true);

      setMessage("");

      await apiRequest(
        `/api/bids/${auction.id}`,
        {
          method: "POST",

          body: JSON.stringify({
            amount: nextBid
          })
        }
      );

      setMessage(
        `Bid placed: ₹${nextBid.toLocaleString("en-IN")}`
      );

      await loadData();

    } catch (error) {

      setMessage(
        error.message
      );

      await loadData();

    } finally {

      setBidding(false);

    }
  }


  if (loading) {

    return (
      <div className="dashboard">
        Loading franchise dashboard...
      </div>
    );
  }


  return (
    <div className="dashboard">

      <header className="dashboard-header">

        <div>

          <h1>
            {team?.name ||
              "Franchise"}
          </h1>

          <p>
            Welcome, {user.full_name}
          </p>

        </div>


        <button
          onClick={onLogout}
          className="logout-button"
        >
          Logout
        </button>

      </header>


      {team && (

        <div className="purse-card">

          <span>
            Remaining Purse
          </span>

          <strong>
            ₹{Number(
              team.purse_remaining
            ).toLocaleString(
              "en-IN"
            )}
          </strong>

        </div>

      )}


      {message && (

        <div className="dashboard-message">
          {message}
        </div>

      )}


      {auction ? (

        <section className="franchise-auction">

          <div className="auction-status">
            {auction.status}
          </div>


          <h2>
            LIVE PLAYER
          </h2>


          <div className="franchise-player">

            <h1>
              Player ID:
              <br />
              {auction.player_id}
            </h1>


            <div className="franchise-bid">

              <span>
                Current Bid
              </span>

              <strong>
                ₹{Number(
                  auction.current_bid
                ).toLocaleString(
                  "en-IN"
                )}
              </strong>

            </div>


            <div className="timer">

              {auction.status === "LIVE"
                ? `${timeLeft}s`
                : "--"}

            </div>


            <p>
              Highest Bidder
            </p>

            <strong>
              {auction.highest_team_id ||
                "No bids yet"}
            </strong>


            <button
              className="bid-button"
              onClick={placeBid}
              disabled={
                bidding ||
                auction.status !==
                  "LIVE" ||
                timeLeft <= 0
              }
            >

              {bidding
                ? "BIDDING..."
                : `BID ₹${(
                    Number(
                      auction.current_bid
                    ) + 10000
                  ).toLocaleString(
                    "en-IN"
                  )}`}

            </button>

          </div>

        </section>

      ) : (

        <section className="waiting-screen">

          <h2>
            Waiting for next player
          </h2>

          <p>
            The auctioneer has not started
            the next auction yet.
          </p>

        </section>

      )}

    </div>
  );
}


export default FranchiseDashboard;
