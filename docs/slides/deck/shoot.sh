#!/usr/bin/env bash
# 用本機 Chrome 無頭模式截圖：./shoot.sh [檔名前綴…]（預設全部）
cd "$(dirname "$0")"; mkdir -p shots
for f in slides/${1:-}*.html; do n=$(basename "$f" .html)
  timeout 60 google-chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1920,1080 \
    --virtual-time-budget=8000 --screenshot="shots/$n.png" "file://$PWD/$f" 2>/dev/null; done
