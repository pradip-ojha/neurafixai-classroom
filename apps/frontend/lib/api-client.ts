export type ApiEnvelope<T> = {
  success?: boolean;
  data?: T;
  message?: string;
  request_id?: string;
  error?: {
    code: string;
    message: string;
  };
};

const mainApiUrl = process.env.NEXT_PUBLIC_MAIN_API_URL ?? "http://localhost:8000";

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${mainApiUrl}${path}`, {
    ...init,
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

