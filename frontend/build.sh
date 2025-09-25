npm run build
cd dist
echo miniapp.snipla.ru > CNAME
rm -rf .git
git init
git config --global --add safe.directory /mnt/nvme0n1p4/miko/Projects/TgMiniAppTemplate/frontend/dist
git add .
git commit -m "build"
git remote add origin git@github.com:sht0rmx/tgminiapptemplate.git
git remote set-url origin https://github.com/sht0rmx/tgminiapptemplate.git
git branch -M pages-build
git push -u -f origin pages-build
