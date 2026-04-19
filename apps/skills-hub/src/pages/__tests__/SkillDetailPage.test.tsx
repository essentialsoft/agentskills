import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { SkillDetailPage } from "../SkillDetailPage";

const findOrFetchSkill = vi.fn();

vi.mock("../../hooks/useSkills", () => ({
  useSkills: () => ({
    status: "success",
    error: null,
    skills: [],
    reload: vi.fn(),
    findOrFetchSkill,
  }),
}));

describe("SkillDetailPage", () => {
  it("loads deep-linked skill when not already cached", async () => {
    findOrFetchSkill.mockResolvedValue({
      name: "email-generator",
      description: "Generate interview emails",
      argumentHint: "type",
      purpose: "Generate emails",
      slug: "email-generator",
      tags: ["communication"],
      sourcePath: "skills/email-generator/SKILL.md",
    });

    render(
      <MemoryRouter initialEntries={["/skills/email-generator"]}>
        <Routes>
          <Route path="/skills/:name" element={<SkillDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "email-generator" })).toBeInTheDocument();
    });

    expect(screen.getByText(/npx skills add essentialsoft\/agentskills@email-generator/i)).toBeInTheDocument();
  });
});
