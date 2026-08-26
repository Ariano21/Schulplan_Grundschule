import { createContext, useContext, useState, type ReactNode } from "react";
import { api, clearToken, getToken, setToken } from "../api/client";
import type { Rolle } from "../api/types";

interface TokenResponse {
  access_token: string;
  token_type: string;
  rolle: Rolle;
  schule_id: number;
}

interface AuthState {
  rolle: Rolle;
  schuleId: number;
}

interface AuthContextValue {
  user: AuthState | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const USER_KEY = "schulplan_user";

function loadStoredUser(): AuthState | null {
  if (!getToken()) return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthState;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthState | null>(loadStoredUser);

  async function login(email: string, password: string) {
    const response = await api.post<TokenResponse>("/auth/login", { email, password });
    setToken(response.access_token);
    const state: AuthState = { rolle: response.rolle, schuleId: response.schule_id };
    localStorage.setItem(USER_KEY, JSON.stringify(state));
    setUser(state);
  }

  function logout() {
    clearToken();
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth muss innerhalb von AuthProvider verwendet werden.");
  return ctx;
}
