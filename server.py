import logging
from fastapi import FastAPI
from APIRouter import router
import os
from seed_users import seed

# Logging
logging.basicConfig(
    filename="my_app.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

if not os.path.exists("test.db"):# if the database file does not exist, seed the database
    seed()


# FastAPI app and CORS
app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)