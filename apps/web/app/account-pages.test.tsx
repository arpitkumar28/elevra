import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PracticeTestPage } from "./account-pages";

const mocks = vi.hoisted(() => ({
  useAuth: vi.fn(),
  getTest: vi.fn(),
  listTestAttempts: vi.fn(),
  getTestAttempt: vi.fn(),
  startTest: vi.fn(),
  saveTestAnswer: vi.fn(),
  submitTest: vi.fn(),
}));

vi.mock("./auth-provider", () => ({
  useAuth: mocks.useAuth,
  authenticatedApi: {
    getTest: mocks.getTest,
    listTestAttempts: mocks.listTestAttempts,
    getTestAttempt: mocks.getTestAttempt,
    startTest: mocks.startTest,
    saveTestAnswer: mocks.saveTestAnswer,
    submitTest: mocks.submitTest,
  },
}));

const test = {
  id: "test-1",
  slug: "test-1",
  title: "Practice Test",
  type: "practice",
  duration_minutes: 20,
  questions: [
    {
      id: "question-1",
      text: "Choose the correct answer.",
      position: 0,
      options: [
        { id: "option-a", text: "Option A", position: 0 },
        { id: "option-b", text: "Option B", position: 1 },
      ],
    },
  ],
};

describe("practice test workflow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.useAuth.mockReturnValue({
      withSession: (request: (token: string) => unknown) => request("access"),
    });
    mocks.getTest.mockResolvedValue(test);
    mocks.listTestAttempts.mockResolvedValue([]);
    mocks.getTestAttempt.mockResolvedValue({ id: "attempt-1", test_id: "test-1", answers: [] });
    mocks.startTest.mockResolvedValue({ attempt_id: "attempt-1", started_at: "now", test });
    mocks.saveTestAnswer.mockResolvedValue({ status: "saved" });
    mocks.submitTest.mockResolvedValue({
      attempt_id: "attempt-1",
      score: 1,
      total_questions: 1,
      submitted_at: "now",
    });
  });

  it("starts an attempt, saves an answer, and reports the API score", async () => {
    render(<PracticeTestPage testId="test-1" />);
    fireEvent.click(await screen.findByRole("button", { name: "Start or continue test" }));
    fireEvent.click(await screen.findByLabelText("Option A"));
    await waitFor(() =>
      expect(mocks.saveTestAnswer).toHaveBeenCalledWith(
        "attempt-1",
        "question-1",
        "option-a",
        "access",
      ),
    );
    fireEvent.click(screen.getByRole("button", { name: "Submit attempt" }));
    expect(await screen.findByText("Score: 1 of 1")).toBeDefined();
  });

  it("restores a saved answer for an active attempt", async () => {
    mocks.listTestAttempts.mockResolvedValue([
      { id: "attempt-1", test_id: "test-1", started_at: "now" },
    ]);
    mocks.getTestAttempt.mockResolvedValue({
      id: "attempt-1",
      test_id: "test-1",
      answers: [{ question_id: "question-1", option_id: "option-b" }],
    });
    render(<PracticeTestPage testId="test-1" />);
    expect(((await screen.findByLabelText("Option B")) as HTMLInputElement).checked).toBe(true);
    expect(screen.getByRole("button", { name: "Submit attempt" })).toBeDefined();
  });
});
