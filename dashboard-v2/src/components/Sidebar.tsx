"use client";

import { useState } from "react";

interface SidebarProps {
  activePage: string;
  onPageChange: (page: string) => void;
}

const menuItems = [
  {
    id: "general",
    title: "通用项目设置",
    icon: "⚙️",
    items: [
      { id: "sites", label: "站点列表管理" },
      { id: "adsense", label: "AdSense 绑定" },
    ],
  },
  {
    id: "ai",
    title: "AI模型与API配置",
    icon: "🤖",
    items: [
      { id: "models", label: "模型切换" },
      { id: "api-keys", label: "API Key 管理" },
      { id: "tokens", label: "Token 监控" },
    ],
  },
  {
    id: "content",
    title: "内容生产配置",
    icon: "📝",
    items: [
      { id: "articles", label: "每日文章数量" },
      { id: "keywords", label: "关键词模式" },
      { id: "pipeline", label: "7阶段参数" },
    ],
  },
  {
    id: "growth",
    title: "增长黑客配置",
    icon: "📈",
    items: [
      { id: "clusters", label: "推广集群管理" },
      { id: "platforms", label: "平台白名单" },
      { id: "heroes", label: "108好汉身份池" },
    ],
  },
  {
    id: "monitor",
    title: "监控与风险",
    icon: "🛡️",
    items: [
      { id: "risk", label: "风控阈值" },
      { id: "pigeon", label: "飞鸽速度" },
      { id: "backup", label: "自动备份" },
    ],
  },
  {
    id: "system",
    title: "系统设置",
    icon: "🔧",
    items: [
      { id: "theme", label: "主题切换" },
      { id: "notifications", label: "通知方式" },
      { id: "export", label: "数据导出" },
    ],
  },
];

export function Sidebar({ activePage, onPageChange }: SidebarProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>("general");

  return (
    <aside className="w-64 border-r border-card-border bg-card-bg backdrop-blur-sm overflow-y-auto">
      {/* 标题 */}
      <div className="p-4 border-b border-card-border">
        <h2 className="text-lg font-bold text-imperial-gold">驿政司</h2>
        <p className="text-xs text-ash-gray">配置管理</p>
      </div>

      {/* 菜单项 */}
      <nav className="p-2">
        {menuItems.map((section) => (
          <div key={section.id} className="mb-2">
            {/* 章节标题 */}
            <button
              onClick={() => setExpandedSection(expandedSection === section.id ? null : section.id)}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-card-border transition-colors"
            >
              <span>{section.icon}</span>
              <span className="text-sm font-medium text-parchment">{section.title}</span>
              <span className="ml-auto text-ash-gray">
                {expandedSection === section.id ? "▼" : "▶"}
              </span>
            </button>

            {/* 子项 */}
            {expandedSection === section.id && (
              <div className="ml-6 mt-1 space-y-1">
                {section.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => onPageChange(item.id)}
                    className={`w-full text-left px-3 py-1.5 rounded text-sm transition-colors ${
                      activePage === item.id
                        ? "bg-imperial-gold/20 text-imperial-gold"
                        : "text-ash-gray hover:text-parchment hover:bg-card-border"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}
