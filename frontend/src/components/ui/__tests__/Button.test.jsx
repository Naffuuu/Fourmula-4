import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import Button from "../Button";

describe("Button", () => {
  it("renders children text", () => {
    render(<Button>Save changes</Button>);
    expect(screen.getByRole("button", { name: /save changes/i })).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click me</Button>);
    fireEvent.click(screen.getByRole("button", { name: /click me/i }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled and unclickable while loading", () => {
    const onClick = vi.fn();
    render(
      <Button loading onClick={onClick}>
        Submitting
      </Button>
    );
    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("respects the explicit disabled prop", () => {
    render(<Button disabled>Can't click</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
