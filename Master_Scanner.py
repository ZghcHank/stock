import os
import subprocess
from datetime import datetime

today_str = datetime.today().strftime("%Y%m%d")
print(f"==================================================")
print(f"🚀 Hank 雲端指揮官控制台啟動 | 執行日期: {today_str}")
print(f"==================================================")

# 📝 請在下方陣列中，精準填入你 D 槽裡各個策略子程式的完整「檔案名稱」
# 這樣雲端機器人就會像你在本機一樣，按順序去執行它們！
my_scripts = [
    "裸K進階.py",
    "pig.py",      # 👈 填入你實際的朱家泓策略檔名
    "入住帝寶線.py",      # 👈 填入你實際的帝寶線策略檔名
    "四線發動.py",
    "回後買上漲進階圖片.py",      # 👈 填入你實際的均線策略檔名
    "突破ABC.py"     # 👈 填入你實際的 ABC 切線檔名
]

for script in my_scripts:
    if os.path.exists(script):
        print(f"🏃‍♂️ 正在啟動子策略程式: 【{script}】...")
        try:
            # 呼叫 Python 執行子程式，並即時印出 log
            result = subprocess.run(["python", script], check=True, text=True)
            print(f"🟢 【{script}】雲端執行成功！")
        except subprocess.CalledProcessError as e:
            print(f"❌ 【{script}】執行過程中發生錯誤: {e}")
    else:
        print(f"🟡 找不到檔案 【{script}】，自動跳過。")

print(f"==================================================")
print(f"🏁 全自動策略排程串接完畢！")
print(f"==================================================")

# ==========================================================================================
# 🌟 HANK 獨家：五大飆股模組 - 後端自動化共振大會師引擎 (自動串接於 Master_Scanner 尾端)
# ==========================================================================================
try:
    import pandas as pd
    import glob
    import os
    from datetime import datetime

    date_str = datetime.today().strftime("%Y%m%d")
    print("\n==================================================")
    print("🎨 啟動後端大會師：地毯式搜羅今日所有策略 Excel 進行共振分析...")
    print("==================================================")

    # 搜尋今天產出的所有 Excel 檔案
    excel_files = glob.glob(f"*_{date_str}/*.xlsx") + glob.glob(f"*_{date_str}*.xlsx")
    all_matched_rows = []

    for file_path in excel_files:
        if "🎨_全策略大會師總表_" in file_path:
            continue
        try:
            # 從檔名抓取策略名稱
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
            print(f"⚠️ 讀取 {file_path} 失敗: {e}")

    if all_matched_rows:
        base_df = pd.DataFrame(all_matched_rows)
        
        # 進行關鍵的共振計算
        confluence_df = base_df.groupby(['代號', '股票名稱']).agg({
            '來自策略': lambda x: " | ".join(sorted(list(set(x)))),
            '今日收盤': 'last',
            '今昨量倍數': 'max',
            '今日成交量(張)': 'max',
            '破底停損': 'last',
            '目標壓力': 'last'
        }).reset_index()
        
        # 計算這檔股票今天同時被幾個策略選中
        confluence_df['觸發策略次數'] = base_df.groupby(['代號', '股票名稱'])['來自策略'].count().reset_index()['來自策略']
        confluence_df = confluence_df.sort_values(by='觸發策略次數', ascending=False)
        
        # 建立一個專屬的今日會師資料夾，供 Dashboard 讀取
        master_folder = f"大會師總戰報_{date_str}"
        os.makedirs(master_folder, exist_ok=True)
        master_excel_path = os.path.join(master_folder, f"🎨_全策略大會師總表_{date_str}.xlsx")
        
        confluence_df.to_excel(master_excel_path, index=False)
        print(f"🎯 【大會師大成功】今日全策略共整合 {len(confluence_df)} 檔標的，已存至 {master_excel_path}")
    else:
        print("🟡 提示：今日所有策略皆無篩選出標的，大會師總表留空。")
    print("==================================================")
except Exception as e:
    print(f"💥 後端共振引擎執行失敗: {e}")