export type ParsedSkill = {
  name: string;
  description: string;
  argumentHint: string;
  purpose: string;
};

export type Skill = ParsedSkill & {
  slug: string;
  tags: string[];
  sourcePath: string;
};

export type SkillsLoadStatus = "loading" | "success" | "error";

export type SkillsError = {
  kind: "rate-limit" | "network" | "unknown";
  message: string;
};
