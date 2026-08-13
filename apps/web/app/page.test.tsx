import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Page from "./[[...slug]]/page";

describe("Elevra web app", () => {
  it("renders the home experience", () => {
    render(<Page params={{ slug: [] }} />);
    expect(screen.getByText("Your Career & Exam Companion")).toBeDefined();
  });
});
