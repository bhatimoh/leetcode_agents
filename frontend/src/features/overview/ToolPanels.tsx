import type { Contest, Submission } from "../../types/analysis";

type ContestPanelProps = {
  contest: Contest;
};

export function ContestPanel({ contest }: ContestPanelProps) {
  const rating = contest.rating === null ? "—" : Math.round(contest.rating).toLocaleString();
  const rank = contest.globalRanking === null ? "—" : contest.globalRanking.toLocaleString();
  const top = contest.topPercentage === null ? "—" : `${contest.topPercentage.toFixed(1)}%`;

  return (
    <section className="panel" aria-label="Contest tool">
      <p className="eyebrow">Contest tool</p>
      <h3>{contest.attended === 0 ? "No contests yet" : `${contest.attended} attended`}</h3>
      <dl className="identity-stats stacked">
        <div>
          <dt>Rating</dt>
          <dd>{rating}</dd>
        </div>
        <div>
          <dt>Global rank</dt>
          <dd>{rank}</dd>
        </div>
        <div>
          <dt>Top</dt>
          <dd>{top}</dd>
        </div>
      </dl>
      <h4>Previous five contests</h4>
      {contest.recent.length === 0 ? (
        <p className="muted">No attended contests in the public history.</p>
      ) : (
        <ul className="submissions">
          {contest.recent.map((round) => (
            <li key={round.title}>
              <div>
                <strong>{round.title}</strong>
                <span>
                  {round.problemsSolved}/{round.totalProblems}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

type SubmissionListProps = {
  submissions: Submission[];
};

export function SubmissionList({ submissions }: SubmissionListProps) {
  return (
    <section className="panel" aria-label="Submission tool">
      <p className="eyebrow">Submission tool</p>
      <h3>Recent tries</h3>
      {submissions.length === 0 ? (
        <p className="muted">No recent public submissions.</p>
      ) : (
        <ul className="submissions">
          {submissions.slice(0, 8).map((submission, index) => (
            <li key={`${submission.title}-${index}`}>
              <div>
                <strong>{submission.title}</strong>
                <span className={submission.status === "Accepted" ? "pill pill-easy" : "pill pill-hard"}>
                  {submission.status}
                </span>
              </div>
              <p>{submission.language}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
