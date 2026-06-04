import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案地毯式全自動升級工具 (智慧縮排對齊版) 啟動")
print("==================================================")

# 找出 D:\Stock 底下所有的 Python 檔案
py_files = glob.glob("*.py")

session_code = """import requests
if 'session' not in locals() and 'session' not in globals():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    })"""

for file_path in py_files:
    # 略過補丁程式本身與網頁面板
    if file_path in ["patcher.py", "Dashboard.py"]:
        continue
        
    print(f"\n📁 正在檢查檔案: {file_path} ...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    modified = False
    
    # 1. 智慧修復：自動修正目前已經被舊補丁弄壞的縮排 (IndentationError)
    # 自動捕獲第一行的縮排空白 \1，強行將第二行 mpf.plot 也套用相同的縮排量
    broken_pattern = r'([ \t]*)plot_df\s*=\s*([a-zA-Z0-9_]+)\.tail\(125\)\n[ \t]*mpf\.plot\(\s*plot_df\s*,'
    if re.search(broken_pattern, content):
        print(f"  🟢 [修復] 偵測到縮排錯誤的 K 線代碼，正在進行全自動精密對齊...")
        content = re.sub(broken_pattern, r'\1plot_df = \2.tail(125)\n\1mpf.plot(plot_df,', content)
        modified = True

    # 2. 智慧注入：如果檔案是乾淨原版，自動偵測前置空白並動態注入半年線範圍
    clean_pattern = r'([ \t]*)mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,'
    if "tail(125)" not in content and re.search(clean_pattern, content):
        print(f"  🟢 [K線] 偵測到原始繪圖語法，正在依據原有縮排動態注入「半年期 K 線」功能...")
        content = re.sub(clean_pattern, r'\1plot_df = \2.tail(125)\n\1mpf.plot(plot_df,', content)
        modified = True

    # 3. 檢查是否需要注入 requests session 雲端防封鎖外衣
    if "yf.download" in content or "yf.Ticker" in content:
        if "session = requests.Session()" not in content and "requests.Session()" not in content:
            print(f"  🟢 [注入] 正在頂端注入瀏覽器 Session 外衣...")
            content = session_code + "\n\n" + content
            modified = True
            
        if "yf.download" in content and "session=" not in content and "session =" not in content:
            print(f"  🟢 [修正] 正在幫 yf.download 綁定 session 參數...")
            content = re.sub(r'yf\.download\(\s*', 'yf.download(session=session, ', content)
            modified = True

    # 4. 檢查並修正雅虎股市網址格式
    if "tw.stock.yahoo.com" in content and "split" not in content:
        print(f"  🟢 [網址] 正在將雅虎連結格式修正為純數字跳轉...")
        content = content.replace("quote/{ticker}", "quote/{ticker.split('.')[0]}")
        content = content.replace("quote/{ticker.strip()}", "quote/{ticker.split('.')[0]}")
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✨ {file_path} 精密修復與升級成功！")
    else:
        print(f"  🟡 無需改動，檔案安全。")

print("\n==================================================")
print("🎯 【全自動智慧對齊補丁執行完畢】")
print("==================================================")