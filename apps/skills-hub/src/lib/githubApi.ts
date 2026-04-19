import { parseSkillMarkdown } from "./parseSkillMarkdown";
import { toSkill } from "./skillTransforms";
import type { Skill } from "../types/skill";

const API_BASE = "https://api.github.com";
const REPO_OWNER = import.meta.env.VITE_SKILLS_REPO_OWNER || "essentialsoft";
const REPO_NAME = import.meta.env.VITE_SKILLS_REPO_NAME || "agentskills";
const REPO_REF = import.meta.env.VITE_SKILLS_REPO_REF || "main";
const SKILLS_ROOT = import.meta.env.VITE_SKILLS_ROOT_PATH || "skills";

type GithubDirectoryEntry = {
  name: string;
  path: string;
  type: "file" | "dir";
};

type GithubFileResponse = {
  content?: string;
  encoding?: string;
};

export class GithubRateLimitError extends Error {}

export function isGithubRateLimitError(error: unknown): boolean {
  return error instanceof GithubRateLimitError;
}

async function fetchJson<T>(url: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(url, {
      headers: {
        Accept: "application/vnd.github+json",
      },
    });
  } catch {
    throw new Error("Network request to GitHub failed.");
  }

  if (!response.ok) {
    const remaining = response.headers.get("x-ratelimit-remaining");
    if (response.status === 403 && remaining === "0") {
      throw new GithubRateLimitError("GitHub API rate limit exceeded.");
    }
    throw new Error(`GitHub API request failed with status ${response.status}.`);
  }

  return (await response.json()) as T;
}

function decodeBase64(value: string): string {
  if (typeof atob === "function") {
    return atob(value);
  }
  throw new Error("Base64 decoding is not available in this environment.");
}

export async function fetchSkillDirectoryNames(): Promise<string[]> {
  const url = `${API_BASE}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${SKILLS_ROOT}?ref=${REPO_REF}`;
  const entries = await fetchJson<GithubDirectoryEntry[]>(url);

  return entries
    .filter((entry) => entry.type === "dir")
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b));
}

export async function fetchSkillByName(skillName: string): Promise<Skill | null> {
  const skillPath = `${SKILLS_ROOT}/${skillName}/SKILL.md`;
  const url = `${API_BASE}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${skillPath}?ref=${REPO_REF}`;

  try {
    const file = await fetchJson<GithubFileResponse>(url);
    if (!file.content || file.encoding !== "base64") {
      return null;
    }

    const markdown = decodeBase64(file.content.replace(/\n/g, ""));
    const parsed = parseSkillMarkdown(markdown);
    if (!parsed) {
      return null;
    }

    return toSkill(parsed, skillPath);
  } catch (error) {
    if (isGithubRateLimitError(error)) {
      throw error;
    }

    return null;
  }
}

export async function fetchAllSkills(): Promise<Skill[]> {
  const names = await fetchSkillDirectoryNames();
  const fetched = await Promise.all(names.map((name) => fetchSkillByName(name)));

  return fetched.filter((skill): skill is Skill => Boolean(skill));
}
