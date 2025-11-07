FROM python:3.9-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY agent.py .
COPY main.py .

# 創建資料目錄
RUN mkdir -p /app/data

# 設置環境變數
ENV PYTHONUNBUFFERED=1

# 啟動應用
CMD ["python", "main.py"]
