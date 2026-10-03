import type { StuckLoop } from "../../types/analysis";

type StuckLoopsProps = {
  loops: StuckLoop[];
};

export function StuckLoops({ loops }: StuckLoopsProps) {
  return (
    <section className="block">
      <h3>Stuck loops</h3>
      {loops.length === 0 ? (
        <p className="muted">No repeated unsolved problem in the recent submissions.</p>
      ) : (
        <ul className="loops">
          {loops.map((loop) => (
            <li key={loop.title}>
              <div className="gap-head">
                <strong>{loop.title}</strong>
                <span>
                  {loop.attempts} attempts · {loop.lastStatus}
                </span>
              </div>
              <p>{loop.note}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
