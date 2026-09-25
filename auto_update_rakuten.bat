@echo off
setlocal
cd /d "C:\Users\dhoan\Documents\GitHub\kurashi-benri"

echo [%date% %time%] Starting Rakuten update...

python scripts\update_products.py
if errorlevel 1 (
  echo [%date% %time%] Python update failed.
  exit /b 1
)

git diff --quiet -- products.json
if %errorlevel%==0 (
  echo [%date% %time%] No product changes. Nothing to push.
  exit /b 0
)

git add products.json
git commit -m "Update Rakuten products"
if errorlevel 1 (
  echo [%date% %time%] Git commit failed.
  exit /b 1
)

git push origin main
if errorlevel 1 (
  echo [%date% %time%] Git push failed.
  exit /b 1
)

echo [%date% %time%] Update complete.
endlocal
