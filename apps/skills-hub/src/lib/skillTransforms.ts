import type { ParsedSkill, Skill } from "../types/skill";

export function toSkill(parsed: ParsedSkill, sourcePath: string): Skill {
  return {
    ...parsed,
    slug: parsed.name,
    tags: parsed.name.split("-").filter(Boolean),
    sourcePath,
  };
}
