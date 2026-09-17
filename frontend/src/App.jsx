import { useState } from "react";

import Login from "./Login";
import AdminDashboard from "./AdminDashboard";
import FranchiseDashboard from "./FranchiseDashboard";


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


 if (user.role === "franchise") {

  return (
    <FranchiseDashboard
      user={user}
      onLogout={logout}
    />
  );
}
}


export default App;
