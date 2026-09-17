import { useEffect, useState } from "react";
import { createClient } from "@supabase/supabase-js";
const SUPABASE_URL =
  import.meta.env.VITE_SUPABASE_URL;

const SUPABASE_ANON_KEY =
  import.meta.env.VITE_SUPABASE_ANON_KEY;

const supabase =
  createClient(
    SUPABASE_URL,
    SUPABASE_ANON_KEY
  );

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


function ProjectorDisplay() {

  const [auction, setAuction] =
    useState(null);

  const [timeLeft, setTimeLeft] =
    useState(0);

  const [loading, setLoading] =
    useState(true);


  const token =
    localStorage.getItem(
      "spl_access_token"
    );


  async function loadAuction() {

    try {

      const response =
        await fetch(
          `${API_URL}/api/auction/current`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`
            }
          }
        );

      if (!response.ok) {
        throw new Error(
          "Failed to load auction"
        );
      }

      const data =
        await response.json();

      setAuction(
        data.auction || null
      );

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  }


 useEffect(() => {

  loadAuction();


  const channel =
    supabase
      .channel("spl-projector-live")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "auctions"
        },
        () => {
          loadAuction();
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
          loadAuction();
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

    const timer =
      setInterval(
        updateTimer,
        250
      );

    return () =>
      clearInterval(timer);

  }, [
    auction?.ends_at,
    auction?.status
  ]);


  if (loading) {

    return (
      <div className="projector-screen">
        <h1>
          SPHOORTHY PREMIER LEAGUE
        </h1>

        <p>
          Loading auction...
        </p>
      </div>
    );

  }


  if (!auction) {

    return (
      <div className="projector-screen">

        <div className="projector-brand">
          SPHOORTHY
        </div>

        <h1>
          PREMIER LEAGUE
        </h1>

        <div className="projector-waiting">

          <h2>
            AUCTION WILL BEGIN SOON
          </h2>

          <p>
            Please wait for the auctioneer
            to start the next player.
          </p>

        </div>

      </div>
    );

  }


  return (
    <div className="projector-screen">

      <header className="projector-header">

        <div className="projector-brand">
          SPHOORTHY
        </div>

        <div className="projector-title">
          PREMIER LEAGUE
        </div>

        <div className="projector-live">
          {auction.status === "LIVE"
            ? "🔴 LIVE"
            : auction.status}

        </div>

      </header>


      <main className="projector-main">

        <section className="projector-player">

          <div className="projector-photo">

            {auction.player_photo_url ? (

              <img
                src={
                  auction.player_photo_url
                }
                alt="Player"
              />

            ) : (

              <div className="no-photo">
                PLAYER
              </div>

            )}

          </div>


          <div className="projector-player-info">

            <h1>
              {auction.player_name ||
                "Player"}
            </h1>

            <p>
              {auction.role ||
                "Cricket Player"}
            </p>

            <p>
              {auction.department ||
                ""}
            </p>


            <div className="base-price">

              Base Price

              <strong>
                ₹{Number(
                  auction.base_price ||
                    0
                ).toLocaleString(
                  "en-IN"
                )}
              </strong>

            </div>

          </div>

        </section>


        <section className="projector-bidding">

          <div className="current-bid-label">
            CURRENT BID
          </div>

          <div className="projector-current-bid">

            ₹{Number(
              auction.current_bid
            ).toLocaleString(
              "en-IN"
            )}

          </div>


          <div className="highest-bidder">

            <span>
              HIGHEST BIDDER
            </span>

            <strong>
              {auction.highest_team_name ||
                "NO BIDS"}
            </strong>

          </div>


          <div className="projector-timer">

            {auction.status === "LIVE"
              ? timeLeft
              : "--"}

            {auction.status === "LIVE" && (
              <small>
                SEC
              </small>
            )}

          </div>

        </section>

      </main>


      <footer className="projector-footer">

        <span>
          SPHOORTHY ENGINEERING COLLEGE
        </span>

        <span>
          LIVE PLAYER AUCTION
        </span>

      </footer>

    </div>
  );
}


export default ProjectorDisplay;
