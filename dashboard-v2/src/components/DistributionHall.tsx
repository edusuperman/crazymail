"use client";

import { useState } from "react";
import { CarrierPigeon } from "./CarrierPigeon";

// 32个平台
const platforms = [
  // 社媒
  { id: "facebook", name: "Facebook", icon: "📘", category: "社媒" },
  { id: "instagram", name: "Instagram", icon: "📸", category: "社媒" },
  { id: "twitter", name: "X/Twitter", icon: "🐦", category: "社媒" },
  { id: "tiktok", name: "TikTok", icon: "🎵", category: "社媒" },
  { id: "youtube", name: "YouTube", icon: "📺", category: "社媒" },
  { id: "reddit", name: "Reddit", icon: "🤖", category: "社媒" },
  { id: "linkedin", name: "LinkedIn", icon: "💼", category: "社媒" },
  { id: "pinterest", name: "Pinterest", icon: "📌", category: "社媒" },
  // 短视频
  { id: "kuaishou", name: "快手", icon: "🎬", category: "短视频" },
  { id: "douyin", name: "抖音国际版", icon: "🎤", category: "短视频" },
  { id: "snapchat", name: "Snapchat", icon: "👻", category: "短视频" },
  { id: "threads", name: "Threads", icon: "🧵", category: "短视频" },
  // 新闻/博客
  { id: "medium", name: "Medium", icon: "📝", category: "新闻/博客" },
  { id: "substack", name: "Substack", icon: "📰", category: "新闻/博客" },
  { id: "wordpress", name: "WordPress", icon: "📰", category: "新闻/博客" },
  { id: "blogger", name: "Blogger", icon: "📰", category: "新闻/博客" },
  { id: "hackernews", name: "Hacker News", icon: "📰", category: "新闻/博客" },
  { id: "producthunt", name: "Product Hunt", icon: "📰", category: "新闻/博客" },
  // 技术论坛
  { id: "stackoverflow", name: "Stack Overflow", icon: "💻", category: "技术论坛" },
  { id: "github", name: "GitHub", icon: "🐙", category: "技术论坛" },
  { id: "devto", name: "Dev.to", icon: "💻", category: "技术论坛" },
  { id: "v2ex", name: "V2EX", icon: "💻", category: "技术论坛" },
  { id: "csdn", name: "CSDN", icon: "💻", category: "技术论坛" },
  { id: "juejin", name: "掘金", icon: "💻", category: "技术论坛" },
  // 问答
  { id: "quora", name: "Quora", icon: "❓", category: "问答" },
  { id: "stackexchange", name: "Stack Exchange", icon: "❓", category: "问答" },
  { id: "zhihu", name: "知乎", icon: "❓", category: "问答" },
  { id: "yahoo", name: "Yahoo Answers", icon: "❓", category: "问答" },
  // 独立站
  { id: "tempmails-top", name: "tempmails.top", icon: "📧", category: "独立站" },
  { id: "tempmails-io", name: "tempmails.io", icon: "📧", category: "独立站" },
  { id: "tempmails-org", name: "tempmails.org", icon: "📧", category: "独立站" },
  { id: "all-sites", name: "20站总图标", icon: "🌐", category: "独立站" },
];

// 模拟好汉数据（部分）
const heroes = [
  { id: "songjiang", name: "宋江", nickname: "及时雨", status: "working", target: "reddit" },
  { id: "lujunyi", name: "卢俊义", nickname: "玉麒麟", status: "resting", target: null },
  { id: "wuyong", name: "吴用", nickname: "智多星", status: "working", target: "twitter" },
  { id: "gongsunsheng", name: "公孙胜", nickname: "入云龙", status: "done", target: null },
  { id: "linchong", name: "林冲", nickname: "豹子头", status: "working", target: "youtube" },
  { id: "wusong", name: "武松", nickname: "行者", status: "error", target: null },
  { id: "luzhishen", name: "鲁智深", nickname: "花和尚", status: "working", target: "github" },
  { id: "likui", name: "李逵", nickname: "黑旋风", status: "resting", target: null },
  // ... 更多好汉
];

const statusColors: Record<string, string> = {
  working: "bg-jade-green",
  error: "bg-vermillion",
  stopped: "bg-ash-gray",
  done: "bg-imperial-gold",
  resting: "bg-ink-blue",
};

