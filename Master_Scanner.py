import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np

# ================= 1. 雲端解鎖：建立瀏覽器偽裝外衣 =================
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
})

# ================= 2. 初始化設定與日期定義 =================
today_str = datetime.today().strftime("%Y%m%d")
print(f"==================================================")
print(f"🚀 Hank 台股量化自動化掃描系統啟動 | 執行日期: {today_str}")
print(f"==================================================")

# 模擬台股精選追蹤清單 (可自由增減，格式必須為 .TW 或 .TWO)
stock_pool = [
    "2641.TWO", "3483.TWO", "6126.TWO", "2497.TW", "5388.TW", 
    "3071.TWO", "3227.TWO", "6558.TW", "6443.TW", "4526.TW",
    "2330.TW", "2317.TW", "2454.TW", "2308.TW", "2382.TW"
]

# ================= 3. 核心功能：安全資料下載器 =================
def fetch_market_data(tickers):
    print(f"📥 正在透過安全雲端通道下載 {len(tickers)} 檔台股歷史數據...")
    try:
        # 🌟 關鍵關鍵：將 session=session 傳入，偽裝成瀏覽器下載
        df_all = yf.download(
            tickers=tickers, 
            period="1y", 
            session=session, 
            group_by='ticker', 
            auto_adjust=True, 
            progress=False
        )
        return df_all
    except Exception as e:
        print(f"❌ 雲端數據下載失敗: {e}")
        return None

# ================= 4. 六大策略邏輯核心 (封裝示範) =================
# 💡 提示：此處已幫您把計算好、符合 Dashboard 的欄位排版設定完畢。
#    您可以直接將您原本各別策略（如朱家泓、老余裸K）的精準數學公式填入對應的 function 中。

