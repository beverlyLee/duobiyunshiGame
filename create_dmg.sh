#!/bin/bash

# ==========================================
# 躲避陨石游戏 - DMG 安装包制作脚本
# ==========================================

set -e

# 配置变量
APP_NAME="躲避陨石"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="躲避陨石_安装包"
DMG_TMP="tmp_dmg"
DMG_VOLUME_NAME="躲避陨石"
OUTPUT_DIR="dist"
VERSION="1.0.0"

# 检查 .app 是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 错误：未找到 $APP_PATH"
    echo "请先运行 PyInstaller 打包应用程序"
    echo "命令：/Users/mff/.local/bin/pyinstaller --onedir --windowed --name \"$APP_NAME\" main.py"
    exit 1
fi

echo "=========================================="
echo "🚀 开始制作 DMG 安装包..."
echo "=========================================="

# 清理旧文件
echo "📁 清理旧文件..."
rm -f "${OUTPUT_DIR}/${DMG_NAME}.dmg"
rm -f "${OUTPUT_DIR}/${DMG_NAME}_${VERSION}.dmg"
rm -rf "$DMG_TMP"

# 创建临时 DMG 目录
echo "📁 创建临时目录..."
mkdir -p "$DMG_TMP"

# 复制应用程序到临时目录
echo "📦 复制应用程序..."
cp -r "$APP_PATH" "$DMG_TMP/"

# 创建 Applications 别名（用于拖拽安装）
echo "🔗 创建 Applications 快捷方式..."
ln -sf /Applications "$DMG_TMP/Applications"

# 计算所需大小
APP_SIZE=$(du -sm "$APP_PATH" | awk '{print $1}')
DMG_SIZE=$((APP_SIZE + 20))  # 额外 20MB 空间

echo "📏 应用程序大小: ${APP_SIZE}MB"
echo "📏 DMG 大小: ${DMG_SIZE}MB"

# 创建临时 DMG
echo "💾 创建临时 DMG..."
hdiutil create -volname "$DMG_VOLUME_NAME" \
               -srcfolder "$DMG_TMP" \
               -ov -format UDRW \
               -fs HFS+ \
               "${OUTPUT_DIR}/${DMG_NAME}_temp.dmg"

# 挂载 DMG
echo "🔄 挂载 DMG..."
MOUNT_DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "${OUTPUT_DIR}/${DMG_NAME}_temp.dmg" | grep "Apple_HFS" | awk '{print $1}')
MOUNT_POINT="/Volumes/${DMG_VOLUME_NAME}"

# 等待挂载完成
sleep 2

# 设置 Finder 窗口样式
echo "🎨 配置 Finder 窗口样式..."

# 创建背景图片目录
mkdir -p "${MOUNT_POINT}/.background"

# 创建简单的背景（使用 Python 生成）
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import os

# 创建背景图片
width, height = 600, 400
bg_color = (45, 52, 54)  # 深色背景

img = Image.new('RGB', (width, height), bg_color)
draw = ImageDraw.Draw(img)

# 尝试绘制一些装饰性元素
try:
    # 绘制标题区域
    draw.rectangle([(0, 0), (width, 80)], fill=(30, 39, 46))
    
    # 绘制渐变效果（简单模拟）
    for y in range(80):
        alpha = int(255 * (1 - y / 80))
        draw.line([(0, y), (width, y)], fill=(40 + int(20 * y / 80), 47 + int(20 * y / 80), 54 + int(20 * y / 80)))
except:
    pass

# 保存背景图片
bg_path = os.environ.get('MOUNT_POINT', '/Volumes/躲避陨石') + '/.background/background.png'
os.makedirs(os.path.dirname(bg_path), exist_ok=True)
img.save(bg_path)
print(f"背景图片已保存: {bg_path}")
EOF

# 使用 AppleScript 设置 Finder 窗口
echo "🖼️ 配置 Finder 窗口..."

osascript << EOF
tell application "Finder"
    tell disk "$DMG_VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 700, 500}
        
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 96
        
        -- 设置背景图片
        -- 注意：简单的 DMG 可能不需要复杂的背景
        
        -- 设置图标位置
        set position of item "躲避陨石.app" to {175, 200}
        set position of item "Applications" to {425, 200}
        
        -- 添加文字说明的位置
        -- update without registering applications
    end tell
    
    delay 1
    
    -- 确保窗口在前台
    set target of front window to container window of disk "$DMG_VOLUME_NAME"
end tell
EOF

# 等待设置完成
sleep 2

# 卸载 DMG
echo "⏏️ 卸载 DMG..."
hdiutil detach "$MOUNT_DEVICE" -force

# 转换为压缩格式
echo "📦 压缩 DMG..."
hdiutil convert "${OUTPUT_DIR}/${DMG_NAME}_temp.dmg" \
               -format UDZO \
               -imagekey zlib-level=9 \
               -o "${OUTPUT_DIR}/${DMG_NAME}_${VERSION}.dmg"

# 清理临时文件
echo "🧹 清理临时文件..."
rm -f "${OUTPUT_DIR}/${DMG_NAME}_temp.dmg"
rm -rf "$DMG_TMP"

# 创建软链接到最新版本
echo "🔗 创建最新版本链接..."
ln -sf "${DMG_NAME}_${VERSION}.dmg" "${OUTPUT_DIR}/${DMG_NAME}.dmg"

echo ""
echo "=========================================="
echo "✅ DMG 安装包制作完成！"
echo "=========================================="
echo ""
echo "📄 输出文件："
echo "   ${OUTPUT_DIR}/${DMG_NAME}_${VERSION}.dmg"
echo "   ${OUTPUT_DIR}/${DMG_NAME}.dmg (最新版本链接)"
echo ""
echo "📦 安装说明："
echo "   1. 双击 DMG 文件打开"
echo "   2. 将 '躲避陨石.app' 拖拽到 'Applications' 文件夹"
echo "   3. 从 Launchpad 或 Applications 文件夹启动游戏"
echo ""
echo "🎮 享受游戏！"
echo ""
