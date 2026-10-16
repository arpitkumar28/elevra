import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AdminWorkspace } from "../../admin/app/content-manager";
import type { AdminContentPage } from "@elevra/api-client";

const apiMocks = vi.hoisted(() => ({
  listAdminContent: vi.fn(),
  listAdminQueue: vi.fn(),
  getAdminContent: vi.fn(),
  createAdminContent: vi.fn(),
  updateAdminContent: vi.fn(),
  adminContentAction: vi.fn(),
  deleteAdminContent: vi.fn(),
  addAdminTestQuestion: vi.fn(),
  updateAdminTestQuestion: vi.fn(),
  deleteAdminTestQuestion: vi.fn(),
  refreshSession: vi.fn(),
  getMe: vi.fn(),
  withSession: vi.fn(),
}));

vi.mock("@elevra/api-client", () => ({
  ApiError: class ApiError extends Error {
    constructor(message: string) { super(message); }
  },
  createApiClient: () => apiMocks,
}));

vi.mock("../../admin/app/admin-session", () => ({
  useAuth: () => ({ withSession: apiMocks.withSession }),
}));

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a href={href as string} {...props}>{children}</a>
  ),
}));

const emptyPage: AdminContentPage<Record<string, unknown>> = { items: [], page: 1, page_size: 12, total: 0, total_pages: 0 };

describe("admin content manager", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.listAdminContent.mockResolvedValue(emptyPage);
    apiMocks.withSession.mockImplementation((request: (token: string) => Promise<unknown>) => request("admin-session"));
    apiMocks.refreshSession.mockResolvedValue({ access_token: "admin-session", expires_in: 3600 });
    apiMocks.getMe.mockResolvedValue({ id: "admin", role: "admin", email: "admin@example.com", name: "Admin" });
  });

  function renderWorkspace(route: string) {
    return render(<AdminWorkspace route={route} />);
  }

  it("shows a loading state and then persisted content", async () => {
    let resolve!: (value: typeof emptyPage) => void;
    apiMocks.listAdminContent.mockReturnValueOnce(new Promise<typeof emptyPage>(done => { resolve = done; }));
    renderWorkspace("courses");
    expect(screen.getByRole("status").textContent).toContain("Loading courses");
    resolve({ ...emptyPage, items: [{ id: "course-1", title: "Policy course", slug: "policy-course", provider: "Elevra", status: "draft", updated_at: "2026-05-01T00:00:00Z" }], total: 1, total_pages: 1 });
    expect(await screen.findByText("Policy course")).toBeDefined();
  });

  it("shows API errors and retries the list request", async () => {
    apiMocks.listAdminContent.mockRejectedValueOnce(new Error("Admin API offline"));
    renderWorkspace("current-affairs");
    expect((await screen.findByRole("alert")).textContent).toContain("Admin API offline");
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() => expect(apiMocks.listAdminContent).toHaveBeenCalledTimes(2));
    expect(await screen.findByText("No current affairs match these filters.")).toBeDefined();
  });

  it("creates a validated draft and reports success", async () => {
    apiMocks.createAdminContent.mockResolvedValue({ id: "course-2", title: "Civics", slug: "civics", provider: "Elevra", skills: [], certificate: false, status: "draft" });
    renderWorkspace("courses");
    await screen.findByText("No courses match these filters.");
    fireEvent.click(screen.getByRole("button", { name: "Create course" }));
    fireEvent.change(screen.getByLabelText("Course title"), { target: { value: "Civics" } });
    fireEvent.change(screen.getByLabelText("URL slug"), { target: { value: "civics" } });
    fireEvent.change(screen.getByLabelText("Provider"), { target: { value: "Elevra" } });
    fireEvent.click(screen.getByRole("button", { name: "Create draft" }));
    await waitFor(() => expect(apiMocks.createAdminContent).toHaveBeenCalledWith(
      "courses",
      expect.objectContaining({ title: "Civics", slug: "civics", provider: "Elevra", skills: [] }),
      "admin-session",
    ));
    expect(await screen.findByText("Draft created.")).toBeDefined();
  });
});
