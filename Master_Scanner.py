import subprocess
import sys
import time

def run_scripts_sequentially(scripts):
    print("="*70)
    print("🚀 啟動【全自動量化掃描系統】 總控制台 (Master Controller)")
    print("="*70)
    
    total_scripts = len(scripts)
    
    for i, script in enumerate(scripts, 1):
        print(f"\n[{i}/{total_scripts}] ➤ 正在啟動策略模組: 【 {script} 】...")
        start_time = time.time()
        
        try:
            # 使用 subprocess 呼叫另一個 python 檔案並等待它完成
            # sys.executable 會自動抓取您目前系統使用的 Python 執行檔
            process = subprocess.run([sys.executable, script], check=True)
            
            elapsed = time.time() - start_time
            print(f"\n✅ 模組 【 {script} 】 執行完畢！(耗時: {elapsed:.1f} 秒)")
            
            # 策略之間的緩衝休息時間，避免過度頻繁請求被 Yahoo 封鎖
            if i < total_scripts:
                print("⏳ 休息 5 秒鐘後啟動下一個模組...")
                time.sleep(5)
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ 執行 【 {script} 】 時發生內部錯誤，跳過並執行下一個！")
        except FileNotFoundError:
            print(f"\n⚠️ 找不到檔案: 【 {script} 】，請確認檔名是否正確且在同一個資料夾。")
            
    print("\n" + "="*70)
    print("🎉 今日所有量化掃描任務已全部完成！")
    print("📂 請前往各個【日期資料夾】查看今天的精選報表與 K 線圖。")
    print("="*70)

if __name__ == "__main__":
    # 📝 將您想執行的 Python 檔案名稱放在這個清單中
    # 您可以自由調整順序，或是把今天不想跑的策略前面加上 # 註解掉
    target_scripts = [
        "回後買上漲進階圖片.py",  # 策略 1: 朱家泓(進階雙引擎)
        "pig.py",                # 策略 2: 朱家泓(基礎版)
        "裸K進階.py",            # 策略 3: 老余裸K破底翻
        "入住帝寶線.py",         # 策略 4: 底部多頭吞噬
        "四線發動.py",           # 策略 5: 四均線糾結起漲
        "突破ABC.py"             # 策略 6: ABC下降切線突破 (ZigZag版)
    ]
    
    run_scripts_sequentially(target_scripts)