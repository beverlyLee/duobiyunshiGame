# 先清理旧的打包文件
rm -rf build dist __pycache__ "躲避陨石.spec"

# 重新打包 .app
/Users/mff/.local/bin/pyinstaller --onedir --windowed --name "躲避陨石" main.py

