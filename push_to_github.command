#!/bin/bash
cd "$(dirname "$0")"

echo "📦 准备推送到 GitHub..."
git add index.html listings.json pool.html sync_listings.py deploy.command images/ .gitignore 2>/dev/null

git commit -m "Add pool.html and update listings" 2>/dev/null || echo "（没有新变更需要提交）"

echo "🚀 推送到 GitHub..."
git push origin main

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ 推送成功！"
  echo ""
  echo "接下来开启 GitHub Pages："
  echo "1. 打开 https://github.com/wantingfff0713-glitch/niko-listings/settings/pages"
  echo "2. Source 选 Deploy from a branch"
  echo "3. Branch 选 main / (root)"
  echo "4. 点 Save"
  echo ""
  echo "然后访问："
  echo "https://wantingfff0713-glitch.github.io/niko-listings/pool.html"
  open "https://github.com/wantingfff0713-glitch/niko-listings/settings/pages"
else
  echo "❌ 推送失败，请检查网络连接"
fi

echo ""
echo "按任意键关闭..."
read -n 1
