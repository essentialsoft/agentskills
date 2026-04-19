import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { CopyCommand } from "../components/CopyCommand";
import { StatusState } from "../components/StatusState";
import { useSkills } from "../hooks/useSkills";
import { getInstallCommand } from "../lib/installCommand";
import type { Skill } from "../types/skill";

export function SkillDetailPage() {
  const { name } = useParams<{ name: string }>();
  const { skills, findOrFetchSkill, status, error } = useSkills();
  const [skill, setSkill] = useState<Skill | null>(null);
  const [isLoadingSkill, setIsLoadingSkill] = useState(true);

  const normalizedName = useMemo(() => (name ?? "").trim(), [name]);

  useEffect(() => {
    let active = true;

    if (!normalizedName) {
      setSkill(null);
      setIsLoadingSkill(false);
      return () => {
        active = false;
      };
    }

    const existing = skills.find((item) => item.slug === normalizedName);
    if (existing) {
      setSkill(existing);
      setIsLoadingSkill(false);
      return () => {
        active = false;
      };
    }

    setIsLoadingSkill(true);
    findOrFetchSkill(normalizedName)
      .then((fetched) => {
        if (!active) {
          return;
        }
        setSkill(fetched);
        setIsLoadingSkill(false);
      })
      .catch(() => {
        if (!active) {
          return;
        }
        setSkill(null);
        setIsLoadingSkill(false);
      });

    return () => {
      active = false;
    };
  }, [findOrFetchSkill, normalizedName, skills]);

  if (isLoadingSkill || status === "loading") {
    return <StatusState title="Loading skill" message="Fetching skill details..." />;
  }

  if (!skill) {
    const description =
      status === "error"
        ? error?.message ?? "Failed to load skill details."
        : "Skill not found in the selected repository.";

    return <StatusState title="Skill unavailable" message={description} />;
  }

  const installCommand = getInstallCommand(skill.slug);

  return (
    <article className="skill-detail">
      <Link to="/" className="back-link">
        Back to catalog
      </Link>
      <h2>{skill.name}</h2>
      <p>{skill.description}</p>

      <section>
        <h3>Purpose</h3>
        <p>{skill.purpose}</p>
      </section>

      <section>
        <h3>Argument hint</h3>
        <p>{skill.argumentHint || "No argument hint provided."}</p>
      </section>

      <ul className="tag-list" aria-label="Skill tags">
        {skill.tags.map((tag) => (
          <li key={tag}>{tag}</li>
        ))}
      </ul>

      <CopyCommand command={installCommand} />
    </article>
  );
}
