cd /Users/mff/Documents/trae/duobiyunshiGame

# 1. 先检查是否有挂载的 DMG，强制卸载
hdiutil info | grep -E "躲避陨石|dmg" | grep "/dev/"

# 2. 强制卸载所有相关挂载（如果有）
# hdiutil detach /dev/diskN （N 是数字，根据上面的输出）

# 3. 清理旧文件
rm -f dist/躲避陨石_安装包*.dmg
rm -rf dmg_temp

# 4. 创建最简单的 DMG
mkdir -p dmg_temp
cp -r dist/躲避陨石.app dmg_temp/
ln -sf /Applications dmg_temp/Applications

# 5. 直接创建压缩 DMG（不挂载，不配置窗口）
hdiutil create \
    -volname "躲避陨石" \
    -srcfolder dmg_temp \
    -ov \
    -format UDZO \
    -imagekey zlib-level=9 \
    dist/躲避陨石_安装包.dmg

# 6. 清理
rm -rf dmg_temp

# 7. 完成
echo "✅ DMG 创建完成"
ls -lh dist/躲避陨石_安装包.dmg
