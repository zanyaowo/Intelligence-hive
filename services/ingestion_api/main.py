from fastapi import FastAPI, Request
import uvicorn
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.post("/ingest")
async def ingest_data(request: Request):
    try:
        data = await request.json()
        logging.info(f"Received data: {data}")
        # In a real application, you would process and store this data
        return {"status": "success", "message": "Data received"}
    except Exception as e:
        logging.error(f"Error receiving data: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
