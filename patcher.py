import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案地毯式全自動升級工具 (終極大滿貫版) 啟動")
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
    
    # 1. 檢查是否需要注入 requests session 雲端防封鎖外衣
    if "yf.download" in content or "yf.Ticker" in content:
        if "session = requests.Session()" not in content and "requests.Session()" not in content:
            print(f"  🟢 [注入] 偵測到數據抓取語法，正在頂端注入瀏覽器 Session 外衣...")
            content = session_code + "\n\n" + content
            modified = True
            
        if "yf.download" in content and "session=" not in content and "session =" not in content:
            print(f"  🟢 [修正] 正在幫 yf.download 綁定 session 參數...")
            content = re.sub(r'yf\.download\(\s*', 'yf.download(session=session, ', content)
            modified = True

    # 2. 檢查並修正雅虎股市網址格式
    if "tw.stock.yahoo.com" in content and "split" not in content:
        print(f"  🟢 [網址] 正在將雅虎連結格式修正為純數字跳轉...")
        content = content.replace("quote/{ticker}", "quote/{ticker.split('.')[0]}")
        content = content.replace("quote/{ticker.strip()}", "quote/{ticker.split('.')[0]}")
        modified = True

    # 3. 🌟 新增：智慧調整 K 線圖顯示範圍為「半年 (125天)」
    if "mpf.plot" in content and "tail(125)" not in content:
        print(f"  🟢 [K線] 偵測到繪圖語法，正在自動將繪圖範圍調整為「半年期 (125 根 K 棒)」...")
        # 智慧搜尋：自動捕獲變數名稱，將 mpf.plot(df, 替換為 plot_df = df.tail(125)\n mpf.plot(plot_df,
        content = re.sub(r'mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,', r'plot_df = \1.tail(125)\n            mpf.plot(plot_df,', content)
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✨ {file_path} 功能全面升級成功！")
    else:
        print(f"  🟡 無需改動，檔案安全。")

print("\n==================================================")
print("🎯 【全自動地毯式大滿貫升級完工】")
print("您的所有子策略程式已全面具備：雲端抗封鎖、雅虎連結修正、半年K線特寫！")
print("==================================================")