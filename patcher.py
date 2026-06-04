import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案終極源頭解鎖補丁 (全面攔截 timedelta 版) 啟動")
print("==================================================")

py_files = glob.glob("*.py")

for file_path in py_files:
    if file_path in ["patcher.py", "Dashboard.py", "Master_Scanner.py"]:
        continue
        
    print(f"\n📁 正在深度手術檔案: {file_path} ...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    modified = False
    
    # 1. 🔥 攔截隱藏版時間限制：將 timedelta(days=90) 等等通通強制改成 days=365 (一年份)
    if "timedelta" in content and re.search(r'days\s*=\s*\d+', content):
        print(f"  🟢 [時間解鎖] 偵測到隱藏的 timedelta 限制，強制拉長源頭至 365 天...")
        content = re.sub(r'days\s*=\s*\d+', 'days=365', content)
        modified = True

    # 2. 解鎖標準版 period 限制
    if "yf.download" in content:
        if re.search(r'period\s*=\s*[\'"][^\'"]+[\'"]', content):
            print(f"  🟢 [源頭解鎖] 強制升級 yf.download 參數為 '1y' ...")
            content = re.sub(r'period\s*=\s*[\'"][^\'"]+[\'"]', 'period="1y"', content)
            modified = True
        elif "period" not in content and "start" not in content:
            print(f"  🟢 [源頭解鎖] 補上預設 period='1y' 參數 ...")
            content = content.replace("yf.download(", "yf.download(period='1y', ")
            modified = True

    # 3. 🔥 精準切片：找到 mpf.plot，智慧捕獲變數名稱，對齊縮排並切出最後 125 根 K 棒
    clean_pattern = r'([ \t]*)mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,'
    if re.search(clean_pattern, content) and "hank_6m_df" not in content:
        print(f"  🟢 [K線切片] 找到繪圖點，動態對齊縮排並切出最後 125 根 K 棒...")
        content = re.sub(clean_pattern, r'\1hank_6m_df = \2.tail(125)\n\1mpf.plot(hank_6m_df,', content)
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✨ {file_path} 隱藏時間防線徹底炸開！")
    else:
        print(f"  🟡 此檔案無需修改。")

print("\n==================================================")
print("🎯 【全自動隱藏時間解鎖完工】")
print("==================================================")