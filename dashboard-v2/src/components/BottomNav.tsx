"use client";

interface BottomNavProps {
  activePage: string;
  onPageChange: (page: string) => void;
}

const navItems = [
  { id: "overview", label: "总览", icon: "📊" },
  { id: "messages", label: "驿件", icon: "📧" },
  { id: "factory", label: "内容工厂", icon: "📝" },
  { id: "growth", label: "推广", icon: "📈" },
  { id: "monitor", label: "监控", icon: "🛡️" },
  { id: "settings", label: "设置", icon: "⚙️" },
];

export function BottomNav({ activePage, onPageChange }: BottomNavProps) {
  return (
    <nav className="flex items-center justify-around border-t border-card-border bg-card-bg backdrop-blur-sm py-2">
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={() => onPageChange(item.id)}
          className={`flex flex-col items-center gap-1 px-3 py-1 rounded-lg transition-colors ${
            activePage === item.id
              ? "text-imperial-gold"
              : "text-ash-gray hover:text-parchment"
          }`}
        >
          <span className="text-xl">{item.icon}</span>
          <span className="text-xs">{item.label}</span>
        </button>
      ))}
    </nav>
  );
}
