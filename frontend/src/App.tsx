import { useState } from "react";
import { streamAgent } from "./api/analysis";
import { StuckLoops } from "./features/loops/StuckLoops";
import { ContestPanel, SubmissionList } from "./features/overview/ToolPanels";
import { ProfilePanel } from "./features/overview/ProfilePanel";
import { Recommendations } from "./features/recommendations/Recommendations";
import { SearchBar } from "./features/search/SearchBar";
import { StudyPlan } from "./features/study-plan/StudyPlan";
import { ContestInfographic } from "./features/analysis/ContestInfographic";
import { TopicChart } from "./features/analysis/PerformanceCharts";
import { AgentTimeline } from "./features/agents/AgentTimeline";
import { TopicGaps } from "./features/topics/TopicGaps";
import type { Contest, Decision, Profile, Submission, TraceStep, UserKnowledge } from "./types/analysis";

type Live = "waiting" | "running" | "done";
type Tab = "analysis" | "agents";

export function App() {
  const [username, setUsername] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [agent1State, setAgent1State] = useState<Live>("waiting");
  const [agent1Detail, setAgent1Detail] = useState("Waiting for a username.");
  const [agent1Trace, setAgent1Trace] = useState<TraceStep[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [contest, setContest] = useState<Contest | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [agent2State, setAgent2State] = useState<Live>("waiting");
  const [agent2Detail, setAgent2Detail] = useState("Starts after the records are in.");
  const [agent2Trace, setAgent2Trace] = useState<TraceStep[]>([]);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [knowledge, setKnowledge] = useState<UserKnowledge | null>(null);
  const [tab, setTab] = useState<Tab>("analysis");

  function reset() {
    setError("");
    setAgent1State("waiting");
    setAgent1Detail("Waiting for a username.");
    setAgent1Trace([]);
    setProfile(null);
    setContest(null);
    setSubmissions([]);
    setAgent2State("waiting");
    setAgent2Detail("Starts after the records are in.");
    setAgent2Trace([]);
    setDecision(null);
    setKnowledge(null);
  }

  async function start() {
    const handle = username.trim();
    if (!handle) {
      return;
    }
    reset();
    setTab("agents");
    setBusy(true);
    setAgent1State("running");
    setAgent1Detail("Starting the record gather.");

    try {
      await streamAgent(handle, (event) => {
        if (event.type === "error") {
          setError(event.detail || "The agent run did not finish.");
          return;
        }
        if (event.type === "status" && event.agent === 1) {
          setAgent1State("running");
          setAgent1Detail(event.detail || "");
        }
        if (event.type === "trace" && event.agent === 1 && event.trace) {
          setAgent1Trace(event.trace);
        }
        if (event.type === "agent1" && event.profile && event.contest && event.submissions && event.trace) {
          setAgent1State("done");
          setAgent1Detail("Records are ready for the coach.");
          setAgent1Trace(event.trace);
          setProfile(event.profile);
          setContest(event.contest);
          setSubmissions(event.submissions);
        }
        if (event.type === "status" && event.agent === 2) {
          setAgent1State("done");
          setAgent2State("running");
          setAgent2Detail(event.detail || "");
        }
        if (event.type === "trace" && event.agent === 2 && event.trace) {
          setAgent2Trace(event.trace);
          if (event.decision) {
            setDecision({
              contestRead: event.decision.contest_read,
              pace: event.decision.pace,
              focusTopics: event.decision.focus_topics,
            });
          }
        }
        if (event.type === "agent2" && event.userKnowledge && event.trace) {
          setAgent2State("done");
          setAgent2Detail("The plan matches the contest performance.");
          setAgent2Trace(event.trace);
          setKnowledge(event.userKnowledge);
          if (event.decision) {
            setDecision({
              contestRead: event.decision.contest_read,
              pace: event.decision.pace,
              focusTopics: event.decision.focus_topics,
            });
          }
        }
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The agent run did not finish.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="shell" id="content">
      <a className="skip" href="#workspace">
        Skip to the workspace
      </a>
      <header className="topbar">
        <div className="topbar-inner">
          <h1>
            <svg className="logo" viewBox="0 0 32 32" aria-hidden="true">
              <rect width="32" height="32" rx="8" fill="#0b1c24" stroke="#2de2ff" strokeWidth="1.4" />
              <path d="M7 22.5h5V15H7v7.5Zm6.5 0h5V10h-5v12.5Zm6.5 0H25V6h-5v16.5Z" fill="#2de2ff" />
              <circle cx="22.5" cy="6" r="1.8" fill="#f4feff" />
            </svg>
            Vishleshan
          </h1>
          <SearchBar username={username} busy={busy} onUsernameChange={setUsername} onSubmit={start} />
        </div>
      </header>
      <main className="page">
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
      <div className="workspace" id="workspace">
        <div className="tabs" role="tablist" aria-label="Workspace">
          <button
            type="button"
            role="tab"
            id="tab-analysis"
            aria-selected={tab === "analysis"}
            aria-controls="panel-analysis"
            className={tab === "analysis" ? "is-selected" : ""}
            onClick={() => setTab("analysis")}
          >
            Analysis
          </button>
          <button
            type="button"
            role="tab"
            id="tab-agents"
            aria-selected={tab === "agents"}
            aria-controls="panel-agents"
            className={tab === "agents" ? "is-selected" : ""}
            onClick={() => setTab("agents")}
          >
            Agents
            {busy ? <span className="tab-live">Live</span> : null}
          </button>
        </div>

        <div role="tabpanel" id="panel-analysis" aria-labelledby="tab-analysis" hidden={tab !== "analysis"}>
          {contest && agent2State !== "waiting" ? (
            <div className="chart-grid">
              <ContestInfographic rounds={contest.recent} />
              {knowledge ? <TopicChart gaps={knowledge.topicGaps} /> : null}
            </div>
          ) : (
            <p className="muted">Run a username to see contest performance.</p>
          )}
          {profile && contest ? (
            <div className="tool-grid">
              <ProfilePanel profile={profile} />
              <div className="tool-side">
                <ContestPanel contest={contest} />
                <SubmissionList submissions={submissions} />
              </div>
            </div>
          ) : null}
          {decision ? (
            <div className="panel">
              <p className="eyebrow">Focus decision</p>
              <p className="summary">{decision.contestRead}</p>
              <ul className="gaps">
                {decision.focusTopics.map((topic) => (
                  <li key={topic.tag}>
                    <div className="gap-head">
                      <strong>{topic.tag}</strong>
                      <span>{decision.pace}</span>
                    </div>
                    <p>{topic.why}</p>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {knowledge ? (
            <div className="panel analysis">
              <p className="summary">{knowledge.summary}</p>
              <TopicGaps gaps={knowledge.topicGaps} />
              <StuckLoops loops={knowledge.stuckLoops} />
              <Recommendations problems={knowledge.recommendations} />
              <StudyPlan steps={knowledge.studyPlan} />
            </div>
          ) : null}
        </div>

        <div role="tabpanel" id="panel-agents" aria-labelledby="tab-agents" hidden={tab !== "agents"}>
          <AgentTimeline
            agent1={{
              name: "Agent 1",
              title: "Gather records",
              state: agent1State,
              detail: agent1Detail,
              trace: agent1Trace,
            }}
            agent2={{
              name: "Agent 2",
              title: "Decide and plan",
              state: agent2State,
              detail: agent2Detail,
              trace: agent2Trace,
            }}
          />
        </div>
      </div>
      </main>
    </div>
  );
}
