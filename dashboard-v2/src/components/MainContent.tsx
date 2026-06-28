"use client";

import { WritingFactory } from "./WritingFactory";
import { DistributionHall } from "./DistributionHall";
import { ContentFactory } from "./ContentFactory";

interface MainContentProps {
  activeTab: "writing" | "distribution" | "factory";
  onTabChange: (tab: "writing" | "distribution" | "factory") => void;
}

export function MainContent({ activeTab, onTabChange }: MainContentProps) {
  return (
    <main className="flex-1 flex flex-col overflow-hidden">
      {/* 页签切换 */}
      <div className="flex border-b border-card-border bg-card-bg backdrop-blur-sm">
        <button
          onClick={() => onTabChange("writing")}
          className={`px-6 py-3 text-sm font-medium transition-colors relative ${
            activeTab === "writing"
              ? "text-imperial-gold"
              : "text-ash-gray hover:text-parchment"
          }`}
        >
          📜 宋徽宗写作工厂
          {activeTab === "writing" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-imperial-gold" />
          )}
        </button>
        <button
          onClick={() => onTabChange("distribution")}
          className={`px-6 py-3 text-sm font-medium transition-colors relative ${
            activeTab === "distribution"
              ? "text-imperial-gold"
              : "text-ash-gray hover:text-parchment"
          }`}
        >
          ⚔️ 108好汉分发大厅
          {activeTab === "distribution" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-imperial-gold" />
          )}
        </button>
        <button
          onClick={() => onTabChange("factory")}
          className={`px-6 py-3 text-sm font-medium transition-colors relative ${
            activeTab === "factory"
              ? "text-imperial-gold"
              : "text-ash-gray hover:text-parchment"
          }`}
        >
          📝 内容工厂
          {activeTab === "factory" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-imperial-gold" />
          )}
        </button>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === "writing" ? <WritingFactory /> : 
         activeTab === "distribution" ? <DistributionHall /> :
         <ContentFactory />}
      </div>
    </main>
  );
}
