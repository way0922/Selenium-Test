# 1. 使用內建有穩定版 Chrome 瀏覽器的 Python 3.10 Linux 環境
FROM selenium/standalone-chrome:120.0 AS base

USER root

# 2. 在 Linux 內安裝 Python 的 pip 工具
RUN apt-get update && apt-get install -y python3-pip python3-dev

# 3. 設定貨櫃內的工作目錄為 /app
WORKDIR /app

# 4. 複製套件清單並安裝
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 5. 複製你本機的所有程式碼與自定義字典檔進去
COPY . .

# 6. 預設啟動指令（若執行 docker run 時不帶參數，預設會跑這行）
CMD ["python3", "main.py"]