/**
 * CrazyMail 前端 API 客户端
 *
 * 统一封装后端 /api/v1/email 接口调用。
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ════════════════════════════════════════════
// 类型定义
// ════════════════════════════════════════════

export interface EmailResponse {
  address: string;
  username: string;
  domain: string;
  provider: string;
}

export interface MessageSummary {
  id: string;
  from_address: string;
  from_name: string;
  subject: string;
  received_at: string | null;
  is_read: boolean;
  has_attachments: boolean;
}

export interface MessageDetail {
  id: string;
  from_address: string;
  from_name: string;
  subject: string;
  body_text: string;
  body_html: string;
  received_at: string | null;
  is_read: boolean;
  has_attachments: boolean;
  attachments: Array<{
    filename: string;
    content_type: string;
    size: number;
    download_url: string;
  }>;
}

// ════════════════════════════════════════════
// 通用请求
// ════════════════════════════════════════════

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error ${res.status}`);
  }
  return res.json();
}

// ════════════════════════════════════════════
// 邮箱接口
// ════════════════════════════════════════════

export async function createEmail(
  username?: string,
  domain?: string,
): Promise<EmailResponse> {
  return request<EmailResponse>("/api/v1/email/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, domain }),
  });
}

export async function getDomains(): Promise<string[]> {
  const data = await request<{ domains: string[] }>("/api/v1/email/domains");
  return data.domains;
}

export async function getMessages(email: string): Promise<MessageSummary[]> {
  return request<MessageSummary[]>(
    `/api/v1/email/messages?email=${encodeURIComponent(email)}`,
  );
}

export async function getMessageDetail(
  messageId: string,
): Promise<MessageDetail> {
  return request<MessageDetail>(
    `/api/v1/email/messages/${encodeURIComponent(messageId)}`,
  );
}

export async function deleteMessage(
  _email: string,
  messageId: string,
): Promise<{ success: boolean; message: string }> {
  return request(`/api/v1/email/messages/${encodeURIComponent(messageId)}`, {
    method: "DELETE",
  });
}

export async function markAsRead(
  messageId: string,
): Promise<{ success: boolean; message: string }> {
  return request(
    `/api/v1/email/messages/${encodeURIComponent(messageId)}/read`,
    { method: "PATCH" },
  );
}
