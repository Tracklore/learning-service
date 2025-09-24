# Curriculum Generation with Gemini API

This document explains how to use the curriculum generation feature powered by Google's Gemini API.

## Setup

1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Set the `GEMINI_API_KEY` environment variable in your `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## How it Works

The curriculum generation works in the following way:

1. A user requests a curriculum for a specific subject and skill level
2. The system uses the Gemini API to generate a personalized curriculum in JSON format
3. The curriculum includes modules with lessons, quizzes, and projects
4. Each module has a title, type, difficulty level, estimated time, and description
5. The curriculum also includes learning objectives and a recommended tutor style

## API Endpoint

To generate a curriculum, make a POST request to `/curriculum/` with the following JSON payload:

```json
{
  "subject": "Python Programming",
  "skill_level": "beginner",
  "path": "newbie"
}
```

The response will be a curriculum object with the following structure:

```json
{
  "curriculum_id": "python_programming_newbie",
  "subject_id": "Python Programming",
  "path": "newbie",
  "modules": [
    {
      "module_id": "unique_identifier",
      "title": "Module title",
      "type": "lesson|quiz|project",
      "difficulty": "easy|medium|hard",
      "estimated_time_min": 30,
      "resources": ["https://example.com/resource1"],
      "description": "Brief description of what this module covers"
    }
  ],
  "recommended_tutor_style": "friendly",
  "learning_objectives": [
    "Objective 1",
    "Objective 2"
  ]
}
```

## Fallback Mechanism

If the Gemini API is not configured or fails to generate a curriculum, the system will fall back to using mock data. This ensures that the service remains functional even when the AI service is unavailable.

## Development Environment

For development and testing, you can use the `.env.development` file which contains placeholder values. This allows you to test the application without a real API key.

To use the development environment, set the `ENV_FILE` environment variable:

```bash
ENV_FILE=.env.development python scripts/test_development_env.py
```

## Testing

To test the curriculum generation, you can run the demo script:

```bash
python scripts/demo_curriculum.py
```

Or run the tests:

```bash
python -m pytest tests/test_curriculum.py -v
```

For testing with the development environment:

```bash
python scripts/test_development_env.py
```