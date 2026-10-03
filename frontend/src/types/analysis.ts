export type Difficulty = "Easy" | "Medium" | "Hard";

export type DifficultyCounts = {
  easy: number;
  medium: number;
  hard: number;
};

export type TagStat = {
  tag: string;
  solved: number;
};

export type Profile = {
  username: string;
  realName: string;
  ranking: number | null;
  acceptanceRate: number;
  solved: DifficultyCounts;
  tagStats: TagStat[];
};

export type ContestRound = {
  title: string;
  problemsSolved: number;
  totalProblems: number;
};

export type Contest = {
  attended: number;
  rating: number | null;
  globalRanking: number | null;
  topPercentage: number | null;
  recent: ContestRound[];
};

export type Submission = {
  title: string;
  status: string;
  language: string;
};

export type TraceStep = {
  phase: string;
  detail: string;
};

export type FocusTopic = {
  tag: string;
  why: string;
};

export type Decision = {
  contestRead: string;
  pace: string;
  focusTopics: FocusTopic[];
};

export type TopicGap = {
  tag: string;
  solved: number;
  severity: "high" | "medium";
  howToStudy: string;
};

export type StuckLoop = {
  title: string;
  tag: string;
  attempts: number;
  lastStatus: string;
  note: string;
};

export type RecommendedProblem = {
  title: string;
  difficulty: Difficulty;
  tag: string;
  reason: string;
  url: string;
};

export type StudyProblem = {
  title: string;
  difficulty: Difficulty;
  url: string;
  due: string;
};

export type StudyStep = {
  order: number;
  topic: string;
  focus: string;
  topicDue: string;
  problems: StudyProblem[];
};

export type UserKnowledge = {
  summary: string;
  topicGaps: TopicGap[];
  stuckLoops: StuckLoop[];
  recommendations: RecommendedProblem[];
  studyPlan: StudyStep[];
};

export type AgentRun = {
  trace: TraceStep[];
  profile: Profile;
  contest: Contest;
  submissions: Submission[];
  userKnowledge: UserKnowledge;
};
