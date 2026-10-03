import type { RecommendedProblem } from "../../types/analysis";

type RecommendationsProps = {
  problems: RecommendedProblem[];
};

export function Recommendations({ problems }: RecommendationsProps) {
  return (
    <section className="block">
      <h3>Questions to solve next</h3>
      <ol className="recs">
        {problems.map((problem) => (
          <li key={problem.title}>
            <div className="gap-head">
              <a href={problem.url} target="_blank" rel="noreferrer">
                <strong>{problem.title}</strong>
              </a>
              <span className={`pill pill-${problem.difficulty.toLowerCase()}`}>{problem.difficulty}</span>
            </div>
            <p>
              {problem.tag}. {problem.reason}
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}
