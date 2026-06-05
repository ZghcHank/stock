import os
import re
import glob

print("==================================================")
print("🚀 Hank 專案終極源頭解鎖補丁 (當日硬碟快取秒讀版) 啟動")
print("==================================================")

# 智慧快取核心函數代碼 (將會被動態注入到每個子策略的頂端)
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
        
        # 🟢 0秒硬碟解鎖機制：存在當日快取就直接秒讀
        for f_path in [cache_file, fallback_file]:
            if os.path.exists(f_path):
                try:
                    return pd.read_pickle(f_path)
                except Exception:
                    pass
                    
    # 若硬碟沒檔案 (網路防護補償網)，才真正發動網路下載
    df = yf.download(*args, **kwargs)
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
        
    modified = False
    
    # 1. 攔截任何形式的 timedelta 限制 (強制拉長源頭至 365 天份數據)
    timedelta_pattern = r'timedelta\(\s*(?:days\s*=\s*)?(\d+)\s*\)'
    if re.search(timedelta_pattern, content):
        content = re.sub(timedelta_pattern, 'timedelta(days=365)', content)
        modified = True

    # 2. 精準對齊切出 125 根 K 棒（半年線圖表特寫）
    clean_pattern = r'([ \t]*)mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,'
    if re.search(clean_pattern, content) and "hank_6m_df" not in content:
        print(f"  🟢 [K線切片] 找到繪圖點，動態對齊縮排並切出最後 125 根 K 棒...")
        content = re.sub(clean_pattern, r'\1hank_6m_df = \2.tail(125)\n\1mpf.plot(hank_6m_df,', content)
        modified = True

    # 3. ⚡ 終極大絕招：將 yf.download 掉包成硬碟快取讀取版
    if "yf.download" in content and "cached_yf_download" not in content:
        print(f"  🟢 [快取防護] 正在注入硬碟 0 秒快取解鎖晶片...")
        content = cached_download_code + "\n\n" + content
        content = content.replace("yf.download(", "cached_yf_download(")
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✨ {file_path} 智慧快取與半年線架構優化成功！")
    else:
        print(f"  🟡 此檔案已具備快取功能，安全通過。")

print("\n==================================================")
print("🎯 【全自動當日硬碟快取升級完工】")
print("==================================================")