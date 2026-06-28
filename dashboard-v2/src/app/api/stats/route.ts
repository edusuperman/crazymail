import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function GET() {
  try {
    // 调用 Python 数据提供器
    const { stdout } = await execAsync(
      'python src/lib/data-provider.py',
      { cwd: process.cwd(), timeout: 30000 }
    );
    
    const data = JSON.parse(stdout);
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to get stats:", error);
    
    // 返回基本数据
    return NextResponse.json({
      timestamp: new Date().toISOString(),
      articles: { count: 0, list: [] },
      heroes: { count: 0, transparent_count: 0 },
      site: { url: "https://tempmails.top/", status: "unknown", code: "0" },
      api: { status: "unknown", code: "0" },
    });
  }
}
