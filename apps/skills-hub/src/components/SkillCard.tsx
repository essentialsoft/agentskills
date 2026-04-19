import { Link } from "react-router-dom";
import type { Skill } from "../types/skill";

type SkillCardProps = {
  skill: Skill;
};

export function SkillCard({ skill }: SkillCardProps) {
  return (
    <article className="skill-card">
      <h3>
        <Link to={`/skills/${skill.slug}`}>{skill.name}</Link>
      </h3>
      <p>{skill.description}</p>
      <ul className="tag-list" aria-label={`${skill.name} tags`}>
        {skill.tags.map((tag) => (
          <li key={tag}>{tag}</li>
        ))}
      </ul>
    </article>
  );
}
