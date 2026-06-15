import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Copy,
  RefreshCw,
  Sparkles,
  Shield,
  Mail,
  Trash2,
  Inbox as InboxIcon,
  Clock,
  CheckCircle2,
  ChevronDown,
  Lock,
  Zap,
  Eye,
  Server,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { mailApi, type EmailMessage, type MailboxAddress } from "@/lib/mail-api";
import { cn } from "@/lib/utils";

const STORAGE_KEY = "tempmail.pro.address.v1";

function loadStored(): MailboxAddress | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as MailboxAddress) : null;
  } catch {
    return null;
  }
}

function saveStored(addr: MailboxAddress | null) {
  if (typeof window === "undefined") return;
  if (addr) localStorage.setItem(STORAGE_KEY, JSON.stringify(addr));
  else localStorage.removeItem(STORAGE_KEY);
}

function timeAgo(iso: string) {
  const diff = Math.max(0, Date.now() - new Date(iso).getTime());
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export function MailWorkspace() {
  const qc = useQueryClient();
  const [address, setAddress] = useState<MailboxAddress | null>(null);
  const [username, setUsername] = useState("");
  const [domain, setDomain] = useState<string>("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const seenIdsRef = useRef<Set<string>>(new Set());
  const initRef = useRef(false);

  // hydrate from storage
  useEffect(() => {
    const stored = loadStored();
    if (stored) {
      setAddress(stored);
      setDomain(stored.domain);
    }
  }, []);

  const domainsQuery = useQuery({
    queryKey: ["mail", "domains"],
    queryFn: () => mailApi.domains(),
    staleTime: 60_000,
  });

  const createMut = useMutation({
    mutationFn: (vars: { username?: string; domain?: string }) =>
      mailApi.createEmail(vars),
    onSuccess: (addr) => {
      setAddress(addr);
      setDomain(addr.domain);
      saveStored(addr);
      seenIdsRef.current = new Set();
      qc.removeQueries({ queryKey: ["mail", "messages"] });
      toast.success("New mailbox ready", { description: addr.address });
    },
    onError: (e: Error) =>
      toast.error("Failed to create mailbox", { description: e.message }),
  });

  // auto-create one on first visit if none stored & backend reachable
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    const stored = loadStored();
    if (!stored) {
      createMut.mutate({});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const inboxQuery = useQuery({
    queryKey: ["mail", "messages", address?.address],
    queryFn: () => mailApi.messages(),
    enabled: !!address,
    refetchInterval: 5000,
    refetchOnWindowFocus: true,
  });

  // toast on new mail
  useEffect(() => {
    const msgs = inboxQuery.data?.messages;
    if (!msgs) return;
    if (seenIdsRef.current.size === 0) {
      msgs.forEach((m) => seenIdsRef.current.add(m.id));
      return;
    }
    const fresh = msgs.filter((m) => !seenIdsRef.current.has(m.id));
    fresh.forEach((m) => {
      seenIdsRef.current.add(m.id);
      toast.success(`New mail: ${m.subject || "(no subject)"}`, {
        description: `from ${m.from_name || m.from_address}`,
      });
    });
  }, [inboxQuery.data]);

  const deleteMut = useMutation({
    mutationFn: (id: string) => mailApi.delete(id),
    onSuccess: () => {
      toast("Message deleted");
      qc.invalidateQueries({ queryKey: ["mail", "messages"] });
    },
    onError: (e: Error) => toast.error("Delete failed", { description: e.message }),
  });

  const markReadMut = useMutation({
    mutationFn: (id: string) => mailApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mail", "messages"] }),
  });

  const handleGenerate = () => {
    createMut.mutate({
      username: username.trim() || undefined,
      domain: domain || undefined,
    });
  };

  const handleCopy = async () => {
    if (!address) return;
    try {
      await navigator.clipboard.writeText(address.address);
      toast.success("Address copied", { description: address.address });
    } catch {
      toast.error("Clipboard unavailable");
    }
  };

  const messages = inboxQuery.data?.messages ?? [];
  const unreadCount = messages.filter((m) => !m.is_read).length;

  const domains = domainsQuery.data?.domains ?? [];
  const effectiveDomain = domain || domains[0] || "";

  const handleExpand = (m: EmailMessage) => {
    const next = expandedId === m.id ? null : m.id;
    setExpandedId(next);
    if (next && !m.is_read) markReadMut.mutate(m.id);
  };

  return (
    <section className="relative" aria-label="Temporary mailbox">
      <Card className="border-border/60 bg-card/80 shadow-[var(--shadow-card)] backdrop-blur p-6 md:p-8 space-y-6">
        {/* Address bar */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">
              <span className="inline-block size-2 rounded-full bg-success animate-pulse" />
              Your live inbox
            </div>
            <Badge variant="secondary" className="font-mono text-[10px]">
              {address?.provider ?? "tempmail"}
            </Badge>
          </div>

          <div className="group rounded-xl border border-border bg-surface/70 p-4 md:p-5 flex flex-col md:flex-row md:items-center gap-3">
            <Mail className="size-5 text-primary shrink-0" aria-hidden />
            <div className="font-mono text-lg md:text-2xl font-semibold tracking-tight break-all flex-1 select-all">
              {address?.address ?? (
                <span className="text-muted-foreground">generating…</span>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="soft"
                onClick={handleCopy}
                disabled={!address}
                aria-label="Copy address"
              >
                <Copy /> Copy
              </Button>
              <Button
                variant="hero"
                onClick={() => createMut.mutate({})}
                disabled={createMut.isPending}
                aria-label="Generate new address"
              >
                <Sparkles className={cn(createMut.isPending && "animate-spin")} />
                New
              </Button>
            </div>
          </div>
        </div>

        {/* Customize */}
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr_auto] gap-3 items-end">
          <div>
            <label className="text-xs font-medium text-muted-foreground" htmlFor="username">
              Custom username
            </label>
            <Input
              id="username"
              placeholder="e.g. signup-test"
              value={username}
              onChange={(e) => setUsername(e.target.value.replace(/[^a-z0-9._-]/gi, ""))}
              className="mt-1 font-mono"
            />
          </div>
          <div className="hidden md:flex pb-2 text-2xl text-muted-foreground">@</div>
          <div>
            <label className="text-xs font-medium text-muted-foreground" htmlFor="domain">
              Domain
            </label>
            <Select value={effectiveDomain} onValueChange={setDomain}>
              <SelectTrigger id="domain" className="mt-1 font-mono">
                <SelectValue placeholder={domainsQuery.isLoading ? "Loading…" : "Pick a domain"} />
              </SelectTrigger>
              <SelectContent>
                {domains.map((d) => (
                  <SelectItem key={d} value={d} className="font-mono">
                    {d}
                  </SelectItem>
                ))}
                {domains.length === 0 && (
                  <SelectItem value="__none" disabled>
                    No domains
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>
          <Button
            onClick={handleGenerate}
            disabled={createMut.isPending}
            className="md:mb-0"
            size="lg"
          >
            <Sparkles /> Generate
          </Button>
        </div>

        {/* Inbox */}
        <div className="pt-2 border-t border-border/70">
          <div className="flex items-center justify-between mt-5 mb-3">
            <div className="flex items-center gap-2">
              <InboxIcon className="size-5 text-primary" />
              <h2 className="text-lg font-semibold">Inbox</h2>
              {unreadCount > 0 && (
                <Badge className="bg-primary text-primary-foreground">{unreadCount} new</Badge>
              )}
              <span className="text-xs text-muted-foreground">
                · {messages.length} total
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => inboxQuery.refetch()}
              disabled={inboxQuery.isFetching}
              aria-label="Refresh inbox"
            >
              <RefreshCw className={cn(inboxQuery.isFetching && "animate-spin")} />
              Refresh
            </Button>
          </div>

          <Inbox
            messages={messages}
            loading={inboxQuery.isLoading}
            error={inboxQuery.error as Error | null}
            expandedId={expandedId}
            onExpand={handleExpand}
            onDelete={(id) => deleteMut.mutate(id)}
          />

          <p className="mt-4 text-xs text-muted-foreground flex items-center gap-1.5">
            <Clock className="size-3.5" /> Auto-refreshing every 5 seconds. Keep this tab open.
          </p>
        </div>
      </Card>
    </section>
  );
}

function Inbox({
  messages,
  loading,
  error,
  expandedId,
  onExpand,
  onDelete,
}: {
  messages: EmailMessage[];
  loading: boolean;
  error: Error | null;
  expandedId: string | null;
  onExpand: (m: EmailMessage) => void;
  onDelete: (id: string) => void;
}) {
  if (error) {
    return (
      <EmptyState
        icon={<Server className="size-7" />}
        title="Can't reach mail server"
        body={
          <>
            Make sure the API is running on{" "}
            <code className="font-mono text-foreground">http://localhost:8000</code>{" "}
            (or set <code className="font-mono text-foreground">VITE_API_BASE_URL</code>).
          </>
        }
      />
    );
  }

  if (loading && messages.length === 0) {
    return (
      <div className="space-y-2" aria-busy>
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-16 rounded-lg bg-muted/60 animate-pulse" />
        ))}
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <EmptyState
        icon={<InboxIcon className="size-7" />}
        title="Inbox is empty"
        body="Send something to your address — new mail appears here within seconds."
      />
    );
  }

  return (
    <ul className="divide-y divide-border/70 rounded-lg border border-border/60 overflow-hidden">
      {messages.map((m) => {
        const expanded = expandedId === m.id;
        return (
          <li key={m.id} className={cn("bg-card/40", !m.is_read && "bg-accent/30")}>
            <button
              type="button"
              onClick={() => onExpand(m)}
              className="w-full text-left px-4 py-3 flex items-start gap-3 hover:bg-accent/50 transition-colors"
              aria-expanded={expanded}
            >
              <span
                className={cn(
                  "mt-2 size-2 rounded-full shrink-0",
                  m.is_read ? "bg-transparent border border-muted-foreground/40" : "bg-primary",
                )}
                aria-label={m.is_read ? "read" : "unread"}
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between gap-3">
                  <p className={cn("truncate text-sm", !m.is_read ? "font-semibold" : "font-medium")}>
                    {m.from_name || m.from_address}
                  </p>
                  <span className="text-xs text-muted-foreground shrink-0">
                    {timeAgo(m.received_at)}
                  </span>
                </div>
                <p className={cn("truncate text-sm mt-0.5", !m.is_read ? "text-foreground" : "text-muted-foreground")}>
                  {m.subject || "(no subject)"}
                </p>
              </div>
              <ChevronDown
                className={cn(
                  "size-4 text-muted-foreground transition-transform shrink-0 mt-1",
                  expanded && "rotate-180",
                )}
              />
            </button>
            {expanded && (
              <div className="px-4 pb-4 -mt-1 space-y-3 bg-background/40">
                <div className="text-xs text-muted-foreground font-mono">
                  {m.from_address} · {new Date(m.received_at).toLocaleString()}
                </div>
                <MailBody html={m.body_html} text={m.body_text} />
                <div className="flex items-center justify-between pt-2">
                  {m.is_read ? (
                    <span className="text-xs text-success flex items-center gap-1">
                      <CheckCircle2 className="size-3.5" /> Read
                    </span>
                  ) : (
                    <span className="text-xs text-muted-foreground">Marked as read</span>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(m.id)}
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 /> Delete
                  </Button>
                </div>
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function MailBody({ html, text }: { html?: string; text?: string }) {
  const safeHtml = useMemo(() => {
    if (!html) return null;
    // very basic strip of scripts/iframes; backend should already be safe
    return html
      .replace(/<script[\s\S]*?<\/script>/gi, "")
      .replace(/<iframe[\s\S]*?<\/iframe>/gi, "")
      .replace(/ on[a-z]+="[^"]*"/gi, "");
  }, [html]);

  if (safeHtml) {
    return (
      <div
        className="prose prose-sm max-w-none rounded-md border border-border/60 bg-card p-4 [&_a]:text-primary [&_a]:underline-offset-2 break-words"
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: safeHtml }}
      />
    );
  }
  return (
    <pre className="whitespace-pre-wrap break-words text-sm rounded-md border border-border/60 bg-card p-4 font-sans">
      {text || "(empty body)"}
    </pre>
  );
}

function EmptyState({
  icon,
  title,
  body,
}: {
  icon: React.ReactNode;
  title: string;
  body: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-surface/40 px-6 py-10 text-center">
      <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-accent text-accent-foreground">
        {icon}
      </div>
      <h3 className="mt-4 font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground max-w-md mx-auto">{body}</p>
    </div>
  );
}

export const trustItems = [
  { icon: Lock, title: "Zero signup", body: "No account, no password, no tracking cookies." },
  { icon: Zap, title: "Realtime", body: "Inbox refreshes every 5 seconds automatically." },
  { icon: Eye, title: "Stay private", body: "Shield your real inbox from spam and leaks." },
  { icon: Shield, title: "Disposable by design", body: "Burn the address whenever you're done." },
];
