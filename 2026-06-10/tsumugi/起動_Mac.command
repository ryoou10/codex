#!/bin/bash
# TSUMUGI 起動用(Mac)。ダブルクリックで起動し、ブラウザが自動で開きます。
cd "$(dirname "$0")"
python3 -m tsumugi.app
echo ""
echo "アプリを終了しました。このウィンドウは閉じて構いません。"
read -r -p "Enterキーで閉じる " _
