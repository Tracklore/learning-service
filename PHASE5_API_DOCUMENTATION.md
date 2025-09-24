# Phase 5: Progress Tracking & Feedback API Documentation

This document provides comprehensive documentation for the progress tracking and feedback features implemented in Phase 5 of the Tracklore learning service.

## Base URL
All API endpoints are relative to:
```
http://localhost:8000
```

## Progress Tracking Endpoints

### Update User Progress
Update user's progress for a lesson or module.

**Endpoint:** `POST /progress/`

**Request Body:**
```json
{
  "user_id": "user_123",
  "lesson_id": "lesson_456",
  "module_id": "module_789",
  "subject": "Mathematics",
  "completed": true,
  "score": 85.5,
  "time_spent_seconds": 1800,
  "repeated_mistakes": ["concept_1", "concept_2"],
  "notes": "Completed with good understanding"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/progress/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "lesson_id": "math_algebra_1",
    "subject": "Mathematics",
    "completed": true,
    "score": 85.5,
    "time_spent_seconds": 1800
  }'
```

**Example Response:**
```json
{
  "user_id": "user_123",
  "subject": "Mathematics",
  "current_lesson_id": "math_algebra_1",
  "current_module_id": null,
  "total_lessons_completed": 5,
  "total_modules_completed": 0,
  "overall_score": 82.4,
  "completion_percentage": 50.0,
  "message": "Progress updated successfully",
  "last_updated": "2023-10-15T10:30:00"
}
```

### Get User Progress
Get a user's progress for a specific subject.

**Endpoint:** `GET /progress/{user_id}/{subject}`

**Path Parameters:**
- `user_id`: The ID of the user
- `subject`: The subject to retrieve progress for

**Example Request:**
```bash
curl -X GET "http://localhost:8000/progress/user_123/Mathematics"
```

**Example Response:**
```json
{
  "user_id": "user_123",
  "subject": "Mathematics",
  "total_lessons_completed": 5,
  "total_modules_completed": 1,
  "overall_score": 82.4,
  "time_spent_total_seconds": 9000,
  "current_module_id": "module_789",
  "current_lesson_id": "lesson_456",
  "last_accessed": "2023-10-15T10:30:00",
  "completion_percentage": 50.0,
  "knowledge_state": null,
  "strengths": ["algebra", "geometry"],
  "weaknesses": ["calculus"],
  "learning_pace": "normal"
}
```

### Get Progress Analytics
Get detailed analytics for a user's progress in a specific subject.

**Endpoint:** `GET /progress/{user_id}/{subject}/analytics`

**Path Parameters:**
- `user_id`: The ID of the user
- `subject`: The subject to retrieve analytics for

**Example Request:**
```bash
curl -X GET "http://localhost:8000/progress/user_123/Mathematics/analytics"
```

**Example Response:**
```json
{
  "user_id": "user_123",
  "subject": "Mathematics",
  "learning_velocity": 1.5,
  "accuracy_trend": [
    {"date": "2023-10-10T09:00:00", "score": 78.0},
    {"date": "2023-10-11T09:00:00", "score": 82.0},
    {"date": "2023-10-12T09:00:00", "score": 85.0}
  ],
  "time_spent_trend": [
    {"date": "2023-10-10T09:00:00", "seconds": 1800},
    {"date": "2023-10-11T09:00:00", "seconds": 2000},
    {"date": "2023-10-12T09:00:00", "seconds": 1600}
  ],
  "weak_areas": ["calculus", "trigonometry"],
  "strong_areas": ["algebra", "geometry"],
  "estimated_completion_days": 15
}
```

### Reset User Progress
Reset a user's progress for a specific subject.

**Endpoint:** `DELETE /progress/{user_id}/{subject}`

