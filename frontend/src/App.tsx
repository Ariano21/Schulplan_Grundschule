import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import LoginPage from "./pages/LoginPage";
import GrunddatenPage from "./pages/GrunddatenPage";
import StundenplanPage from "./pages/StundenplanPage";

function RequireAuth({ children }: { children: JSX.Element }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      {user && (
        <header className="app-header">
          <div className="brand">Schulplan</div>
          <nav>
            <NavLink to="/grunddaten" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
              Grunddaten
            </NavLink>
            <NavLink to="/stundenplan" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
              Stundenplan
            </NavLink>
          </nav>
          <div style={{ display: "flex", alignItems: "center", gap: "0.8rem" }}>
            <span className="role-badge">{user.rolle}</span>
            <button className="btn" onClick={logout}>
              Abmelden
            </button>
          </div>
        </header>
      )}
      <main className="app-main">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/grunddaten"
            element={
              <RequireAuth>
                <GrunddatenPage />
              </RequireAuth>
            }
          />
          <Route
            path="/stundenplan"
            element={
              <RequireAuth>
                <StundenplanPage />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to={user ? "/grunddaten" : "/login"} replace />} />
        </Routes>
      </main>
    </div>
  );
}
