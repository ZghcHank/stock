import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
import yfinance as yf
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================================================
# ⚙️ 網頁基本設定
# =========================================================================
st.set_page_config(page_title="Hank 飆股完全體量化戰情室", layout="wide", page_icon="👑")

st.title("👑 Hank 飆股決策量化戰情室")
st.markdown("已解鎖：**大盤多空濾網 / 智慧特徵標籤 / 資金聚落 / 實戰賺賠比量尺 / K線分流快篩 / 3D動態K線 / 移動止損筆記本**")
st.divider()

base_dir = os.getcwd()

# =========================================================================
# 🛡️ 核心模組一：大盤多空濾網高亮看板 (TAIEX Regime Filter)
# =========================================================================
if os.path.exists("market_regime.json"):
    try:
        with open("market_regime.json", "r", encoding="utf-8") as f:
            regime_data = json.load(f)
        if regime_data["color"] == "success":
            st.success(f"### 🎯 系統加權趨勢：{regime_data['regime']} (大盤點位: {regime_data['close']} | 月線: {regime_data['ma20']} | 季線: {regime_data['ma60']})\n👉 **作多建議**：{regime_data['advice']}")
        else:
            st.error(f"### 🚨 系統加權趨勢：{regime_data['regime']} (大盤點位: {regime_data['close']} | 月線: {regime_data['ma20']} | 季線: {regime_data['ma60']})\n👉 **風控建議**：{regime_data['advice']}")
    except Exception:
        pass

# =========================================================================
# 🔍 側邊欄控制中心
# =========================================================================
st.sidebar.header("🔍 戰術篩選中心")
selected_date = st.sidebar.date_input("請選擇歷史覆盤日期", datetime.today())
date_str = selected_date.strftime("%Y%m%d")

st.sidebar.subheader("⚡ [大會師分頁] K線快篩分流器")
filter_volume = st.sidebar.slider("1. 最低成交量門檻 (張)", 0, 10000, 500, step=100)
filter_multiple = st.sidebar.slider("2. 最低量能暴發倍數", 1.0, 5.0, 1.0, step=0.5)
only_show_confluence = st.sidebar.checkbox("3. 🔥 只看多策略共振焦點股", value=False)
hide_high_price = st.sidebar.checkbox("4. 💸 隱藏高價股 (股價 > 300元)", value=False)

# =========================================================================
# 🗺️ 策略映射與輔助字典 (完美對齊 Hank 實際生成的所有子資料夾名稱)
# =========================================================================
strategies_map = {
    "朱家泓：回後買上漲 (基礎版)": {"folder": "回後買上漲圖表(基礎版)_", "excel": "回後買上漲基礎版_"},
    "朱家泓：回後買上漲 (標準版 1+2)": {"folder": "回後買上漲圖表_", "excel": "回後買上漲_標準版(1+2)_"},
    "朱家泓：回後買上漲 (嚴格版 1+2+3)": {"folder": "回後買上漲圖表_", "excel": "回後買上漲_嚴格版(1+2+3)_"},
    "老余流：裸K破底翻 (賺賠比)": {"folder": "老余裸K圖表_", "excel": "老余裸K_賺賠比精選_"},
    "型態：入住帝寶線 (多頭吞噬)": {"folder": "帝寶線圖表_", "excel": "帝寶線_多頭吞噬精選_"},
    "均線：四均線糾結起漲": {"folder": "四均線起漲圖表_", "excel": "四均線起漲精選_"},
    "型態：突破 ABC 下降切線": {"folder": "ABC突破切線圖表_", "excel": "ABC突破切線精選_"}
}

def get_industry_fallback(ticker_prefix):
    mapping = {
        "3483": "散熱模組", "6126": "電子零組件", "2317": "不敗代工龍頭", "4741": "特種化學",
        "2528": "營建工程", "4542": "半導體設備", "8390": "綠能環保", "6525": "生技醫療",
        "7780": "生技醫療", "3356": "光電光通訊", "6861": "生技醫療"
    }
    return mapping.get(ticker_prefix, "半導體與其他電子")

