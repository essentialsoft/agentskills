import { describe, expect, it } from "vitest";
import { filterSkills, getAvailableTags } from "../filterSkills";
import type { Skill } from "../../types/skill";

const skills: Skill[] = [
  {
    name: "email-generator",
    description: "Generate interview emails",
    argumentHint: "type, recipient",
    purpose: "Generate emails",
    slug: "email-generator",
    tags: ["communication", "writing"],
    sourcePath: "skills/email-generator/SKILL.md",
  },
  {
    name: "code-reviewer",
    description: "Review code for regressions",
    argumentHint: "diff",
    purpose: "Review changes",
    slug: "code-reviewer",
    tags: ["engineering", "quality"],
    sourcePath: "skills/code-reviewer/SKILL.md",
  },
];

describe("filterSkills", () => {
  it("filters by text query", () => {
    const result = filterSkills(skills, { query: "interview", tag: "all" });
    expect(result).toHaveLength(1);
    expect(result[0].slug).toBe("email-generator");
  });

  it("filters by tag", () => {
    const result = filterSkills(skills, { query: "", tag: "quality" });
    expect(result).toHaveLength(1);
    expect(result[0].slug).toBe("code-reviewer");
  });

  it("returns all when no filters are provided", () => {
    const result = filterSkills(skills, { query: "", tag: "all" });
    expect(result).toHaveLength(2);
  });
});

describe("getAvailableTags", () => {
  it("returns sorted unique tags", () => {
    expect(getAvailableTags(skills)).toEqual([
      "communication",
      "engineering",
      "quality",
      "writing",
    ]);
  });
});
