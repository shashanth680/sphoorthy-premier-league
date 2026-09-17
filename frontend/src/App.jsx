import { useState } from "react";

import Login from "./Login";


function App() {

  const [user, setUser] =
    useState(() => {

      const savedUser =
        localStorage.getItem(
          "spl_user"
        );

      return savedUser
        ? JSON.parse(savedUser)
        : null;
    });


  function logout() {

    localStorage.removeItem(
      "spl_access_token"
    );

    localStorage.removeItem(
      "spl_refresh_token"
    );

    localStorage.removeItem(
      "spl_user"
    );

    setUser(null);
  }


  if (!user) {

    return (
      <Login
        onLogin={setUser}
      />
    );
  }


  return (
    <div style={{
      padding: "40px"
    }}>

      <h1>
        Sphoorthy Premier League
      </h1>

      <h2>
        Welcome, {user.full_name}
      </h2>

      <p>
        Role: {user.role}
      </p>

      {user.team_id && (
        <p>
          Team ID: {user.team_id}
        </p>
      )}

      <button
        onClick={logout}
      >
        Logout
      </button>

    </div>
  );
}


export default App;
