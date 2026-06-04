import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案地毯式全自動升級工具 (半年 K 線攔截版) 啟動")
print("==================================================")

py_files = glob.glob("*.py")

for file_path in py_files:
    if file_path in ["patcher.py", "Dashboard.py"]:
        continue
        
    print(f"\n📁 正在檢查檔案: {file_path} ...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    modified = False
    
    # 1. 🌟 核心功能：攔截並取代所有的短天期裁切法 (如 .tail(60), .tail(20) 通通變 125)
    if re.search(r'\.tail\(\s*\d+\s*\)', content):
        print(f"  🟢 [K線] 發現 .tail() 裁切限制，正在強行放大至「半年期 (125天)」...")
        content = re.sub(r'\.tail\(\s*\d+\s*\)', '.tail(125)', content)
        modified = True
        
    # 2. 🌟 核心功能：攔截並取代陣列切片限制 (如 [-60:], [-30:] 通通變 [-125:])
    if re.search(r'\[\s*-\s*\d+\s*:\s*\]', content):
        print(f"  🟢 [K線] 發現 [ -X : ] 切片限制，正在強行放大至「半年期 (125天)」...")
        content = re.sub(r'\[\s*-\s*\d+\s*:\s*\]', '[-125:]', content)
        modified = True

    # 3. 順手修復可能殘留的二次重複賦值幽靈代碼 (維持乾淨縮排)
    if "plot_df = plot_df.tail(125)" in content:
        content = content.replace("plot_df = plot_df.tail(125)", "")
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✨ {file_path} 半年期視角全面解鎖！")
    else:
        print(f"  🟡 此檔案無裁切限制，檔案安全。")

print("\n==================================================")
print("🎯 【全自動半年 K 線攔截升級完工】")
print("==================================================")