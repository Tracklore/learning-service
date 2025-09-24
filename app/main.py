# app/main.py
from fastapi import FastAPI
from app.routes.topic_selection import router as topic_router
from app.routes.skill_level import router as skill_router
from app.routes.curriculum import router as curriculum_router
from app.routes.tutor import router as tutor_router
from app.routes.teaching import router as teaching_router
from app.routes.evaluation import router as evaluation_router
from app.routes.adaptive_learning import router as adaptive_router
from app.routes.progress import router as progress_router
from app.routes.feedback import router as feedback_router

app = FastAPI(
    title="Learning Service API",
    description="API for the Tracklore learning service with tutor persona and adaptive learning features",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Tutor",
            "description": "Operations related to tutor selection and management"
        },
        {
            "name": "Teaching",
            "description": "Operations related to teaching sessions and lesson delivery"
        },
        {
            "name": "Evaluation",
            "description": "Operations related to answer evaluation and hint generation"
        },
        {
            "name": "Adaptive Learning",
            "description": "Operations related to adaptive learning path adjustments"
        },
        {
            "name": "Progress",
            "description": "Operations related to progress tracking and analytics"
        },
        {
            "name": "Feedback",
            "description": "Operations related to feedback collection and processing"
        }
    ]
)

# Include the routers
app.include_router(topic_router)
app.include_router(skill_router)
app.include_router(curriculum_router)
app.include_router(tutor_router)
app.include_router(teaching_router)
app.include_router(evaluation_router)
app.include_router(adaptive_router)
app.include_router(progress_router)
app.include_router(feedback_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

def run_dev():
    """Run the app in development mode."""
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
