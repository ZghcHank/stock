import os
import sys
import subprocess
import glob
from datetime import datetime
import pandas as pd
import yfinance as yf
import requests
import io

print("==================================================")
print(f"🚀 Hank 雲端指揮官控制台啟動 | 執行日期: {datetime.today().strftime('%Y%m%d')}")
print("==================================================")

# ==========================================================================================
# 📊 步驟一：全自動網頁爬蟲 - 實時取得台股上市/上櫃全市場股票清單
# ==========================================================================================
def get_all_taiwan_tickers():
    print(">> 正在從臺灣證券交易所與櫃買中心取得最新的全市場股票清單...")
    tickers = []
    
    # 1. 抓取上市股票 (Mode 2)
    try:
        res_twse = requests.get("https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", timeout=15)
        # 🟢 修正：使用 io.StringIO 包裹，完美消滅 Python 3.14 的 FutureWarning 警告
        df_twse = pd.read_html(io.StringIO(res_twse.text))[0]
        df_twse.columns = df_twse.iloc[0]
        df_twse = df_twse.iloc[1:]
        for val in df_twse['有價證券代號及名稱'].dropna():
            parts = str(val).split()
            if len(parts) >= 2 and len(parts[0]) == 4 and parts[0].isdigit(): 
                tickers.append(f"{parts[0]}.TW")
    except Exception as e:
        print(f"  ⚠️ 上市股票清單抓取局部受阻: {e}")

    # 2. 抓取上櫃股票 (Mode 4)
    try:
        res_tpex = requests.get("https://isin.twse.com.tw/isin/C_public.jsp?strMode=4", timeout=15)
        # 🟢 修正：使用 io.StringIO 包裹
        df_tpex = pd.read_html(io.StringIO(res_tpex.text))[0]
        col_name = df_tpex.iloc[0].dropna().values[0]
        df_tpex.columns = df_tpex.iloc[0]
        df_tpex = df_tpex.iloc[1:]
        for val in df_tpex[col_name].dropna():
            parts = str(val).split()
            if len(parts) >= 2 and len(parts[0]) == 4 and parts[0].isdigit():
                tickers.append(f"{parts[0]}.TWO")
    except Exception as e:
        print(f"  ⚠️ 上櫃股票清單抓取局部受阻: {e}")

    # 3. 終極防護網
    tickers = list(set(tickers))
    if not tickers:
        print("  🚨 [警告] 證交所網路連線中斷！自動啟動核心精選標的進行防護防爆...")
        # 🟢 修正：精準修正上櫃股票為 .TWO 後綴，終結 Yahoo 404 報錯
        tickers = ["2317.TW", "2330.TW", "3483.TWO", "6126.TWO", "4741.TWO", "2528.TW", "4542.TWO", "8390.TWO", "6525.TWO", "2360.TW"]
        
    print(f"  ✅ 總共集結 {len(tickers)} 檔全市場股票準備進行掃描。")
    return tickers

tickers_list = get_all_taiwan_tickers()

# ==========================================================================================
# ⚡ 步驟二：大宗批次預載引擎
# ==========================================================================================
try:
    print("\n==================================================")
    print("⚡ [黃金快取] 啟動當日全市場大數據一次性高速打包預載...")
    print("==================================================")
    
    date_str = datetime.today().strftime("%Y%m%d")
    cache_dir = os.path.join("yf_cache", date_str)
    os.makedirs(cache_dir, exist_ok=True)
    
    chunk_size = 300
    for i in range(0, len(tickers_list), chunk_size):
        chunk = tickers_list[i:i+chunk_size]
        print(f"📥 正在極速包裹下載第 {i} 到 {min(i+chunk_size, len(tickers_list))} 檔股票的年度大數據...")
        try:
            data = yf.download(chunk, period="1y", group_by="ticker", progress=False, auto_adjust=True)
            for ticker in chunk:
                if ticker in data.columns.levels[0]:
                    ticker_df = data[ticker].dropna(how='all')
                    if not ticker_df.empty:
                        ticker_df.to_pickle(os.path.join(cache_dir, f"{ticker}_1y.pkl"))
        except Exception as e:
            print(f"  ⚠️ 此批次打包下載失敗: {e}")
            
    print("==================================================")
    print("✨ [快取完工] 全市場數據已成功收納至硬碟！子策略即將開啟 0 秒解鎖模式！")
    print("==================================================\n")
