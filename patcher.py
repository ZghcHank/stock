# -*- coding: utf-8 -*-
import os
import re
import glob
import base64

# =========================================================================
# 🔐 1. Hank 補丁密鑰隔離晶片 (100% ASCII Base64 Encoded)
# =========================================================================
P_DB = {
    "title_banner": "PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0K8J+agCBIYW5rIOWwiOahiOe1gualtea6kOmgreino+mOluijnOS4gSAo5a6M5YWo5YWN55ar54Sh6ZmQ6YGe6L+054mIKSDllZ/li5UKPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0=",
    "op_file": "8J+TgSDmraPlnKjmt7HluqbmiYvooZPmqpTmoYg6IA==",
    "clean_old": "ICDwn6e5IOWBtea4rOWIsOiIiueJiOW/q+WPluS7o+eivO+8jOato+WcqOWFqOiHquWLlemHjee9ruaqlOahiOeCuuS5vua3qOaomea6lueJiC4uLg==",
    "kline_slice": "ICDwn5+iIFtL57ea5YiH54mHXSDmib7liLDnuarlnJbpu57vvIzli5XmhYvlsI3pvYrnuK7mjpLkuKbliIflh7rmnIDlvowgMTI1IOaguSBLIOajki4uLg==",
    "cache_inject": "ICDwn5+iIFvlv6vlj5bpmLLorbddIOato+WcqOWuieWFqOazqOWFpeehrOeinyAwIOenkuW/q+WPluino+mOluaZtueJhy4uLg==",
    "file_done": "ICDinKgg5a6J5YWo5rSX5ruM6IiH5qW16YCf5b+r5Y+W5Y2H57Sa5a6M5bel77yB",
    "final_done": "Cj09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CvCfjq8g44CQ5YWo6Ieq5YuV6KOc5LiB6YeN5Yi35a6M5bel44CR5omA5pyJ5a2Q562W55Wl5bey6YCy5YWl5pyA6auY6YCf56eS6K6A54uA5oWL77yBCj09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09"
}

def txt(key):
    return base64.b64decode(P_DB[key]).decode('utf-8')

# 智慧快取解鎖源碼晶片 (純 ASCII，絕對安全)
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

# =========================================================================
# ⚙️ 2. 自動化批量補丁改寫手術核心
# =========================================================================
if __name__ == "__main__":
    print(txt("title_banner"))
    
    py_files = glob.glob("*.py")
    
    for file_path in py_files:
        # 核心安全守衛：絕對不能改寫大指揮官、戰情室網頁與補丁自己！
        if file_path in ["patcher.py", "Dashboard.py", "Master_Scanner.py", "Backtest_Engine.py"]:
            continue
            
        print(txt("op_file") + file_path + " ...")
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # 🧼 A. 先行洗滌重置機制：如果檔案之前被改壞了，強行還原成乾淨標準版
        if "def cached_yf_download" in content:
            print(txt("clean_old"))
            content = re.sub(r'def cached_yf_download[\s\S]*?return df\n', '', content)
            content = content.replace("cached_yf_download(", "yf.download(")
            
        modified = False
        
        # 🧱 B. 補釘二：攔截並將歷史天數限制強制擴展到 1 年 (365天)
        timedelta_pattern = r'timedelta\(\s*(?:days\s*=\s*)?(\d+)\s*\)'
        if re.search(timedelta_pattern, content):
            content = re.sub(timedelta_pattern, 'timedelta(days=365)', content)
            modified = True
            
        # 🧱 C. 補釘三：繪圖前自動插入 125 根 K 棒半年線切片特寫
        clean_pattern = r'([ \t]*)mpf\.plot\(\s*([a-zA-Z0-9_]+)\s*,'
        if re.search(clean_pattern, content) and "hank_6m_df" not in content:
            print(txt("kline_slice"))
            content = re.sub(clean_pattern, r'\1hank_6m_df = \2.tail(125)\n\1mpf.plot(hank_6m_df,', content)
            modified = True
            
        # 🧱 D. 補釘一：全自動注入硬碟 0 秒快取解鎖晶片
        if "yf.download" in content and "cached_yf_download" not in content:
            print(txt("cache_inject"))
            content = cached_download_code + "\n\n" + content
            content = content.replace("yf.download(", "cached_yf_download(")
            modified = True
            
        # 手術完畢，寫回硬碟
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(txt("file_done"))
        
    print(txt("final_done"))