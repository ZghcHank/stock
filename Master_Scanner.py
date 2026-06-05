import os
import sys
import subprocess
import glob
from datetime import datetime
import pandas as pd
import yfinance as yf
import requests

print("==================================================")
print(f"🚀 Hank 雲端指揮官控制台啟動 | 執行日期: {datetime.today().strftime('%Y%m%d')}")
print("==================================================")

# ==========================================================================================
# 📊 步驟一：全自動網頁爬蟲 - 實時取得台股上市/上櫃全市場股票清單 (約 1900+ 檔)
# ==========================================================================================
def get_all_taiwan_tickers():
    print(">> 正在從臺灣證券交易所與櫃買中心取得最新的全市場股票清單...")
    tickers = []
    
    # 1. 抓取上市股票 (Mode 2)
    try:
        res_twse = requests.get("https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", timeout=15)
        df_twse = pd.read_html(res_twse.text)[0]
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
        df_tpex = pd.read_html(res_tpex.text)[0]
        # 櫃買中心網頁欄位名稱有空格，做防呆相容處理
        col_name = df_tpex.iloc[0].dropna().values[0]
        df_tpex.columns = df_tpex.iloc[0]
        df_tpex = df_tpex.iloc[1:]
        for val in df_tpex[col_name].dropna():
            parts = str(val).split()
            if len(parts) >= 2 and len(parts[0]) == 4 and parts[0].isdigit():
                tickers.append(f"{parts[0]}.TWO")
    except Exception as e:
        print(f"  ⚠️ 上櫃股票清單抓取局部受阻: {e}")

    # 3. 終極防護網：如果遇到網路大斷線，自動啟動實戰核心骨幹清單，確保程式絕不崩潰
    tickers = list(set(tickers))
    if not tickers:
        print("  🚨 [警告] 證交所網路連線中斷！自動啟動核心精選標的進行防護防爆...")
        tickers = ["2317.TW", "2330.TW", "3483.TWO", "6126.TWO", "4741.TW", "2528.TW", "4542.TW", "8390.TWO", "6525.TW", "2360.TW"]
        
    print(f"  ✅ 總共集結 {len(tickers)} 檔全市場股票準備進行掃描。")
    return tickers

# 呼叫函數取得清單
tickers_list = get_all_taiwan_tickers()

# ==========================================================================================
# ⚡ 步驟二：大宗批次預載引擎 - 1分鐘內將 1900+ 檔股票打包下載至硬碟，實現 0 秒秒讀
# ==========================================================================================
try:
    print("\n==================================================")
    print("⚡ [黃金快取] 啟動當日全市場大數據一次性高速打包預載...")
    print("==================================================")
    
    date_str = datetime.today().strftime("%Y%m%d")
    cache_dir = os.path.join("yf_cache", date_str)
    os.makedirs(cache_dir, exist_ok=True)
    
    # 採用 300 檔股票為一組的「大宗聯合成批下載」，效率比單檔下載飆升數百倍
    chunk_size = 300
    for i in range(0, len(tickers_list), chunk_size):
        chunk = tickers_list[i:i+chunk_size]
        print(f"📥 正在極速包裏下載第 {i} 到 {min(i+chunk_size, len(tickers_list))} 檔股票的年度大數據...")
        try:
            # group_by='ticker' 會自動將 300 檔的多重欄位依股票代號做完美分類
            data = yf.download(chunk, period="1y", group_by="ticker", progress=False, auto_adjust=True)
            
            for ticker in chunk:
                if ticker in data.columns.levels[0]:
                    ticker_df = data[ticker].dropna(how='all')
                    if not ticker_df.empty:
                        # 使用 Pickle 極速二進位格式儲存於硬碟快取中
                        ticker_df.to_pickle(os.path.join(cache_dir, f"{ticker}_1y.pkl"))
        except Exception as e:
            print(f"  ⚠️ 此批次打包下載失敗，子策略稍後將自動走網路補償網。錯誤: {e}")
            
    print("==================================================")
    print("✨ [快取完工] 全市場數據已成功收納至硬碟！子策略即將開啟 0 秒解鎖模式！")
    print("==================================================\n")
except Exception as e:
    print(f"💥 快取預載引擎發生未預期錯誤: {e}")

# ==========================================================================================
# 🏃‍♂️ 步驟三：策略調度核心排程 - 依序啟動你 D 槽中的各個量化策略子副程式
# ==========================================================================================
# 📝 請確保這裡填寫的副程式檔名，跟你 D 槽實體檔案的大小寫、中文字完全一致
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
            # 呼叫系統執行 python 子程式
            result = subprocess.run(["python", script], check=True)
            if result.returncode == 0:
                print(f"🟢 【{script}】雲端快取秒讀執行成功！")
            else:
                print(f"❌ 【{script}】回報異常，退出碼: {result.returncode}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 【{script}】執行過程中發生錯誤: {e}")
    else:
        print(f"🟡 找不到檔案 【{script}】，大指揮官自動跳過該策略。")

# ==========================================================================================
# 🎨 步驟四：五大飆股模組 - 後端全策略數據大會師與多策略共振交叉分析引擎
# ==========================================================================================
try:
    print("\n==================================================")
    print("🎨 啟動後端大會師：地毯式搜羅今日所有策略 Excel 進行共振分析...")
    print("==================================================")

    date_str = datetime.today().strftime("%Y%m%d")
    # 地毯式搜尋今日各策略產出的 Excel 報表
    excel_files = glob.glob(f"*_{date_str}/*.xlsx") + glob.glob(f"*_{date_str}*.xlsx")
    all_matched_rows = []

    for file_path in excel_files:
        # 防呆：避免重複讀取到大會師總表自己
        if "🎨_全策略大會師總表_" in file_path:
            continue
        try:
            # 從 Excel 檔名提取純粹的策略標題
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
        
        # 進行最高端的群組交叉共振計算
        confluence_df = base_df.groupby(['代號', '股票名稱']).agg({
            '來自策略': lambda x: " | ".join(sorted(list(set(x)))), # 串接所有觸發的策略名稱
            '今日收盤': 'last',
            '今昨量倍數': 'max',
            '今日成交量(張)': 'max',
            '破底停損': 'last',
            '目標壓力': 'last'
        }).reset_index()
        
        # 精準統計觸發次數（共振頻率）
        confluence_df['觸發策略次數'] = base_df.groupby(['代號', '股票名稱'])['來自策略'].count().reset_index()['來自策略']
        confluence_df = confluence_df.sort_values(by='觸發策略次數', ascending=False)
        
        # 建立專屬大會師總戰報目錄供前端 Dashboard 讀取
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