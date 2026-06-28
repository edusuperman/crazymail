"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { MainContent } from "@/components/MainContent";
import { DataPanel } from "@/components/DataPanel";
import { Header } from "@/components/Header";
import { BottomNav } from "@/components/BottomNav";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"writing" | "distribution" | "factory">("writing");
  const [activePage, setActivePage] = useState("overview");

  return (
    <div className="flex flex-col h-screen">
      {/* 顶部状态栏 */}
      <Header />
      
      {/* 主体内容 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 左侧配置菜单 */}
        <Sidebar activePage={activePage} onPageChange={setActivePage} />
        
        {/* 中间主区域 */}
        <MainContent activeTab={activeTab} onTabChange={setActiveTab} />
        
        {/* 右侧数据概览 */}
        <DataPanel activeTab={activeTab} />
      </div>
      
      {/* 底部导航栏 */}
      <BottomNav activePage={activePage} onPageChange={setActivePage} />
    </div>
  );
}
