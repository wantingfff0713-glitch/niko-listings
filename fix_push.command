#!/bin/bash
cd ~/Desktop/niko-listings

echo "🔧 清理 git 锁文件..."
find .git -name "*.lock" -delete 2>/dev/null
rm -f .git/index.lock .git/HEAD.lock 2>/dev/null

echo "📋 文件状态："
git status --short

echo ""
echo "➕ 添加所有文件..."
git add -A

echo "📝 提交..."
git commit -m "Update pool.html - manual upload redesign" 2>&1

echo ""
echo "🚀 推送到 GitHub..."
git push origin main 2>&1

echo ""
echo "✅ 完成！"
echo "访问：https://wantingfff0713-glitch.github.io/niko-listings/pool.html"
echo ""
echo "按任意键关闭..."
read -n 1
