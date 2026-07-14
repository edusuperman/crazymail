#!/bin/bash
# 部署验证脚本
# 用法: bash tools/verify-deployment.sh
# 用途: 每次部署后自动验证，确保线上实际可访问

set -e

SITE_URL="https://tempmails.top"
PASS=0
FAIL=0

echo "=========================================="
echo "CrazyMail 部署验证"
echo "时间: $(date)"
echo "=========================================="

echo ""
echo "=== 第一层：线上实际内容验证 ==="

# 1. 首页SSR输出
echo -n "1. 首页SSR输出检查... "
LOADING=$(curl -s "$SITE_URL/" | grep -c "Loading" || true)
if [ "$LOADING" == "0" ]; then
    echo "✅ 通过 (无Loading)"
    PASS=$((PASS+1))
else
    echo "❌ 失败 (发现$LOADING个Loading)"
    FAIL=$((FAIL+1))
fi

# 2. 首页有H1
echo -n "2. 首页H1检查... "
H1_COUNT=$(curl -s "$SITE_URL/" | grep -c "<h1" || true)
if [ "$H1_COUNT" -ge "1" ]; then
    echo "✅ 通过 ($H1_COUNT个H1)"
    PASS=$((PASS+1))
else
    echo "❌ 失败 (无H1)"
    FAIL=$((FAIL+1))
fi

# 3. 首页有正文
echo -n "3. 首页内容检查... "
PAGE_SIZE=$(curl -s "$SITE_URL/" | wc -c)
if [ "$PAGE_SIZE" -gt "5000" ]; then
    echo "✅ 通过 (${PAGE_SIZE}字节)"
    PASS=$((PASS+1))
else
    echo "❌ 失败 (${PAGE_SIZE}字节，目标>5000)"
    FAIL=$((FAIL+1))
fi

# 4. 博客文章可访问（抽样）
echo ""
echo "=== 博客文章抽样检查 ==="
SAMPLE_URLS=(
    "$SITE_URL/blog/best-temporary-email-services-2026"
    "$SITE_URL/blog/how-to-create-temporary-email-guide"
    "$SITE_URL/blog/temporary-email-for-verification-guide"
    "$SITE_URL/blog/is-temporary-email-safe-guide"
    "$SITE_URL/blog/temporary-email-for-students-guide"
    "$SITE_URL/blog/temporary-email-for-online-privacy"
    "$SITE_URL/blog/disposable-email-for-spam-protection-guide"
    "$SITE_URL/blog/temporary-email-for-developers-guide"
    "$SITE_URL/blog/temporary-email-for-signing-up"
    "$SITE_URL/blog/temporary-email-vs-permanent-email-differences"
)

BLOG_PASS=0
BLOG_FAIL=0
for url in "${SAMPLE_URLS[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    CONTENT=$(curl -s "$url" | grep -c "Not Found" || true)
    if [ "$STATUS" == "200" ] && [ "$CONTENT" == "0" ]; then
        echo "  ✅ $url"
        BLOG_PASS=$((BLOG_PASS+1))
    else
        echo "  ❌ $url (状态: $STATUS, Not Found: $CONTENT)"
        BLOG_FAIL=$((BLOG_FAIL+1))
    fi
done

if [ "$BLOG_FAIL" == "0" ]; then
    echo "4. 博客文章检查... ✅ 通过 ($BLOG_PASS/$((BLOG_PASS+BLOG_FAIL)))"
    PASS=$((PASS+1))
else
    echo "4. 博客文章检查... ❌ 失败 ($BLOG_PASS通过, $BLOG_FAIL失败)"
    FAIL=$((FAIL+1))
fi

# 5. ads.txt
echo ""
echo "=== 其他文件检查 ==="
echo -n "5. ads.txt检查... "
ADS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL/ads.txt")
if [ "$ADS_STATUS" == "200" ]; then
    echo "✅ 通过"
    PASS=$((PASS+1))
else
    echo "❌ 失败 (状态: $ADS_STATUS)"
    FAIL=$((FAIL+1))
fi

# 6. robots.txt
echo -n "6. robots.txt检查... "
ROBOTS=$(curl -s "$SITE_URL/robots.txt" | head -1)
if [[ "$ROBOTS" == *"robots.txt"* ]]; then
    echo "✅ 通过"
    PASS=$((PASS+1))
else
    echo "❌ 失败"
    FAIL=$((FAIL+1))
fi

# 7. Sitemap
echo -n "7. Sitemap检查... "
SITEMAP_COUNT=$(curl -s "$SITE_URL/sitemap.xml" | grep -c '<loc>' || true)
if [ "$SITEMAP_COUNT" -gt "0" ]; then
    echo "✅ 通过 ($SITEMAP_COUNT个URL)"
    PASS=$((PASS+1))
else
    echo "❌ 失败 (无URL)"
    FAIL=$((FAIL+1))
fi

# 汇总
echo ""
echo "=========================================="
echo "验证结果汇总"
echo "=========================================="
echo "通过: $PASS"
echo "失败: $FAIL"
echo "总计: $((PASS+FAIL))"

if [ "$FAIL" == "0" ]; then
    echo ""
    echo "✅ 全部通过！可以认为部署成功。"
    exit 0
else
    echo ""
    echo "❌ 有$FAIL项失败，请修复后再认为部署成功。"
    exit 1
fi
