import { useState } from "react";

import { login } from "./api";


function Login({ onLogin }) {

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  async function handleSubmit(event) {

    event.preventDefault();

    setError("");
    setLoading(true);

    try {

      const data =
        await login(
          email,
          password
        );

      localStorage.setItem(
        "spl_access_token",
        data.access_token
      );

      localStorage.setItem(
        "spl_refresh_token",
        data.refresh_token
      );

      localStorage.setItem(
        "spl_user",
        JSON.stringify(data.user)
      );

      onLogin(data.user);

    } catch (error) {

      setError(
        error.message
      );

    } finally {

      setLoading(false);

    }
  }


  return (
    <div className="login-page">

      <div className="login-card">

        <h1>
          SPHOORTHY
        </h1>

        <h2>
          PREMIER LEAGUE
        </h2>

        <p>
          Live Cricket Auction
        </p>


        <form
          onSubmit={handleSubmit}
        >

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(event) =>
              setEmail(
                event.target.value
              )
            }
            required
          />


          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(event) =>
              setPassword(
                event.target.value
              )
            }
            required
          />


          {error && (
            <div className="login-error">
              {error}
            </div>
          )}


          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "LOGIN"}
          </button>

        </form>

      </div>

    </div>
  );
}


export default Login;
