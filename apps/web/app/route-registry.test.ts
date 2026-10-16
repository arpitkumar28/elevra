import { describe, expect, it } from "vitest";
import { isKnownWebRoute } from "./[[...slug]]/route-registry";

describe("web route registry", () => {
  it("recognizes the home, account, content, and detail routes", () => {
    expect(isKnownWebRoute([])).toBe(true);
    expect(isKnownWebRoute(["profile"])).toBe(true);
    expect(isKnownWebRoute(["courses", "course-id"])).toBe(true);
    expect(isKnownWebRoute(["opportunities", "opportunity-slug"])).toBe(true);
  });

  it("rejects unsupported paths and extra detail segments", () => {
    expect(isKnownWebRoute(["unknown"])).toBe(false);
    expect(isKnownWebRoute(["profile", "extra"])).toBe(false);
    expect(isKnownWebRoute(["courses", "id", "extra"])).toBe(false);
  });
});
