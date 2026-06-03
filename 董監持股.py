import requests
if 'session' not in locals() and 'session' not in globals():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    })

import datetime
import yfinance as yf


def get_chairman_stock_yahoo(stock_id):
    """透過 Yahoo Finance API 獲取台股最新董監事與經理人持股明細"""

    # 台灣股票在 Yahoo Finance 的代號格式為 "股號.TW" (例如 2330.TW)
    yahoo_ticker = f"{stock_id}.TW"

    print(f"🚀 正在從 Yahoo Finance 數據庫讀取 【{stock_id}】 的股權籌碼資料...")

    try:
        # 建立個股物件
        ticker = yf.Ticker(yahoo_ticker)

        # 獲取主要股東與內部人持股明細 (Major Holders / Insider Officers)
        # Yahoo 的 info 字典中包含了公司高層的基本資料與持股狀況
        info = ticker.info

        # 檢查是否成功獲取資料
        if not info or "longName" not in info:
            print(
                f"❌ 找不到股票代號 【{stock_id}】。請確認輸入是否正確（目前僅支援上市櫃股票）。"
            )
            return

        company_name = info.get("longName", "")
        print(f"🏢 公司名稱：{company_name}")

        # 獲取內部經理人與董監事名單 (company_officers)
        officers = info.get("companyOfficers", [])

        if not officers:
            print(
                f"⚠️ 成功連線，但 Yahoo 數據庫中暫無 【{stock_id}】 的詳細董監事持股明細。"
            )
            print(
                "提示：部分中小型公司可能未揭露於國際數據庫，建議大型權值股優先測試。"
            )
            return

        chairman_found = False

        print(f"\n========================================")
        print(f" 📈 查詢結果：【{stock_id}】 最新內部人持股明細")
        print(f"========================================")

        for officer in officers:
            title = officer.get("title", "")  # 職稱 (通常為英文)
            name = officer.get("name", "")  # 姓名
            # Yahoo 提供的總持股數 (可能為張數或股數，依申報公告為準)
            total_shares = officer.get("totalShares", None)

            # 判定職稱是否包含董事長 (Chairman)
            if "Chairman" in title or "董事長" in title:
                chairman_found = True
                print(f"🔥 【董事長資料】")

            # 格式化數字
            if total_shares is not None:
                shares_formatted = f"{total_shares:,} 股/張"
            else:
                shares_formatted = "未公開或持股過低未達申報標準"

            print(f"🔹 職稱：{title}")
            print(f"🔹 姓名：{name}")
            print(f"🔹 申報持股：{shares_formatted}")
            print(f"----------------------------------------")

        if not chairman_found:
            print(
                "💡 提示：名單中未直接標註 'Chairman'，上述為該公司目前登記在前幾大的核心高階主管與董事明細。"
            )

        print(f"========================================\n")

    except Exception as e:
        print(f"運行時發生未知錯誤: {e}")
        print("提示：請檢查網路連線是否正常。")


if __name__ == "__main__":
    print("--- 台灣股市董事長持股查詢系統 (Yahoo 不卡關版) ---")
    stock_code = input("請輸入股票代號 (如 2330): ").strip()

    # 執行查詢
    get_chairman_stock_yahoo(stock_code)