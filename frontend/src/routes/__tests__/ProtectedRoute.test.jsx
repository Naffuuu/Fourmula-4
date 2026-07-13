import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "../ProtectedRoute";

let mockAuthState = {};
vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => mockAuthState,
}));

function renderWithRoute(path, allowedRoles) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/dashboard" element={<div>Dashboard fallback</div>} />
        <Route element={<ProtectedRoute allowedRoles={allowedRoles} />}>
          <Route path={path} element={<div>Protected content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  it("shows a loading state while auth status is unresolved", () => {
    mockAuthState = { user: null, status: "loading" };
    renderWithRoute("/missions/whistleblower");
    expect(screen.queryByText(/protected content/i)).not.toBeInTheDocument();
  });

  it("redirects unauthenticated users to /login", () => {
    mockAuthState = { user: null, status: "unauthenticated" };
    renderWithRoute("/missions/whistleblower");
    expect(screen.getByText(/login page/i)).toBeInTheDocument();
  });

  it("renders protected content for authenticated users", () => {
    mockAuthState = { user: { id: "1", role: "student" }, status: "authenticated" };
    renderWithRoute("/missions/whistleblower");
    expect(screen.getByText(/protected content/i)).toBeInTheDocument();
  });

  it("blocks a student from a captain-only route", () => {
    mockAuthState = { user: { id: "1", role: "student" }, status: "authenticated" };
    renderWithRoute("/missions/seating", ["second_captain", "third_captain"]);
    expect(screen.getByText(/dashboard fallback/i)).toBeInTheDocument();
  });

  it("allows a captain onto a captain-only route", () => {
    mockAuthState = { user: { id: "1", role: "second_captain" }, status: "authenticated" };
    renderWithRoute("/missions/seating", ["second_captain", "third_captain"]);
    expect(screen.getByText(/protected content/i)).toBeInTheDocument();
  });
});
