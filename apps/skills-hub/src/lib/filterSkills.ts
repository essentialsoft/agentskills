import type { Skill } from "../types/skill";

export type SkillFilters = {
  query: string;
  tag: string;
};

export function filterSkills(skills: Skill[], filters: SkillFilters): Skill[] {
  const normalizedQuery = filters.query.trim().toLowerCase();

  return skills.filter((skill) => {
    const tagMatches = filters.tag === "all" || skill.tags.includes(filters.tag);

    if (!normalizedQuery) {
      return tagMatches;
    }

    const haystack = `${skill.name} ${skill.description} ${skill.purpose}`.toLowerCase();
    return tagMatches && haystack.includes(normalizedQuery);
  });
}

export function getAvailableTags(skills: Skill[]): string[] {
  return Array.from(new Set(skills.flatMap((skill) => skill.tags))).sort((a, b) =>
    a.localeCompare(b),
  );
}
