import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { CatalogPage } from "../CatalogPage";

vi.mock("../../hooks/useSkills", () => ({
  useSkills: () => ({
    status: "success",
    error: null,
    skills: [
      {
        name: "email-generator",
        description: "Generate interview emails",
        argumentHint: "type",
        purpose: "Generate emails",
        slug: "email-generator",
        tags: ["communication"],
        sourcePath: "skills/email-generator/SKILL.md",
      },
      {
        name: "code-reviewer",
        description: "Review pull requests",
        argumentHint: "diff",
        purpose: "Review code",
        slug: "code-reviewer",
        tags: ["quality"],
        sourcePath: "skills/code-reviewer/SKILL.md",
      },
    ],
    reload: vi.fn(),
    findOrFetchSkill: vi.fn(),
  }),
}));

describe("CatalogPage", () => {
  it("renders catalog and filters by query", () => {
    render(
      <MemoryRouter>
        <CatalogPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("email-generator")).toBeInTheDocument();
    expect(screen.getByText("code-reviewer")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Search skills"), {
      target: { value: "email" },
    });

    expect(screen.getByText("email-generator")).toBeInTheDocument();
    expect(screen.queryByText("code-reviewer")).toBeNull();
  });
});
