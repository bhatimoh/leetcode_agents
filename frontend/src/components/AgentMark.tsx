type AgentMarkProps = {
  label: string;
  title: string;
  state: "waiting" | "running" | "done";
  detail: string;
  live?: boolean;
};

export function AgentMark({ label, title, state, detail, live = false }: AgentMarkProps) {
  return (
    <header className={`agent-mark is-${state}`}>
      <span className="agent-step">{label}</span>
      <div>
        <h2>{title}</h2>
        <p aria-live={live ? "polite" : undefined}>{detail}</p>
      </div>
    </header>
  );
}
