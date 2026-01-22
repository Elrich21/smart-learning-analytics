from fastapi import FastAPI
from backend.database import engine

app =FastAPI(title="Smart Learning Analytics Platform")

@app.get("/")
def root():
    return {"message": "Backend is running succesfully"}
    
@app.get("/db-check")
def db_check():
    try:
        with engine.connect() as connection:
            return {"status": "Database connected successfully"}
    except Exception as e:
        return {"error": str(e)}
