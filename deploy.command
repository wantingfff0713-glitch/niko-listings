#!/bin/bash
cd "$(dirname "$0")"

# Install netlify CLI if not present
if ! command -v netlify &>/dev/null; then
  echo "📦 正在安装 Netlify CLI..."
  npm install -g netlify-cli
fi

echo "🚀 部署到 Netlify..."
netlify deploy --prod --dir .
echo ""
echo "按任意键关闭窗口..."
read -n 1
