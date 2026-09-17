import { useState } from "react";

import Login from "./Login";
import AdminDashboard from "./AdminDashboard";


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


  if (user.role === "admin") {

    return (
      <AdminDashboard
        user={user}
        onLogout={logout}
      />
    );
  }


  return (
    <div className="dashboard">

      <h1>
        Welcome to SPL
      </h1>

      <p>
        Franchise dashboard coming next.
      </p>

      <button
        onClick={logout}
      >
        Logout
      </button>

    </div>
  );
}


export default App;
