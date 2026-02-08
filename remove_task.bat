@echo off
schtasks /delete /tn "\CopartScraper" /f
echo Task CopartScraper removed.
pause