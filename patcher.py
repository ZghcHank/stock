import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案終極源頭解鎖補丁 (完全免疫無限遞迴版) 啟動")
print("==================================================")

# 智慧快取防護函數 (內部使用 getattr 繞過文字取代，徹底免疫無限遞迴)
cached_download_code = """
def cached_yf_download(*args, **kwargs):
    import os
    import pandas as pd
    import yfinance as yf
    from datetime import datetime
    
    ticker = args[0] if args else kwargs.get('tickers')
    period = kwargs.get('period', '1y')
    
    if ticker and isinstance(ticker, str):
        date_str = datetime.today().strftime("%Y%m%d")
        cache_file = os.path.join("yf_cache", date_str, f"{ticker}_{period}.pkl")
        fallback_file = os.path.join("yf_cache", date_str, f"{ticker}_1y.pkl")
        
        for f_path in [cache_file, fallback_file]:
            if os.path.exists(f_path):
                try:
                    return pd.read_pickle(f_path)
                except Exception:
                    pass
                    
    # 🌟 使用 getattr 避開字串 replace 關鍵字，完美斷開無限遞迴死結
    raw_download = getattr(yf, 'download')
    df = raw_download(*args, **kwargs)
    if ticker and isinstance(ticker, str) and not df.empty:
        try:
            date_str = datetime.today().strftime("%Y%m%d")
            cache_dir = os.path.join("yf_cache", date_str)
            os.makedirs(cache_dir, exist_ok=True)
            df.to_pickle(os.path.join(cache_dir, f"{ticker}_{period}.pkl"))
        except Exception:
            pass
    return df
"""

py_files = glob.glob("*.py")

for file_path in py_files:
    if file_path in ["patcher.py", "Dashboard.py", "Master_Scanner.py"]:
        continue
        
    print(f"\n📁 正在深度手術檔案: {file_path} ...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 🧼 先行洗滌重置機制：如果檔案之前被改壞了，強行還原成乾淨原版
    if "def cached_yf_download" in content:
        print("  🧹 偵測到舊版無限遞迴髒代碼，正在全自動重置檔案為乾淨標準版...")
        content = re.sub(r'def cached_yf_download[\s\S]*?return df\n', '', content)
        content = content.replace("cached_yf_download(", "yf.download(")

    modified = False
    
    # 1. 攔截任何形式的 timedelta 限制
    timedelta_pattern = r'timedelta\(\s*(?:days\s*=\s*)?(\d+)\s*\)'
    if re.search(timedelta_pattern, content):
        content = re.sub(timedelta_pattern, 'timedelta(days=365)', content)
        modified = True

    # 2. 精準對齊切出 125 根 K 棒（半年線圖表）
    clean_pattern = r'([ \t]*)mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,'
    if re.search(clean_pattern, content) and "hank_6m_df" not in content:
        print(f"  🟢 [K線切片] 找到繪圖點，動態對齊縮排並切出最後 125 根 K 棒...")
        content = re.sub(clean_pattern, r'\1hank_6m_df = \2.tail(125)\n\1mpf.plot(hank_6m_df,', content)
        modified = True

    # 3. 注入絕對安全的硬碟快取解鎖晶片
    if "yf.download" in content and "cached_yf_download" not in content:
        print(f"  🟢 [快取防護] 正在安全注入硬碟 0 秒快取解鎖晶片...")
        content = cached_download_code + "\n\n" + content
        content = content.replace("yf.download(", "cached_yf_download(")
        modified = True

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✨ {file_path} 安全洗滌與極速快取升級完工！")

print("\n==================================================")
print("🎯 【全自動無限遞迴解鎖與重刷完工】")
print("==================================================")