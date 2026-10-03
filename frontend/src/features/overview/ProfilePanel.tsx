import type { Profile } from "../../types/analysis";

type ProfilePanelProps = {
  profile: Profile;
};

const difficultyMeta = [
  { key: "easy" as const, label: "Easy" },
  { key: "medium" as const, label: "Medium" },
  { key: "hard" as const, label: "Hard" },
];

export function ProfilePanel({ profile }: ProfilePanelProps) {
  const total = profile.solved.easy + profile.solved.medium + profile.solved.hard;
  const maxTag = Math.max(...profile.tagStats.map((tag) => tag.solved), 1);

  return (
    <section className="panel" aria-label="Profile tool">
      <div className="identity">
        <div>
          <p className="eyebrow">Profile tool</p>
          <h3>{profile.username}</h3>
        </div>
        <dl className="identity-stats">
          <div>
            <dt>Ranking</dt>
            <dd>{profile.ranking ? profile.ranking.toLocaleString() : "—"}</dd>
          </div>
          <div>
            <dt>Acceptance</dt>
            <dd>{profile.acceptanceRate.toFixed(1)}%</dd>
          </div>
          <div>
            <dt>Solved</dt>
            <dd>{total}</dd>
          </div>
        </dl>
      </div>

      <div className="difficulty">
        {difficultyMeta.map((item) => {
          const count = profile.solved[item.key];
          const width = total === 0 ? 0 : Math.round((count / total) * 100);
          return (
            <div key={item.key} className={`diff diff-${item.key}`}>
              <div className="diff-label">
                <span>{item.label}</span>
                <strong>{count}</strong>
              </div>
              <div className="bar" aria-hidden="true">
                <span style={{ width: `${width}%` }} />
              </div>
            </div>
          );
        })}
      </div>

      <h4>Topics solved</h4>
      <ul className="tag-list">
        {profile.tagStats.map((tag) => (
          <li key={tag.tag}>
            <div className="tag-name">
              <span>{tag.tag}</span>
              <span>{tag.solved}</span>
            </div>
            <div className="bar thin" aria-hidden="true">
              <span style={{ width: `${Math.round((tag.solved / maxTag) * 100)}%` }} />
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
