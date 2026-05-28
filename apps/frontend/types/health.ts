export type DependencyStatus = {
  name: string;
  ok: boolean;
  latency_ms?: number | null;
  error?: string | null;
};

export type ReadyResponse = {
  service: string;
  status: "ready" | "not_ready";
  request_id: string;
  dependencies: DependencyStatus[];
};

