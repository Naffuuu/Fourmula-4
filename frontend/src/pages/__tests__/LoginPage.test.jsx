import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "../LoginPage";

const loginMock = vi.fn();

vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({ login: loginMock }),
}));

vi.mock("../../features/auth/GoogleOAuthButton", () => ({
  default: () => <div data-testid="google-oauth-stub" />,
}));

vi.mock("../../features/auth/FacebookOAuthButton", () => ({
  default: () => <div data-testid="facebook-oauth-stub" />,
}));

function renderLoginPage() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <LoginPage />
    </MemoryRouter>
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    loginMock.mockReset();
  });

  it("renders email and password fields plus both OAuth options", () => {
    renderLoginPage();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByTestId("google-oauth-stub")).toBeInTheDocument();
    expect(screen.getByTestId("facebook-oauth-stub")).toBeInTheDocument();
  });

  it("submits email/password to the login action", async () => {
    loginMock.mockResolvedValueOnce({ id: "1", name: "Test" });
    renderLoginPage();

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: "student@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "correcthorse123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        email: "student@example.com",
        password: "correcthorse123",
      });
    });
  });

  it("shows an inline error on incorrect credentials instead of a silent failure", async () => {
    loginMock.mockRejectedValueOnce({ response: { status: 401 } });
    renderLoginPage();

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: "student@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "wrongpassword" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(await screen.findByText(/incorrect email or password/i)).toBeInTheDocument();
  });
});
