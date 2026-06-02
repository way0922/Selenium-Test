# Selenium-Test

# Yahoo Entertainment News Crawler

1資料爬取與清洗:透過python_Selenium.py達到抓取yahoo即時新聞，並指保留12小內之新聞，將新聞名稱與網址一併列出。
3.資料結構化與輸出:Save_csv_file.py透過yahoo即時新聞抓取一定數量新聞，並依照輸出欄位等對應做存取，最後存取至CSＶ檔。

## 專案內容
- `main.py`: 主程式執行檔。
- `python_Selenium.py`:  Selenium 爬蟲程式。
- `Save_csv_file.py`: 負責處理資料並寫入 CSV 檔案程式。
- `Dockerfile`: 定義程式執行環境的Docker設定檔。
- `requirements.txt`: 專案所需的 Python 依賴套件清單。

## 執行需求
- 已安裝 [Docker Desktop](https://www.docker.com/)。


## 如何執行 (使用 Docker)

### 1. 下載專案
  git clone https://github.com/way0922/Selenium-Test.git
  cd Selenium-Test

### 2. 建置 Docker 鏡像
docker build -t yahoo-crawler .


# Windows PowerShell 語法
### 3. 執行爬蟲
docker run --rm -v "${PWD}:/app" yahoo-crawler python3 main.py crawl

### 4.執行分析功能 (Save CSV)
docker run --rm -v "${PWD}:/app" yahoo-crawler python3 main.py analyze
