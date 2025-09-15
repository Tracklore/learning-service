learning-service/
├── README.md                  # Project overview, setup instructions
├── pyproject.toml             # Modern dependency management (Poetry) or setup.cfg/setup.py
├── requirements.txt           # (Optional) For quick installs if not using Poetry
├── .env.example               # Example env vars (DB URL, API keys)
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py                # Entry point (FastAPI app or CLI)
│   ├── config.py              # App-wide settings (dotenv / pydantic BaseSettings)
│   ├── routes/                # API endpoints
│   │   ├── __init__.py
│   │   ├── subjects.py        # Subject selection endpoints
│   │   ├── curriculum.py      # Curriculum generation endpoints
│   │   ├── tutor.py           # Tutor persona endpoints
│   │   └── feedback.py        # User feedback endpoints
│   ├── services/              # Core business logic
│   │   ├── __init__.py
│   │   ├── subject_service.py
│   │   ├── curriculum_service.py
│   │   ├── tutor_service.py
│   │   └── feedback_service.py
│   ├── models/                # Pydantic models / dataclasses
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   ├── curriculum_model.py
│   │   ├── tutor_model.py
│   │   └── feedback_model.py
│   ├── db/                    # Database + vector store layer
│   │   ├── __init__.py
│   │   ├── vector_store.py    # Integration with Pinecone/Weaviate/Qdrant
│   │   └── persistence.py     # User data CRUD operations
│   ├── llm/                   # LLM integration logic
│   │   ├── __init__.py
│   │   ├── curriculum_llm.py  # Curriculum generation
│   │   ├── teaching_llm.py    # Interactive teaching & Q&A
│   │   └── embeddings.py      # Embedding generation for user/content
│   └── utils/                 # Shared helpers
│       ├── __init__.py
│       ├── logger.py
│       ├── validators.py
│       └── constants.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_subjects.py
│   ├── test_curriculum.py
│   ├── test_tutor.py
│   ├── test_feedback.py
│   └── test_llm.py
└── scripts/
    ├── seed_data.py           # Preload subjects/topics into DB
    └── run_dev.py             # Local dev runner
