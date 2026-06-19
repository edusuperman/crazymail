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

type TranslationValue = string | string[] | [string, string][];
type Translations = Record<string, Record<string, TranslationValue>>;

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
    "footer.tagline": "Free disposable email for privacy protection.",
    "footer.tagline2": "Built with ♥ for privacy",
    "footer.copyright": "© 2026 TempMails.top. All rights reserved.",
    "footer.cols": [
      { t: "Product", l: ["Features", "How it Works", "Pricing", "Browser Extensions"] },
      { t: "Legal", l: ["Privacy Policy", "Terms of Service", "Cookie Policy"] },
      { t: "Support", l: ["FAQ", "Contact Us", "Status Page"] },
    ],
    "faq.title": "Frequently Asked Questions",
    "faq.kicker": "FAQ",
    "faq.title1": "Got questions?",
    "faq.title2": "We've got answers.",
    "faq.contact": "Can't find what you're looking for? Contact us at",
    "faq.items": [
      ["What is a temporary email?", "A temporary email (also called a disposable email or temp mail) is a short-lived email address that you can use to sign up for services, download content, or verify accounts without exposing your real email address. It helps protect your privacy and keeps your primary inbox free from spam."],
      ["How long does a temporary email last?", "Our temporary emails are valid for 10 minutes by default. After that, the email address and all associated messages are permanently deleted. You can always generate a new temporary email address whenever you need one."],
      ["Is temporary email really free?", "Yes! TempMails.top is 100% free to use. There are no hidden fees, no premium tiers, and no credit card required. You can create and use as many temporary email addresses as you need."],
      ["Can I send emails with a temporary address?", "No, temporary emails are receive-only. This design choice helps prevent abuse and keeps the service free for everyone. If you need to send emails, we recommend using a traditional email service."],
      ["Is my privacy protected?", "Absolutely. We don't require any personal information to use our service. We don't track your IP address, don't use cookies for tracking, and all emails are automatically deleted after expiration. Your privacy is our top priority."],
      ["Can I use temporary email for account verification?", "Yes! Many users use temporary emails to verify accounts on websites, apps, and services. However, some services may block known temporary email domains. If you encounter this, simply generate a new email address."],
    ],
    "what.title": "What is Temporary Email?",
    "what.desc": "A disposable email address that protects your privacy.",
    "apps.title": "Mobile Apps",
    "apps.coming": "Coming Soon",
    "features.instant": "Instant Setup",
    "features.privacy": "Privacy Protected",
    "features.free": "100% Free",
    "features.fast": "Lightning Fast",
    "premium.kicker": "PREMIUM",
    "premium.title1": "Unlock more power",
    "premium.title2": "with Premium",
    "premium.desc": "Get access to extended email retention, custom domains, and priority support.",
    "premium.bullets": ["24-hour email retention", "Custom domain support", "Priority support", "No ads"],
    "premium.cta1": "Get Premium",
    "premium.cta2": "Learn more",
    "nav.home": "Home",
    "nav.features": "Features",
    "nav.faq": "FAQ",
    "nav.premium": "Premium",
    "inbox.newMail": "New mail received",
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
    "footer.tagline": "免费一次性邮箱，保护您的隐私。",
    "footer.tagline2": "用 ♥ 为隐私而建",
    "footer.copyright": "© 2026 TempMails.top. 保留所有权利。",
    "footer.cols": [
      { t: "产品", l: ["功能", "工作原理", "定价", "浏览器扩展"] },
      { t: "法律", l: ["隐私政策", "服务条款", "Cookie 政策"] },
      { t: "支持", l: ["常见问题", "联系我们", "状态页面"] },
    ],
    "faq.title": "常见问题",
    "faq.kicker": "常见问题",
    "faq.title1": "有问题？",
    "faq.title2": "我们有答案。",
    "faq.contact": "找不到您要找的内容？请联系我们",
    "faq.items": [
      ["什么是临时邮箱？", "临时邮箱（也称为一次性邮箱或临时邮件）是一个短期有效的电子邮件地址，您可以使用它来注册服务、下载内容或验证账户，而无需暴露您的真实电子邮件地址。它有助于保护您的隐私，并保持您的主收件箱免受垃圾邮件的困扰。"],
      ["临时邮箱能用多久？", "我们的临时邮箱默认有效期为 10 分钟。之后，该电子邮件地址和所有关联的消息将被永久删除。您可以随时生成新的临时邮箱地址。"],
      ["临时邮箱真的免费吗？", "是的！TempMails.top 完全免费使用。没有隐藏费用，没有高级套餐，无需信用卡。您可以根据需要创建和使用任意数量的临时邮箱地址。"],
      ["我可以用临时邮箱发送邮件吗？", "不可以，临时邮箱只能接收邮件。这个设计选择有助于防止滥用，并保持服务对所有人免费。如果您需要发送邮件，我们建议使用传统的电子邮件服务。"],
      ["我的隐私受到保护吗？", "绝对受到保护。我们不需要任何个人信息即可使用我们的服务。我们不跟踪您的 IP 地址，不使用跟踪 Cookie，所有邮件在到期后自动删除。您的隐私是我们的首要任务。"],
      ["我可以用临时邮箱进行账户验证吗？", "可以！许多用户使用临时邮箱来验证网站、应用程序和服务上的账户。但是，某些服务可能会阻止已知的临时邮箱域名。如果您遇到这种情况，只需生成一个新的邮箱地址即可。"],
    ],
    "what.title": "什么是临时邮箱？",
    "what.desc": "保护您隐私的一次性邮箱地址。",
    "apps.title": "手机应用",
    "apps.coming": "即将推出",
    "features.instant": "即时创建",
    "features.privacy": "隐私保护",
    "features.free": "完全免费",
    "features.fast": "极速体验",
    "premium.kicker": "高级版",
    "premium.title1": "解锁更多功能",
    "premium.title2": "升级高级版",
    "premium.desc": "获取延长的邮箱保留时间、自定义域名和优先支持。",
    "premium.bullets": ["24 小时邮箱保留", "自定义域名支持", "优先支持", "无广告"],
    "premium.cta1": "获取高级版",
    "premium.cta2": "了解更多",
    "nav.home": "首页",
    "nav.features": "功能",
    "nav.faq": "常见问题",
    "nav.premium": "高级版",
    "inbox.newMail": "收到新邮件",
  },
};

function getTranslation(lang: Lang, key: string): TranslationValue {
  return translations[lang]?.[key] ?? translations.en[key] ?? key;
}

interface I18nContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: Record<string, Record<string, TranslationValue>>;
}

const I18nContext = createContext<I18nContextValue>({
  lang: "en",
  setLang: () => {},
  t: translations.en as unknown as Record<string, Record<string, TranslationValue>>,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");

  const t = new Proxy({} as Record<string, Record<string, TranslationValue>>, {
    get(_, section: string) {
      return new Proxy({} as Record<string, TranslationValue>, {
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
