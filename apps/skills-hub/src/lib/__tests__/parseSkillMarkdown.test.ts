import { describe, expect, it } from "vitest";
import { parseSkillMarkdown } from "../parseSkillMarkdown";

const SAMPLE = `---
name: email-generator
description: "Generate email templates"
argument-hint: "Email type, recipient"
---

# Purpose

Generate professional interview emails.
`;

describe("parseSkillMarkdown", () => {
  it("extracts frontmatter and purpose", () => {
    const parsed = parseSkillMarkdown(SAMPLE);
    expect(parsed?.name).toBe("email-generator");
    expect(parsed?.description).toBe("Generate email templates");
    expect(parsed?.argumentHint).toBe("Email type, recipient");
    expect(parsed?.purpose).toContain("professional interview emails");
  });

  it("returns null for missing name", () => {
    const parsed = parseSkillMarkdown("---\ndescription: x\n---");
    expect(parsed).toBeNull();
  });

  it("is tolerant when purpose section is missing", () => {
    const parsed = parseSkillMarkdown("---\nname: x\ndescription: y\n---");
    expect(parsed?.purpose).toBe("Purpose section not available.");
  });
});
