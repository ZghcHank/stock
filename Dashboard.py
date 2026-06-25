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
# 🎨 1. 頂級 UI/UX 視覺重構：完美轉譯 Sandbox CSS 核心美學與玻璃擬態
# =========================================================================
st.set_page_config(
    page_title="Hank Quant Command Center", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# 注入 Sandbox 專屬高質感 Slate 深色調色盤
st.markdown("""
    <style>
    /* 全域背景與基底文字洗滌 */
    .stApp {
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
    }
    
    /* 側邊欄 Sandbox 化 */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
    
    /* 頂級主標題與副標題 */
    .dashboard-title {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.04em;
        margin-bottom: 5px;
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .dashboard-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 25px;
        font-weight: 500;
    }
    
    /* 半透明玻璃擬態數據卡片 (Grid Cards) */
    .sandbox-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 22px;
        border-radius: 12px;
        backdrop-filter: blur(8px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .sandbox-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateY(-2px);
    }
    .card-label {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .card-val {
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    
    /* 專業控制面板區塊標題 */
    .panel-header {
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 30px;
        margin-bottom: 15px;
        padding-left: 12px;
        border-left: 4px solid #38bdf8;
    }
    
    /* 現代化 Streamlit Tabs 頁籤樣式修正 */
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        background-color: transparent !important;
        border: none !important;
        padding: 14px 28px !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #94a3b8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
    
    /* 表格與內建元件暗色系調和 */
    div[data-testid="stDataFrame"] {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# ⚙️ 2. 系統底層核心與環境變數設定
# =========================================================================
base_dir = os.getcwd()

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
# 🧭 3. 側邊欄戰術控制台
# =========================================================================
st.sidebar.markdown("<div style='padding: 10px 0px;'><span style='font-size:20px; font-weight:800; color:#38bdf8;'>Hank Quant</span></div>", unsafe_allow_html=True)
selected_date = st.sidebar.date_input("🗓️ 選擇覆盤日期", datetime.today())
date_str = selected_date.strftime("%Y%m%d")

st.sidebar.markdown("<br><span style='color:#64748b; font-weight:600; font-size:12px;'>📊 GRID FILTERS</span>", unsafe_allow_html=True)
filter_volume = st.sidebar.slider("最低成交量門檻 (張)", 0, 10000, 500, step=100)
filter_multiple = st.sidebar.slider("最低量能暴發倍數", 1.0, 5.0, 1.0, step=0.5)
only_show_confluence = st.sidebar.checkbox("🔥 只看多策略共振焦點股", value=False)
hide_high_price = st.sidebar.checkbox("💸 隱藏高價股 (股價 > 300元)", value=False)

# =========================================================================
# 👑 4. 頂部看板：系統主標題與大盤多空濾網
# =========================================================================
st.markdown('<div class="dashboard-title">Hank Quant Intelligence System</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">機構法人級多模態智慧量化戰情室控制台</div>', unsafe_allow_html=True)

if os.path.exists("market_regime.json"):
    try:
        with open("market_regime.json", "r", encoding="utf-8") as f:
            regime_data = json.load(f)
        if regime_data["color"] == "success":
            st.success(f"### 🎯 大盤安全係數判讀：{regime_data['regime']} (指數點位: {regime_data['close']} | 季線位階: {regime_data['ma60']})\n👉 **多頭開槍建議**：{regime_data['advice']}")
        else:
            st.error(f"### 🚨 大盤安全係數判讀：{regime_data['regime']} (指數點位: {regime_data['close']} | 季線位階: {regime_data['ma60']})\n👉 **空頭防守建議**：{regime_data['advice']}")
    except Exception:
        pass

# =========================================================================
# 🔮 核心繪圖引擎功能：3D 互動式 Plotly K 線組件
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
    
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['5MA'], line=dict(color='#38bdf8', width=1.5), name='5MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['20MA'], line=dict(color='#a855f7', width=1.8), name='20MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['60MA'], line=dict(color='#10b981', width=2.2), name='60MA'), row=1, col=1)
    
    close_vals = df_plot['Close'].values.flatten()
    open_vals = df_plot['Open'].values.flatten()
    vol_colors = ['#f43f5e' if c >= o else '#10b981' for c, o in zip(close_vals, open_vals)]
    
    fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'].values.flatten(), marker_color=vol_colors, name='成交量'), row=2, col=1)
    
    fig.update_layout(xaxis_rangeslider_visible=False, height=360, margin=dict(t=10, b=10, l=10, r=10), template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

# =========================================================================
# 🏗️ 建立大四重黃金頁籤分流架構 (🌟 正式結合 ETF 長線複利面板)
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs(["⚡ 今日全策略大會師總報", "🔍 個別策略獨立覆盤點兵", "🛡️ Hank 觀測部位與移動停損筆記", "🧱 核心 ETF 複利資產配置"])

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
            
            with st.spinner("📥 正在連線雲端洗滌即時行情數據..."):
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

            # 智慧時間差對齊機制
            live_prices = df_master['代號'].map(current_prices).astype(float).round(2)
            if date_str == datetime.today().strftime("%Y%m%d"):
                df_master['目前最新價'] = df_master['今日收盤']
                df_master['自篩選日漲跌幅'] = 0.0
            else:
                df_master['currently_latest_price' if 'currently_latest_price' in df_master.columns else '目前最新價'] = live_prices
                df_master['自篩選日漲跌幅'] = (((df_master['目前最新價'] - df_master['今日收盤']) / df_master['今日收盤']) * 100).round(2)

            df_master['創半年高'] = df_master.apply(lambda r: r['目前最新價'] >= half_year_highs.get(r['代號'], 0), axis=1)
            df_master['產業族群'] = df_master['代號'].apply(lambda x: get_industry_fallback(x.split('.')[0]))

            confluence_stocks = df_master[df_master['觸發策略次數'] >= 2]
            
            grid_col1, grid_col2, grid_col3, grid_col4 = st.columns(4)
            grid_col1.markdown(f'<div class="sandbox-card"><div class="card-label">📋 總篩選標的數</div><div class="card-val" style="color:#ffffff;">{len(df_master)} <span style="font-size:14px;color:#64748b;">STOCKS</span></div></div>', unsafe_allow_html=True)
            grid_col2.markdown(f'<div class="sandbox-card"><div class="card-label">🔥 多策略共振焦點</div><div class="card-val" style="color:#f43f5e;">{len(confluence_stocks)} <span style="font-size:14px;color:#64748b;">CONFLUENCE</span></div></div>', unsafe_allow_html=True)
            grid_col3.markdown(f'<div class="sandbox-card"><div class="card-label">👑 創半年新高個股</div><div class="card-val" style="color:#eab308;">{df_master["創半年高"].sum()} <span style="font-size:14px;color:#64748b;">HIGHS</span></div></div>', unsafe_allow_html=True)
            
            focus_name = "N/A"
            if not confluence_stocks.empty: focus_name = str(confluence_stocks['股票名稱'].iloc[0])
            elif not df_master.empty: focus_name = str(df_master['股票名稱'].iloc[0])
            grid_col4.markdown(f'<div class="sandbox-card"><div class="card-label">⭐ 今日第一優先標的</div><div class="card-val" style="color:#38bdf8; font-size:22px; padding-top:4px;">{focus_name}</div></div>', unsafe_allow_html=True)

            if not confluence_stocks.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                for _, row in confluence_stocks.iterrows():
                    st.info(f"🏆 **【多策略共振焦點股】{row['股票名稱']} ({row['代號'].split('.')[0]})**：同時觸發了 **【{row['來自策略']}】**！主力資金強烈匯集！")

            st.markdown('<div class="panel-header">📊 當日主力資金聚落熱度圖</div>', unsafe_allow_html=True)
            st.bar_chart(df_master['產業族群'].value_counts(), horizontal=True, height=140)

            df_filtered = df_master.copy()
            df_filtered = df_filtered[df_filtered['今日成交量(張)'] >= filter_volume]
            df_filtered = df_filtered[df_filtered['今昨量倍數'] >= filter_multiple]
            if only_show_confluence: df_filtered = df_filtered[df_filtered['觸發策略次數'] >= 2]
            if hide_high_price: df_filtered = df_filtered[df_filtered['目前最新價'] <= 300]

            st.markdown('<div class="panel-header">📋 大會師終極整合追蹤明細</div>', unsafe_allow_html=True)
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

            st.markdown('<div class="panel-header">👁️ 全自動多模態影線圖表作戰特寫</div>', unsafe_allow_html=True)
            if df_filtered.empty:
                st.warning("🟡 在目前的快篩條件下，沒有符合條件的 K 線圖表可顯示。")
            else:
                img_cols = st.columns(2)
                for idx, (_, row) in enumerate(df_filtered.iterrows()):
                    ticker = str(row['代號']).split('.')[0]
                    stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
                    
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
                        st.markdown(f"#### 📊 {ticker} {stock_name} <span style='color:#38bdf8; font-size:13px;'>[{row['⚡ 飆股特徵標籤']}]</span>", unsafe_allow_html=True)
                        if img_path and os.path.exists(img_path):
                            st.image(Image.open(img_path), use_container_width=True)
                        with st.expander("🔮 展開 3D 互動式動態 K 線與精密均線特寫"):
                            draw_plotly_candlestick(row['代號'], date_str, chart_key=f"tab1_{ticker}_{idx}")
        else:
            st.info("☕ 操盤手紀律：今日全市場大會師，皆未發現符合條件標的。")
    else:
        st.info(f"☕ 尚未產出本日大會師總表 Excel。請確認雲端大指揮官是否已執行。")

# =========================================================================
# 🔍 TAB 2：個別策略獨立覆盤點兵
# =========================================================================
with tab2:
    st.markdown('<div class="panel-header">🎯 個別策略詳細歷史覆盤調閱</div>', unsafe_allow_html=True)
    selected_strategy = st.selectbox("🗂️ 請選擇您要深入覆盤的單一特定策略", list(strategies_map.keys()))
    strat_info = strategies_map[selected_strategy]
    strat_folder = os.path.join(base_dir, f"{strat_info['folder']}{date_str}")
    strat_excel = os.path.join(strat_folder, f"{strat_info['excel']}{date_str}.xlsx")
    
    if os.path.exists(strat_excel):
        df_strat = pd.read_excel(strat_excel)
        scan_price_col = None
        for col in ['今日收盤', '進場價(今日收盤)']:
            if col in df_strat.columns: scan_price_col = col; break
                
        if scan_price_col and '代號' in df_strat.columns and not df_strat.empty:
            with st.spinner("🔄 正在調閱獨立策略即時行情..."):
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
        
        st.markdown('<div class="panel-header">👁️ 該特定型態專屬線型特寫畫廊</div>', unsafe_allow_html=True)
        strat_img_cols = st.columns(2)
        for idx, row in df_strat.iterrows():
            ticker = str(row['代號']).split('.')[0]
            stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
            specific_img_path = os.path.join(strat_folder, f"{ticker}_{stock_name}.png")
            
            with strat_img_cols[idx % 2]:
                st.markdown(f"#### 📊 {ticker} {stock_name}")
                if os.path.exists(specific_img_path):
                    st.image(Image.open(specific_img_path), use_container_width=True)
                with st.expander("🔮 展開 3D 互動式動態 K 線與精密均線特寫"):
                    draw_plotly_candlestick(row['代號'], date_str, chart_key=f"tab2_{ticker}_{idx}")
    else:
        st.info(f"☕ 操盤手紀律：在指定日期下，該特定型態目前並無符合型態的標的。")

# =========================================================================
# 🛡️ TAB 3：觀測部位與移動停損筆記本
# =========================================================================
with tab3:
    st.markdown('<div class="panel-header">🛡️ Hank 實戰追蹤部位與動態移動停損防護盾</div>', unsafe_allow_html=True)
    st.markdown("當你實際開槍進場買進、或想高度觀測某檔強勢股時，在此鎖定。系統會全自動發動**「移動停損追蹤機制」**（自進場最高點回檔 X% 強制發出高亮平倉警戒）。")
    
    wl_path = "watchlist.json"
    if os.path.exists(wl_path):
        try:
            with open(wl_path, "r", encoding="utf-8") as f: watchlist = json.load(f)
        except Exception: watchlist = []
    else: watchlist = []

    with st.form("Sandbox新增觀測股票表單"):
        c1, c2, c3, c4 = st.columns(4)
        new_t = c1.text_input("💎 股票代號 (例: 2317.TW 或 3483.TWO)")
        new_n = c2.text_input("📛 股票名稱 (例: 鴻海)")
        new_p = c3.number_input("💵 買入進場成本價", min_value=0.0, step=0.1)
        new_ts = c4.slider("🛡️ 移動停損門檻百分比 (%)", 3.0, 15.0, 10.0, step=0.5)
        submit_btn = st.form_submit_button("🚀 注入防守密鑰，啟動資安防護監控")
        
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
        
        with st.spinner("📥 正在向雲端清洗追蹤部位之即時價格與利潤率..."):
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
            status = "📈 獲利奔跑中" if cp > stop_price else "🚨 觸發移動停損！請立即平倉全數出場！"
            
            final_wl.append({
                "鎖定日期": item["date"], "代號": item["ticker"], "股票名稱": item["name"],
                "進場成本": item["entry_price"], "歷史最高價": hp, "動態停損價": stop_price,
                "目前市價": cp, "實質總報酬": f"{pnl:+}%", "安全狀態預警": status
            })
            
        res_df = pd.DataFrame(final_wl)
        
        def highlight_status(val):
            if "🚨" in str(val): return 'background-color: #fca5a5; color: #7f1d1d; font-weight: bold;'
            return 'background-color: #bbf7d0; color: #14532d;'
            
        st.subheader("📊 Hank 實戰觀測部位實時追蹤主面板")
        st.dataframe(res_df.style.map(highlight_status, subset=['安全狀態预警']), use_container_width=True, hide_index=True)
        
        if st.button("🗑️ 清空所有觀測部位 (重新開始歸零)"):
            if os.path.exists(wl_path): os.remove(wl_path)
            st.rerun()

# =========================================================================
# 🧱 TAB 4：核心 ETF 複利資產配置 (🌟 深度整合大眾 ETF 規劃網站功能)
# =========================================================================
with tab4:
    st.markdown('<div class="panel-header">🧱 核心防守：長線 ETF 資產配置與定期定額複利增長控制台</div>', unsafe_allow_html=True)
    st.markdown("將低風險的『大盤/高股息 ETF 長線投資』與手上的『飆股策略』結合。本分頁完美複刻了機構級複利資產模擬器。")
    
    # 建立雙欄版面：左側輸入、右側即時看報表卡片
    calc_col1, calc_col2 = st.columns([4, 6])
    
    with calc_col1:
        st.markdown("#### ⚙️ 複利與定期定額配置參數")
        init_invest = st.number_input("1. 初始單筆投入本金 (元)", min_value=0, value=100000, step=10000)
        monthly_invest = st.number_input("2. 每月定期定額投入金額 (元)", min_value=0, value=15000, step=1000)
        annual_rate = st.slider("3. 預期年化報酬率 (%)", min_value=1.0, max_value=20.0, value=9.5, step=0.5)
        invest_years = st.slider("4. 預計長期投資年限 (年)", min_value=1, max_value=40, value=15, step=1)
        
        # 進行嚴密的複利滾存數學模型推算
        total_months = invest_years * 12
        monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
        
        months = []
        principal_history = []
        wealth_history = []
        interest_history = []
        
        current_wealth = init_invest
        current_principal = init_invest
        
        for m in range(1, total_months + 1):
            current_wealth = current_wealth * (1 + monthly_rate) + monthly_invest
            current_principal += monthly_invest
            
            # 每隔一年紀錄一次，用來畫高質感的面積圖
            if m % 12 == 0 or m == 1:
                year_num = round(m / 12) if m > 1 else 0
                months.append(f"第 {year_num} 年" if year_num > 0 else "初始")
                principal_history.append(current_principal)
                wealth_history.append(current_wealth)
                interest_history.append(max(0, current_wealth - current_principal))

    with calc_col2:
        # 致敬 Sandbox 奢華玻璃卡片，秀出試算終點的財富成果
        st.markdown("#### 🏆 預期長線財富增長終值")
        kpi_etf1, kpi_etf2, kpi_etf3 = st.columns(3)
        kpi_etf1.markdown(f'<div class="sandbox-card"><div class="card-label">💰 累計最終財富</div><div class="card-val" style="color:#22c55e;">{round(current_wealth):,} 元</div></div>', unsafe_allow_html=True)
        kpi_etf2.markdown(f'<div class="sandbox-card"><div class="card-label">💵 總計投入本金</div><div class="card-val" style="color:#ffffff;">{round(current_principal):,} 元</div></div>', unsafe_allow_html=True)
        kpi_etf3.markdown(f'<div class="sandbox-card"><div class="card-label">🔥 純複利時間獲利</div><div class="card-val" style="color:#38bdf8;">{round(max(0, current_wealth - current_principal)):,} 元</div></div>', unsafe_allow_html=True)
        
        # 繪製對方的經典圖表：Plotly 本金 vs 複利 堆疊面積增長圖
        fig_etf = go.Figure()
        fig_etf.add_trace(go.Scatter(
            x=months, y=principal_history,
            mode='lines', line=dict(width=0.5, color='#94a3b8'),
            stackgroup='one', name='總投入本金成本', fillcolor='rgba(148, 163, 184, 0.2)'
        ))
        fig_etf.add_trace(go.Scatter(
            x=months, y=interest_history,
            mode='lines', line=dict(width=0.5, color='#38bdf8'),
            stackgroup='one', name='純時間累積複利獲利', fillcolor='rgba(56, 189, 248, 0.4)'
        ))
        fig_etf.update_layout(
            height=280, margin=dict(t=15, b=10, l=10, r=10),
            template='plotly_dark', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_etf, use_container_width=True, key="etf_compound_chart")

    st.divider()
    st.markdown('<div class="panel-header">🐳 實時聯線：台灣核心防守型熱門 ETF 監控看板</div>', unsafe_allow_html=True)
    
    # 動態下載台灣前三大長線配置 ETF 行情
    etf_tickers = ["0050.TW", "0056.TW", "00878.TW"]
    etf_cols = st.columns(3)
    
    with st.spinner("📥 正在連線 Yahoo Finance 打包三大核心 ETF 位階大數據..."):
        for idx, etf_code in enumerate(etf_tickers):
            try:
                etf_data = yf.download(etf_code, period="1y", progress=False, auto_adjust=True)
                if not etf_data.empty:
                    etf_close = etf_data['Close'].values.flatten()
                    etf_price = round(float(etf_close[-1]), 2)
                    
                    # 計算長線季線位置
                    ma60_val = round(float(pd.Series(etf_close).rolling(60).mean().iloc[-1]), 2)
                    status_text = "🟢 穩健多頭排列 (股價在季線之上)" if etf_price > ma60_val else "🚨 跌破長線季線 (轉為保守防守)"
                    status_color = "#10b981" if etf_price > ma60_val else "#f43f5e"
                    
                    with etf_cols[idx]:
                        st.markdown(f"""
                        <div class="sandbox-card" style="border-top: 4px solid {status_color};">
                            <div class="card-label" style="font-size:15px; color:#ffffff; font-weight:700;">📈 {etf_code}</div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                                <span style="font-size:13px; color:#64748b;">實時最新價</span>
                                <span style="font-size:24px; font-weight:700; color:#f8fafc;">{etf_price} 元</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px;">
                                <span style="font-size:13px; color:#64748b;">長線生命季線</span>
                                <span style="font-size:14px; font-weight:600; color:#94a3b8;">{ma60_val} 元</span>
                            </div>
                            <div style="margin-top:15px; font-size:12px; font-weight:700; color:{status_color}; text-align:center;">
                                {status_text}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception:
                etf_cols[idx].info(f"🛰️ {etf_code} 雲端快取數據預載中...")