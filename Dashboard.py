import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
import yfinance as yf

# ================= 網頁基本設定 =================
st.set_page_config(page_title="Hank 飆股完全體量化戰情室", layout="wide", page_icon="👑")

st.title("👑 Hank 飆股決策量化戰情室")
st.markdown("融合 **全策略大會師看板** 與 **個別策略深入覆盤** 的終極雙重火力操盤介面。")
st.divider()

# ================= 全系統策略資料夾映射定義 =================
strategies_map = {
    "朱家泓：回後買上漲 (基礎版)": {
        "folder": "回後買上漲圖表(基礎版)_",
        "excel": "回後買上漲基礎版_"
    },
    "朱家泓：回後買上漲 (標準版 1+2)": {
        "folder": "回後買上漲圖表_",
        "excel": "回後買上漲_標準版(1+2)_"
    },
    "朱家泓：回後買上漲 (嚴格版 1+2+3)": {
        "folder": "回後買上漲圖表_",
        "excel": "回後買上漲_嚴格版(1+2+3)_"
    },
    "老余流：裸K破底翻 (賺賠比)": {
        "folder": "老余裸K圖表_",
        "excel": "老余裸K_賺賠比精選_"
    },
    "型態：入住帝寶線 (多頭吞噬)": {
        "folder": "帝寶線圖表_",
        "excel": "帝寶線_多頭吞噬精選_"
    },
    "均線：四均線糾結起漲": {
        "folder": "四均線起漲圖表_",
        "excel": "四均線起漲精選_"
    },
    "型態：突破 ABC 下降切線": {
        "folder": "ABC突破切線圖表_",
        "excel": "ABC突破切線精選_"
    }
}

# ================= 側邊欄設定 (全域日期 + 分頁一快篩) =================
st.sidebar.header("🔍 戰術篩選中心")
selected_date = st.sidebar.date_input("請選擇歷史覆盤日期", datetime.today())
date_str = selected_date.strftime("%Y%m%d")

st.sidebar.subheader("⚡ [分頁一專用] K線快篩分流器")
filter_volume = st.sidebar.slider("1. 最低成交量門檻 (張)", 0, 10000, 500, step=100)
filter_multiple = st.sidebar.slider("2. 最低量能暴發倍數", 1.0, 5.0, 1.0, step=0.5)
only_show_confluence = st.sidebar.checkbox("3. 🔥 只看多策略共振焦點股", value=False)
hide_high_price = st.sidebar.checkbox("4. 💸 隱藏高價股 (股價 > 300元)", value=False)

base_dir = os.getcwd()

# 模擬一個簡單快速的台股產業聚落對照字典
def get_industry_fallback(ticker_prefix):
    mapping = {
        "3483": "散熱模組", "6126": "電子零組件", "2317": "不敗代工龍頭", "4741": "特種化學",
        "2528": "營建工程", "4542": "半導體設備", "8390": "綠能環保", "6525": "生技醫療",
        "7780": "生技醫療", "3356": "光電光通訊", "6861": "生技醫療"
    }
    return mapping.get(ticker_prefix, "半導體與其他電子")

# =========================================================================
# 🌟 建立黃金雙分頁 (Tabs) 架構
# =========================================================================
tab1, tab2 = st.tabs(["🎯 今日全策略大會師總報", "🔍 個別策略獨立覆盤點兵"])