except Exception as e:
    print(f"💥 快取預載引擎發生未預期錯誤: {e}")

# ==========================================================================================
# 🏃‍♂️ 步驟三：策略調度核心排程
# ==========================================================================================
my_scripts = [
    "裸K進階.py",
    "入住帝寶線.py",
    "四線發動.py", 
    "突破ABC.py"
]

print("==================================================")
print("🏃‍♂️ 開始依序調度子策略進行硬碟 0 秒極速覆盤...")
print("==================================================")

for script in my_scripts:
    if os.path.exists(script):
        print(f"🏃‍♂️ 正在啟動子策略程式: 【{script}】...")
        try:
            result = subprocess.run(["python", script], check=True)
            if result.returncode == 0:
                print(f"🟢 【{script}】雲端快取秒讀執行成功！")
            else:
                print(f"❌ 【{script}】回報異常，退出碼: {result.returncode}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 【{script}】執行過程中發生錯誤: {e}")
    else:
        print(f"🟡 找不到檔案 【{script}】，自動跳過。")

# ==========================================================================================
# 🎨 步驟四：五大飆股模組 - 後端全策略數據大會師
# ==========================================================================================
try:
    print("\n==================================================")
    print("🎨 啟動後端大會師：地毯式搜羅今日所有策略 Excel 進行共振分析...")
    print("==================================================")

    excel_files = glob.glob(f"*_{date_str}/*.xlsx") + glob.glob(f"*_{date_str}*.xlsx")
    all_matched_rows = []

    for file_path in excel_files:
        if "🎨_全策略大會師總表_" in file_path:
            continue
        try:
            strat_name = os.path.basename(file_path).split('_')[0].replace(".xlsx", "")
            temp_df = pd.read_excel(file_path)
            
            if not temp_df.empty and '代號' in temp_df.columns:
                for _, row in temp_df.iterrows():
                    all_matched_rows.append({
                        '代號': str(row['代號']).strip(),
                        '股票名稱': str(row.get('股票名稱', row['代號'])).strip(),
                        '來自策略': strat_name,
                        '今日收盤': row.get('今日收盤', row.get('進場價(今日收盤)', None)),
                        '今昨量倍數': row.get('今昨量倍數', 1.0),
                        '今日成交量(張)': row.get('今日成交量(張)', 0),
                        '破底停損': row.get('破底停損', row.get('停損價', None)),
                        '目標壓力': row.get('目標壓力', row.get('目標價', None))
                    })
        except Exception as e:
            print(f"  ⚠️ 讀取策略報表 {file_path} 失敗: {e}")

    if all_matched_rows:
        base_df = pd.DataFrame(all_matched_rows)
        confluence_df = base_df.groupby(['代號', '股票名稱']).agg({
            '來自策略': lambda x: " | ".join(sorted(list(set(x)))),
            '今日收盤': 'last',
            '今昨量倍數': 'max',
            '今日成交量(張)': 'max',
            '破底停損': 'last',
            '目標壓力': 'last'
        }).reset_index()
        
        confluence_df['觸發策略次數'] = base_df.groupby(['代號', '股票名稱'])['來自策略'].count().reset_index()['來自策略']
        confluence_df = confluence_df.sort_values(by='觸發策略次數', ascending=False)
        
        master_folder = f"大會師總戰報_{date_str}"
        os.makedirs(master_folder, exist_ok=True)
        master_excel_path = os.path.join(master_folder, f"🎨_全策略大會師總表_{date_str}.xlsx")
        
        confluence_df.to_excel(master_excel_path, index=False)
        print(f"🎯 【大會師大成功】今日全策略共交叉整合 {len(confluence_df)} 檔標的，已順利存至 {master_excel_path}")
    else:
        print("🟡 提示：今日所有子策略均無篩選出符合型態的標的，大會師總戰報留空。")
        
    print("==================================================")
    print("🏁 全自動量化交易排程、智慧快取、共振大會師全部串接完畢！")
    print("==================================================")
except Exception as e:
    print(f"💥 後端共振大會師引擎執行時發生未預期錯誤: {e}")