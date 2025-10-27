FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 暴露端口
EXPOSE 8083

# 啟動應用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8083"]
