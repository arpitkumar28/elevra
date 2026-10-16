import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AdminNav } from "../../admin/app/admin-nav";

vi.mock("next/navigation", () => ({ usePathname: () => "/dashboard" }));

describe("admin cross-app navigation", () => {
  it("links back to the configured student website", () => {
    render(<AdminNav />);

    expect(screen.getByRole("link", { name: "Open Student Website" }).getAttribute("href")).toBe(
      "http://localhost:3000",
    );
  });
});
