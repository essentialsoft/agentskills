import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchAllSkills,
  fetchSkillByName,
  isGithubRateLimitError,
} from "../lib/githubApi";
import type { Skill, SkillsError, SkillsLoadStatus } from "../types/skill";

type UseSkillsResult = {
  status: SkillsLoadStatus;
  skills: Skill[];
  error: SkillsError | null;
  reload: () => Promise<void>;
  findOrFetchSkill: (name: string) => Promise<Skill | null>;
};

let skillsCache: Skill[] | null = null;
let loadingPromise: Promise<Skill[]> | null = null;

export function __resetSkillsCacheForTests() {
  skillsCache = null;
  loadingPromise = null;
}

function toError(error: unknown): SkillsError {
  if (isGithubRateLimitError(error)) {
    return {
      kind: "rate-limit",
      message: "GitHub API rate limit reached. Please retry later.",
    };
  }

  if (error instanceof Error && error.message.toLowerCase().includes("network")) {
    return {
      kind: "network",
      message: "Unable to reach GitHub. Check your network and retry.",
    };
  }

  return {
    kind: "unknown",
    message: "Could not load skills right now.",
  };
}

async function loadSkills(force = false): Promise<Skill[]> {
  if (!force && skillsCache) {
    return skillsCache;
  }

  if (!force && loadingPromise) {
    return loadingPromise;
  }

  loadingPromise = fetchAllSkills().then((skills) => {
    skillsCache = skills;
    loadingPromise = null;
    return skills;
  });

  return loadingPromise;
}

export function useSkills(): UseSkillsResult {
  const [status, setStatus] = useState<SkillsLoadStatus>("loading");
  const [skills, setSkills] = useState<Skill[]>(skillsCache ?? []);
  const [error, setError] = useState<SkillsError | null>(null);

  const reload = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const loaded = await loadSkills(true);
      setSkills(loaded);
      setStatus("success");
    } catch (loadError) {
      setError(toError(loadError));
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    let active = true;

    loadSkills()
      .then((loaded) => {
        if (!active) {
          return;
        }
        setSkills(loaded);
        setStatus("success");
      })
      .catch((loadError: unknown) => {
        if (!active) {
          return;
        }
        setError(toError(loadError));
        setStatus("error");
      });

    return () => {
      active = false;
    };
  }, []);

  const findOrFetchSkill = useCallback(
    async (name: string): Promise<Skill | null> => {
      const normalized = name.trim();
      if (!normalized) {
        return null;
      }

      const cached = (skillsCache ?? skills).find((skill) => skill.slug === normalized);
      if (cached) {
        return cached;
      }

      const fetched = await fetchSkillByName(normalized);
      if (!fetched) {
        return null;
      }

      skillsCache = [...(skillsCache ?? skills), fetched];
      setSkills(skillsCache);
      return fetched;
    },
    [skills],
  );

  return useMemo(
    () => ({
      status,
      skills,
      error,
      reload,
      findOrFetchSkill,
    }),
    [error, findOrFetchSkill, reload, skills, status],
  );
}
