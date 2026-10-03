import type { StudyStep } from "../../types/analysis";

type StudyPlanProps = {
  steps: StudyStep[];
};

function formatDue(iso: string) {
  const [year, month, day] = iso.split("-").map(Number);
  if (!year || !month || !day) {
    return iso;
  }
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

export function StudyPlan({ steps }: StudyPlanProps) {
  return (
    <section className="block">
      <h3>How to study</h3>
      <p className="muted">Each problem opens on LeetCode. Finish it by the date beside the link.</p>
      <ol className="plan">
        {steps.map((step) => (
          <li key={step.order}>
            <span className="order">{step.order}</span>
            <div>
              <strong>{step.topic}</strong>
              <p>{step.focus}</p>
              <p className="deadline">Topic target: {formatDue(step.topicDue)}</p>
              <ul className="problem-links">
                {step.problems.map((problem) => (
                  <li key={problem.url}>
                    <a href={problem.url} target="_blank" rel="noreferrer">
                      {problem.title}
                    </a>
                    <span className={`pill pill-${problem.difficulty.toLowerCase()}`}>{problem.difficulty}</span>
                    <span>Solve by {formatDue(problem.due)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
