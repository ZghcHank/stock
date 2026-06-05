import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案終極源頭解鎖補丁 (無差別 timedelta 攔截版) 啟動")
print("==================================================")

py_files = glob.glob("*.py")

for file_path in py_files:
    if file_path in ["patcher.py", "Dashboard.py", "Master_Scanner.py"]:
        continue
        
    print(f"\n📁 正在深度手術檔案: {file_path} ...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    modified = False
    
    # 1. 🔥 終極攔截：將任何形式的 timedelta 限制 (如 timedelta(90) 或 timedelta(days=60)) 通通修正為 365 天
    # 支援：timedelta(90), timedelta(days=90), timedelta(  60  ) 等各種變形
    timedelta_pattern = r'timedelta\(\s*(?:days\s*=\s*)?(\d+)\s*\)'
    if re.search(timedelta_pattern, content):
        print(f"  🟢 [源頭強索] 偵測到隱蔽的 timedelta 歷史限制，強制炸開源頭至 365 天份數據...")
        content = re.sub(timedelta_pattern, 'timedelta(days=365)', content)
        modified = True

    # 2. 解鎖標準版 period 限制
    if "yf.download" in content:
        if re.search(r'period\s*=\s*[\'"][^\'"]+[\'"]', content):
            content = re.sub(r'period\s*=\s*[\'"][^\'"]+[\'"]', 'period="1y"', content)
            modified = True
        elif "period" not in content and "start" not in content:
            content = content.replace("yf.download(", "yf.download(period='1y', ")
            modified = True

    # 3. 精準對齊切出 125 根 K 棒（半年線圖表）
    clean_pattern = r'([ \t]*)mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,'
    if re.search(clean_pattern, content) and "hank_6m_df" not in content:
        print(f"  🟢 [K線切片] 找到繪圖點，動態對齊縮排並切出最後 125 根 K 棒...")
        content = re.sub(clean_pattern, r'\1hank_6m_df = \2.tail(125)\n\1mpf.plot(hank_6m_df,', content)
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✨ {file_path} 時間防線徹底破網！")
    else:
        print(f"  🟡 此檔案無阻礙，安全通過。")

print("\n==================================================")
print("🎯 【全自動隱藏時間封鎖解鎖完工】")
print("==================================================")