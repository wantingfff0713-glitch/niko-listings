#!/bin/bash
cd ~/Desktop/niko-listings
echo "📁 当前文件夹：$(pwd)"
echo "📋 检查文件状态..."
git status --short
echo ""
echo "➕ 添加所有文件..."
git add -A
echo ""
echo "📝 提交..."
git commit -m "Add pool.html and images" 2>&1
echo ""
echo "🚀 推送到 GitHub..."
git push origin main 2>&1
echo ""
echo "✅ 完成！"
echo "访问：https://wantingfff0713-glitch.github.io/niko-listings/pool.html"
echo ""
echo "按任意键关闭..."
read -n 1
