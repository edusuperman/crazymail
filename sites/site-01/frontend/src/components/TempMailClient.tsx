"use client";

import { useState, useEffect, useRef } from "react";
import {
  createEmail,
  getMessages,
  getMessageDetail,
  type EmailResponse,
  type MessageSummary,
  type MessageDetail,
} from "@/lib/api-client";

export default function TempMailClient() {
  const [email, setEmail] = useState<EmailResponse | null>(null);
  const [messages, setMessages] = useState<MessageSummary[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<MessageDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [copyOk, setCopyOk] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!email) return;
    const addr = email.address;
    const poll = () => {
      getMessages(addr)
        .then((list) => setMessages(list))
        .catch(() => {});
    };
    timerRef.current = setInterval(poll, 5000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [email]);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    setExpandedId(null);
    setDetail(null);
    try {
      const res = await createEmail();
      setEmail(res);
      setMessages([]);
      // 立即拉取第一批邮件
      getMessages(res.address)
        .then((list) => setMessages(list))
        .catch(() => {});
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate email");
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!email) return;
    try {
      await navigator.clipboard.writeText(email.address);
      setCopyOk(true);
      setTimeout(() => setCopyOk(false), 2000);
    } catch {
      /* fallback: 静默 */
    }
  }

  async function handleExpand(id: string) {
    if (expandedId === id) {
      setExpandedId(null);
      setDetail(null);
      return;
    }
    setExpandedId(id);
    setDetail(null);
    try {
      const d = await getMessageDetail(id);
      setDetail(d);
    } catch {
      setDetail(null);
    }
  }

  function formatTime(iso: string | null): string {
    if (!iso) return "";
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white">
      {/* Hero */}
      <header className="flex flex-col items-center pt-16 pb-10 px-4 text-center">
        <h1 className="text-5xl sm:text-6xl font-extrabold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
          TempMail Pro
        </h1>
        <p className="mt-4 text-lg text-slate-400 max-w-md">
          Protect your privacy with disposable email addresses. No sign-up, no
          tracking, instant inbox.
        </p>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-8 relative inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-3 text-lg font-semibold text-white shadow-lg transition hover:scale-105 disabled:opacity-60 disabled:cursor-not-allowed animate-pulse"
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

      {/* 邮箱地址展示 */}
      {email && (
        <section className="flex flex-col items-center px-4 pb-6">
          <div className="flex items-center gap-3 rounded-xl bg-slate-800/60 border border-slate-700 px-6 py-4 max-w-full">
            <span className="text-xl sm:text-2xl font-mono text-cyan-300 truncate">
              {email.address}
            </span>
            <button
              onClick={handleCopy}
              className="shrink-0 rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm font-medium transition"
            >
              {copyOk ? "Copied!" : "Copy"}
            </button>
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Provider: {email.provider}
          </p>
        </section>
      )}

      {/* 收件箱 */}
      {email && (
        <section className="flex-1 w-full max-w-2xl mx-auto px-4 pb-16">
          <h2 className="text-xl font-semibold mb-4 text-slate-200">
            Inbox
            {messages.length > 0 && (
              <span className="ml-2 text-sm font-normal text-slate-500">
                ({messages.length})
              </span>
            )}
          </h2>

          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500">
              <svg
                className="w-16 h-16 mb-4 opacity-40"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m0 0V9a2 2 0 012-2h8a2 2 0 012 2v4m-6 0h4"
                />
              </svg>
              <p className="text-lg">No messages yet</p>
              <p className="text-sm mt-1">
                Emails sent to your address will appear here
              </p>
            </div>
          ) : (
            <ul className="space-y-3">
              {messages.map((msg) => (
                <li
                  key={msg.id}
                  className="rounded-xl bg-slate-800/50 border border-slate-700 overflow-hidden transition hover:border-slate-500"
                >
                  <button
                    onClick={() => handleExpand(msg.id)}
                    className="w-full text-left px-5 py-4 flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4"
                  >
                    <span
                      className={`font-medium truncate max-w-[180px] ${
                        msg.is_read ? "text-slate-400" : "text-white"
                      }`}
                    >
                      {msg.from_name || msg.from_address}
                    </span>
                    <span
                      className={`flex-1 truncate ${
                        msg.is_read ? "text-slate-500" : "text-slate-300"
                      }`}
                    >
                      {msg.subject || "(no subject)"}
                    </span>
                    <span className="text-xs text-slate-500 whitespace-nowrap">
                      {formatTime(msg.received_at)}
                    </span>
                  </button>

                  {expandedId === msg.id && (
                    <div className="border-t border-slate-700 px-5 py-4 text-sm text-slate-300 bg-slate-900/40">
                      {detail ? (
                        detail.body_html ? (
                          <div
                            className="max-w-none [&_a]:text-cyan-400 [&_a]:underline [&_img]:max-w-full [&_img]:h-auto"
                            dangerouslySetInnerHTML={{
                              __html: detail.body_html,
                            }}
                          />
                        ) : (
                          <pre className="whitespace-pre-wrap break-words">
                            {detail.body_text}
                          </pre>
                        )
                      ) : (
                        <p className="text-slate-500 animate-pulse">
                          Loading…
                        </p>
                      )}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {/* 底部 */}
      <footer className="text-center text-xs text-slate-600 py-6">
        TempMail Pro &mdash; Your privacy, your inbox.
      </footer>
    </div>
  );
}
