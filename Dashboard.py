import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# ================= 網頁基本設定 =================
st.set_page_config(page_title="Hank 量化交易戰情室", layout="wide", page_icon="📈")

st.title("🚀 Hank 專屬量化交易戰情室")
st.markdown("自動彙整每日策略掃描結果，結合 K 線圖表進行高效率覆盤。")
st.divider()

# ================= 側邊欄：設定篩選條件 =================
st.sidebar.header("🔍 篩選條件")

# 1. 選擇日期 (預設為今天)
selected_date = st.sidebar.date_input("請選擇掃描日期", datetime.today())
date_str = selected_date.strftime("%Y%m%d")

# 2. 定義我們所有的策略與對應的資料夾/檔名格式
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
    # 讀取 Excel 檔案
    df = pd.read_excel(excel_path)
    
    # 顯示數據卡片
    col1, col2, col3 = st.columns(3)
    col1.metric("今日符合檔數", f"{len(df)} 檔")
    
    st.subheader(f"📊 {selected_strategy} - 數據清單")
    # 將網址欄位轉換為真正的超連結 (若有的話)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("👁️ 實戰圖表檢視 (左手數據，右手開槍)")
    
    # 動態產生每檔股票的圖表
    # 以 2 欄的方式並排顯示圖片，節省空間
    img_cols = st.columns(2)
    
    for idx, row in df.iterrows():
        ticker = str(row['代號']).split('.')[0]
        stock_name = str(row['股票名稱']).replace("/", "").replace("\\", "").strip()
        img_filename = f"{ticker}_{stock_name}.png"
        img_path = os.path.join(folder_path, img_filename)
        
        # 決定圖片放在左欄還是右欄
        col_to_use = img_cols[idx % 2]
        
        with col_to_use:
            if os.path.exists(img_path):
                image = Image.open(img_path)
                st.image(image, caption=f"{ticker} {stock_name}", use_container_width=True)
            else:
                st.warning(f"找不到 {ticker} {stock_name} 的圖表檔案")
else:
    st.error(f"找不到日期 **{selected_date.strftime('%Y-%m-%d')}** 的 【{selected_strategy}】 資料！")
    st.info("💡 請確認：\n1. 您今天是否已經執行過該策略的掃描程式？\n2. 若遇假日無開盤，請從左側欄選擇前一個交易日。")