import type { AgentRun, Contest, Decision, Profile, Submission, TraceStep, UserKnowledge } from "../types/analysis";

export type AgentEvent = {
  type: "status" | "trace" | "agent1" | "agent2" | "error";
  agent?: 1 | 2;
  detail?: string;
  trace?: TraceStep[];
  profile?: Profile;
  contest?: Contest;
  submissions?: Submission[];
  decision?: {
    contest_read: string;
    pace: string;
    focus_topics: { tag: string; why: string }[];
  };
  userKnowledge?: UserKnowledge;
};

export async function streamAgent(username: string, onEvent: (event: AgentEvent) => void): Promise<void> {
  const response = await fetch("/api/analysis/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  if (!response.ok || !response.body) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail || "The agent run did not finish.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      const line = chunk.split("\n").find((item) => item.startsWith("data: "));
      if (!line) {
        continue;
      }
      onEvent(JSON.parse(line.slice(6)) as AgentEvent);
    }
  }
}

export type { AgentRun, Decision };
