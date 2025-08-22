from fastapi import FastAPI
from .api.commands import files, inputs, pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# include your first router
app.include_router(files.router, prefix="/api")
app.include_router(inputs.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")


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
