const accountRoutes = new Set([
  "dashboard",
  "login",
  "register",
  "profile",
  "notifications",
  "saved",
]);

const detailRoutes = new Set([
  "exams",
  "opportunities",
  "explore",
  "jobs",
  "internships",
  "scholarships",
  "competitions",
  "courses",
  "current-affairs",
  "tests",
]);

export function isKnownWebRoute(parts: string[]): boolean {
  if (parts.length === 0) return true;
  const [section] = parts;

  if (section === "career") return parts.length === 1;
  if (detailRoutes.has(section)) return parts.length <= 2;
  if (accountRoutes.has(section)) return parts.length === 1;
  return false;
}
