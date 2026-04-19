import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { __resetSkillsCacheForTests, useSkills } from "../useSkills";

const mockedApi = vi.hoisted(() => ({
  fetchAllSkills: vi.fn(),
  fetchSkillByName: vi.fn(),
}));

vi.mock("../../lib/githubApi", () => ({
  fetchAllSkills: mockedApi.fetchAllSkills,
  fetchSkillByName: mockedApi.fetchSkillByName,
  isGithubRateLimitError: (error: unknown) =>
    error instanceof Error && error.message.includes("rate limit"),
}));

describe("useSkills", () => {
  beforeEach(() => {
    __resetSkillsCacheForTests();
    mockedApi.fetchAllSkills.mockReset();
    mockedApi.fetchSkillByName.mockReset();
  });

  it("loads skills successfully", async () => {
    mockedApi.fetchAllSkills.mockResolvedValue([
      {
        name: "email-generator",
        description: "Generate email templates",
        argumentHint: "Email type",
        purpose: "Generate professional emails.",
        slug: "email-generator",
        tags: ["email", "generator"],
        sourcePath: "skills/email-generator/SKILL.md",
      },
    ]);

    const { result } = renderHook(() => useSkills());
    expect(result.current.status).toBe("loading");

    await waitFor(() => expect(result.current.status).toBe("success"));
    expect(result.current.skills).toHaveLength(1);
  });

  it("maps rate-limit errors to user-friendly state", async () => {
    mockedApi.fetchAllSkills.mockRejectedValue(new Error("rate limit exceeded"));

    const { result } = renderHook(() => useSkills());

    await waitFor(() => expect(result.current.status).toBe("error"));
    expect(result.current.error?.kind).toBe("rate-limit");
  });

  it("fetches a skill on demand for deep-linked detail routes", async () => {
    mockedApi.fetchAllSkills.mockResolvedValue([]);
    mockedApi.fetchSkillByName.mockResolvedValue({
      name: "code-reviewer",
      description: "Review code",
      argumentHint: "diff",
      purpose: "Review code changes",
      slug: "code-reviewer",
      tags: ["review"],
      sourcePath: "skills/code-reviewer/SKILL.md",
    });

    const { result } = renderHook(() => useSkills());
    await waitFor(() => expect(result.current.status).toBe("success"));

    const skill = await result.current.findOrFetchSkill("code-reviewer");
    expect(skill?.slug).toBe("code-reviewer");
    expect(mockedApi.fetchSkillByName).toHaveBeenCalledWith("code-reviewer");
  });
});
