from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()


from backend.routes import router as api_router
from backend.db import populate_personas_from_yaml


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Parameters
    ----------
    _: FastAPI
        The FastAPI application instance.
    """

    populate_personas_from_yaml()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
