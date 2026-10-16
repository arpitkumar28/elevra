import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Page from "./[[...slug]]/page";

describe("Elevra web app", () => {
  it("renders the home experience", () => {
    render(<Page params={{ slug: [] }} />);
    expect(screen.getByRole("heading", { name: /your career.*exam companion/i })).toBeDefined();
  });

  it("delegates unsupported paths to Next.js not-found handling", () => {
    expect(() => Page({ params: { slug: ["not-a-route"] } })).toThrow("NEXT_NOT_FOUND");
  });
});
