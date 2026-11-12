/**
 * Resolve the public FastAPI base URL for the student and admin web apps.
 *
 * A deployed browser must never fall back to localhost: that points to the
 * visitor's own machine, not the Elevra backend.
 */
export const PRODUCTION_API_BASE_URL = "https://elevra-api-jrxa.onrender.com/api/v1";
export const LOCAL_API_BASE_URL = "http://localhost:8000/api/v1";

export function resolveApiBaseUrl(
  configured = process.env.NEXT_PUBLIC_API_BASE_URL,
  environment = process.env.NODE_ENV,
): string {
  const override = configured?.trim();
  if (override) return override;
  return environment === "production" ? PRODUCTION_API_BASE_URL : LOCAL_API_BASE_URL;
}
