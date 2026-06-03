import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
import yfinance as yf

# ================= 網頁基本設定 =================
st.set_page_config(page_title="Hank 量化交易戰情室", layout="wide", page_icon="📈")

st.title("🚀 Hank 專屬量化交易戰情室")
st.markdown("自動彙整每日策略掃描結果，結合 K 線圖表進行高效率覆盤。")
st.divider()

# ================= 側邊欄：設定篩選條件 =================
st.sidebar.header("🔍 篩選條件")

selected_date = st.sidebar.date_input("請選擇掃描日期", datetime.today())
date_str = selected_date.strftime("%Y%m%d")

strategies = {
    "朱家泓：回後買上漲 (基礎版)": {
        "folder": f"回後買上漲圖表(基礎版)_{date_str}",
        "excel": f"回後買上漲基礎版_{date_str}.xlsx"
    },
    "朱家泓：回後買上漲 (標準版 1+2)": {
        "folder": f"回後買上漲圖表_{date_str}",
        "excel": f"回後買上漲_標準版(1+2)_{date_str}.xlsx"
    },
    "朱家泓：回後買上漲 (嚴格版 1+2+3)": {
        "folder": f"回後買上漲圖表_{date_str}",
        "excel": f"回後買上漲_嚴格版(1+2+3)_{date_str}.xlsx"
    },
    "老余流：裸K破底翻 (賺賠比)": {
        "folder": f"老余裸K圖表_{date_str}",
        "excel": f"老余裸K_賺賠比精選_{date_str}.xlsx"
    },
    "型態：入住帝寶線 (多頭吞噬)": {
        "folder": f"帝寶線圖表_{date_str}",
        "excel": f"帝寶線_多頭吞噬精選_{date_str}.xlsx"
    },
    "均線：四均線糾結起漲": {
        "folder": f"四均線起漲圖表_{date_str}",
        "excel": f"四均線起漲精選_{date_str}.xlsx"
    },
    "型態：突破 ABC 下降切線": {
        "folder": f"ABC突破切線圖表_{date_str}",
        "excel": f"ABC突破切線精選_{date_str}.xlsx"
    }
}

selected_strategy = st.sidebar.selectbox("請選擇要查看的策略", list(strategies.keys()))

# ================= 主畫面資料抓取與顯示 =================
base_dir = os.getcwd()
strategy_info = strategies[selected_strategy]
folder_path = os.path.join(base_dir, strategy_info["folder"])
excel_path = os.path.join(folder_path, strategy_info["excel"])

if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    
    scan_price_col = None
    for col in ['今日收盤', '進場價(今日收盤)']:
        if col in df.columns:
            scan_price_col = col
            break
            
    if scan_price_col and '代號' in df.columns and not df.empty:
        with st.spinner("🔄 正在從雲端獲取今日最新行情並計算漲跌幅..."):
            tickers = df['代號'].tolist()
            try:
                latest_df = yf.download(tickers, period="2d", progress=False, auto_adjust=True)
                current_prices = {}
                if len(tickers) == 1:
                    ticker = tickers[0]
                    current_prices[ticker] = latest_df['Close'].iloc[-1]
                else:
                    for ticker in tickers:
                        if ticker in latest_df['Close'].columns:
                            current_prices[ticker] = latest_df['Close'][ticker].iloc[-1]
                            
                df['篩選日收盤價'] = df[scan_price_col].round(2)
                df['目前最新價'] = df['代號'].map(current_prices).round(2)
                df['自篩選日漲跌幅'] = ((df['目前最新價'] - df['篩選日收盤價']) / df['篩選日收盤價'] * 100).round(2)
                
                if scan_price_col != '篩選日收盤價' and scan_price_col in df.columns:
                    df = df.drop(columns=[scan_price_col])
                    
                cols = list(df.columns)
                if '股票名稱' in cols:
                    idx = cols.index('股票名稱') + 1
                    new_fields = ['篩選日收盤價', '突破最新價' if '目前最新價' not in new_fields else '目前最新價', '自篩選日漲跌幅']
                    new_fields = ['篩選日收盤價', '目前最新價', '自篩選日漲跌幅']
                    for field in reversed(new_fields):
                        if field in cols:
                            cols.remove(field)
                            cols.insert(idx, field)
                    df = df[cols]
                    
            except Exception as e:
                st.sidebar.warning(f"即時行情獲取失敗: {e}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("今日符合檔數", f"{len(df)} 檔")
    if '自篩選日漲跌幅' in df.columns and not df.empty:
        avg_ret = df['自篩選日漲跌幅'].mean()
        col2.metric("清單平均報酬", f"{avg_ret:+.2f}%")
    
    st.subheader(f"📊 {selected_strategy} - 數據清單")
    
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "篩選日收盤價": st.column_config.NumberColumn("篩選日收盤", format="%.2f 元"),
            "目前最新價": st.column_config.NumberColumn("目前最新價", format="%.2f 元"),
            "自篩選日漲跌幅": st.column_config.NumberColumn("自篩選日漲跌幅", format="%+.2f%%"),
            "雅虎股市連結": st.column_config.LinkColumn("雅虎股市連結", display_text="點我查看")
        }
    )
    
    st.divider()
    st.subheader("👁️ 實戰圖表檢視 (左手數據，右手開槍)")
    
    img_cols = st.columns(2)
    for idx, row in df.iterrows():
        ticker = str(row['代號']).split('.')[0]
        stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
        img_filename = f"{ticker}_{stock_name}.png"
        img_path = os.path.join(folder_path, img_filename)
        
        col_to_use = img_cols[idx % 2]
        with col_to_use:
            if os.path.exists(img_path):
                # 🌟 核心防爆機制：防止壞圖、假圖搞崩網頁
                try:
                    image = Image.open(img_path)
                    st.image(image, caption=f"{ticker} {stock_name}", use_container_width=True)
                except Exception:
                    st.warning(f"⚠️ {ticker} {stock_name} 的 K 線圖表格式產生中或暫時無法讀取。")
            else:
                st.warning(f"找不到 {ticker} {stock_name} 的圖表檔案")
else:
    st.info(f"☕ **操盤手紀律：** 在 **{selected_date.strftime('%Y-%m-%d')}**，【{selected_strategy}】策略無符合篩選條件的標的。")