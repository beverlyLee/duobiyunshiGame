#!/bin/bash

# ==========================================
# 躲避陨石游戏 - 简单版 DMG 安装包制作脚本
# ==========================================

set -e

# 配置变量
APP_NAME="躲避陨石"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="躲避陨石_安装包"
VERSION="1.0.0"
VOLUME_NAME="躲避陨石 v${VERSION}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 .app 是否存在
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}🚀 开始制作 DMG 安装包...${NC}"
echo -e "${BLUE}==========================================${NC}"

if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}❌ 错误：未找到 $APP_PATH${NC}"
    echo ""
    echo "请先运行以下命令打包应用程序："
    echo -e "${YELLOW}   /Users/mff/.local/bin/pyinstaller --onedir --windowed --name \"$APP_NAME\" main.py${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 找到应用程序: $APP_PATH${NC}"

# 检查是否需要创建临时目录
TMP_DIR="dmg_temp"
mkdir -p "$TMP_DIR"

# 复制应用程序
echo -e "${GREEN}📦 复制应用程序...${NC}"
cp -r "$APP_PATH" "$TMP_DIR/"

# 创建 Applications 快捷方式
echo -e "${GREEN}🔗 创建 Applications 快捷方式...${NC}"
ln -sf /Applications "$TMP_DIR/Applications"

# 计算 DMG 大小
APP_SIZE=$(du -sm "$APP_PATH" | awk '{print $1}')
DMG_SIZE=$((APP_SIZE + 30))  # 额外 30MB

echo -e "${YELLOW}📏 应用程序大小: ${APP_SIZE}MB${NC}"
echo -e "${YELLOW}📏 DMG 大小: ${DMG_SIZE}MB${NC}"

# 创建 DMG 文件名
DMG_FINAL="dist/${DMG_NAME}_${VERSION}.dmg"
DMG_TMP="dist/${DMG_NAME}_temp.dmg"

# 清理旧文件
rm -f "$DMG_FINAL" "$DMG_TMP"
rm -f "dist/${DMG_NAME}.dmg"

# 创建临时 DMG
echo -e "${GREEN}💾 创建 DMG 镜像...${NC}"
hdiutil create \
    -volname "$VOLUME_NAME" \
    -srcfolder "$TMP_DIR" \
    -ov \
    -format UDRW \
    "$DMG_TMP"

# 挂载 DMG 进行配置
echo -e "${GREEN}🔄 挂载 DMG 进行配置...${NC}"
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TMP")
MOUNT_DEVICE=$(echo "$MOUNT_OUTPUT" | grep "Apple_HFS" | awk '{print $1}')
MOUNT_POINT=$(echo "$MOUNT_OUTPUT" | grep "Apple_HFS" | cut -d' ' -f3-)

echo -e "${YELLOW}   挂载点: $MOUNT_POINT${NC}"
echo -e "${YELLOW}   设备: $MOUNT_DEVICE${NC}"

# 等待挂载完成
sleep 2

# 使用 AppleScript 配置窗口
echo -e "${GREEN}🖼️ 配置 Finder 窗口样式...${NC}"

osascript <<END
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 650, 480}
        
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 96
        
        -- 设置图标位置
        set position of item "${APP_NAME}.app" to {160, 220}
        set position of item "Applications" to {430, 220}
        
        close
        open
    end tell
end tell
END

# 等待设置完成
sleep 2

# 卸载 DMG
echo -e "${GREEN}⏏️ 卸载 DMG...${NC}"
hdiutil detach "$MOUNT_DEVICE" -force

# 压缩 DMG
echo -e "${GREEN}📦 压缩 DMG (最高压缩)...${NC}"
hdiutil convert "$DMG_TMP" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "$DMG_FINAL"

# 清理临时文件
echo -e "${GREEN}🧹 清理临时文件...${NC}"
rm -f "$DMG_TMP"
rm -rf "$TMP_DIR"

# 创建最新版本链接
ln -sf "$(basename "$DMG_FINAL")" "dist/${DMG_NAME}.dmg"

echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}✅ DMG 安装包制作完成！${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${YELLOW}📄 输出文件：${NC}"
echo "   带版本: $DMG_FINAL"
echo "   最新版本: dist/${DMG_NAME}.dmg (链接)"
echo ""
echo -e "${YELLOW}📦 安装说明：${NC}"
echo "   1. 双击 DMG 文件打开"
echo "   2. 将 '${APP_NAME}.app' 拖拽到 'Applications' 文件夹"
echo "   3. 从 Launchpad 或 Applications 文件夹启动游戏"
echo ""
echo -e "${GREEN}🎮 享受游戏！${NC}"
echo ""