# =========================================================================
# 🏠 TAB 1：今日全策略大會師總報
# =========================================================================
with tab1:
    master_folder = os.path.join(base_dir, f"大會師總戰報_{date_str}")
    master_excel = os.path.join(master_folder, f"🎨_全策略大會師總表_{date_str}.xlsx")

    if os.path.exists(master_excel):
        df_master = pd.read_excel(master_excel)
        
        if not df_master.empty:
            tickers = df_master['代號'].astype(str).tolist()
            current_prices = {}
            half_year_highs = {}
            
            with st.spinner("📥 正在大會師洗滌即時行情與計算半年新高..."):
                try:
                    for t in tickers:
                        history = yf.download(t, period="6m", progress=False, auto_adjust=True)
                        if not history.empty:
                            current_prices[t] = float(history['Close'].iloc[-1])
                            half_year_highs[t] = float(history['Close'].max())
                except Exception: pass

            df_master['目前最新價'] = df_master['代號'].map(current_prices).astype(float).round(2)
            df_master['自篩選日漲跌幅'] = (((df_master['目前最新價'] - df_master['今日收盤']) / df_master['今日收盤']) * 100).round(2)
            df_master['創半年高'] = df_master.apply(lambda r: r['目前最新價'] >= half_year_highs.get(r['代號'], 0), axis=1)
            df_master['產業族群'] = df_master['代號'].apply(lambda x: get_industry_fallback(x.split('.')[0]))

            # 看板頭部：共振焦點與產業聚落
            col_top1, col_top2 = st.columns([6, 4])
            with col_top1:
                st.subheader("🔥 今日多策略共振金牌焦點")
                confluence_stocks = df_master[df_master['觸發策略次數'] >= 2]
                if not confluence_stocks.empty:
                    for _, row in confluence_stocks.iterrows():
                        st.info(f"🏆 **{row['股票名稱']} ({row['代號'].split('.')[0]})**：同時觸發了 **【{row['來自策略']}】**！極具波段大潛力！")
                else:
                    st.markdown("<p style='color:gray;'>🟢 今日暫無多策略共振標的，清單皆為單一策略精選。</p>", unsafe_allow_html=True)
            with col_top2:
                st.subheader("📊 今日資金聚落分析")
                st.bar_chart(df_master['產業族群'].value_counts(), horizontal=True, height=160)

            st.divider()

            # 快篩器執行過濾
            df_filtered = df_master.copy()
            df_filtered = df_filtered[df_filtered['今日成交量(張)'] >= filter_volume]
            df_filtered = df_filtered[df_filtered['今昨量倍數'] >= filter_multiple]
            if only_show_confluence: df_filtered = df_filtered[df_filtered['觸發策略次數'] >= 2]
            if hide_high_price: df_filtered = df_filtered[df_filtered['目前最新價'] <= 300]

            st.subheader("📊 大會師整合追蹤清單")
            
            def generate_badges(row):
                b = []
                if row['觸發策略次數'] >= 2: b.append("🔥多策略共振")
                if row['今昨量倍數'] >= 2.0: b.append("⚡巨量突破")
                if row['創半年高']: b.append("👑創半年高")
                if row['今日成交量(張)'] > 3000: b.append("🐳主力大進場")
                return " / ".join(b) if b else "✨型態符合"

            def generate_rr_scale(row):
                sl, tp, cp = row['破底停損'], row['目標壓力'], row['目前最新價']
                if pd.isna(sl) or pd.isna(tp) or pd.isna(cp) or sl >= tp: return "📐 數據不足"
                risk, reward = cp - sl, tp - cp
                rr = (reward / risk) if risk > 0 else 0
                if cp <= sl: return "🚨 已跌破停損點 🚨"
                if cp >= tp: return "🎉 已抵達目標壓力 突破中!"
                return f"🔴停損({int(sl)})---🟢目前({int(cp)})---🔵目標({int(tp)}) [賺賠: {rr:.1f}]"

            df_filtered['⚡ 飆股特徵標籤'] = df_filtered.apply(generate_badges, axis=1)
            df_filtered['🎯 實戰開槍預警 (賺賠比量尺)'] = df_filtered.apply(generate_rr_scale, axis=1)

            st.dataframe(
                df_filtered[['代號', '股票名稱', '產業族群', '⚡ 飆股特徵標籤', '🎯 實戰開槍預警 (賺賠比量尺)', '今日收盤', '目前最新價', '自篩選日漲跌幅', '來自策略']], 
                use_container_width=True, hide_index=True,
                column_config={"自篩選日漲跌幅": st.column_config.NumberColumn("自篩選日漲跌幅", format="%+.2f%%")}
            )

            # K線圖檢視
            st.divider()
            st.subheader("👁️ 大會師過濾標的 - 半年期 K 線圖特寫")
            if df_filtered.empty:
                st.warning("🟡 在目前的快篩條件下，沒有符合條件的 K 線圖表可顯示。")
            else:
                img_cols = st.columns(2)
                for idx, (_, row) in enumerate(df_filtered.iterrows()):
                    ticker = str(row['代號']).split('.')[0]
                    stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
                    strategies_folders = [f"老余裸K圖表_{date_str}", f"帝寶線圖表_{date_str}", f"ABC突破切線圖表_{date_str}", f"四均線起漲圖表_{date_str}", f"回後買上漲圖表_{date_str}"]
                    img_path = None
                    for folder in strategies_folders:
                        p = os.path.join(base_dir, folder, f"{ticker}_{stock_name}.png")
                        if os.path.exists(p): img_path = p; break
                    
                    with img_cols[idx % 2]:
                        if img_path and os.path.exists(img_path):
                            st.image(Image.open(img_path), caption=f"📊 {ticker} {stock_name} ({row['⚡ 飆股特徵標籤']})", use_container_width=True)
                        else:
                            st.warning(f"找不到 {ticker} {stock_name} 的圖表檔案。")
        else:
            st.info("☕ 今日全市場策略大會師皆未發現符合特徵標的。")
    else:
        st.info(f"☕ 尚未產出本日大會師總表 Excel。請確認雲端大指揮官是否有發動。")

