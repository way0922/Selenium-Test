
#url = "https://tw.news.yahoo.com/entertainment/archive/"
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def parse_time_to_hours(time_str):
    # 以小時為單位，分鐘轉小時
    time_str = time_str.strip().replace(" ", "")
    minute_match = re.search(r'(\d+)(分鐘前|分前|min前|m前)', time_str)
    if minute_match:
        return int(minute_match.group(1)) / 60.0
    hour_match = re.search(r'(\d+)(小時前|hr前|h前)', time_str)
    if hour_match:
        return float(hour_match.group(1))
    if "剛剛" in time_str  in time_str:
        return 0.0
    #如果顯示天、年、月代表太久，不用處理
    if "天" in time_str or "年" in time_str or "月" in time_str:
        return 999.0
    return 999.0

def crawl_yahoo_entertainment_bug_free():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  
    # Docker參數設定
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage') # 解決記憶體空間不足問題
    chrome_options.headless = False  
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # 瀏覽器驅動
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = "https://tw.news.yahoo.com/entertainment/archive/"
    print(f"正在前往網頁: {url}")
    driver.get(url)
    time.sleep(5)
    
 
    #設定滑動次數上限
    TOTAL_SCROLL_STEPS = 40  
    
    # 用來記錄上一次滾動後的「新聞總筆數」，預設為 0
    last_news_count = 0
    # 用來記錄連續幾次網頁內容完全沒有更新
    no_update_streak = 0

    #視窗滑動迴圈
    for step in range(1, TOTAL_SCROLL_STEPS + 1):
        try:
            # 利用 XPath 抓取所有 h3 標籤，這是 Yahoo 新聞標題的 HTML 標籤
            current_h3s = driver.find_elements(By.XPATH, '//main//h3 | //div[@id="Col1"]//h3 | //li[contains(@class, "StreamItem")]//h3')
            if not current_h3s:
                current_h3s = driver.find_elements(By.XPATH, '//h3')
                
            # --- 避免重複迴圈 ---
            current_news_count = len(current_h3s)
            # 如果這次抓到的標題數量跟上次一樣（代表滑動後沒長出新新聞）
            if current_news_count == last_news_count and current_news_count > 0:
                no_update_streak += 1
                print(f" 網頁內容未更新 ({no_update_streak}/2).無更多新聞。")
                #如果連續兩次滑動都沒更新，判斷網頁到底了，強制離開迴圈
                if no_update_streak >= 2:
                    print("網頁已到底部")
                    break
            else:
                no_update_streak = 0  # 如果有新新聞，計數器歸零
                
            last_news_count = current_news_count  # 更新歷史筆數
            
            # 執行滾動
            if current_h3s:
                last_news_element = current_h3s[-1]
                # 控制滾動，scrollIntoView()將目標元素捲動到瀏覽器可視範圍內
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_news_element)
                print(f"   [進度 {step}] 滾動至：'{last_news_element.text[:12]}...' (當前加載總數: {current_news_count} 篇)")
            else:
                driver.execute_script("window.scrollBy(0, 1000);")
                
        except Exception:
            driver.execute_script("window.scrollBy(0, 1000);")
            
        time.sleep(2.5)  # 等待 Lazy Loading 載入
        
        # --- Early Stop ---
        try:
            #XPATH抓所有新聞標題
            check_h3s = driver.find_elements(By.XPATH, '//main//h3 | //div[@id="Col1"]//h3 | //li[contains(@class, "StreamItem")]//h3')
            #有抓資料才執行
            if check_h3s:

                #只取出最後 15 篇新聞判斷是否新聞最舊的
                bottom_news = check_h3s[-15:]
                over_12h_streak = 0  
                
                for h3 in reversed(bottom_news):
                    parent_context = h3.find_element(By.XPATH, './ancestor::div[1] | ./ancestor::li[1]')
                    full_text = parent_context.text.replace('\n', ' ').replace(' ', '')

                    #用字串來抓，EX:"2小時前"
                    time_match = re.search(r'(\d+小時前|\d+分鐘前|剛剛|\d+分前|\d+hr前|天前)', full_text)
                    
                    if time_match:
                        last_time_str = time_match.group(1)
                        if "天前" in last_time_str or parse_time_to_hours(last_time_str) >= 12.0:
                            over_12h_streak += 1
                        else:
                            over_12h_streak = 0
                ##門檻值
                if over_12h_streak >= 8:
                    print(f"\n網頁底端已連續出現 {over_12h_streak} 篇超過 12 小時新聞")
                    break
        except:
            pass


    print("=" * 80)
    
    # 存新聞
    final_news_dict = {}
    #抓網頁上所有載入的新聞標題 h3
    all_final_h3s = driver.find_elements(By.XPATH, '//main//h3 | //div[@id="Col1"]//h3 | //li[contains(@class, "StreamItem")]//h3')
    
    for h3 in all_final_h3s:
        try:
            #取得標題並去除前後空白
            title = h3.text.strip()
            if not title or title in final_news_dict:
                continue
                
            link = ""
            try: link = h3.find_element(By.XPATH, './/a').get_attribute('href')
            except:
                try: link = h3.get_attribute('href')
                except: pass
                
            parent_context = h3.find_element(By.XPATH, './ancestor::div[1] | ./ancestor::li[1]')
            full_text = parent_context.text.replace('\n', ' ').replace(' ', '')
            
            time_match = re.search(r'(\d+小時前|\d+分鐘前|剛剛|\d+分前|\d+hr前)', full_text)
            
            if time_match:
                time_str = time_match.group(1)
                hours_ago = parse_time_to_hours(time_str)
                # 小於12hr才計算存放
                if hours_ago <= 12.0:
                    final_news_dict[title] = {
                        "time": time_str,
                        "link": link
                    }
        except:
            continue

    # --- 輸出最終結果 ex:1. 【X小時前】 內容... 連結: https ---
    for idx, (title, info) in enumerate(final_news_dict.items(), 1):
        print(f"{idx}. 【{info['time']}】 {title}")
        if info['link']: print(f"   連結: {info['link']}")
        print("-" * 80)
        
    print(f"\n 12 小時內的新聞共抓到 {len(final_news_dict)} 篇。")
    driver.quit()

if __name__ == "__main__":
    crawl_yahoo_entertainment_bug_free()