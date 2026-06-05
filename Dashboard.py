import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
import yfinance as yf

# ================= 網頁基本設定 =================
st.set_page_config(page_title="Hank 飆股核心量化戰情室", layout="wide", page_icon="👑")

st.title("👑 Hank 飆股決策量化戰情室")
st.markdown("融合 **多策略共振 / 智慧型特徵標籤 / 資金聚落分析 / 實戰賺賠比量尺 / K線分流快篩** 的完全體操盤介面。")
st.divider()

# ================= 側邊欄設定與快篩分流器 (功能 5) =================
st.sidebar.header("🔍 戰術篩選中心")
selected_date = st.sidebar.date_input("請選擇歷史覆盤日期", datetime.today())
date_str = selected_date.strftime("%Y%m%d")

st.sidebar.subheader("⚡ K線圖圖表快篩分流器")
filter_volume = st.sidebar.slider("1. 最低成交量門檻 (張)", 0, 10000, 500, step=100)
filter_multiple = st.sidebar.slider("2. 最低量能暴發倍數", 1.0, 5.0, 1.0, step=0.5)
only_show_confluence = st.sidebar.checkbox("3. 🔥 只看多策略共振焦點股", value=False)
hide_high_price = st.sidebar.checkbox("4. 💸 隱藏高價股 (股價 > 300元)", value=False)

# 讀取今日大會師總表
base_dir = os.getcwd()
master_folder = os.path.join(base_dir, f"大會師總戰報_{date_str}")
master_excel = os.path.join(master_folder, f"🎨_全策略大會師總表_{date_str}.xlsx")

# 模擬一個簡單快速的台股產業聚落對照字典 (功能 3 的防護網，若 yfinance info 太慢時備用)
def get_industry_fallback(ticker_prefix):
    mapping = {
        "3483": "散熱模組", "6126": "電子零組件", "2317": "不敗代工龍頭", "4741": "特種化學",
        "2528": "營建工程", "4542": "半導體設備", "8390": "綠能環保", "6525": "生技醫療",
        "7780": "生技醫療", "3356": "光電光通訊", "6861": "生技醫療"
    }
    return mapping.get(ticker_prefix, "半導體與其他電子")

