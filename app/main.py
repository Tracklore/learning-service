from fastapi import FastAPI
from app.routes.topic_selection import router as topic_router
from app.routes.skill_level import router as skill_router

app = FastAPI(title="Learning Service API")

# Include the routers
app.include_router(topic_router)
app.include_router(skill_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

def run_dev():
    """Run the app in development mode."""
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
