// Temp-mail API client. Connects to the real backend at localhost:8000.

export type TempMessage = {
  id: string;
  from_address: string;
  from_name?: string;
  subject: string;
  body_text?: string;
  body_html?: string;
  received_at: string;
  is_read: boolean;
  has_attachments?: boolean;
};

export type Mailbox = {
  address: string;
  username: string;
  domain: string;
  provider?: string;
};

const BASE = (typeof window !== "undefined" && (window as any).__TEMPMAIL_API__) || import.meta.env.VITE_API_BASE || "";

const DEFAULT_DOMAINS = [
  "bltiwd.com",
  "wnbaldwy.com",
  "bwmyga.com",
  "ozsaip.com",
  "yzcalo.com",
  "lnovic.com",
  "ruutukf.com",
  "gmeenramy.com",
];

async function tryFetch<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 10000);
    const res = await fetch(`${BASE}${path}`, { ...init, signal: ctrl.signal });
    clearTimeout(t);
    if (!res.ok) {
      console.error(`API error: ${res.status} ${res.statusText}`);
      return null;
    }
    return (await res.json()) as T;
  } catch (err) {
    console.error(`API fetch failed:`, err);
    return null;
  }
}

// ---------- public API ----------
export async function getDomains(): Promise<string[]> {
  const r = await tryFetch<{ domains: string[] }>("/api/v1/email/domains");
  if (r?.domains) {
    return r.domains;
  }
  return [];
}

export function loadSavedMailbox(): Mailbox | null {
  if (typeof window === "undefined") return null;
  const address = localStorage.getItem("tempmail_address");
  const username = localStorage.getItem("tempmail_username");
  const domain = localStorage.getItem("tempmail_domain");
  if (address && username && domain) {
    return { address, username, domain, provider: "tempmailio" };
  }
  return null;
}

export async function getCurrentMailbox(): Promise<Mailbox | null> {
  return await tryFetch<Mailbox>("/api/v1/email/current");
}

export async function createMailbox(username?: string, domain?: string, forceNew?: boolean): Promise<Mailbox> {
  // 优先复用后端已有邮箱（避免每次刷新都创建新邮箱）
  // 但 forceNew=true 时跳过复用（用于 Random 按钮）
  if (!username && !domain && !forceNew) {
    const existing = await getCurrentMailbox();
    if (existing) {
      console.log("复用后端已有邮箱:", existing.address);
      if (typeof window !== "undefined") {
        localStorage.setItem("tempmail_address", existing.address);
        localStorage.setItem("tempmail_username", existing.username);
        localStorage.setItem("tempmail_domain", existing.domain);
      }
      return existing;
    }
  }
  const r = await tryFetch<Mailbox>("/api/v1/email/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, domain }),
  });
  if (!r) {
    throw new Error("Failed to create mailbox: backend unavailable");
  }
  if (typeof window !== "undefined") {
    localStorage.setItem("tempmail_address", r.address);
    localStorage.setItem("tempmail_username", r.username);
    localStorage.setItem("tempmail_domain", r.domain);
  }
  return r;
}

export async function getMessages(): Promise<{ email: string; messages: TempMessage[]; total: number }> {
  const savedAddress = typeof window !== "undefined" ? localStorage.getItem("tempmail_address") : null;
  const emailParam = savedAddress ? `?email=${encodeURIComponent(savedAddress)}` : "";

  const r = await tryFetch<{ email: string; messages: TempMessage[]; total: number }>(`/api/v1/email/messages${emailParam}`);
  if (r) {
    return r;
  }
  return { email: "", messages: [], total: 0 };
}

export async function getMessage(id: string): Promise<TempMessage | null> {
  return await tryFetch<TempMessage>(`/api/v1/email/messages/${id}`);
}

export async function deleteMessage(id: string): Promise<boolean> {
  const r = await tryFetch<{ success: boolean }>(`/api/v1/email/messages/${id}`, { method: "DELETE" });
  if (r) return !!r.success;
  return false;
}

export async function markRead(id: string): Promise<void> {
  await tryFetch(`/api/v1/email/messages/${id}/read`, { method: "PATCH" });
}

export { DEFAULT_DOMAINS };
