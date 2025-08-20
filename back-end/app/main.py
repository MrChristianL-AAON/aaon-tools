from fastapi import FastAPI
from .api.commands import files, inputs, pipeline

app = FastAPI()

# include your first router
app.include_router(files.router)
app.include_router(inputs.router)
app.include_router(pipeline.router)

@app.get("/")
def read_root():
    return {"message": "Test"}