**Path Parameters:**
- `user_id`: The ID of the user
- `subject`: The subject to reset progress for

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/progress/user_123/Mathematics"
```

**Example Response:**
```json
{
  "user_id": "user_123",
  "subject": "Mathematics",
  "message": "Progress for user user_123 in subject Mathematics has been reset",
  "reset": true
}
```

## Feedback Endpoints

### Submit Feedback
Submit feedback about lessons, tutors, or the learning experience.

**Endpoint:** `POST /feedback/submit`

**Request Body:**
```json
{
  "user_id": "user_123",
  "subject": "Mathematics",
  "lesson_id": "math_algebra_1",
  "module_id": "module_789",
  "tutor_id": "tutor_456",
  "feedback_type": "lesson",
  "rating": 4,
  "content_rating": 5,
  "difficulty_rating": 3,
  "tutor_rating": 4,
  "feedback_text": "The lesson was helpful but a bit too fast",
  "suggestions": ["Slow down explanations", "Add more examples"],
  "would_recommend": true,
  "emotional_state": "engaged",
  "context_tags": ["first_lesson", "review_session"],
  "timestamp": "2023-10-15T10:30:00"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/feedback/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "subject": "Mathematics",
    "lesson_id": "math_algebra_1",
    "feedback_type": "lesson",
    "rating": 4,
    "feedback_text": "The lesson was helpful but a bit too fast",
    "timestamp": "2023-10-15T10:30:00"
  }'
```

**Example Response:**
```json
{
  "feedback_id": "feedback_abc123",
  "message": "Feedback submitted successfully",
  "user_id": "user_123",
  "timestamp": "2023-10-15T10:30:00"
}
```

### Submit Curriculum Feedback
Submit feedback about a curriculum.

**Endpoint:** `POST /feedback/curriculum`

**Request Body:**
```json
{
  "user_id": "user_123",
  "curriculum_id": "math_algebra_curriculum",
  "learning_path": "newbie",
  "overall_satisfaction": 4,
  "pacing_feedback": 3,
  "content_relevance": 5,
  "effectiveness": 4,
  "feedback_text": "Good curriculum, could use more real-world examples",
  "suggested_improvements": ["Add real-world examples", "Include more practice problems"],
  "completed_modules": 5,
  "total_modules": 10,
  "timestamp": "2023-10-15T10:30:00"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/feedback/curriculum" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "curriculum_id": "math_algebra_curriculum",
    "learning_path": "newbie",
    "overall_satisfaction": 4,
    "feedback_text": "Good curriculum, could use more real-world examples",
    "completed_modules": 5,
    "total_modules": 10,
    "timestamp": "2023-10-15T10:30:00"
  }'
