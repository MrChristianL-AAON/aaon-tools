from fastapi import FastAPI
from .api.commands import files, inputs, pipeline
from .api.update_archive import build, upload_debs, result

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# include your first router
# command builder
app.include_router(files.router, prefix="/api")
app.include_router(inputs.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")

# update builder
app.include_router(build.router, prefix="/api")
app.include_router(upload_debs.router, prefix="/api")
app.include_router(result.router, prefix="/api")

origins = [
    "http://localhost:5173",  # SvelteKit dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AAON Tools API!"}

@app.get("/info")
def get_info():
    return {"app": "AAON Tools API", "version": "1.0.0"}