# ================= 主畫面核心邏輯 =================
if os.path.exists(master_excel):
    df_master = pd.read_excel(master_excel)
    
    if not df_master.empty:
        # 一次性向雲端獲取即時大數據
        tickers = df_master['代號'].astype(str).tolist()
        current_prices = {}
        half_year_highs = {}
        
        with st.spinner("📥 正在雲端洗滌即時行情與計算半年新高特徵..."):
            try:
                # 抓取歷史與即時數據來判斷是否創半年新高 (功能 2)
                for t in tickers:
                    history = yf.download(t, period="6m", progress=False, auto_adjust=True)
                    if not history.empty:
                        current_prices[t] = float(history['Close'].iloc[-1])
                        half_year_highs[t] = float(history['Close'].max())
            except Exception:
                pass

        # 寫入即時比價數據
        df_master['目前最新價'] = df_master['代號'].map(current_prices).astype(float).round(2)
        df_master['自篩選日漲跌幅'] = (((df_master['目前最新價'] - df_master['今日收盤']) / df_master['今日收盤']) * 100).round(2)
        
        # 建立動態計算欄位
        df_master['創半年高'] = df_master.apply(lambda r: r['目前最新價'] >= half_year_highs.get(r['代號'], 0), axis=1)
        df_master['產業族群'] = df_master['代號'].apply(lambda x: get_industry_fallback(x.split('.')[0]))

        # =========================================================================
        # 🌟 功能 1 & 功能 3：共振焦點與產業聚落看板 (網頁最頂端發光區)
        # =========================================================================
        col_top1, col_top2 = st.columns([6, 4])
        
        with col_top1:
            st.subheader("🔥 今日多策略共振金牌焦點")
            confluence_stocks = df_master[df_master['觸發策略次數'] >= 2]
            if not confluence_stocks.empty():
                for _, row in confluence_stocks.iterrows():
                    st.info(f"🏆 **{row['股票名稱']} ({row['代號'].split('.')[0]})**：同時觸發了 **【{row['來自策略']}】**！主力進場訊號強烈，極具波段大潛力！")
            else:
                st.markdown("<p style='color:gray;'>🟢 今日暫無多策略共振標的，清單皆為單一策略精選。</p>", unsafe_allow_html=True)
                
        with col_top2:
            st.subheader("📊 今日资金聚落分析")
            sector_counts = df_master['產業族群'].value_counts()
            st.bar_chart(sector_counts, horizontal=True, height=180)

        st.divider()

        # =========================================================================
        # 🌟 功能 5：動態過濾快篩器執行
        # =========================================================================
        df_filtered = df_master.copy()
        df_filtered = df_filtered[df_filtered['今日成交量(張)'] >= filter_volume]
        df_filtered = df_filtered[df_filtered['今昨量倍數'] >= filter_multiple]
        if only_show_confluence:
            df_filtered = df_filtered[df_filtered['觸發策略次數'] >= 2]
        if hide_high_price:
            df_filtered = df_filtered[df_filtered['目前最新價'] <= 300]

        # =========================================================================
        # 🌟 功能 2 & 功能 4：智慧標籤與實戰賺賠比量尺表格
        # =========================================================================
        st.subheader("📊 滿血追蹤數據清單 (自動計算核心特徵)")

        # 1. 計算智慧型特徵標籤 (功能 2)
        def generate_badges(row):
            badges = []
            if row['觸發策略次數'] >= 2: badges.append("🔥多策略共振")
            if row['今昨量倍數'] >= 2.0: badges.append("⚡巨量突破")
            if row['創半年高']: badges.append("👑創半年新高")
            if row['今日成交量(張)'] > 3000: badges.append("🐳主力大進場")
            return " / ".join(badges) if badges else "✨型態符合"

        # 2. 計算賺賠比視覺化符號 (功能 4)
        def generate_rr_scale(row):
            sl = row['破底停損']
            tp = row['目標壓力']
            cp = row['目前最新價']
            if pd.isna(sl) or pd.isna(tp) or pd.isna(cp) or sl >= tp:
                return "📐 數據不足，以K線圖為主"
            
            # 計算賺賠比 (Reward to Risk ratio)
            risk = cp - sl
            reward = tp - cp
            rr_ratio = (reward / risk) if risk > 0 else 0
            
            # 線型刻度視覺化
            if cp <= sl: return "🚨 已跌破停損點 🚨"
            if cp >= tp: return "🎉 已抵達目標壓力 突破中!"
            
            # 用文字指針畫出相對位置： [停損]-------[目前價]----------------[目標]
            return f"🔴停損({int(sl)})---🟢目前({int(cp)})---🔵目標({int(tp)}) [賺賠比: {rr_ratio:.1f}]"

        df_filtered['⚡ 飆股特徵標籤'] = df_filtered.apply(generate_badges, axis=1)
        df_filtered['🎯 實戰開槍預警 (賺賠比量尺)'] = df_filtered.apply(generate_rr_scale, axis=1)

        # 整理最終顯示表格
        df_display = df_filtered[[
            '代號', '股票名稱', '產業族群', '⚡ 飆股特徵標籤', '🎯 實戰開槍預警 (賺賠比量尺)', 
            '今日收盤', '目前最新價', '自篩選日漲跌幅', '來自策略'
        ]]

        st.dataframe(
            df_display, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "今日收盤": st.column_config.NumberColumn("篩選日收盤", format="%.2f 元"),
                "目前最新價": st.column_config.NumberColumn("目前最新價", format="%.2f 元"),
                "自篩選日漲跌幅": st.column_config.NumberColumn("自篩選日漲跌幅", format="%+.2f%%"),
                "來自策略": st.column_config.TextColumn("觸發的策略來源")
            }
        )

        # =========================================================================
        # 🖼️ K線圖顯示區 (完美結合快篩分流)
        # =========================================================================
        st.divider()
        st.subheader("👁️ 篩選後標的 - 半年期 K 線圖特寫檢視")
        
        if df_filtered.empty:
            st.warning("🟡 報告長官：在目前的快篩條件下，沒有符合條件的 K 線圖表可顯示，請放寬側邊欄門檻。")
        else:
            img_cols = st.columns(2)
            for idx, (_, row) in enumerate(df_filtered.iterrows()):
                ticker = str(row['代號']).split('.')[0]
                stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
                
                # 動態配對資料夾路徑，去找真正畫好的半年期圖片
                # 遍歷目前可能存在的所有策略子資料夾去找圖
                strat_first = row['來自策略'].split(' | ')[0]
                
                # 自動對齊先前的資料夾命名規則
                strategies_folders = [
                    f"老余裸K圖表_{date_str}", f"帝寶線圖表_{date_str}", 
                    f"ABC突破切線圖表_{date_str}", f"四均線起漲圖表_{date_str}", f"回後買上漲圖表_{date_str}"
                ]
                
                img_path = None
                for folder in strategies_folders:
                    p = os.path.join(base_dir, folder, f"{ticker}_{stock_name}.png")
                    if os.path.exists(p):
                        img_path = p
                        break
                
                with img_cols[idx % 2]:
                    if img_path and os.path.exists(img_path):
                        try:
                            st.image(Image.open(img_path), caption=f"📊 {ticker} {stock_name} (標籤: {row['⚡ 飆股特徵標籤']})", use_container_width=True)
                        except Exception:
                            st.warning(f"⚠️ {ticker} {stock_name} 的 K 線圖格式產生中...")
                    else:
                        st.warning(f"找不到 {ticker} {stock_name} 的半年期圖表檔案，可能今日該特定策略未開槍。")
    else:
        st.info("☕ **操盤手紀律：** 今日全市場各大策略大會師，皆未發現符合特徵的標的。耐心等待大盤落底！")
else:
    st.info(f"☕ **大會師通知：** 在 **{selected_date.strftime('%Y-%m-%d')}** 這天，您的雲端大指揮官尚未產出「大會師總表 Excel」。請確認 Actions 有正常跑完喔！")