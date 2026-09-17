import { useEffect, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


function AdminDashboard({ user, onLogout }) {

  const [players, setPlayers] =
    useState([]);

  const [auction, setAuction] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [message, setMessage] =
    useState("");

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

      setLoading(true);

      const [
        playersData,
        auctionData
      ] = await Promise.all([

        apiRequest(
          "/api/players"
        ),

        apiRequest(
          "/api/auction/current"
        )

      ]);

      setPlayers(
        playersData.players || []
      );

      setAuction(
        auctionData.auction || null
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

  }, []);


  async function startAuction(
    playerId
  ) {

    try {

      setMessage("");

      const data =
        await apiRequest(
          "/api/auction/start",
          {
            method: "POST",

            body: JSON.stringify({
              player_id:
                playerId
            })
          }
        );

      setAuction(
        data.auction
      );

      setMessage(
        "Auction started successfully"
      );

      await loadData();

    } catch (error) {

      setMessage(
        error.message
      );
    }
  }


  async function pauseAuction() {

    if (!auction) return;

    try {

      const data =
        await apiRequest(
          `/api/auction/${auction.id}/pause`,
          {
            method: "POST"
          }
        );

      setMessage(
        "Auction paused"
      );

      setAuction(
        previous => ({
          ...previous,
          status: data.status
        })
      );

    } catch (error) {

      setMessage(
        error.message
      );
    }
  }


  async function resumeAuction() {

    if (!auction) return;

    try {

      const data =
        await apiRequest(
          `/api/auction/${auction.id}/resume`,
          {
            method: "POST"
          }
        );

      setMessage(
        "Auction resumed"
      );

      setAuction(
        previous => ({
          ...previous,
          status: data.status
        })
      );

    } catch (error) {

      setMessage(
        error.message
      );
    }
  }


  async function markSold() {

    if (!auction) return;

    try {

      const data =
        await apiRequest(
          `/api/auction/${auction.id}/sold`,
          {
            method: "POST"
          }
        );

      setMessage(
        `Player SOLD for ₹${data.final_price}`
      );

      setAuction(null);

      await loadData();

    } catch (error) {

      setMessage(
        error.message
      );
    }
  }


  async function markUnsold() {

    if (!auction) return;

    try {

      await apiRequest(
        `/api/auction/${auction.id}/unsold`,
        {
          method: "POST"
        }
      );

      setMessage(
        "Player marked UNSOLD"
      );

      setAuction(null);

      await loadData();

    } catch (error) {

      setMessage(
        error.message
      );
    }
  }


  if (loading) {

    return (
      <div className="dashboard">
        Loading auction dashboard...
      </div>
    );
  }


  return (
    <div className="dashboard">

      <header className="dashboard-header">

        <div>
          <h1>
            SPL Auction Control
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


      {message && (
        <div className="dashboard-message">
          {message}
        </div>
      )}


      {auction ? (

        <section className="live-auction">

          <h2>
            🔴 LIVE AUCTION
          </h2>

          <div className="auction-info">

            <h3>
              Player ID
            </h3>

            <p>
              {auction.player_id}
            </p>

            <h3>
              Current Bid
            </h3>

            <p className="current-bid">
              ₹{Number(
                auction.current_bid
              ).toLocaleString("en-IN")}
            </p>

            <h3>
              Highest Team
            </h3>

            <p>
              {auction.highest_team_id ||
                "No bids yet"}
            </p>

            <h3>
              Status
            </h3>

            <p>
              {auction.status}
            </p>

          </div>


          <div className="auction-actions">

            {auction.status === "LIVE" && (
              <button
                onClick={pauseAuction}
              >
                Pause
              </button>
            )}


            {auction.status === "PAUSED" && (
              <button
                onClick={resumeAuction}
              >
                Resume
              </button>
            )}


            <button
              onClick={markSold}
            >
              SOLD
            </button>


            <button
              onClick={markUnsold}
            >
              UNSOLD
            </button>

          </div>

        </section>

      ) : (

        <section className="player-section">

          <h2>
            Available Players
          </h2>

          {players.length === 0 ? (

            <p>
              No players available.
            </p>

          ) : (

            <div className="player-grid">

              {players
                .filter(
                  player =>
                    player.status ===
                    "AVAILABLE"
                )
                .map(player => (

                  <div
                    className="player-card"
                    key={player.id}
                  >

                    <h3>
                      {player.name}
                    </h3>

                    <p>
                      {player.department ||
                        "Department not available"}
                    </p>

                    <p>
                      {player.role ||
                        "Role not available"}
                    </p>

                    <p>
                      Base Price:{" "}
                      {player.base_price === null
                        ? "Not assigned"
                        : `₹${Number(
                            player.base_price
                          ).toLocaleString(
                            "en-IN"
                          )}`}
                    </p>


                    <button
                      disabled={
                        player.base_price ===
                        null
                      }
                      onClick={() =>
                        startAuction(
                          player.id
                        )
                      }
                    >
                      START AUCTION
                    </button>

                  </div>

                ))}

            </div>

          )}

        </section>

      )}

    </div>
  );
}


export default AdminDashboard;
