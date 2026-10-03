import type { ContestRound } from "../../types/analysis";

type ContestInfographicProps = {
  rounds: ContestRound[];
};

export function ContestInfographic({ rounds }: ContestInfographicProps) {
  const ordered = [...rounds].reverse();
  if (ordered.length === 0) {
    return <p className="muted">No attended contests to chart.</p>;
  }

  const solved = ordered.reduce((sum, round) => sum + round.problemsSolved, 0);
  const offered = ordered.reduce((sum, round) => sum + round.totalProblems, 0);
  const missed = Math.max(offered - solved, 0);
  const rate = offered === 0 ? 0 : Math.round((solved / offered) * 100);
  const trend = contestTrend(ordered);
  const maxTotal = Math.max(...ordered.map((round) => round.totalProblems), 1);

  return (
    <figure className="infographic">
      <figcaption>
        <h3>Contest performance</h3>
        <p>Last {ordered.length} attended contests, oldest on the left. The solid part of each column is questions solved.</p>
      </figcaption>
      <ul className="stat-row">
        <li>
          <strong>
            {solved}/{offered}
          </strong>
          <span>Questions solved</span>
        </li>
        <li>
          <strong>{rate}%</strong>
          <span>Solve rate</span>
        </li>
        <li>
          <strong>{missed}</strong>
          <span>Missed</span>
        </li>
        <li>
          <strong>{trend}</strong>
          <span>Trend</span>
        </li>
      </ul>
      <div className="columns" role="img" aria-label={ordered.map((round) => `${round.title}: ${round.problemsSolved} of ${round.totalProblems}`).join(". ")}>
        {ordered.map((round) => {
          const height = Math.round((round.totalProblems / maxTotal) * 140);
          const solvedHeight = round.totalProblems === 0 ? 0 : Math.round((round.problemsSolved / round.totalProblems) * height);
          const shortName = round.title.replace("Weekly Contest ", "W").replace("Biweekly Contest ", "B");
          return (
            <div className="column" key={round.title}>
              <div className="column-plot" style={{ height: 140 }}>
                <div className="column-offered" style={{ height }} title={`${round.problemsSolved} solved, ${round.totalProblems - round.problemsSolved} missed`}>
                  <div className="column-solved" style={{ height: solvedHeight }} />
                </div>
              </div>
              <strong>{round.problemsSolved}/{round.totalProblems}</strong>
              <span>{shortName}</span>
            </div>
          );
        })}
      </div>
    </figure>
  );
}

function contestTrend(ordered: ContestRound[]) {
  if (ordered.length < 2) {
    return "One contest";
  }
  const rate = (round: ContestRound) => (round.totalProblems === 0 ? 0 : round.problemsSolved / round.totalProblems);
  const latest = rate(ordered[ordered.length - 1]);
  const older = ordered.slice(0, -1).reduce((sum, round) => sum + rate(round), 0) / (ordered.length - 1);
  if (latest > older + 0.12) {
    return "Improving";
  }
  if (latest + 0.12 < older) {
    return "Dropping";
  }
  return "Steady";
}
