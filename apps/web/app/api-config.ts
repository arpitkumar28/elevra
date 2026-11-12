/**
 * Resolve the public FastAPI base URL for the student and admin web apps.
 *
 * A deployed browser must never fall back to localhost: that points to the
 * visitor's own machine, not the Elevra backend. Production overrides must be
 * valid HTTPS URLs and cannot point back to the browser's own computer.
 */
export const PRODUCTION_API_BASE_URL = "https://elevra-api-jrxa.onrender.com/api/v1";
export const LOCAL_API_BASE_URL = "http://localhost:8000/api/v1";

export function resolveApiBaseUrl(
  configured = process.env.NEXT_PUBLIC_API_BASE_URL,
  environment = process.env.NODE_ENV,
): string {
  const override = configured?.trim();

  if (environment === "production") {
    if (!override) return PRODUCTION_API_BASE_URL;

    try {
      const parsed = new URL(override);
      const localHosts = new Set(["localhost", "127.0.0.1", "0.0.0.0", "::1"]);
      if (parsed.protocol !== "https:" || localHosts.has(parsed.hostname)) {
        return PRODUCTION_API_BASE_URL;
      }
    } catch {
      return PRODUCTION_API_BASE_URL;
    }
  }

  return override || LOCAL_API_BASE_URL;
}
