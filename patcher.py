import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案終極源頭解鎖補丁 (1年數據 + 6個月繪圖) 啟動")
print("==================================================")

py_files = glob.glob("*.py")

for file_path in py_files:
    if file_path in ["patcher.py", "Dashboard.py", "Master_Scanner.py"]:
        continue
        
    print(f"\n📁 正在深度手術檔案: {file_path} ...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    modified = False
    
    # 先清除並還原上一次可能殘留的舊切片變數，確保乾淨重刷
    content = re.sub(r'[ \t]*hank_6m_df\s*=\s*.*\n', '', content)
    content = content.replace("(hank_6m_df,", "(df,")
    content = content.replace("(hank_6m_df\s*,", "(df,")
    
    # 1. 🔥 解鎖源頭：把 yf.download 裡面的 period 限制通通強制改成 "1y" (一年份)
    if "yf.download" in content:
        if re.search(r'period\s*=\s*[\'"][^\'"]+[\'"]', content):
            print(f"  🟢 [源頭解鎖] 發現限制長度的 period 參數，強制升級為 '1y' ...")
            content = re.sub(r'period\s*=\s*[\'"][^\'"]+[\'"]', 'period="1y"', content)
            modified = True
        elif "period" not in content and "start" not in content:
            print(f"  🟢 [源頭解鎖] 補上預設 period='1y' 參數 ...")
            content = content.replace("yf.download(", "yf.download(period='1y', ")
            modified = True

    # 2. 🔥 精準切片：找到 mpf.plot，智慧捕獲它的變數名稱，並在正上方切出 125 天（半年）
    clean_pattern = r'([ \t]*)mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,'
    if re.search(clean_pattern, content):
        print(f"  🟢 [K線切片] 找到繪圖點，動態對齊縮排並切出最後 125 根 K 棒...")
        content = re.sub(clean_pattern, r'\1hank_6m_df = \2.tail(125)\n\1mpf.plot(hank_6m_df,', content)
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✨ {file_path} 源頭與繪圖雙重解鎖成功！")
    else:
        print(f"  🟡 此檔案無需修改。")

print("\n==================================================")
print("🎯 【終極源頭與切片雙重解鎖完工】")
print("==================================================")