```

**Example Response:**
```json
{
  "feedback_id": "curriculum_feedback_def456",
  "message": "Curriculum feedback submitted successfully",
  "user_id": "user_123",
  "timestamp": "2023-10-15T10:30:00"
}
```

### Get Feedback Analytics
Get aggregated feedback analytics for a subject.

**Endpoint:** `GET /feedback/{subject}/analytics`

**Path Parameters:**
- `subject`: The subject to retrieve analytics for

**Example Request:**
```bash
curl -X GET "http://localhost:8000/feedback/Mathematics/analytics"
```

**Example Response:**
```json
{
  "subject": "Mathematics",
  "average_rating": 4.2,
  "total_feedback": 25,
  "positive_feedback": 18,
  "negative_feedback": 3,
  "common_suggestions": ["More examples", "Slower explanations"],
  "rating_distribution": {
    "1": 1,
    "2": 2,
    "3": 4,
    "4": 8,
    "5": 10
  },
  "top_feedback_topics": ["lesson", "content", "difficulty"],
  "timestamp": "2023-10-15T10:30:00"
}
```

### Get User Feedback History
Get feedback history for a specific user.

**Endpoint:** `GET /feedback/user/{user_id}`

**Path Parameters:**
- `user_id`: The ID of the user

**Example Request:**
```bash
curl -X GET "http://localhost:8000/feedback/user/user_123"
```

### Process Feedback Adjustment
Process feedback for a user and subject to trigger immediate curriculum adjustments.

**Endpoint:** `POST /feedback/process-adjustment/{user_id}/{subject}`

**Path Parameters:**
- `user_id`: The ID of the user
- `subject`: The subject to adjust curriculum for

**Example Request:**
```bash
curl -X POST "http://localhost:8000/feedback/process-adjustment/user_123/Mathematics"
```

**Example Response:**
```json
{
  "user_id": "user_123",
  "subject": "Mathematics",
  "success": true,
  "message": "Curriculum adjustment processed successfully for user user_123 in subject Mathematics"
}
```

## Error Responses

The API uses the following error codes:

- `200`: Success
- `404`: Resource not found
- `422`: Validation error
- `500`: Internal server error

### Example Error Response:
```json
{
  "detail": "User progress not found"
}
```

## Model Definitions

### ProgressUpdateRequest
```json
{
  "user_id": "string",
  "lesson_id": "string (optional)",
  "module_id": "string (optional)",
  "subject": "string",
  "completed": "boolean (optional)",
  "score": "number (optional)",
  "time_spent_seconds": "integer (optional)",
  "repeated_mistakes": "array of strings (optional)",
  "notes": "string (optional)"
}
```

### FeedbackSubmission
```json
{
  "user_id": "string",
  "subject": "string",
  "lesson_id": "string (optional)",
  "module_id": "string (optional)",
  "tutor_id": "string (optional)",
  "feedback_type": "string (lesson, tutor, content, difficulty, overall)",
  "rating": "integer (optional, 1-5)",
  "content_rating": "integer (optional, 1-5)",
  "difficulty_rating": "integer (optional, 1-5)",
  "tutor_rating": "integer (optional, 1-5)",
  "feedback_text": "string (optional)",
  "suggestions": "array of strings (optional)",
  "would_recommend": "boolean (optional)",
  "emotional_state": "string (optional)",
  "context_tags": "array of strings (optional)",
  "timestamp": "datetime"
}
```

## Feedback to Curriculum Adjustment Flow

The system uses feedback to dynamically adjust the curriculum for each user. The process works as follows:

1. User submits feedback via `/feedback/submit` or `/feedback/curriculum`
2. System analyzes the feedback content and ratings
3. If feedback indicates difficulty or dissatisfaction, the system may trigger:
   - Slower pacing for the user
   - Additional practice content for weak areas
   - Remedial content for topics with low ratings
   - Tutor style changes

### Process Flow:
1. **Submit Feedback**: User submits feedback with ratings and comments
2. **Analysis**: System processes feedback to identify patterns
3. **Decision**: System determines if curriculum adjustment is needed based on:
   - Rating thresholds (e.g., < 3/5)
   - Sentiment analysis of feedback text
   - Consistency of feedback across related topics
4. **Adjustment**: If needed, system triggers curriculum adjustments
5. **Verification**: System monitors user's subsequent performance

### Adjustment Triggers:
- Overall rating < 3/5
- Content rating < 3/5
- Difficulty rating < 2/5 or > 4/5 (indicating misalignment)
- Comments containing specific phrases like "too difficult", "too easy", "not helpful"
- Pattern of low ratings on related topics

### Example API Call for Feedback Processing:
```bash
# Submit feedback indicating difficulty
curl -X POST "http://localhost:8000/feedback/submit" 
  -H "Content-Type: application/json" 
  -d '{
    "user_id": "user_123",
    "subject": "Mathematics",
    "lesson_id": "math_algebra_1",
    "feedback_type": "difficulty",
    "rating": 2,
    "difficulty_rating": 2,
    "feedback_text": "This lesson was too hard for my current level",
    "suggestions": ["Provide more examples", "Slow down explanations"],
    "timestamp": "2023-10-15T10:30:00"
  }'

