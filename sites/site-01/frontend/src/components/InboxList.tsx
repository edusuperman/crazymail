"use client";

import type { MessageSummary, MessageDetail } from "@/lib/api-client";
import EmailViewer from "./EmailViewer";

interface InboxListProps {
  messages: MessageSummary[];
  messagesLoading: boolean;
  refreshing: boolean;
  expandedId: string | null;
  detail: MessageDetail | null;
  onRefresh: () => void;
  onDelete: (messageId: string) => void;
  onExpand: (id: string) => void;
}

function formatTime(iso: string | null): string {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function InboxList({
  messages,
  messagesLoading,
  refreshing,
  expandedId,
  detail,
  onRefresh,
  onDelete,
  onExpand,
}: InboxListProps) {
  return (
    <section className="flex-1 w-full max-w-2xl mx-auto px-4 pb-16">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-slate-200">
          Inbox
          {messages.length > 0 && (
            <span className="ml-2 text-sm font-normal text-slate-500">
              ({messages.length})
            </span>
          )}
        </h2>
        <button
          onClick={onRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 rounded-lg glass-light px-3 py-2 text-sm font-medium btn-glow transition disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <svg
            className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {messagesLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="glass rounded-xl px-5 py-4 animate-pulse"
            >
              <div className="flex items-center gap-4">
                <div className="w-32 h-4 bg-slate-700 rounded" />
                <div className="flex-1 h-4 bg-slate-700 rounded" />
                <div className="w-20 h-3 bg-slate-700 rounded" />
              </div>
            </div>
          ))}
        </div>
      ) : messages.length === 0 ? (
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
        <ul className="divide-y divide-slate-700/50">
          {messages.map((msg) => (
            <li
              key={msg.id}
              className="glass first:rounded-t-xl last:rounded-b-xl overflow-hidden shadow-inner-glow transition hover:bg-slate-800/40"
            >
              <div className="flex items-center">
                <button
                  onClick={() => onExpand(msg.id)}
                  className="flex-1 text-left px-5 py-4 flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4"
                >
                  <div className="flex items-center gap-2 min-w-0 sm:w-48 shrink-0">
                    {!msg.is_read && (
                      <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
                    )}
                    <div className="min-w-0">
                      <span
                        className={`block truncate ${
                          msg.is_read
                            ? "text-slate-400 font-normal"
                            : "text-white font-semibold"
                        }`}
                      >
                        {msg.from_name || msg.from_address}
                      </span>
                      {msg.from_name && msg.from_address && (
                        <span className="block truncate text-xs text-slate-500">
                          {msg.from_address}
                        </span>
                      )}
                    </div>
                  </div>
                  <span
                    className={`flex-1 truncate ${
                      msg.is_read
                        ? "text-slate-500"
                        : "text-slate-200 font-medium"
                    }`}
                  >
                    {msg.subject || "(no subject)"}
                  </span>
                  <span className="text-xs text-slate-500 whitespace-nowrap">
                    {formatTime(msg.received_at)}
                  </span>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(msg.id);
                  }}
                  className="shrink-0 p-2 mr-2 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-700/50 transition"
                  title="Delete email"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>

              {expandedId === msg.id && (
                <EmailViewer message={msg} detail={detail} />
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
