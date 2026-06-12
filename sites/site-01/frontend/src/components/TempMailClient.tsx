"use client";

import { useState, useEffect, useRef } from "react";
import {
  createEmail,
  getMessages,
  getMessageDetail,
  deleteMessage,
  markAsRead,
  type EmailResponse,
  type MessageSummary,
  type MessageDetail,
} from "@/lib/api-client";
import { useToast, ToastContainer } from "@/components/Toast";
import EmailGenerator from "@/components/EmailGenerator";
import InboxList from "@/components/InboxList";
import FAQ from "@/components/FAQ";

export default function TempMailClient() {
  const [email, setEmail] = useState<EmailResponse | null>(null);
  const [messages, setMessages] = useState<MessageSummary[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<MessageDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [copyOk, setCopyOk] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emailHighlight, setEmailHighlight] = useState(false);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const prevCountRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const toast = useToast();

  useEffect(() => {
    if (!email) return;
    const addr = email.address;
    const poll = () => {
      getMessages(addr)
        .then((list) => {
          setMessages((prev) => {
            if (prevCountRef.current > 0 && list.length > prevCountRef.current) {
              toast.success("New email received!");
            }
            prevCountRef.current = list.length;
            return list;
          });
        })
        .catch(() => {});
    };
    timerRef.current = setInterval(poll, 5000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [email, toast]);

  async function handleGenerate(username?: string, domain?: string) {
    setLoading(true);
    setError(null);
    setExpandedId(null);
    setDetail(null);
    try {
      const res = await createEmail(username, domain);
      setEmail(res);
      setMessages([]);
      prevCountRef.current = 0;
      setMessagesLoading(true);
      setEmailHighlight(true);
      setTimeout(() => setEmailHighlight(false), 1500);
      toast.success("Email created!");
      getMessages(res.address)
        .then((list) => {
          setMessages(list);
          prevCountRef.current = list.length;
        })
        .catch(() => {})
        .finally(() => setMessagesLoading(false));
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
      toast.success("Copied to clipboard!");
      setTimeout(() => setCopyOk(false), 2000);
    } catch {
      /* fallback: silent */
    }
  }

  async function handleRefresh() {
    if (!email || refreshing) return;
    setRefreshing(true);
    try {
      const list = await getMessages(email.address);
      setMessages(list);
      prevCountRef.current = list.length;
      toast.success("Inbox refreshed!");
    } catch {
      toast.error("Failed to refresh");
    } finally {
      setRefreshing(false);
    }
  }

  async function handleDelete(messageId: string) {
    if (!email) return;
    try {
      await deleteMessage(email.address, messageId);
      setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
      if (expandedId === messageId) {
        setExpandedId(null);
        setDetail(null);
      }
      toast.success("Email deleted");
    } catch {
      toast.error("Failed to delete email");
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

    // Mark as read immediately in UI
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === id ? { ...msg, is_read: true } : msg
      )
    );

    // Call markAsRead API (fire-and-forget, don't block UI)
    markAsRead(id).catch(() => {});

    try {
      const d = await getMessageDetail(id);
      setDetail(d);
    } catch {
      setDetail(null);
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 bg-grid-texture text-white">
      <ToastContainer toasts={toast.toasts} />

      <EmailGenerator
        email={email}
        loading={loading}
        copyOk={copyOk}
        emailHighlight={emailHighlight}
        error={error}
        onGenerate={handleGenerate}
        onCopy={handleCopy}
      />

      {email && (
        <InboxList
          messages={messages}
          messagesLoading={messagesLoading}
          refreshing={refreshing}
          expandedId={expandedId}
          detail={detail}
          onRefresh={handleRefresh}
          onDelete={handleDelete}
          onExpand={handleExpand}
        />
      )}

      <FAQ />

      {/* Footer */}
      <footer className="text-center text-xs text-slate-600 py-6 px-4">
        <div className="flex flex-col items-center gap-2">
          <p className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            Privacy First — No tracking, no logs, emails auto-expire
          </p>
          <p>
            Built with{" "}
            <span className="text-red-400">❤</span> by{" "}
            <span className="text-slate-400">CrazyMail</span>
          </p>
          <a href="/privacy" className="text-slate-500 hover:text-slate-300 transition">
            Privacy Policy
          </a>
        </div>
      </footer>
    </div>
  );
}
