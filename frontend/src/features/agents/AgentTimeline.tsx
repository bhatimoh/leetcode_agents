import type { TraceStep } from "../../types/analysis";

type Live = "waiting" | "running" | "done";

type AgentFeedProps = {
  name: string;
  title: string;
  state: Live;
  detail: string;
  trace: TraceStep[];
};

type AgentTimelineProps = {
  agent1: AgentFeedProps;
  agent2: AgentFeedProps;
};

export function AgentTimeline({ agent1, agent2 }: AgentTimelineProps) {
  return (
    <div className="timeline">
      <AgentFeed {...agent1} />
      <AgentFeed {...agent2} />
    </div>
  );
}

function AgentFeed({ name, title, state, detail, trace }: AgentFeedProps) {
  const last = trace[trace.length - 1];
  const showNow = state === "running" && detail !== last?.detail;

  return (
    <section className={`feed is-${state}`} aria-label={name}>
      <header className="feed-head">
        <span className="agent-step">{name}</span>
        <div>
          <h2>{title}</h2>
          <p>{state === "waiting" ? detail : state === "done" ? "Finished" : "Working"}</p>
        </div>
      </header>
      <ol className="steps">
        {trace.map((step, index) => (
          <li key={`${step.phase}-${index}`} className="step is-done">
            <span className="step-mark" aria-hidden="true" />
            <div>
              <span className="step-phase">{step.phase}</span>
              <p>{step.detail}</p>
            </div>
          </li>
        ))}
        {showNow ? (
          <li className="step is-now" aria-current="step">
            <span className="step-mark" aria-hidden="true" />
            <div>
              <span className="step-phase">now</span>
              <p aria-live="polite">{detail}</p>
            </div>
          </li>
        ) : null}
        {state === "waiting" && trace.length === 0 ? <li className="step is-wait"><p>{detail}</p></li> : null}
      </ol>
    </section>
  );
}
