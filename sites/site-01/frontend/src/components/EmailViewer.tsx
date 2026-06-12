"use client";

import type { MessageSummary, MessageDetail } from "@/lib/api-client";

interface EmailViewerProps {
  message: MessageSummary;
  detail: MessageDetail | null;
}

function sanitizeHtml(html: string): string {
  // Remove script tags and their content
  let sanitized = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");
  // Remove event handlers (on*)
  sanitized = sanitized.replace(/\s+on\w+\s*=\s*["'][^"']*["']/gi, "");
  sanitized = sanitized.replace(/\s+on\w+\s*=\s*[^\s>]*/gi, "");
  // Remove javascript: protocol in href/src
  sanitized = sanitized.replace(/href\s*=\s*["']javascript:[^"']*["']/gi, 'href="#"');
  sanitized = sanitized.replace(/src\s*=\s*["']javascript:[^"']*["']/gi, 'src=""');
  // Remove data: protocol in src (can be used for XSS)
  sanitized = sanitized.replace(/src\s*=\s*["']data:[^"']*["']/gi, 'src=""');
  // Remove <iframe>, <object>, <embed>, <form> tags
  sanitized = sanitized.replace(/<\/?(?:iframe|object|embed|form|base|link|meta|style)\b[^>]*>/gi, "");
  return sanitized;
}

export default function EmailViewer({ detail }: EmailViewerProps) {
  return (
    <div className="border-t-2 border-cyan-500/30 px-5 py-5 text-sm text-slate-200 glass">
      {detail ? (
        detail.body_html ? (
          <div
            className="max-w-none p-4 rounded-lg bg-slate-900/60 [&_a]:text-cyan-400 [&_a]:underline [&_a:hover]:text-cyan-300 [&_img]:max-w-full [&_img]:h-auto"
            dangerouslySetInnerHTML={{
              __html: sanitizeHtml(detail.body_html),
            }}
          />
        ) : (
          <pre className="whitespace-pre-wrap break-words p-4 rounded-lg bg-slate-900/60">
            {detail.body_text}
          </pre>
        )
      ) : (
        <p className="text-slate-400 animate-pulse">Loading…</p>
      )}
    </div>
  );
}
