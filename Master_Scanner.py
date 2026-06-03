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
    "pig.py.py",      # 👈 填入你實際的朱家泓策略檔名
    "入住帝寶線.py",      # 👈 填入你實際的帝寶線策略檔名
    "四線發動.py"
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