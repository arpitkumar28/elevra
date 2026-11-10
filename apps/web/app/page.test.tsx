import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { notFoundMock } = vi.hoisted(() => ({
  notFoundMock: vi.fn(() => {
    throw new Error("notFound called");
  }),
}));

vi.mock("next/navigation", () => ({
  notFound: notFoundMock,
}));

import Page from "./[[...slug]]/page";

describe("Elevra web app", () => {
  it("renders the home experience", async () => {
    render(await Page({ params: Promise.resolve({ slug: [] }) }));
    expect(screen.getByRole("heading", { name: /your career.*exam companion/i })).toBeDefined();
  });

  it("delegates unsupported paths to Next.js not-found handling", async () => {
    await expect(Page({ params: Promise.resolve({ slug: ["not-a-route"] }) })).rejects.toThrow(
      "notFound called",
    );
    expect(notFoundMock).toHaveBeenCalledOnce();
  });
});