# Process the feedback for curriculum adjustment
curl -X POST "http://localhost:8000/feedback/process-adjustment/user_123/Mathematics"
```

## Adaptive Learning Integration

The progress tracking and feedback systems are integrated with the adaptive learning features. Based on user performance and feedback, the system can:

1. Identify strengths and weaknesses to adapt content
2. Adjust curriculum difficulty or pacing
3. Generate personalized learning paths
4. Trigger interventions when users struggle

### Adaptive Mechanisms:

#### 1. Knowledge State Embeddings
The system creates vector representations of a user's knowledge state to:
- Identify knowledge gaps
- Find similar users for peer learning
- Recommend appropriate content based on knowledge level

#### 2. Dynamic Curriculum Adjustment
Based on progress and feedback, the system can:
- Switch to a different learning path (e.g., from "newbie" to "amateur" if user excels)
- Add remedial modules for weak areas
- Accelerate through topics the user already masters
- Adjust pacing based on learning velocity

#### 3. Real-time Adaptation
During learning sessions, the system may:
- Provide additional hints when a user struggles
- Offer different explanations based on preferred learning style
- Suggest taking a break if engagement drops
- Recommend switching to a different topic if frustration is detected

#### 4. Personalization Based on Sentiment
The system tracks user sentiment through feedback to:
- Adjust teaching style based on emotional state
- Provide additional support when user feels frustrated
- Offer challenges when user feels confident

### Example Adaptive Learning Flow:
```
User performs poorly on topic A → System identifies weakness → 
Additional practice modules added → User shows improvement → 
System adjusts difficulty back to normal
```

For more details about adaptive learning, see the adaptive learning API documentation.

## Knowledge State Embeddings

The system uses embeddings to represent a user's knowledge state in a multi-dimensional space. These embeddings are used for:

1. **Recommendation**: Finding appropriate content based on knowledge level
2. **Gap Detection**: Identifying areas where the user's knowledge is incomplete
3. **Comparison**: Finding users with similar knowledge profiles
4. **Adaptation**: Adjusting curriculum based on knowledge state

The embedding dimension is 128, and the system updates embeddings based on:
- Lesson completion and scores
- Time spent on different topics  
- Feedback ratings
- Interaction patterns

## Frontend Integration Code Samples

### JavaScript/React Example:

#### Submitting Progress
```javascript
// Update user progress after completing a lesson
async function updateLessonProgress(userId, lessonId, subject, score, timeSpent) {
  try {
    const response = await fetch('http://localhost:8000/progress/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        lesson_id: lessonId,
        subject: subject,
        completed: true,
        score: score,
        time_spent_seconds: timeSpent
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Progress updated:', result);
    return result;
  } catch (error) {
    console.error('Error updating progress:', error);
    throw error;
  }
}
```

#### Submitting Feedback
```javascript
// Submit feedback after lesson completion
async function submitFeedback(feedbackData) {
  try {
    const response = await fetch('http://localhost:8000/feedback/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedbackData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Feedback submitted:', result);
    return result;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
}

// Example usage
const feedback = {
  user_id: 'user_123',
  subject: 'Mathematics',
  lesson_id: 'math_algebra_1',
  feedback_type: 'lesson',
  rating: 4,
  content_rating: 5,
  feedback_text: 'The lesson was helpful but a bit too fast',
  suggestions: ['Slow down explanations', 'Add more examples'],
  would_recommend: true,
  timestamp: new Date().toISOString()
};

submitFeedback(feedback);
```

#### Getting User Progress Analytics
```javascript
// Get user's progress analytics
async function getUserProgressAnalytics(userId, subject) {
  try {
    const response = await fetch(`http://localhost:8000/progress/${userId}/${subject}/analytics`);
    
    if (!response.ok) {
      if (response.status === 404) {
        console.log('No analytics available yet');
        return null; // No analytics yet
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const analytics = await response.json();
    console.log('Progress analytics:', analytics);
    return analytics;
  } catch (error) {
    console.error('Error fetching analytics:', error);
    throw error;
  }
}

// Example usage
getUserProgressAnalytics('user_123', 'Mathematics')
  .then(analytics => {
    if (analytics) {
      // Display learning velocity, weak areas, etc. to the user
      console.log(`Learning velocity: ${analytics.learning_velocity} lessons/day`);
      console.log(`Weak areas: ${analytics.weak_areas.join(', ')}`);
    }
  });
```

#### Processing Curriculum Adjustment Based on Feedback
```javascript
// Process curriculum adjustment based on collected feedback
async function processCurriculumAdjustment(userId, subject) {
  try {
    const response = await fetch(`http://localhost:8000/feedback/process-adjustment/${userId}/${subject}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Curriculum adjustment result:', result);
    return result;
  } catch (error) {
    console.error('Error processing curriculum adjustment:', error);
    throw error;
  }
}

// Example: Process adjustment after user submits multiple feedbacks
processCurriculumAdjustment('user_123', 'Mathematics')
  .then(result => {
    if (result.success) {
      console.log('Curriculum adjusted successfully');
      // Refresh the learning path in the UI
    } else {
      console.log('Curriculum adjustment failed:', result.message);
    }
  });
```