import type { TopicGap } from "../../types/analysis";

type TopicGapsProps = {
  gaps: TopicGap[];
};

export function TopicGaps({ gaps }: TopicGapsProps) {
  return (
    <section className="block">
      <h3>Topics to study</h3>
      <ul className="gaps">
        {gaps.map((gap) => (
          <li key={gap.tag} className={`severity-${gap.severity}`}>
            <div className="gap-head">
              <strong>{gap.tag}</strong>
              <span>{gap.solved} solved</span>
            </div>
            <p>{gap.howToStudy}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
