import requests
from bs4 import BeautifulSoup
import csv
import re
import os
import jieba
import jieba.posseg as pseg

# Yahoo 娛樂新聞網頁
WEB_URL = "https://tw.news.yahoo.com/entertainment"

# ====================================================
# 🔥 關鍵優化：載入自定義娛樂字典
# ====================================================
## 加入藝人名稱
DICT_PATH = "entertainment_dict.txt"
if os.path.exists(DICT_PATH):
    jieba.load_userdict(DICT_PATH)
    print(f"載入演藝圈專用字典：{DICT_PATH}")
else:
    print(f"找不到 {DICT_PATH}，將使用 jieba 預設字典")


def fetch_yahoo_entertainment_news_via_web(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"正在直接爬取網頁 HTML 畫面...")
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"無法取得網頁，錯誤代碼: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('li', class_=re.compile(r'StreamItem|js-stream-content'))
        
        scraped_data = []
        
        for article in articles:
            #標題
            title_tag = article.find('h3')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            #連結
            link_tag = article.find('a', href=True)
            link = ""
            if link_tag:
                href = link_tag['href']
                link = href if href.startswith('http') else "https://tw.news.yahoo.com" + href
            #摘要
            summary_tag = article.find('p')
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            ## 通常來源後面會接著時間，ex: "XX娛樂 • 2小時前"
            source_block = article.find('div', class_=re.compile(r'C\(\$c-fuji-grey-f\)|compText'))
            source_raw = ""
            if source_block:
                source_raw = source_block.get_text(strip=True)
            else:
                meta_divs = article.find_all('div')
                for div in meta_divs:
                    if "•" in div.text:
                        source_raw = div.text.strip()
                        break
            
            if "•" in source_raw:
                ## 切割並取得 "XX娛樂"
                source = source_raw.split("•")[0].strip()
            elif "·" in source_raw: 
                source = source_raw.split("·")[0].strip()
            else:
                source = source_raw.strip() if source_raw else "Yahoo奇摩新聞"
            # 如果是廣告或沒有標題，直接跳過這筆，處理下一筆
            if source in ["Ad", "廣告", "精選", ""] or not title:
                continue
                
            scraped_data.append({
                "新聞標題": title,
                "新聞連結": link,
                "新聞來源": source,
                "新聞內文摘要": summary
            })
            
        print(f"從網頁畫面擷取到 {len(scraped_data)} 則最新娛樂新聞。")
        return scraped_data
        
    except Exception as e:
        print(f"抓取過程中發生異常: {e}")
        return []


def analyze_and_structure_data(news_list):
    structured_data = []
    
    # 演唱會判斷關鍵字
    concert_keywords = ["演唱會", "巡演", "巡迴演出", "Live House", "售票", "小巨蛋", "音樂祭", "加場", "大巨蛋", "搶票"]
    
    # 排除常見的娛樂新聞系統誤判詞（這些詞雖在jieba 容易誤判）
    blacklist = ["小巨蛋", "大巨蛋", "金曲獎", "金馬獎", "金鐘獎", "導演", "編劇", "經紀人", "工作室", "主辦單位", "網友", "粉絲"]

    for news in news_list:
        # 結合標題與摘要，擴大判斷範圍
        full_text = news["新聞標題"] + " " + news["新聞內文摘要"]
        
        # 1. 判斷是否為演唱會
        is_concert = "是" if any(kw in full_text for kw in concert_keywords) else "否"
        
        # 2. 使用 jieba.posseg 進行詞性抽樣
        words = pseg.cut(full_text)
        entities = set()
        
        for word, flag in words:
            # nr: 人名, nz: 其他專名(包含自定義字典裡的樂團與特殊藝名)
            # 限制長度在 2~6 字之間，過濾掉單字或過長的雜訊
            if flag in ['nr', 'nz'] and 2 <= len(word) <= 6:
                word_clean = word.strip()
                if word_clean not in blacklist:
                    entities.add(word_clean)
                    
        # 3. 多個人名用「,」隔開，沒有則填入 Null
        if entities:
            entity_str = ",".join(list(entities))
        else:
            entity_str = "Null"
            
        structured_data.append({
            "新聞標題": news["新聞標題"],
            "新聞連結": news["新聞連結"],
            "新聞來源": news["新聞來源"],
            "新聞內文摘要": news["新聞內文摘要"],
            "實體(人名/團體)": entity_str,
            "是否為演唱會": is_concert
        })
        
    return structured_data


def output_to_csv(data, filename="news_information.csv"):
    if not data:
        print("沒有資料可供輸出。")
        return
        
    fieldnames = ["新聞標題", "新聞連結", "新聞來源", "新聞內文摘要", "實體(人名/團體)", "演唱會"]
    
    try:
        with open(filename, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"CSV 檔案建立成功，請查看資料夾下的「{filename}」")
    except Exception as e:
        print(f"輸出 CSV 時發生錯誤: {e}")


if __name__ == "__main__":
    raw_news = fetch_yahoo_entertainment_news_via_web(WEB_URL)
    
    if raw_news:
        final_data = analyze_and_structure_data(raw_news)
        output_to_csv(final_data)