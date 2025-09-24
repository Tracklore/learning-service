# learning-service
Learning Service powers Tracklore's personalized education engine. It lets users pick any subject, assess their skill level, choose a learning style, and customize their AI tutor's tone and complexity. It then generates adaptive, science-backed curriculums that evolve with user feedback.

## Features
- Subject selection and normalization
- Skill level assessment
- Personalized curriculum generation using Gemini API
- AI tutor persona customization
- User feedback integration
- Analytics with BigQuery

## Curriculum Generation
The service uses Google's Gemini API to generate personalized curriculums based on the selected subject and skill level. The curriculum is structured with modules that include lessons, quizzes, and projects tailored to the user's learning path.

## Analytics
The service includes BigQuery analytics for tracking:
- Curriculum generation success rates
- API usage statistics
- Model performance comparisons
- Fallback to mock data occurrences

See [BIGQUERY_ANALYTICS.md](BIGQUERY_ANALYTICS.md) for setup instructions.

## Development Setup

1. Copy the development environment file:
   ```bash
   cp .env.development .env
   ```

2. For development with the `.env.development` file, set the `ENV_FILE` environment variable:
   ```bash
   ENV_FILE=.env.development python -m app.main
   ```

3. To use your own Gemini API key, replace the placeholder in `.env` or `.env.development`:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

The application will automatically fall back to mock data if the API key is not set or is invalid.
