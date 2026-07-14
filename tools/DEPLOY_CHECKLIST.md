# 部署验证清单（Deployment Verification Checklist）
# 位置: tools/DEPLOY_CHECKLIST.md
# 用途: 每次部署后必须逐项验证，全部通过才能说"已解决"
# 创建时间: 2026-07-14
# 来源: Grok Build审计发现的问题

## 使用时机
- 每次Vercel部署后
- 每次Sitemap更新后
- 每次批量文章生成后
- 说"已解决"或"已完成"之前

## 验证清单

### 第一层：线上实际内容验证（必须）

| # | 检查项 | 方法 | 通过标准 |
|---|--------|------|----------|
| 1 | 首页SSR输出 | `curl -s https://tempmails.top/ \| grep -c "Loading"` | Loading数量=0 |
| 2 | 首页有H1 | `curl -s https://tempmails.top/ \| grep -c "<h1"` | H1数量≥1 |
| 3 | 首页有正文 | `curl -s https://tempmails.top/ \| wc -c` | 字节数>5000 |
| 4 | 博客文章可访问 | 随机抽10篇，检查HTTP状态和内容 | 全部200且有文章H1 |
| 5 | Sitemap URL数=线上200数 | 对比sitemap中的URL和实际可访问数 | 差异<5% |
| 6 | ads.txt可访问 | `curl -s -o /dev/null -w "%{http_code}" https://tempmails.top/ads.txt` | 200 |
| 7 | robots.txt可访问 | `curl -s https://tempmails.top/robots.txt` | 有内容 |

### 第二层：SEO结构验证（必须）

| # | 检查项 | 方法 | 通过标准 |
|---|--------|------|----------|
| 8 | 每页只有1个H1 | 抽查5篇文章 | 每页H1数=1 |
| 9 | 每页只有1个canonical | 抽查5篇文章 | 每页canonical数=1 |
| 10 | 无双canonical冲突 | 检查blog.tsx布局 | 文章页不嵌套列表 |
| 11 | meta语言一致 | 检查html lang和meta内容 | 语言一致 |
| 12 | 无虚假hreflang | 检查是否有独立翻译页 | 无翻译页则删除hreflang |

### 第三层：GSC验证（部署后24小时内）

| # | 检查项 | 方法 | 通过标准 |
|---|--------|------|----------|
| 13 | 重新提交Sitemap | GSC API或手动 | 已提交 |
| 14 | 请求重新抓取 | 对软404 URL使用URL检查API | 已请求 |
| 15 | 检查索引状态 | GSC API查询 | 软404数量下降 |

## 验证脚本

```bash
#!/bin/bash
# 快速验证脚本
# 用法: bash tools/verify-deployment.sh

echo "=== 第一层：线上实际内容验证 ==="

# 1. 首页SSR输出
LOADING=$(curl -s https://tempmails.top/ | grep -c "Loading")
echo "首页Loading数: $LOADING (目标: 0)"

# 2. 首页有H1
H1_COUNT=$(curl -s https://tempmails.top/ | grep -c "<h1")
echo "首页H1数: $H1_COUNT (目标: ≥1)"

# 3. 首页有正文
PAGE_SIZE=$(curl -s https://tempmails.top/ | wc -c)
echo "首页字节数: $PAGE_SIZE (目标: >5000)"

# 4. 博客文章可访问（抽样）
echo ""
echo "=== 博客文章抽样检查 ==="
SAMPLE_URLS=(
  "https://tempmails.top/blog/best-temporary-email-services-2026"
  "https://tempmails.top/blog/how-to-create-temporary-email-guide"
  "https://tempmails.top/blog/temporary-email-for-verification-guide"
  "https://tempmails.top/blog/is-temporary-email-safe-guide"
  "https://tempmails.top/blog/temporary-email-for-students-guide"
)

PASS=0
FAIL=0
for url in "${SAMPLE_URLS[@]}"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  CONTENT=$(curl -s "$url" | grep -c "Not Found")
  if [ "$STATUS" == "200" ] && [ "$CONTENT" == "0" ]; then
    echo "✅ $url"
    PASS=$((PASS+1))
  else
    echo "❌ $url (状态: $STATUS, Not Found: $CONTENT)"
    FAIL=$((FAIL+1))
  fi
done
echo "通过: $PASS, 失败: $FAIL"

# 5. ads.txt
echo ""
echo "=== ads.txt检查 ==="
ADS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tempmails.top/ads.txt)
echo "ads.txt状态: $ADS_STATUS (目标: 200)"

# 6. Sitemap URL数
SITEMAP_COUNT=$(curl -s https://tempmails.top/sitemap.xml | grep -c '<loc>')
echo "Sitemap URL数: $SITEMAP_COUNT"
```

## 规则

1. **第一层全部通过** → 才能说"部署成功"
2. **第二层全部通过** → 才能说"SEO就绪"
3. **第三层完成** → 才能说"已提交Google"

## 违反后果

如果跳过验证说"已解决"，但实际未验证：
- 用户信任度下降
- 问题被隐藏，流量无法增长
- 需要重新审计

## 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-07-14 | 初始版本，基于Grok Build审计发现的问题 |
