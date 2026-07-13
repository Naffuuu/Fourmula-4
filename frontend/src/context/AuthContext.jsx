import { createContext, useCallback, useEffect, useState } from "react";
import api, { setAccessToken, setUnauthorizedHandler } from "../lib/apiClient";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // "loading" = we haven't yet determined auth state (e.g. on hard refresh
  // we try /auth/refresh once using the httpOnly cookie before deciding).
  const [status, setStatus] = useState("loading");

  const clearSession = useCallback(() => {
    setAccessToken(null);
    setUser(null);
    setStatus("unauthenticated");
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(clearSession);
  }, [clearSession]);

  // On first mount, attempt a silent refresh so a hard page reload doesn't
  // boot an already-logged-in user back to /login.
  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.post("/auth/refresh");
        setAccessToken(data.access_token);
        const me = await api.get("/auth/me");
        setUser(me.data);
        setStatus("authenticated");
      } catch {
        clearSession();
      }
    })();
  }, [clearSession]);

  const login = useCallback(async ({ email, password }) => {
    const { data } = await api.post("/auth/login", { email, password });
    setAccessToken(data.access_token);
    setUser(data.user);
    setStatus("authenticated");
    return data.user;
  }, []);

  const loginWithOAuth = useCallback(async (provider, credential) => {
    const { data } = await api.post(`/oauth/${provider}`, { credential });
    setAccessToken(data.access_token);
    setUser(data.user);
    setStatus("authenticated");
    return data.user;
  }, []);

  const signup = useCallback(async (payload) => {
    const { data } = await api.post("/auth/signup", payload);
    setAccessToken(data.access_token);
    setUser(data.user);
    setStatus("authenticated");
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } finally {
      clearSession();
    }
  }, [clearSession]);

  return (
    <AuthContext.Provider
      value={{ user, status, login, loginWithOAuth, signup, logout, setUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}
