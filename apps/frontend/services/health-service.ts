import { apiGet } from "@/lib/api-client";

export type HealthResponse = {
  service: string;
  status: string;
  request_id: string;
};

export function getMainBackendHealth() {
  return apiGet<HealthResponse>("/health");
}

