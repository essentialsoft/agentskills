import { useMemo, useState } from "react";
import { SearchFilterBar } from "../components/SearchFilterBar";
import { SkillCard } from "../components/SkillCard";
import { StatusState } from "../components/StatusState";
import { useSkills } from "../hooks/useSkills";
import { filterSkills, getAvailableTags } from "../lib/filterSkills";

export function CatalogPage() {
  const { status, skills, error, reload } = useSkills();
  const [query, setQuery] = useState("");
  const [tag, setTag] = useState("all");

  const tags = useMemo(() => getAvailableTags(skills), [skills]);
  const filtered = useMemo(
    () => filterSkills(skills, { query, tag }),
    [query, skills, tag],
  );

  if (status === "loading") {
    return (
      <StatusState title="Loading skills" message="Fetching skills from GitHub..." />
    );
  }

  if (status === "error") {
    const title = error?.kind === "rate-limit" ? "GitHub rate limit hit" : "Could not load skills";
    return (
      <StatusState
        title={title}
        message={error?.message ?? "Unexpected error while loading skills."}
        actionLabel="Retry"
        onAction={() => {
          void reload();
        }}
      />
    );
  }

  if (skills.length === 0) {
    return (
      <StatusState
        title="No skills found"
        message="No skills were returned from the repository."
        actionLabel="Retry"
        onAction={() => {
          void reload();
        }}
      />
    );
  }

  return (
    <>
      <SearchFilterBar
        query={query}
        tag={tag}
        tags={tags}
        onQueryChange={setQuery}
        onTagChange={setTag}
      />

      {filtered.length === 0 ? (
        <StatusState
          title="No matching skills"
          message="Try a different search value or reset your tag filter."
          actionLabel="Reset filters"
          onAction={() => {
            setQuery("");
            setTag("all");
          }}
        />
      ) : (
        <section className="skills-grid">
          {filtered.map((skill) => (
            <SkillCard key={skill.slug} skill={skill} />
          ))}
        </section>
      )}
    </>
  );
}
