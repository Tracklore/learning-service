# learning-service phases

## **Phase 1: Setup & Foundation**

1. **Repo Setup**
    - Initialize GitHub repo (✅ already done).
    - Add `.gitignore`, `README.md`, and `requirements.txt` or `pyproject.toml`.
    - Choose dependency manager (Poetry preferred).
    - Add `.env.example` for API keys (LLM, vector DB).
2. **Environment & Tooling**
    - Setup Python virtual environment.
    - Install FastAPI, Uvicorn, Pydantic, HTTPX, Pytest, and dotenv.
    - Add a logging utility (`structlog` or Python `logging`).
3. **Basic App Structure**
    - Create `app/` folder with `main.py` (FastAPI app + router registration).
    - Setup `/health` route to confirm service runs.

---

## **Phase 2: Core Domain Modeling**

1. **Pydantic Models**
    - `UserModel`: skill level, preferences, tutor persona.
    - `CurriculumModel`: subject, topics, level, generated curriculum plan.
    - `TutorModel`: humor, tone, language complexity.
    - `FeedbackModel`: difficulty rating, quiz results, progress.
2. **Subject & Level Input**
    - Build `/subjects` endpoint to list available subjects.
    - Build `/skill-level` endpoint to accept user level (newbie/amateur/pro).

---

## **Phase 3: Curriculum Engine**

1. **Curriculum Generation**
    - Build `curriculum_service.py` to:
        - Take subject + skill level + user preferences.
        - Call LLM to generate multiple learning paths (fast-track, deep-dive).
    - Store curriculum in vector DB for future retrieval.
2. **Learning Methods**
    - Research **scientifically proven learning methods** (spaced repetition, interleaving, active recall).
    - Encode them as curriculum generation options.
    - Let user pick preferred method via `/curriculum/method`.
3. Enhanced  curriculum_model.py:
    
    ```python
    from pydantic import BaseModel
    from typing import List, Optional
    
    class Module(BaseModel):
        module_id: str
        title: str
        type: str  # e.g., "lesson", "quiz", "project"
        difficulty: str  # "easy", "medium", "hard"
        estimated_time_min: Optional[int] = None
        resources: Optional[List[str]] = None
        embedding_vector: Optional[List[float]] = None  # For semantic search
    
    class Curriculum(BaseModel):
        curriculum_id: str
        subject_id: str
        path: str  # e.g., "newbie", "pro"
        modules: List[Module]  # Fully detailed modules
        recommended_tutor_style: Optional[str] = None  # e.g., "friendly"
        learning_objectives: Optional[List[str]] = None
    
    class LearningPath(BaseModel):
        user_id: str
        curriculum_id: str
        completed_modules: List[str] = []
        progress: float = 0.0  # 0-100%
        completion_status: str = "incomplete"
    ```
    
    **4. Benefits of this Enhanced Model**
    
    - Each module is **self-contained with metadata** → easier to display and track progress
    - Supports **adaptive curriculum** → LLM can dynamically reorder modules or add optional ones
    - Can integrate **vector embeddings** → semantic search, recommending relevant lessons, questions, or explanations
    - Flexible for future **gamification or assessment metrics**

---

## **Phase 4: Tutor Persona & Teaching**

1. **Tutor Selection**
    - Build `/tutor` endpoint for selecting:
        - Character style, humor level, tone, complexity.
    - Store persona in user profile (vector DB + relational fallback).
2. **Teaching LLM**
    - Create `teaching_llm.py` to:
        - Deliver lessons step by step.
        - Ask interactive questions.
        - Evaluate answers and give hints.
        - Adjust explanation complexity dynamically.

---

## **Phase 5: Progress Tracking & Feedback**

1. **Progress Tracking**
    - Add `/progress` endpoint to store:
        - Lessons completed, scores, repeated mistakes.
    - Embed user’s knowledge state into vector DB.
2. **Feedback Loop**
    - Build `/feedback` endpoint:
        - User rates difficulty or requests style change.
        - Regenerate curriculum or adjust pacing dynamically.

---

## **Phase 6: LLM & Vector DB Integration**

1. **LLM Layer**
    - Create `llm/` folder with:
        - `curriculum_llm.py`: generates curriculum.
        - `teaching_llm.py`: interactive tutor.
        - `embeddings.py`: generates user/content embeddings.
    - Start with **Claude 3.5 Sonnet** or **GPT-4o-mini** (for MVP).
2. **Vector Database**
    - Choose a vector DB (Pinecone/Weaviate/Qdrant).
    - Implement `vector_store.py` with:
        - Upsert user embeddings.
        - Search for nearest lessons/explanations.
        - Retrieve and update progress data.

---

## **Phase 7: Testing & QA**

1. **Unit Tests**
    - Test each route (subject, curriculum, tutor, feedback).
    - Mock LLM calls (so tests don’t burn tokens).
    - Test vector DB integration with dummy embeddings.
2. **Integration Tests**
    - Simulate a user flow:
        - Select subject → pick level → get curriculum → get lesson → send feedback.

---

## **Phase 8: Documentation & Deployment**

1. **Docs**
    - Update README with:
        - Setup steps.
        - Example API calls.
        - How to add new subjects or methods.
    - Add OpenAPI schema for easy API exploration.
2. **Deployment**
    - Containerize with Docker.
    - Deploy on Fly.io/Render/EC2 (whichever you prefer).
    - Setup CI/CD (GitHub Actions) for tests + auto-deploy.

---

## **Stretch Goals (Future)**

- Add **multimodal support** (images/diagrams in lessons).
- Add **gamification layer** (points, streaks, leaderboards).
- Build **real-time tutor chat UI** (Next.js frontend).
- Support **offline learning mode** (pre-cached lessons).