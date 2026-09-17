import { useState } from "react";

import Login from "./Login";
import AdminDashboard from "./AdminDashboard";
import FranchiseDashboard from "./FranchiseDashboard";
import ProjectorDisplay from "./ProjectorDisplay";


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


  // Projector display
  // This opens the clean auction screen.
  if (
    window.location.pathname ===
    "/display"
  ) {

    return (
      <ProjectorDisplay />
    );
  }


  // Login
  if (!user) {

    return (
      <Login
        onLogin={setUser}
      />
    );
  }


  // Admin
  if (user.role === "admin") {

    return (
      <AdminDashboard
        user={user}
        onLogout={logout}
      />
    );
  }


  // Franchise
  if (user.role === "franchise") {

    return (
      <FranchiseDashboard
        user={user}
        onLogout={logout}
      />
    );
  }


  return null;
}


export default App;
