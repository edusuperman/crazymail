"use client";

import { useState } from "react";
import type { EmailResponse } from "@/lib/api-client";

interface EmailGeneratorProps {
  email: EmailResponse | null;
  loading: boolean;
  copyOk: boolean;
  emailHighlight: boolean;
  error: string | null;
  onGenerate: (username?: string) => void;
  onCopy: () => void;
}

export default function EmailGenerator({
  email,
  loading,
  copyOk,
  emailHighlight,
  error,
  onGenerate,
  onCopy,
}: EmailGeneratorProps) {
  const [showCustom, setShowCustom] = useState(false);
  const [customPrefix, setCustomPrefix] = useState("");

  function handleGenerate() {
    const username = showCustom && customPrefix.trim() ? customPrefix.trim() : undefined;
    onGenerate(username);
  }

  return (
    <>
      {/* Hero */}
      <header className="flex flex-col items-center pt-16 pb-10 px-4 text-center">
        <h1 className="text-5xl sm:text-6xl font-extrabold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
          TempMail Pro
        </h1>
        <p className="mt-4 text-lg text-slate-400 max-w-md">
          Protect your privacy with disposable email addresses. No sign-up, no
          tracking, instant inbox.
        </p>

        {/* Custom prefix toggle */}
        <div className="mt-6 w-full max-w-xs">
          <button
            onClick={() => setShowCustom(!showCustom)}
            className="text-sm text-slate-500 hover:text-slate-300 transition mb-2"
          >
            {showCustom ? "Hide custom prefix" : "Custom prefix"}
          </button>
          {showCustom && (
            <input
              type="text"
              value={customPrefix}
              onChange={(e) => setCustomPrefix(e.target.value)}
              placeholder="e.g. myname"
              maxLength={30}
              className="w-full px-4 py-2 rounded-lg glass-light text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition mb-3"
            />
          )}
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="relative inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-3 text-lg font-semibold text-white shadow-lg btn-glow transition hover:scale-105 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Generating…
            </span>
          ) : (
            "Generate Email"
          )}
        </button>

        {error && <p className="mt-4 text-red-400 text-sm">{error}</p>}
      </header>

      {/* Email address display */}
      {email && (
        <section className="flex flex-col items-center px-4 pb-6">
          <div
            className={`flex items-center gap-3 rounded-xl px-6 py-4 max-w-full transition-all duration-500 ${
              emailHighlight
                ? "bg-cyan-500/20 border-cyan-400/60 shadow-glass-lg scale-[1.02] animate-breathe-border"
                : "glass shadow-glass animate-breathe-border"
            }`}
          >
            <span className="text-xl sm:text-2xl font-mono text-cyan-300 truncate">
              {email.address}
            </span>
            <button
              onClick={onCopy}
              className="shrink-0 rounded-lg bg-slate-700/80 hover:bg-slate-600 px-4 py-2 text-sm font-medium btn-glow transition"
            >
              {copyOk ? "Copied!" : "Copy"}
            </button>
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Provider: {email.provider}
          </p>
        </section>
      )}
    </>
  );
}
