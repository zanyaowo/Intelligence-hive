from fastapi import FastAPI, Request, Depends
import uvicorn
import logging
from auth import verify_API_key

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.post("/ingest")
async def ingest_data(
    request: Request,
    api_key:str = Depends(verify_API_key)
    ):
    try:
        data = await request.json()
        logging.info(f"Received data: {data}")

        # TODO 處理資料

        return {"status": "success", "seesions_count": len(data)}
    except Exception as e:
        logging.error(f"Error receiving data: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
