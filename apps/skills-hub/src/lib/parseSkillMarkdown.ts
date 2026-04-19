import type { ParsedSkill } from "../types/skill";

function readFrontmatterValue(frontmatter: string, key: string): string {
  const pattern = new RegExp(`^${key}:\\s*(.+)$`, "m");
  const match = frontmatter.match(pattern);
  if (!match) {
    return "";
  }

  return match[1].trim().replace(/^['\"]|['\"]$/g, "");
}

export function parseSkillMarkdown(markdown: string): ParsedSkill | null {
  const fmMatch = markdown.match(/^---\n([\s\S]*?)\n---/);
  if (!fmMatch) {
    return null;
  }

  const frontmatter = fmMatch[1];
  const name = readFrontmatterValue(frontmatter, "name");
  if (!name) {
    return null;
  }

  const description =
    readFrontmatterValue(frontmatter, "description") ||
    "No description provided.";
  const argumentHint = readFrontmatterValue(frontmatter, "argument-hint") || "";

  const purposeMatch = markdown.match(/# Purpose\s*\n\n([\s\S]*?)(\n# |$)/);
  const purpose = purposeMatch
    ? purposeMatch[1].trim()
    : "Purpose section not available.";

  return {
    name,
    description,
    argumentHint,
    purpose,
  };
}