# =========================================================================
# 🔮 核心功能：2D/3D 互動式 Plotly K 線引擎 (動態密鑰防護版)
# =========================================================================
def draw_plotly_candlestick(ticker, d_str, chart_key):
    cache_file = os.path.join(base_dir, "yf_cache", d_str, f"{ticker}_1y.pkl")
    if os.path.exists(cache_file):
        df_chart = pd.read_pickle(cache_file)
    else:
        df_chart = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        
    if df_chart.empty:
        st.warning("無法獲取此標的之歷史硬碟數據。")
        return
        
    close_series = df_chart['Close'].values.flatten() if isinstance(df_chart['Close'], pd.DataFrame) else df_chart['Close']
    
    df_chart['5MA'] = pd.Series(close_series, index=df_chart.index).rolling(5).mean()
    df_chart['20MA'] = pd.Series(close_series, index=df_chart.index).rolling(20).mean()
    df_chart['60MA'] = pd.Series(close_series, index=df_chart.index).rolling(60).mean()
    
    df_plot = df_chart.tail(125)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_width=[0.3, 0.7])
    
    fig.add_trace(go.Candlestick(
        x=df_plot.index, 
        open=df_plot['Open'].values.flatten(), 
        high=df_plot['High'].values.flatten(),
        low=df_plot['Low'].values.flatten(), 
        close=df_plot['Close'].values.flatten(), 
        name='K線'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['5MA'], line=dict(color='orange', width=1), name='5MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['20MA'], line=dict(color='magenta', width=1.5), name='20MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['60MA'], line=dict(color='cyan', width=2), name='60MA'), row=1, col=1)
    
    close_vals = df_plot['Close'].values.flatten()
    open_vals = df_plot['Open'].values.flatten()
    vol_colors = ['red' if c >= o else 'green' for c, o in zip(close_vals, open_vals)]
    
    fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'].values.flatten(), marker_color=vol_colors, name='成交量'), row=2, col=1)
    
    fig.update_layout(xaxis_rangeslider_visible=False, height=400, margin=dict(t=10, b=10, l=10, r=10), template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

# =========================================================================
# 🏗️ 建立大三重黃金頁籤架構
# =========================================================================
tab1, tab2, tab3 = st.tabs(["🎯 今日全策略大會師總報", "🔍 個別策略獨立覆盤點兵", "📝 Hank 觀測部位與移動停損筆記"])

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
                for t in tickers:
                    try:
                        h_file = os.path.join(base_dir, "yf_cache", date_str, f"{t}_1y.pkl")
                        history = pd.read_pickle(h_file) if os.path.exists(h_file) else yf.download(t, period="6m", progress=False, auto_adjust=True)
                        if not history.empty:
                            c_val = history['Close'].values.flatten()[-1]
                            current_prices[t] = float(c_val)
                            half_year_highs[t] = float(history['Close'].values.flatten().max())
                    except Exception:
                        pass

            # 智慧校正：當天覆盤則最新市價完美對齊篩選日收盤
            live_prices = df_master['代號'].map(current_prices).astype(float).round(2)
            if date_str == datetime.today().strftime("%Y%m%d"):
                df_master['目前最新價'] = df_master['今日收盤']
                df_master['自篩選日漲跌幅'] = 0.0
            else:
                df_master['目前最新價'] = live_prices
                df_master['自篩選日漲跌幅'] = (((df_master['目前最新價'] - df_master['今日收盤']) / df_master['今日收盤']) * 100).round(2)

            df_master['創半年高'] = df_master.apply(lambda r: r['目前最新價'] >= half_year_highs.get(r['代號'], 0), axis=1)
            df_master['產業族群'] = df_master['代號'].apply(lambda x: get_industry_fallback(x.split('.')[0]))

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
                st.bar_chart(df_master['產業族群'].value_counts(), horizontal=True, height=140)

            st.divider()
            
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
                if cp >= tp: return "🎉 已抵達目標壓力"
                return f"🔴停損({int(sl)})---🟢目前({int(cp)})---🔵目標({int(tp)}) [賺賠: {rr:.1f}]"

            df_filtered['⚡ 飆股特徵標籤'] = df_filtered.apply(generate_badges, axis=1)
            df_filtered['🎯 實戰開槍預警 (賺賠比量尺)'] = df_filtered.apply(generate_rr_scale, axis=1)

            df_filtered = df_filtered.fillna({'破底停損': '-', '目標壓力': '-', '目前最新價': 0.0, '自篩選日漲跌幅': 0.0})

            st.dataframe(
                df_filtered[['代號', '股票名稱', '產業族群', '⚡ 飆股特徵標籤', '🎯 實戰開槍預警 (賺賠比量尺)', '今日收盤', '目前最新價', '自篩選日漲跌幅', '來自策略']], 
                use_container_width=True, hide_index=True
            )

            st.divider()
            st.subheader("👁️ 大會師過濾標的 - 雙重影線圖表特寫")
            if df_filtered.empty:
                st.warning("🟡 在目前的快篩條件下，沒有符合條件的 K 線圖表可顯示。")
            else:
                img_cols = st.columns(2)
                for idx, (_, row) in enumerate(df_filtered.iterrows()):
                    ticker = str(row['代號']).split('.')[0]
                    stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
                    
                    # 完美涵蓋 Hank 的兩種回後買上漲子資料夾路徑
                    strategies_folders = [
                        f"老余裸K圖表_{date_str}", f"帝寶線圖表_{date_str}", 
                        f"ABC突破切線圖表_{date_str}", f"四均線起漲圖表_{date_str}", 
                        f"回後買上漲圖表_{date_str}", f"回後買上漲圖表(基礎版)_{date_str}"
                    ]
                    img_path = None
                    for folder in strategies_folders:
                        p = os.path.join(base_dir, folder, f"{ticker}_{stock_name}.png")
                        if os.path.exists(p): img_path = p; break
                    
                    with img_cols[idx % 2]:
                        st.markdown(f"### 📊 {ticker} {stock_name} (標籤: {row['⚡ 飆股特徵標籤']})")
                        if img_path and os.path.exists(img_path):
                            st.image(Image.open(img_path), use_container_width=True)
                        with st.expander("🔮 點我展開 3D 互動式動態 K 線與精密均線特寫"):
                            draw_plotly_candlestick(row['代號'], date_str, chart_key=f"tab1_{ticker}_{idx}")
        else:
            st.info("☕ 操盤手紀律：今日全市場全策略大會師，皆未發現符合條件標的。")
    else:
        st.info(f"☕ 尚未產出本日大會師總表 Excel。請確認雲端大指揮官控制台是否已執行。")

# =========================================================================
# 🔍 TAB 2：個別策略獨立覆盤點兵
# =========================================================================
with tab2:
    st.header("🎯 個別獨立策略詳細覆盤")
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
            with st.spinner("🔄 正在單獨調閱最新市價行情..."):
                strat_tickers = df_strat['代號'].tolist()
                strat_prices = {}
                for t in strat_tickers:
                    try:
                        latest_df = yf.download(t, period="2d", progress=False, auto_adjust=True)
                        if not latest_df.empty and 'Close' in latest_df.columns:
                            val = latest_df['Close'].values.flatten()[-1]
                            strat_prices[t] = float(val)
                    except Exception:
                        pass
                        
                df_strat['篩選日收盤'] = pd.to_numeric(df_strat[scan_price_col], errors='coerce').round(2)
                raw_latest = df_strat['代號'].map(strat_prices).astype(float).round(2)
                
                if date_str == datetime.today().strftime("%Y%m%d"):
                    df_strat['目前最新價'] = df_strat['篩選日收盤']
                    df_strat['自篩選日漲跌幅'] = 0.0
                else:
                    df_strat['目前最新價'] = raw_latest
                    df_strat['自篩選日漲跌幅'] = (((df_strat['目前最新價'] - df_strat['篩選日收盤']) / df_strat['篩選日收盤']) * 100).round(2)
                
                if scan_price_col != '篩選日收盤' and scan_price_col in df_strat.columns:
                    df_strat = df_strat.drop(columns=[scan_price_col])
                cols = list(df_strat.columns)
                if '股票名稱' in cols:
                    idx = cols.index('股票名稱') + 1
                    for field in reversed(['篩選日收盤', '目前最新價', '自篩選日漲跌幅']):
                        if field in cols: cols.remove(field); cols.insert(idx, field)
                    df_strat = df_strat[cols]
        
        df_strat = df_strat.fillna('-')
        st.dataframe(df_strat, use_container_width=True, hide_index=True)
        st.divider()
        
        strat_img_cols = st.columns(2)
        for idx, row in df_strat.iterrows():
            ticker = str(row['代號']).split('.')[0]
            stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
            specific_img_path = os.path.join(strat_folder, f"{ticker}_{stock_name}.png")
            
            with strat_img_cols[idx % 2]:
                st.markdown(f"### 📊 {ticker} {stock_name}")
                if os.path.exists(specific_img_path):
                    st.image(Image.open(specific_img_path), use_container_width=True)
                with st.expander("🔮 點我展開 3D 互動式動態 K 線與精密均線特寫"):
                    draw_plotly_candlestick(row['代號'], date_str, chart_key=f"tab2_{ticker}_{idx}")
    else:
        st.info(f"☕ 操盤手紀律：在 {selected_date.strftime('%Y-%m-%d')} 這天，該策略無符合篩選條件的標的。")

# =========================================================================
# 📝 TAB 3：觀測部位與移動停損筆記本
# =========================================================================
with tab3:
    st.header("📝 Hank 觀測部位與移動停損追蹤器")
    st.markdown("在這裡建立自訂追蹤部位，自動發動**「長線利潤追蹤與動態移動止損」**（自持股創高後回檔 X% 預警通知）。")
    
    wl_path = "watchlist.json"
    if os.path.exists(wl_path):
        try:
            with open(wl_path, "r", encoding="utf-8") as f: watchlist = json.load(f)
        except Exception: watchlist = []
    else: watchlist = []

    with st.form("新增觀測股票表單"):
        c1, c2, c3, c4 = st.columns(4)
        new_t = c1.text_input("股票代號 (例: 2317.TW 或 3483.TWO)")
        new_n = c2.text_input("股票名稱 (例: 鴻海)")
        new_p = c3.number_input("進場成本價", min_value=0.0, step=0.1)
        new_ts = c4.slider("移動止損門檻 (%)", 3.0, 15.0, 10.0, step=0.5)
        submit_btn = st.form_submit_button("🚀 強勢鎖定並鎖入防守部位")
        
        if submit_btn and new_t and new_p > 0:
            watchlist.append({
                "ticker": new_t.strip().upper(), "name": new_n.strip(),
                "entry_price": new_p, "trailing_stop_pct": new_ts,
                "highest_price": new_p, "date": datetime.today().strftime("%Y-%m-%d")
            })
            with open(wl_path, "w", encoding="utf-8") as f: json.dump(watchlist, f, ensure_ascii=False, indent=4)
            st.success(f"✨ 成功將 {new_n} ({new_t}) 鎖入動態追蹤守護名單！")
            st.rerun()

    if watchlist:
        wl_df = pd.DataFrame(watchlist)
        wl_tickers = wl_df['ticker'].tolist()
        
        with st.spinner("📥 正在連線雲端洗滌追蹤部位之最新動態價格..."):
            for item in watchlist:
                try:
                    t = item["ticker"]
                    live_wl = yf.download(t, period="2d", progress=False, auto_adjust=True)
                    if not live_wl.empty and 'Close' in live_wl.columns:
                        cp = live_wl['Close'].values.flatten()[-1]
                        item["currently_latest_price"] = round(float(cp), 2)
                        if item["currently_latest_price"] > item["highest_price"]:
                            item["highest_price"] = item["currently_latest_price"]
                except Exception:
                    pass

        final_wl = []
        for item in watchlist:
            cp = item.get("currently_latest_price", item["entry_price"])
            hp = item["highest_price"]
            ts_pct = item["trailing_stop_pct"]
            
            stop_price = round(hp * (1 - ts_pct / 100), 2)
            pnl = round(((cp - item["entry_price"]) / item["entry_price"]) * 100, 2)
            status = "📈 獲利奔跑中" if cp > stop_price else "🚨 觸發移動停損！請全數出清！"
            
            final_wl.append({
                "鎖定日期": item["date"], "代號": item["ticker"], "股票名稱": item["name"],
                "進場成本": item["entry_price"], "歷史最高價": hp, "動態停損價": stop_price,
                "目前市價": cp, "實質總報酬": f"{pnl:+}%", "安全狀態預警": status
            })
            
        res_df = pd.DataFrame(final_wl)
        
        def highlight_status(val):
            if "🚨" in str(val): return 'background-color: #ffcccc; color: black; font-weight: bold;'
            return 'background-color: #d4edda; color: black;'
            
        st.subheader("📊 Hank 實戰觀測部位即時追蹤面板")
        st.dataframe(res_df.style.map(highlight_status, subset=['安全狀態預警']), use_container_width=True, hide_index=True)
        
        if st.button("🗑️ 清空所有觀測部位 (重新開始)"):
            if os.path.exists(wl_path): os.remove(wl_path)
            st.rerun()