# Selenium-Test

# Yahoo Entertainment News Crawler

本專案為一個自動化爬蟲程式，用於抓取 Yahoo 娛樂新聞，並將資料整理為 CSV 格式。本專案已完成 Docker 容器化封裝，確保在任何環境下皆能有一致的執行結果。

## 專案內容
- `main.py`: 主程式執行檔。
- `python_Selenium.py`:  Selenium 爬蟲程式。
- `Save_csv_file.py`: 負責處理資料並寫入 CSV 檔案程式。
- `Dockerfile`: 定義程式執行環境的Docker設定檔。
- `requirements.txt`: 專案所需的 Python 依賴套件清單。

## 執行需求
- 已安裝 [Docker Desktop](https://www.docker.com/)。
- 電腦需具備網際網路連線。

## 如何執行 (使用 Docker)

### 1. 下載專案
git clone https://github.com/way0922/Selenium-Test.git
cd Selenium-Test

2. 建置 Docker 鏡像
docker build -t yahoo-crawler .

3. 執行爬蟲
# Windows PowerShell 語法
docker run --rm -v "${PWD}:/app" yahoo-crawler python main.py crawl

4.執行分析功能 (Save CSV)
docker run --rm -v "${PWD}:/app" yahoo-crawler python main.py analyze
