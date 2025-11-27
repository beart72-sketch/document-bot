#!/bin/bash
cd /home/mixa/document-bot
git add .
git commit -m "Auto-save: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
echo "Changes saved at $(date)"