# =========================================================================
# 🔍 TAB 2：個別策略獨立覆盤點兵 (完美加回原汁原味的獨立查看功能！)
# =========================================================================
with tab2:
    st.header("🎯 個別獨立策略詳細覆盤")
    st.markdown("在這裡你可以挑選單一特定策略，調閱該策略當初完整的 Excel 欄位數據與專屬 K 線。")
    
    # 策略下拉選擇器直接放置於頁面中
    selected_strategy = st.selectbox("請選擇您要深入覆盤的單一策略", list(strategies_map.keys()))
    
    strat_info = strategies_map[selected_strategy]
    strat_folder = os.path.join(base_dir, f"{strat_info['folder']}{date_str}")
    strat_excel = os.path.join(strat_folder, f"{strat_info['excel']}{date_str}.xlsx")
    
    if os.path.exists(strat_excel):
        df_strat = pd.read_excel(strat_excel)
        
        scan_price_col = None
        for col in ['今日收盤', '進場價(今日收盤)']:
            if col in df_strat.columns: scan_price_col = col; break
                
        if scan_price_col and '代號' in df_strat.columns and not df_strat.empty:
            with st.spinner(f"🔄 正在單獨調閱【{selected_strategy}】的最新市價行情..."):
                strat_tickers = df_strat['代號'].tolist()
                try:
                    latest_df = yf.download(strat_tickers, period="2d", progress=False, auto_adjust=True)
                    strat_prices = {}
                    for t in strat_tickers:
                        if 'Close' in latest_df.columns:
                            val = latest_df['Close'][t].iloc[-1] if (isinstance(latest_df['Close'], pd.DataFrame) and t in latest_df['Close'].columns) else latest_df['Close'].iloc[-1]
                            if isinstance(val, pd.Series): val = val.iloc[0] if not val.empty else None
                            if val is not None: strat_prices[t] = float(val)
                                
                    df_strat['篩選日收盤'] = pd.to_numeric(df_strat[scan_price_col], errors='coerce').round(2)
                    df_strat['目前最新價'] = df_strat['代號'].map(strat_prices).astype(float).round(2)
                    df_strat['自篩選日漲跌幅'] = (((df_strat['目前最新價'] - df_strat['篩選日收盤']) / df_strat['篩選日收盤']) * 100).round(2)
                    
                    if scan_price_col != '篩選日收盤' and scan_price_col in df_strat.columns:
                        df_strat = df_strat.drop(columns=[scan_price_col])
                        
                    # 排版優化：將價格與漲跌幅排在股票名稱後面
                    cols = list(df_strat.columns)
                    if '股票名稱' in cols:
                        idx = cols.index('股票名稱') + 1
                        for field in reversed(['篩選日收盤', '目前最新價', '自篩選日漲跌幅']):
                            if field in cols: cols.remove(field); cols.insert(idx, field)
                        df_strat = df_strat[cols]
                except Exception as e:
                    st.warning(f"即時行情獲取失敗: {e}")
        
        # 顯示個別策略的數據卡片
        col_s1, col_s2 = st.columns(2)
        col_s1.metric(f"【{selected_strategy}】符合檔數", f"{len(df_strat)} 檔")
        if '自篩選日漲跌幅' in df_strat.columns and not df_strat.empty:
            avg_strat_ret = pd.to_numeric(df_strat['自篩選日漲跌幅'], errors='coerce').mean()
            if not pd.isna(avg_strat_ret):
                col_s2.metric("此清單今日平均報酬", f"{avg_strat_ret:+.2f}%")
                
        st.subheader("📊 原始策略完整數據清單")
        st.dataframe(
            df_strat, use_container_width=True, hide_index=True,
            column_config={
                "篩選日收盤": st.column_config.NumberColumn("篩選日收盤", format="%.2f 元"),
                "目前最新價": st.column_config.NumberColumn("目前最新價", format="%.2f 元"),
                "自篩選日漲跌幅": st.column_config.NumberColumn("自篩選日漲跌幅", format="%+.2f%%"),
                "雅虎股市連結": st.column_config.LinkColumn("雅虎股市連結", display_text="點我查看")
            }
        )
        
        # 個別策略的專屬 K 線圖展示
        st.divider()
        st.subheader(f"👁️ 【{selected_strategy}】專屬 K 線圖檢視")
        
        strat_img_cols = st.columns(2)
        for idx, row in df_strat.iterrows():
            ticker = str(row['代號']).split('.')[0]
            stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
            img_filename = f"{ticker}_{stock_name}.png"
            specific_img_path = os.path.join(strat_folder, img_filename)
            
            with strat_img_cols[idx % 2]:
                if os.path.exists(specific_img_path):
                    st.image(Image.open(specific_img_path), caption=f"📊 {ticker} {stock_name} (專屬線型)", use_container_width=True)
                else:
                    st.warning(f"找不到 {ticker} {stock_name} 的專屬 K 線圖，可能圖片名稱與 Excel 未完全對齊。")
    else:
        st.info(f"☕ **操盤手紀律：** 在 **{selected_date.strftime('%Y-%m-%d')}** 這天，【{selected_strategy}】策略無符合篩選條件的標的。")