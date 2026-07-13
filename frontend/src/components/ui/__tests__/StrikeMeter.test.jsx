import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import StrikeMeter from "../StrikeMeter";

describe("StrikeMeter", () => {
  it("displays the current value and max", () => {
    render(<StrikeMeter value={2} max={3} />);
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("/3")).toBeInTheDocument();
  });

  it("shows the caption label", () => {
    render(<StrikeMeter value={1} max={3} caption="Warnings" />);
    expect(screen.getByText("Warnings")).toBeInTheDocument();
  });

  it("defaults to a max of 3 strikes", () => {
    render(<StrikeMeter value={0} />);
    expect(screen.getByText("/3")).toBeInTheDocument();
  });
});