const statusLabels: Record<string, string> = {
  working: "执行中",
  error: "报错",
  stopped: "终止",
  done: "完成",
  resting: "休息",
};

export function DistributionHall() {
  const [selectedHero, setSelectedHero] = useState<typeof heroes[0] | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState<typeof platforms[0] | null>(null);

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-parchment">宋江108好汉分发大厅</h2>
        <p className="text-sm text-ash-gray">编外推广 · 全球分舵</p>
      </div>

      {/* 信鸽飞行动效 */}
      <div className="mb-4">
        <CarrierPigeon width={800} height={400} />
      </div>

      {/* 圆形布局 */}
      <div className="relative bg-gradient-to-b from-ink-blue/20 to-ink-black/40 rounded-xl p-8 min-h-[600px]">
        {/* 背景装饰 */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[200px]">
            ⚔️
          </div>
        </div>

        {/* 圆心：总控图标 */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
          <div className="w-20 h-20 rounded-full bg-imperial-gold/20 border-2 border-imperial-gold flex items-center justify-center">
            <span className="text-3xl">👑</span>
          </div>
          <p className="text-xs text-center text-imperial-gold mt-1">宋徽宗印章</p>
        </div>

        {/* 内圈：32个平台图标 */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          {platforms.map((platform, index) => {
            const angle = (index / platforms.length) * 360;
            const radius = 150;
            const x = Math.cos((angle * Math.PI) / 180) * radius;
            const y = Math.sin((angle * Math.PI) / 180) * radius;

            return (
              <div
                key={platform.id}
                onClick={() => setSelectedPlatform(platform)}
                className={`absolute w-10 h-10 rounded-full bg-card-bg border border-card-border flex items-center justify-center cursor-pointer transition-all hover:scale-110 ${
                  selectedPlatform?.id === platform.id ? "ring-2 ring-imperial-gold" : ""
                }`}
                style={{
                  transform: `translate(${x}px, ${y}px)`,
                  left: "-20px",
                  top: "-20px",
                }}
                title={platform.name}
              >
                <span className="text-lg">{platform.icon}</span>
              </div>
            );
          })}
        </div>

        {/* 外圈：好汉（简化展示） */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          {heroes.map((hero, index) => {
            const angle = (index / heroes.length) * 360;
            const radius = 250;
            const x = Math.cos((angle * Math.PI) / 180) * radius;
            const y = Math.sin((angle * Math.PI) / 180) * radius;

            return (
              <div
                key={hero.id}
                onClick={() => setSelectedHero(hero)}
                className={`absolute w-14 h-14 rounded-full bg-card-bg border-2 flex items-center justify-center cursor-pointer transition-all hover:scale-110 ${
                  selectedHero?.id === hero.id ? "border-imperial-gold" : "border-card-border"
                }`}
                style={{
                  transform: `translate(${x}px, ${y}px)`,
                  left: "-28px",
                  top: "-28px",
                }}
                title={`${hero.name}（${hero.nickname}）`}
              >
                <div className="text-center">
                  <span className="text-xl">⚔️</span>
                  <div className={`status-light ${hero.status === "working" ? "green" : hero.status === "error" ? "red" : ""} absolute -top-1 -right-1`} />
                </div>
              </div>
            );
          })}
        </div>

        {/* 信鸽飞行示意 */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="animate-pulse">
            <span className="text-2xl">🕊️</span>
          </div>
        </div>
      </div>

      {/* 选中信息 */}
      <div className="grid grid-cols-2 gap-4">
        {selectedHero && (
          <div className="guofeng-card p-4">
            <h3 className="font-bold text-imperial-gold mb-2">
              {selectedHero.name}（{selectedHero.nickname}）
            </h3>
            <p className="text-sm text-ash-gray">
              状态：{statusLabels[selectedHero.status]}
            </p>
            {selectedHero.target && (
              <p className="text-sm text-ash-gray">
                目标平台：{platforms.find(p => p.id === selectedHero.target)?.name}
              </p>
            )}
          </div>
        )}
        {selectedPlatform && (
          <div className="guofeng-card p-4">
            <h3 className="font-bold text-imperial-gold mb-2">
              {selectedPlatform.icon} {selectedPlatform.name}
            </h3>
            <p className="text-sm text-ash-gray">
              分类：{selectedPlatform.category}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
