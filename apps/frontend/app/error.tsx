"use client";

import { RefreshCcw } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="grid min-h-screen place-items-center bg-paper px-6">
      <section className="w-full max-w-md rounded-lg border border-line bg-white p-6 shadow-panel">
        <h1 className="text-xl font-bold text-ink">Unable to load workspace</h1>
        <p className="mt-2 text-sm text-muted">{error.message || "Unexpected frontend error."}</p>
        <button
          type="button"
          onClick={reset}
          className="mt-5 inline-flex min-h-10 items-center gap-2 rounded-md bg-forest px-4 py-2 text-sm font-bold text-white"
        >
          <RefreshCcw className="h-4 w-4" />
          Retry
        </button>
      </section>
    </main>
  );
}

