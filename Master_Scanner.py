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
    # "朱家泓策略.py",      # 👈 如果有其他檔案，請把前面的 # 拿掉並改成正確檔名
    # "四均線糾結.py",
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