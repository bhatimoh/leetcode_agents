import type { ContestRound, TopicGap } from "../../types/analysis";

type ContestChartProps = {
  rounds: ContestRound[];
};

type TopicChartProps = {
  gaps: TopicGap[];
};

export function ContestChart({ rounds }: ContestChartProps) {
  const ordered = [...rounds].reverse();
  if (ordered.length === 0) {
    return <p className="muted">No attended contests to chart.</p>;
  }

  return (
    <figure className="chart-card">
      <figcaption>
        <h3>Questions solved in the last five contests</h3>
        <p>Each bar is the share solved. The count is written beside the bar. Oldest contest is first.</p>
      </figcaption>
      <ul className="chart">
        {ordered.map((round) => {
          const total = Math.max(round.totalProblems, 1);
          const width = Math.round((round.problemsSolved / total) * 100);
          return (
            <li key={round.title}>
              <span className="chart-label">{round.title}</span>
              <div className="chart-track" aria-hidden="true">
                <span style={{ width: `${width}%` }} />
              </div>
              <span className="chart-value">
                {round.problemsSolved} of {round.totalProblems}
              </span>
            </li>
          );
        })}
      </ul>
    </figure>
  );
}

export function TopicChart({ gaps }: TopicChartProps) {
  if (gaps.length === 0) {
    return null;
  }
  const maxSolved = Math.max(...gaps.map((gap) => gap.solved), 1);

  return (
    <figure className="chart-card">
      <figcaption>
        <h3>Topics Agent 2 wants in focus</h3>
        <p>Shorter bars are thinner practice. High priority topics are also marked in text.</p>
      </figcaption>
      <ul className="chart">
        {gaps.map((gap) => (
          <li key={gap.tag}>
            <span className="chart-label">
              {gap.tag}
              <span className="chart-note">{gap.severity === "high" ? "High priority" : "Next"}</span>
            </span>
            <div className="chart-track topic" aria-hidden="true">
              <span style={{ width: `${Math.round((gap.solved / maxSolved) * 100)}%` }} />
            </div>
            <span className="chart-value">{gap.solved} solved</span>
          </li>
        ))}
      </ul>
    </figure>
  );
}
