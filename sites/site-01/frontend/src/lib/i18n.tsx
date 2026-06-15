import { createContext, useContext, useState, type ReactNode } from "react";

export interface LangDef {
  code: string;
  label: string;
  flag: string;
}

export const LANGS: LangDef[] = [
  { code: "en", label: "English", flag: "🇺🇸" },
  { code: "zh", label: "中文", flag: "🇨🇳" },
  { code: "ja", label: "日本語", flag: "🇯🇵" },
  { code: "ko", label: "한국어", flag: "🇰🇷" },
  { code: "es", label: "Español", flag: "🇪🇸" },
  { code: "fr", label: "Français", flag: "🇫🇷" },
  { code: "de", label: "Deutsch", flag: "🇩🇪" },
];

export type Lang = (typeof LANGS)[number]["code"];

type Translations = Record<string, Record<string, string>>;

const translations: Translations = {
  en: {
    "inbox.title": "Inbox",
    "inbox.newMailbox": "New mailbox created",
    "inbox.deleted": "Message deleted",
    "inbox.unsavedToast": "Removed from saved",
    "inbox.empty": "No messages yet",
    "inbox.refresh": "Refresh",
    "inbox.random": "Random",
    "inbox.copy": "Copy",
    "inbox.delete": "Delete",
    "premium.comingSoon": "Coming soon!",
    "header.title": "TempMails.top",
    "header.subtitle": "Free Temporary Email",
    "footer.privacy": "Privacy Policy",
    "footer.terms": "Terms of Service",
    "footer.about": "About",
    "faq.title": "Frequently Asked Questions",
    "what.title": "What is Temporary Email?",
    "what.desc": "A disposable email address that protects your privacy.",
    "apps.title": "Mobile Apps",
    "apps.coming": "Coming Soon",
    "features.instant": "Instant Setup",
    "features.privacy": "Privacy Protected",
    "features.free": "100% Free",
    "features.fast": "Lightning Fast",
  },
  zh: {
    "inbox.title": "收件箱",
    "inbox.newMailbox": "新邮箱已创建",
    "inbox.deleted": "邮件已删除",
    "inbox.unsavedToast": "已取消收藏",
    "inbox.empty": "暂无邮件",
    "inbox.refresh": "刷新",
    "inbox.random": "随机",
    "inbox.copy": "复制",
    "inbox.delete": "删除",
    "premium.comingSoon": "即将推出！",
    "header.title": "TempMails.top",
    "header.subtitle": "免费临时邮箱",
    "footer.privacy": "隐私政策",
    "footer.terms": "服务条款",
    "footer.about": "关于我们",
    "faq.title": "常见问题",
    "what.title": "什么是临时邮箱？",
    "what.desc": "保护您隐私的一次性邮箱地址。",
    "apps.title": "手机应用",
    "apps.coming": "即将推出",
    "features.instant": "即时创建",
    "features.privacy": "隐私保护",
    "features.free": "完全免费",
    "features.fast": "极速体验",
  },
};

function getTranslation(lang: Lang, key: string): string {
  return translations[lang]?.[key] || translations.en[key] || key;
}

interface I18nContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: Record<string, Record<string, string>>;
}

const I18nContext = createContext<I18nContextValue>({
  lang: "en",
  setLang: () => {},
  t: translations.en,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");

  const t = new Proxy({} as Record<string, Record<string, string>>, {
    get(_, section: string) {
      return new Proxy({} as Record<string, string>, {
        get(_, key: string) {
          return getTranslation(lang, `${section}.${key}`);
        },
      });
    },
  });

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
