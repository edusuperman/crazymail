import { useEffect, useRef, useState, useCallback } from "react";
import { Copy, RefreshCw, Shuffle, Trash2, MoreHorizontal, Mail, Inbox, Bookmark, Shield, Zap, Globe, Smartphone, Chrome, Sparkles, X, Check, Lock, Clock, Download, Languages } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator, DropdownMenuLabel, DropdownMenuRadioGroup, DropdownMenuRadioItem } from "@/components/ui/dropdown-menu";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { getDomains, createMailbox, getMessages, getMessage, deleteMessage, markRead, loadSavedMailbox, type TempMessage, type Mailbox } from "@/lib/tempmail-api";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { I18nProvider, useI18n, LANGS, type Lang } from "@/lib/i18n";

function timeAgo(iso: string) {
  const d = (Date.now() - new Date(iso).getTime()) / 1000;
  if (d < 60) return `${Math.max(1, Math.floor(d))}s`;
  if (d < 3600) return `${Math.floor(d / 60)}m`;
  if (d < 86400) return `${Math.floor(d / 3600)}h`;
  return new Date(iso).toLocaleDateString();
}

export function TempMailApp() {
  return (
    <I18nProvider>
      <AppInner />
    </I18nProvider>
  );
}

function AppInner() {
  const { t } = useI18n();
  const [mailbox, setMailbox] = useState<Mailbox | null>(null);
  const [domains, setDomains] = useState<string[]>([]);
  const [messages, setMessages] = useState<TempMessage[]>([]);
  const [openMessageId, setOpenMessageId] = useState<string | null>(null);
  const [openMessage, setOpenMessage] = useState<TempMessage | null>(null);
  const [changeOpen, setChangeOpen] = useState(false);
  const [tab, setTab] = useState<"inbox" | "saved">("inbox");
  const [saved, setSaved] = useState<Record<string, TempMessage>>({});
  const [refreshing, setRefreshing] = useState(false);
  const lastIdsRef = useRef<Set<string>>(new Set());
  const initRef = useRef(false);

  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    (async () => {
      const d = await getDomains();
      if (!d || d.length === 0) {
        toast.error("Failed to load domains. Please check your connection.");
      }
      setDomains(d);
      
      // 优先从 localStorage 加载保存的邮箱
      const saved = loadSavedMailbox();
      if (saved) {
        console.log("Using saved mailbox:", saved.address);
        setMailbox(saved);
      } else {
        // 没有保存的邮箱，创建新的
        const m = await createMailbox();
        if (!m) {
          toast.error("Failed to create mailbox. Please refresh the page.");
        }
        setMailbox(m);
      }
    })();
  }, []);

  const refresh = useCallback(async (silent = false) => {
    if (!silent) setRefreshing(true);
    try {
      const { messages: msgs } = await getMessages();
      const known = lastIdsRef.current;
      const fresh = msgs.filter((m) => !known.has(m.id));
      if (known.size > 0 && fresh.length > 0) {
        fresh.forEach((m) =>
          toast.success(t.inbox.newMail, {
            description: `${m.from_name ?? m.from_address} · ${m.subject}`,
          }),
        );
      }
      lastIdsRef.current = new Set(msgs.map((m) => m.id));
      setMessages(msgs);
    } catch (err) {
      console.error("Failed to refresh messages:", err);
      if (!silent) {
        toast.error("Failed to load messages. Please try again.");
      }
    }
    if (!silent) setTimeout(() => setRefreshing(false), 400);
  }, [t.inbox.newMail]);

  useEffect(() => {
    if (!mailbox) return;
    lastIdsRef.current = new Set();
    refresh(true);
    const id = setInterval(() => refresh(true), 5000);
    return () => clearInterval(id);
  }, [mailbox, refresh]);

  useEffect(() => {
    if (!openMessageId) { setOpenMessage(null); return; }
    (async () => {
      const m = await getMessage(openMessageId);
      if (m) {
        setOpenMessage(m);
        if (!m.is_read) {
          markRead(m.id);
          setMessages((prev) => prev.map((x) => (x.id === m.id ? { ...x, is_read: true } : x)));
        }
      }
    })();
  }, [openMessageId]);

  const copyAddress = () => {
    if (!mailbox) return;
    navigator.clipboard.writeText(mailbox.address);
    toast.success(t.inbox.copied, { description: mailbox.address });
  };
  const newRandom = async () => {
    const m = await createMailbox(undefined, undefined, true);
    setMailbox(m); setMessages([]);
    toast(t.inbox.newMailbox, { description: m.address });
  };
  const deleteCurrent = async () => { await newRandom(); };
  const onChange = async (username: string, domain: string) => {
    const m = await createMailbox(username || undefined, domain);
    setMailbox(m); setMessages([]); setChangeOpen(false);
    toast.success(t.inbox.switched, { description: m.address });
  };
  const onDeleteMsg = async (id: string) => {
    const success = await deleteMessage(id);
    if (success) {
      setMessages((prev) => prev.filter((x) => x.id !== id));
      if (openMessageId === id) setOpenMessageId(null);
      toast(t.inbox.deleted);
    } else {
      toast.error("删除失败：该服务不支持删除邮件，请等待邮件自动过期");
    }
  };
  const toggleSave = (m: TempMessage) => {
    setSaved((prev) => {
      const next = { ...prev };
      if (next[m.id]) { delete next[m.id]; toast(t.inbox.unsavedToast); }
      else { next[m.id] = m; toast.success(t.inbox.savedToast); }
      return next;
    });
  };

  const unread = messages.filter((m) => !m.is_read).length;

  // Loading state
  if (!mailbox) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="mt-4 text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <SiteHeader />

      <section className="relative">
        <div className="mx-auto max-w-6xl px-4 pt-10 pb-6 sm:pt-16 sm:pb-10">
          <div className="mb-8 flex flex-wrap items-center gap-3">
            <Badge className="bg-mint/15 text-primary border border-mint/30 hover:bg-mint/20">
              <span className="relative mr-2 inline-flex h-2 w-2">
                <span className="pulse-dot absolute inset-0 rounded-full bg-mint" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-mint" />
              </span>
              {t.hero.badgeLive}
            </Badge>
            <Badge variant="outline" className="border-border/70">
              <Lock className="mr-1 h-3 w-3" /> {t.hero.badgeSecure}
            </Badge>
            <Badge variant="outline" className="border-border/70">
              <Clock className="mr-1 h-3 w-3" /> {t.hero.badgeBurn}
            </Badge>
          </div>

          <h1 className="font-display text-4xl leading-[1.05] tracking-tight text-foreground sm:text-6xl">
            {t.hero.title1}<br className="hidden sm:block" />
            <span className="italic text-primary"> {t.hero.title2}</span>
          </h1>
          <p className="mt-4 max-w-2xl text-base text-muted-foreground sm:text-lg">
            {t.hero.subtitle}
          </p>

          <div className="grain mt-10 overflow-hidden rounded-2xl border border-border bg-card shadow-[0_30px_60px_-30px_rgb(0_0_0/0.25)]">
            <div className="border-b border-border bg-surface px-5 py-3 sm:px-7">
              <div className="flex items-center justify-between text-xs uppercase tracking-[0.18em] text-muted-foreground">
                <span className="flex items-center gap-2">
                  <Mail className="h-3.5 w-3.5" /> {t.hero.yourMailbox}
                </span>
                <span className="hidden sm:inline">{t.hero.provider} · {mailbox?.provider ?? "—"}</span>
              </div>
            </div>

            <div className="px-5 py-7 sm:px-9 sm:py-10">
              <button
                onClick={copyAddress}
                className="group w-full text-left font-mono text-2xl font-medium tracking-tight text-foreground transition hover:text-primary sm:text-4xl break-all"
                aria-label={t.actions.copyAddress}
              >
                {mailbox?.address ?? t.hero.generating}
                <span className="ml-3 inline-flex translate-y-[-2px] items-center text-xs uppercase tracking-widest text-muted-foreground opacity-0 transition group-hover:opacity-100">
                  {t.hero.clickToCopy}
                </span>
              </button>

              <div className="mt-6 flex flex-wrap items-center gap-2">
                <ActionButton icon={<Copy className="h-4 w-4" />} label={t.actions.copy} onClick={copyAddress} />
                <ActionButton icon={<Shuffle className="h-4 w-4" />} label={t.actions.random} onClick={newRandom} />
                <ActionButton icon={<RefreshCw className="h-4 w-4" />} label={t.actions.change} onClick={() => setChangeOpen(true)} />
                <ActionButton icon={<Trash2 className="h-4 w-4" />} label={t.actions.delete} onClick={deleteCurrent} variant="destructive" />
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" className="gap-2 rounded-full border-border/70 bg-background/60 px-4 hover:bg-surface">
                      <MoreHorizontal className="h-4 w-4" /> {t.actions.more}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-52">
                    <DropdownMenuItem onClick={() => refresh()}>
                      <RefreshCw className="mr-2 h-4 w-4" /> {t.actions.refreshNow}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={copyAddress}>
                      <Copy className="mr-2 h-4 w-4" /> {t.actions.copyAddress}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => toast(t.premium.comingSoon)}>
                      <Sparkles className="mr-2 h-4 w-4" /> {t.actions.upgradePremium}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            <div className="border-t border-border bg-surface/50">
              <Tabs value={tab} onValueChange={(v) => setTab(v as "inbox" | "saved")}>
                <div className="flex items-center justify-between gap-3 px-5 pt-4 sm:px-7">
                  <TabsList className="bg-background/60">
                    <TabsTrigger value="inbox" className="gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                      <Inbox className="h-4 w-4" /> {t.inbox.messages}
                      {unread > 0 && (
                        <span className="ml-1 rounded-full bg-amber px-1.5 text-[10px] font-semibold text-primary">{unread}</span>
                      )}
                    </TabsTrigger>
                    <TabsTrigger value="saved" className="gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                      <Bookmark className="h-4 w-4" /> {t.inbox.saved} · {Object.keys(saved).length}
                    </TabsTrigger>
                  </TabsList>
                  <Button variant="ghost" size="sm" onClick={() => refresh()} className="gap-2 text-muted-foreground hover:text-foreground">
                    <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
                    {t.inbox.refresh}
                  </Button>
                </div>

                <TabsContent value="inbox" className="m-0">
                  <MessageList
                    messages={messages}
                    emptyHint={t.inbox.emptyInbox}
                    onOpen={(id) => setOpenMessageId(id)}
                    onDelete={onDeleteMsg}
                    onSave={toggleSave}
                    savedIds={saved}
                  />
                </TabsContent>
                <TabsContent value="saved" className="m-0">
                  <MessageList
                    messages={Object.values(saved)}
                    emptyHint={t.inbox.emptySaved}
                    onOpen={(id) => setOpenMessageId(id)}
                    onDelete={(id) => toggleSave({ id } as TempMessage)}
                    onSave={toggleSave}
                    savedIds={saved}
                  />
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </div>
      </section>

      <FeatureStrip />
      <WhatIsSection />
      <AppsSection />
      <FaqSection />
      <PremiumCta />
      <SiteFooter />

      <ChangeDialog open={changeOpen} onOpenChange={setChangeOpen} domains={domains} current={mailbox} onConfirm={onChange} />

      <Dialog open={!!openMessageId} onOpenChange={(o) => !o && setOpenMessageId(null)}>
        <DialogContent className="max-w-2xl">
          {openMessage ? (
            <>
              <DialogHeader>
                <DialogTitle className="font-display text-2xl leading-tight">{openMessage.subject}</DialogTitle>
                <DialogDescription className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-1">
                  <span className="font-medium text-foreground">{openMessage.from_name ?? openMessage.from_address}</span>
                  <span className="font-mono text-xs">&lt;{openMessage.from_address}&gt;</span>
                  <span className="text-xs">· {new Date(openMessage.received_at).toLocaleString()}</span>
                </DialogDescription>
              </DialogHeader>
              <div className="max-h-[55vh] overflow-y-auto rounded-lg border border-border bg-surface p-4 text-sm leading-relaxed">
                {openMessage.body_html ? (
                  <div dangerouslySetInnerHTML={{ __html: openMessage.body_html }} />
                ) : (
                  <pre className="whitespace-pre-wrap font-sans">{openMessage.body_text}</pre>
                )}
              </div>
              <DialogFooter className="gap-2 sm:gap-2">
                <Button variant="outline" onClick={() => toggleSave(openMessage)}>
                  <Bookmark className={cn("mr-2 h-4 w-4", saved[openMessage.id] && "fill-current")} />
                  {saved[openMessage.id] ? t.inbox.unbookmark : t.inbox.bookmark}
                </Button>
                <Button variant="destructive" onClick={() => onDeleteMsg(openMessage.id)}>
                  <Trash2 className="mr-2 h-4 w-4" /> {t.inbox.deleteMail}
                </Button>
              </DialogFooter>
            </>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function ActionButton({ icon, label, onClick, variant = "default" }: { icon: React.ReactNode; label: string; onClick: () => void; variant?: "default" | "destructive" }) {
  return (
    <Button
      onClick={onClick}
      className={cn(
        "h-10 gap-2 rounded-full px-4 text-sm font-medium",
        variant === "default" && "bg-primary text-primary-foreground hover:bg-primary/90",
        variant === "destructive" && "bg-destructive/10 text-destructive hover:bg-destructive/20",
      )}
    >
      {icon} {label}
    </Button>
  );
}

function MessageList({
  messages, emptyHint, onOpen, onDelete, onSave, savedIds,
}: {
  messages: TempMessage[]; emptyHint: string;
  onOpen: (id: string) => void; onDelete: (id: string) => void;
  onSave: (m: TempMessage) => void; savedIds: Record<string, TempMessage>;
}) {
  if (messages.length === 0) {
    return (
      <div className="px-7 py-16 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-surface-muted text-muted-foreground">
          <Inbox className="h-6 w-6" />
        </div>
        <p className="mx-auto mt-4 max-w-md text-sm text-muted-foreground">{emptyHint}</p>
      </div>
    );
  }
  return (
    <ul className="divide-y divide-border">
      {messages.map((m) => (
        <li
          key={m.id}
          className={cn(
            "group flex cursor-pointer items-center gap-4 px-5 py-4 transition hover:bg-surface sm:px-7",
            !m.is_read && "bg-amber/[0.06]",
          )}
          onClick={() => onOpen(m.id)}
        >
          <div className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-full font-display text-sm font-semibold",
            !m.is_read ? "bg-primary text-primary-foreground" : "bg-surface-muted text-muted-foreground",
          )}>
            {(m.from_name ?? m.from_address)[0]?.toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className={cn("truncate text-sm", !m.is_read ? "font-semibold text-foreground" : "text-foreground")}>
                {m.from_name ?? m.from_address}
              </span>
              {!m.is_read && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-amber" />}
            </div>
            <p className="mt-0.5 truncate text-sm text-muted-foreground">{m.subject}</p>
          </div>
          <div className="hidden shrink-0 text-xs text-muted-foreground sm:block">{timeAgo(m.received_at)}</div>
          <div className="flex shrink-0 items-center gap-1 opacity-0 transition group-hover:opacity-100">
            <Button size="icon" variant="ghost" className="h-8 w-8" onClick={(e) => { e.stopPropagation(); onSave(m); }}>
              <Bookmark className={cn("h-4 w-4", savedIds[m.id] && "fill-current text-primary")} />
            </Button>
            <Button size="icon" variant="ghost" className="h-8 w-8 text-destructive hover:text-destructive" onClick={(e) => { e.stopPropagation(); onDelete(m.id); }}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </li>
      ))}
    </ul>
  );
}

function ChangeDialog({ open, onOpenChange, domains, current, onConfirm }: {
  open: boolean; onOpenChange: (b: boolean) => void;
  domains: string[]; current: Mailbox | null;
  onConfirm: (username: string, domain: string) => void;
}) {
  const { t } = useI18n();
  const [username, setUsername] = useState("");
  const [domain, setDomain] = useState("");
  useEffect(() => {
    if (open && current) { setUsername(current.username); setDomain(current.domain); }
  }, [open, current]);
  const randomize = () => {
    const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
    setUsername(Array.from({ length: 8 }, () => chars[Math.floor(Math.random() * chars.length)]).join(""));
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="font-display text-2xl">{t.change.title}</DialogTitle>
          <DialogDescription>{t.change.desc}</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div>
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-muted-foreground">{t.change.domain}</label>
            <Select value={domain} onValueChange={setDomain}>
              <SelectTrigger className="h-11"><SelectValue placeholder={t.change.selectDomain} /></SelectTrigger>
              <SelectContent>
                {domains.map((d) => <SelectItem key={d} value={d}>@{d}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-muted-foreground">{t.change.username}</label>
            <div className="flex gap-2">
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9._-]/g, ""))}
                placeholder={t.change.placeholder}
                className="h-11 font-mono"
              />
              <Button type="button" variant="outline" className="h-11 shrink-0 gap-2" onClick={randomize}>
                <Shuffle className="h-4 w-4" /> {t.change.randomize}
              </Button>
            </div>
          </div>
          <div className="flex items-start gap-3 rounded-lg border border-amber/40 bg-amber/10 px-3 py-2.5 text-sm text-foreground">
            <Clock className="mt-0.5 h-4 w-4 shrink-0 text-amber" />
            <span>{t.change.warning1} <strong>{t.change.warning2}</strong></span>
          </div>
        </div>
        <DialogFooter className="gap-2 sm:gap-2">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>{t.change.cancel}</Button>
          <Button onClick={() => onConfirm(username, domain)} disabled={!domain} className="gap-2">
            <Check className="h-4 w-4" /> {t.change.confirm}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function LanguageSwitcher() {
  const { lang, setLang } = useI18n();
  const current = LANGS.find((l) => l.code === lang)!;
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2 border-border/70">
          <Languages className="h-4 w-4" />
          <span className="font-mono text-xs tracking-wider">{current.flag}</span>
          <span className="hidden sm:inline">{current.label}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-44">
        <DropdownMenuLabel className="text-xs uppercase tracking-widest text-muted-foreground">Language</DropdownMenuLabel>
        <DropdownMenuRadioGroup value={lang} onValueChange={(v) => setLang(v as Lang)}>
          {LANGS.map((l) => (
            <DropdownMenuRadioItem key={l.code} value={l.code} className="gap-2">
              <span className="font-mono text-[10px] tracking-wider text-muted-foreground">{l.flag}</span>
              <span>{l.label}</span>
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function SiteHeader() {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5">
        <a href="/" className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
            <Mail className="h-4 w-4" />
          </div>
          <div className="leading-tight">
            <div className="font-display text-base font-semibold tracking-tight">TempMail<span className="text-primary">.</span>Pro</div>
            <div className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">disposable inbox</div>
          </div>
        </a>
        <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
          <a href="#what" className="hover:text-foreground">{t.nav.about}</a>
          <a href="#apps" className="hover:text-foreground">{t.nav.apps}</a>
          <a href="#faq" className="hover:text-foreground">{t.nav.faq}</a>
          <a href="#premium" className="hover:text-foreground">{t.nav.premium}</a>
        </nav>
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <Button variant="outline" size="sm" className="hidden gap-2 sm:inline-flex">
            <Sparkles className="h-4 w-4 text-amber" /> {t.nav.upgrade}
          </Button>
        </div>
      </div>
    </header>
  );
}

function FeatureStrip() {
  const { t } = useI18n();
  const items = [
    { icon: Zap, t: t.features.fast, d: t.features.fastD },
    { icon: Shield, t: t.features.private, d: t.features.privateD },
    { icon: Globe, t: t.features.multi, d: t.features.multiD },
    { icon: Clock, t: t.features.burn, d: t.features.burnD },
  ];
  return (
    <section className="border-y border-border/60 bg-surface/60">
      <div className="mx-auto grid max-w-6xl grid-cols-2 gap-px bg-border/60 sm:grid-cols-4">
        {items.map((it) => (
          <div key={it.t} className="bg-surface/60 px-5 py-6">
            <it.icon className="h-5 w-5 text-primary" />
            <div className="mt-3 font-display text-lg">{it.t}</div>
            <p className="mt-1 text-sm text-muted-foreground">{it.d}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function WhatIsSection() {
  const { t } = useI18n();
  return (
    <section id="what" className="mx-auto max-w-6xl px-4 py-20">
      <div className="grid gap-12 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">{t.whatis.kicker}</div>
          <h2 className="mt-3 font-display text-4xl leading-tight tracking-tight">
            {t.whatis.title1}<br /><span className="italic">{t.whatis.title2}</span>
          </h2>
        </div>
        <div className="space-y-5 text-base leading-relaxed text-foreground">
          <p>{t.whatis.p1}</p>
          <p className="text-muted-foreground">{t.whatis.p2}</p>
          <div className="flex flex-wrap gap-2 pt-2">
            {["temp mail", "disposable email", "burner mail", "anonymous inbox", "10-minute mail"].map((k) => (
              <span key={k} className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted-foreground">{k}</span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function AppsSection() {
  const { t } = useI18n();
  const apps = [
    { name: "iOS App · Coming Soon", sub: "", icon: Smartphone },
    { name: "Android · Coming Soon", sub: "", icon: Smartphone },
    { name: "Chrome · Coming Soon", sub: "", icon: Chrome },
    { name: "Firefox · Coming Soon", sub: "", icon: Globe },
    { name: "Edge · Coming Soon", sub: "", icon: Globe },
    { name: "CLI · Coming Soon", sub: "", icon: Download },
  ];
  return (
    <section id="apps" className="border-t border-border/60 bg-surface/40">
      <div className="mx-auto max-w-6xl px-4 py-20">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">{t.apps.kicker}</div>
            <h2 className="mt-3 font-display text-4xl tracking-tight">{t.apps.title}</h2>
          </div>
          <p className="max-w-md text-sm text-muted-foreground">{t.apps.desc}</p>
        </div>
        <div className="mt-10 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-border bg-border/70 sm:grid-cols-3 lg:grid-cols-6">
          {apps.map((a) => (
            <a key={a.name} href="/coming-soon" className="group bg-card p-6 transition hover:bg-surface">
              <a.icon className="h-6 w-6 text-primary transition group-hover:scale-110" />
              <div className="mt-4 font-display text-base">{a.name}</div>
              {a.sub && <div className="text-xs text-muted-foreground">{a.sub}</div>}
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

function FaqSection() {
  const { t } = useI18n();
  return (
    <section id="faq" className="mx-auto max-w-6xl px-4 py-20">
      <div className="grid gap-12 lg:grid-cols-[1fr_1.4fr]">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">{t.faq.kicker}</div>
          <h2 className="mt-3 font-display text-4xl leading-tight tracking-tight">
            {t.faq.title1}<br /><span className="italic">{t.faq.title2}</span>
          </h2>
          <p className="mt-4 text-sm text-muted-foreground">
            {t.faq.contact} <a href="mailto:hello@tempmail.pro" className="underline">hello@tempmail.pro</a>.
          </p>
        </div>
        <Accordion type="single" collapsible className="w-full">
          {t.faq.items.map(([q, a], i) => (
            <AccordionItem key={i} value={`item-${i}`} className="border-border">
              <AccordionTrigger className="text-left font-display text-lg hover:no-underline">{q}</AccordionTrigger>
              <AccordionContent className="text-base leading-relaxed text-muted-foreground">{a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}

function PremiumCta() {
  const { t } = useI18n();
  return (
    <section id="premium" className="border-y border-border/60 bg-primary text-primary-foreground">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-20 lg:grid-cols-[1.4fr_1fr] lg:items-end">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-amber">{t.premium.kicker}</div>
          <h2 className="mt-3 font-display text-4xl leading-tight tracking-tight sm:text-5xl">
            {t.premium.title1}<br /><span className="italic text-amber">{t.premium.title2}</span>
          </h2>
          <p className="mt-5 max-w-xl text-base leading-relaxed text-primary-foreground/80">{t.premium.desc}</p>
        </div>
        <div className="space-y-3">
          {t.premium.bullets.map((b) => (
            <div key={b} className="flex items-start gap-3 text-sm">
              <Check className="mt-0.5 h-4 w-4 shrink-0 text-amber" /> {b}
            </div>
          ))}
          <div className="flex flex-wrap gap-3 pt-4">
            <Button className="bg-amber text-primary hover:bg-amber/90">{t.premium.cta1}</Button>
            <Button variant="outline" className="border-primary-foreground/30 bg-transparent text-primary-foreground hover:bg-primary-foreground/10">{t.premium.cta2}</Button>
          </div>
        </div>
      </div>
    </section>
  );
}

function SiteFooter() {
  const { t } = useI18n();
  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-14 sm:grid-cols-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
              <Mail className="h-4 w-4" />
            </div>
            <div className="font-display text-base font-semibold tracking-tight">TempMail.Pro</div>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">{t.footer.tagline}</p>
        </div>
        {t.footer.cols.map((c) => (
          <div key={c.t}>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-foreground">{c.t}</div>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              {c.l.map((it) => {
                const isExtension = /extension|erweiterung|拡張|扩展|확장/i.test(it);
                return <li key={it}><a href={isExtension ? "/coming-soon" : "#"} className="hover:text-foreground">{it}</a></li>;
              })}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-border/60">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-5 text-xs text-muted-foreground">
          <div>{t.footer.copyright}</div>
          <div className="font-mono">{t.footer.tagline2}</div>
        </div>
      </div>
    </footer>
  );
}
