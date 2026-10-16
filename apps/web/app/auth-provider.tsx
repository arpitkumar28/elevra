"use client";

import { ApiError, createApiClient, type AuthUser, type ProfileUpdate } from "@elevra/api-client";
import {
  default as React,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

const apiClient = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
});

type AuthStatus = "loading" | "authenticated" | "unauthenticated" | "error";
type Session = { accessToken: string; expiresAt: number; user: AuthUser };
type AuthContextValue = {
  status: AuthStatus;
  user: AuthUser | null;
  error: string;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  retryRestore: () => Promise<void>;
  withSession: <T>(request: (accessToken: string) => Promise<T>) => Promise<T>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<AuthUser | null>(null);
  const [error, setError] = useState("");
  const sessionRef = useRef<Session | null>(null);
  const restorePromiseRef = useRef<Promise<Session> | null>(null);

  const acceptTokens = useCallback(async (tokens: { access_token: string; expires_in: number }) => {
    const account = await apiClient.getMe(tokens.access_token);
    const session = {
      accessToken: tokens.access_token,
      expiresAt: Date.now() + tokens.expires_in * 1000,
      user: account,
    };
    sessionRef.current = session;
    setUser(account);
    setStatus("authenticated");
    setError("");
    return session;
  }, []);

  const retryRestore = useCallback(() => {
    if (restorePromiseRef.current) return restorePromiseRef.current;
    const restoring = (async () => {
      try {
        const tokens = await apiClient.refreshSession();
        return await acceptTokens(tokens);
      } catch (cause) {
        const failure =
          cause instanceof ApiError
            ? cause
            : new ApiError("Unable to restore your session. Check your connection and try again.");
        if (failure.status === 401 || !sessionRef.current) {
          sessionRef.current = null;
          setUser(null);
          setStatus(failure.status === 401 ? "unauthenticated" : "error");
        }
        setError(failure.message);
        throw failure;
      } finally {
        restorePromiseRef.current = null;
      }
    })();
    restorePromiseRef.current = restoring;
    return restoring;
  }, [acceptTokens]);

  useEffect(() => {
    void retryRestore().catch(() => undefined);
  }, [retryRestore]);

  useEffect(() => {
    if (status !== "authenticated" || !sessionRef.current) return;
    const delay = Math.max(sessionRef.current.expiresAt - Date.now() - 60_000, 1_000);
    const timer = window.setTimeout(() => {
      void retryRestore().catch(() => undefined);
    }, delay);
    return () => window.clearTimeout(timer);
  }, [status, user, retryRestore]);

  const signIn = useCallback(
    async (email: string, password: string) => {
      setError("");
      const tokens = await apiClient.login(email, password);
      await acceptTokens(tokens);
    },
    [acceptTokens],
  );

  const signUp = useCallback(
    async (name: string, email: string, password: string) => {
      setError("");
      const tokens = await apiClient.register(name, email, password);
      await acceptTokens(tokens);
    },
    [acceptTokens],
  );

  const withSession = useCallback(
    async <T,>(request: (accessToken: string) => Promise<T>) => {
      const current = sessionRef.current;
      if (!current) throw new ApiError("Sign in to continue.", 401);
      try {
        return await request(current.accessToken);
      } catch (cause) {
        if (!(cause instanceof ApiError) || cause.status !== 401) throw cause;
        const renewed = await retryRestore();
        return request(renewed.accessToken);
      }
    },
    [retryRestore],
  );

  const signOut = useCallback(async () => {
    if (!sessionRef.current) {
      setStatus("unauthenticated");
      setUser(null);
      return;
    }
    await withSession((token) => apiClient.logout(token));
    sessionRef.current = null;
    setUser(null);
    setStatus("unauthenticated");
    setError("");
  }, [withSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user,
      error,
      signIn,
      signUp,
      signOut,
      retryRestore: async () => void (await retryRestore()),
      withSession,
    }),
    [status, user, error, signIn, signUp, signOut, retryRestore, withSession],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}

export { apiClient as authenticatedApi };
export type { ProfileUpdate };