def run_zhujiahong_strategy(stock_data, tickers, level="standard"):
    """ 朱家泓：回後買上漲策略 """
    results = []
    for ticker in tickers:
        try:
            df = stock_data[ticker] if len(tickers) > 1 else stock_data
            if df.empty or len(df) < 60: continue
            
            # --- [您的策略數學公式區] ---
            # 範例計算：多頭排列與回測均線
            df['MA5'] = df['Close'].rolling(5).mean()
            df['MA10'] = df['Close'].rolling(10).mean()
            df['MA20'] = df['Close'].rolling(20).mean()
            
            close_today = df['Close'].iloc[-1]
            close_yesterday = df['Close'].iloc[-2]
            high_yesterday = df['High'].iloc[-2]
            vol_today = df['Volume'].iloc[-1]
            vol_yesterday = df['Volume'].iloc[-2]
            
            # 判定條件 (範例：今日收盤突破昨日高點且量增)
            if close_today > high_yesterday and vol_today > vol_yesterday:
                results.append({
                    "代號": ticker,
                    "股票名稱": ticker.split('.')[0], # 實際運行可接名稱對照表
                    "今日收盤": round(close_today, 2),
                    "昨日高點": round(high_yesterday, 2),
                    "今昨量倍數": round(vol_today / max(vol_yesterday, 1), 1),
                    "今日成交量(張)": int(vol_today // 1000),
                    "昨日成交量(張)": int(vol_yesterday // 1000),
                    "均線狀態": "5>10>20 多頭排列" if df['MA5'].iloc[-1] > df['MA10'].iloc[-1] else "均線糾結",
                    "回測支撐": "踩10MA" if close_today >= df['MA10'].iloc[-1] else "正常突破",
                    "雅虎股市連結": f"https://tw.stock.yahoo.com/quote/{ticker}"
                })
        except Exception:
            continue
    return pd.DataFrame(results)

def run_laoyu_strategy(stock_data, tickers):
    """ 老余流：裸K破底翻策略 """
    results = []
    # --- [請在此填入老余策略的數學公式與過濾條件] ---
    return pd.DataFrame(results)

def run_dibao_strategy(stock_data, tickers):
    """ 型態：入住帝寶線 (多頭吞噬) """
    results = []
    # --- [請在此填入多頭吞噬策略的數學公式] ---
    return pd.DataFrame(results)

def run_ma_cluster_strategy(stock_data, tickers):
    """ 均線：四均線糾結起漲 """
    results = []
    # --- [請在此填入四均線糾結策略的數學公式] ---
    return pd.DataFrame(results)

def run_abc_breakout_strategy(stock_data, tickers):
    """ 型態：突破 ABC 下降切線 """
    results = []
    # --- [請在此填入 ABC 切線突破策略的數學公式] ---
    return pd.DataFrame(results)

# ================= 5. 主程式執行與檔案自動化歸檔 =================
def main():
    # 執行資料下載
    market_data = fetch_market_data(stock_pool)
    if market_data is None:
        print("🛑 無法獲取行情，流程終止。")
        return

    # 定義策略清單、產出資料夾名稱與對應的 Excel 檔名（完美對齊 Dashboard）
    strategy_tasks = {
        "朱家泓：回後買上漲 (基礎版)": {
            "data": run_zhujiahong_strategy(market_data, stock_pool, "basic"),
            "folder": f"回後買上漲圖表(基礎版)_{today_str}",
            "filename": f"回後買上漲基礎版_{today_str}.xlsx"
        },
        "朱家泓：回後買上漲 (標準版 1+2)": {
            "data": run_zhujiahong_strategy(market_data, stock_pool, "standard"),
            "folder": f"回後買上漲圖表_{today_str}",
            "filename": f"回後買上漲_標準版(1+2)_{today_str}.xlsx"
        },
        "朱家泓：回後買上漲 (嚴格版 1+2+3)": {
            "data": run_zhujiahong_strategy(market_data, stock_pool, "strict"),
            "folder": f"回後買上漲圖表_{today_str}",
            "filename": f"回後買上漲_嚴格版(1+2+3)_{today_str}.xlsx"
        },
        "老余流：裸K破底翻 (賺賠比)": {
            "data": run_laoyu_strategy(market_data, stock_pool),
            "folder": f"老余裸K圖表_{today_str}",
            "filename": f"老余裸K_賺賠比精選_{today_str}.xlsx"
        },
        "型態：入住帝寶線 (多頭吞噬)": {
            "data": run_dibao_strategy(market_data, stock_pool),
            "folder": f"帝寶線圖表_{today_str}",
            "filename": f"帝寶線_多頭吞噬精選_{today_str}.xlsx"
        },
        "均線：四均線糾結起漲": {
            "data": run_ma_cluster_strategy(market_data, stock_pool),
            "folder": f"四均線起漲圖表_{today_str}",
            "filename": f"四均線起漲精選_{today_str}.xlsx"
        },
        "型態：突破 ABC 下降切線": {
            "data": run_abc_breakout_strategy(market_data, stock_pool),
            "folder": f"ABC突破切線圖表_{today_str}",
            "filename": f"ABC突破切線精選_{today_str}.xlsx"
        }
    }

    # 開始遍歷執行與存檔
    for name, task in strategy_tasks.items():
        df_res = task["data"]
        folder = task["folder"]
        filename = task["filename"]
        
        # 建立專屬策略日期的資料夾
        os.makedirs(folder, exist_ok=True)
        
        if df_res.empty:
            print(f"⚪ 策略【{name}】今日無符合標的。")
            # 💡 順應保護機制：今天如果沒股票，就不產出 Excel，網頁端會自動呈現精緻優雅提示。
            # 如果之前有舊檔，可以選擇性清除：
            target_file = os.path.join(folder, filename)
            if os.path.exists(target_file):
                os.remove(target_file)
        else:
            # 有符合標的，存成 Excel 供網頁讀取
            excel_out_path = os.path.join(folder, filename)
            df_res.to_excel(excel_out_path, index=False)
            print(f"🟢 策略【{name}】成功篩選出 {len(df_res)} 檔標的！已儲存至 {excel_out_path}")
            
            # 🖼️ [繪圖區簡介]
            # 您可以在此處遍歷 df_res['代號']，產出帶有支撐切線與技術指標的 K 線圖
            # 檔名存成例如: f"{ticker}_{stock_name}.png" 放入 folder 中即可。
            # 範例模擬產生空白圖檔(測試網頁用)：
            for _, row in df_res.iterrows():
                img_name = f"{str(row['代號']).split('.')[0]}_{row['股票名稱']}.png"
                img_full_path = os.path.join(folder, img_name)
                if not os.path.exists(img_full_path):
                    # 建立一個測試用的標記小檔案
                    with open(img_full_path, 'w') as f: f.write('IMAGE_PLACEHOLDER')

    print(f"==================================================")
    # 🌟 本地執行自動 Git 同步區 (在 GitHub Actions 雲端時會由 yml 接手自動略過)
    print(f"🏁 全市場量化掃描完畢！等待同步模組發動...")
    print(f"==================================================")

if __name__ == "__main__":
    main()