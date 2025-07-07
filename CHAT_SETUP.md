# 🌟 Astrological Chat Setup Guide

## Overview

The Astrological Chat feature allows users to have interactive conversations with an AI astrologer powered by ChatGPT. The AI uses the user's birth chart data as context to provide personalized astrological guidance, insights, and answers to questions about their cosmic influences.

## 🚀 Features

### Backend Features
- **OpenAI ChatGPT Integration**: Uses GPT-4 for intelligent astrological conversations
- **Birth Chart Context**: Automatically includes user's planetary positions, houses, and aspects
- **Conversation Memory**: Maintains conversation history for coherent discussions
- **Personalized Responses**: Tailors responses based on specific birth chart data
- **Suggested Questions**: Generates relevant questions based on birth chart analysis
- **Input Validation**: Comprehensive validation for all birth chart parameters
- **Error Handling**: Graceful handling of API failures and invalid inputs

### Frontend Features
- **Modern Chat UI**: Clean, responsive chat interface with message bubbles
- **Real-time Chat**: Live conversation with typing indicators and message status
- **Birth Chart Integration**: Seamless integration with existing birth chart generation
- **Suggested Questions**: Smart question suggestions based on user's chart
- **Conversation History**: Persistent chat history within sessions
- **Mobile Responsive**: Works perfectly on all devices
- **Error Recovery**: Graceful error handling and user feedback

## 🛠️ Setup Instructions

### 1. OpenAI API Setup

#### Get Your OpenAI API Key
1. Go to [OpenAI API Dashboard](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the API key (starts with `sk-`)

#### Set Environment Variable
Add your OpenAI API key to your environment:

```bash
# Option 1: Set in terminal (temporary)
export OPENAI_API_KEY="sk-your-api-key-here"

# Option 2: Add to .env file (recommended)
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env

# Option 3: Set in your shell profile (permanent)
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd starlight_backend
pip install -r requirements.txt
```

#### Start the Backend Server
```bash
# Make sure you're in the backend directory
cd starlight_backend

# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd starlight-astral-guide
npm install
```

#### Start the Frontend Server
```bash
# Make sure you're in the frontend directory
cd starlight-astral-guide

# Start development server
npm run dev:local
```

## 📋 API Endpoints

### Chat Endpoints

#### POST `/api/chat/chat`
Start or continue a conversation with the AI astrologer.

**Request Body:**
```json
{
  "message": "What does my birth chart say about my career?",
  "birth_date": "1994-09-24",
  "birth_time": "14:40",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York",
  "house_system": "Placidus",
  "ayanamsa": "Lahiri",
  "conversation_id": "chat_20241205_143000",
  "user_name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Based on your birth chart, I can see that you have...",
  "conversation_id": "chat_20241205_143000",
  "user_message": "What does my birth chart say about my career?",
  "timestamp": "2024-12-05T14:30:00Z",
  "usage": {
    "total_tokens": 850,
    "prompt_tokens": 650,
    "completion_tokens": 200
  },
  "metadata": {
    "model": "gpt-4",
    "user_name": "John Doe",
    "message_count": 3
  }
}
```

#### POST `/api/chat/suggested-questions`
Get personalized question suggestions based on birth chart.

**Request Body:**
```json
{
  "birth_date": "1994-09-24",
  "birth_time": "14:40",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York",
  "house_system": "Placidus",
  "ayanamsa": "Lahiri"
}
```

**Response:**
```json
{
  "questions": [
    "What does my birth chart reveal about my personality?",
    "How does my Virgo Sun influence my life purpose?",
    "What does my Moon say about my emotional nature?",
    "How can I work with my retrograde planets?"
  ],
  "birth_chart_summary": {
    "sun_sign": "Virgo",
    "moon_sign": "Capricorn",
    "ascendant_sign": "Sagittarius",
    "dominant_sign": "Virgo"
  }
}
```

#### GET `/api/chat/health`
Check the health status of the chat service.

**Response:**
```json
{
  "status": "healthy",
  "service": "Astrological Chat Service",
  "openai_available": true,
  "features": [
    "Personalized Astrological Chat",
    "Birth Chart Context Integration",
    "Conversation History",
    "Suggested Questions",
    "Vedic Astrology Expertise"
  ],
  "timestamp": "2024-12-05T14:30:00Z"
}
```

#### GET `/api/chat/status`
Get detailed status information about the chat service.

**Response:**
```json
{
  "service_name": "Astrological Chat Service",
  "version": "1.0.0",
  "openai_configured": true,
  "active_conversations": 5,
  "conversation_ids": ["chat_20241205_143000", "chat_20241205_144500"],
  "features": {
    "birth_chart_context": true,
    "conversation_memory": true,
    "vedic_astrology": true,
    "personalized_responses": true,
    "suggested_questions": true
  },
  "limits": {
    "max_tokens_per_response": 1000,
    "conversation_history_limit": 20,
    "model": "gpt-4"
  }
}
```

## 🎯 Usage Guide

### 1. Access the Chat Feature

1. **Navigate to Chat**: Click on "AI Chat" in the navigation menu
2. **Enter Birth Details**: Provide your birth date, time, and location
3. **Start Chat**: Click "Start Chat Session" to begin your consultation

### 2. Chat Interface

#### Message Types
- **User Messages**: Your questions and comments (blue bubbles on the right)
- **AI Responses**: Personalized astrological guidance (gray bubbles on the left)
- **System Messages**: Status updates and notifications

#### Suggested Questions
- The chat displays personalized question suggestions based on your birth chart
- Click any suggestion to automatically send it as a message
- Questions are categorized by topic (Personality, Career, Relationships, etc.)

#### Features
- **Real-time Chat**: Messages appear instantly
- **Typing Indicator**: Shows when the AI is generating a response
- **Message History**: Scroll up to see previous messages
- **Copy Responses**: Long-press or right-click to copy AI responses

### 3. Question Examples

#### Personality & Character
- "What does my birth chart reveal about my personality?"
- "What are my key strengths and challenges?"
- "How do my Sun, Moon, and Rising signs work together?"

#### Career & Purpose
- "What career paths suit my astrological makeup?"
- "How can I use my planetary energies for success?"
- "What does my 10th house say about my career?"

#### Relationships
- "How can I improve my relationships based on my chart?"
- "What does my Venus placement mean for love?"
- "How do my relationship patterns show in my chart?"

#### Spiritual Growth
- "What spiritual practices would benefit me most?"
- "How can I work with challenging planetary transits?"
- "What does my North Node say about my soul purpose?"

## 🔧 Configuration Options

### AI Model Settings
- **Model**: GPT-4 (configurable in `chat_service.py`)
- **Max Tokens**: 1000 tokens per response
- **Temperature**: 0.7 (balanced creativity and accuracy)
- **Conversation History**: Last 20 messages

### Birth Chart Context
- **House System**: Placidus (default), Koch, Equal, Whole Sign
- **Ayanamsa**: Lahiri (default), multiple Vedic systems available
- **Timezone**: Auto-detected or manually specified

### Conversation Management
- **Session Storage**: In-memory (Redis recommended for production)
- **History Limit**: 20 messages per conversation
- **Timeout**: No automatic timeout (persists until server restart)

## 🛡️ Security & Privacy

### Data Protection
- **No Storage**: Conversations are not permanently stored
- **Session Only**: Chat history exists only during the session
- **API Security**: OpenAI API key is server-side only
- **Input Validation**: All inputs are validated and sanitized

### Privacy Features
- **Anonymous Usage**: No personal data required beyond birth details
- **Local Storage**: Birth chart data stored locally in browser
- **No Tracking**: No user tracking or analytics
- **Secure Transmission**: All API calls use HTTPS

## 🐛 Troubleshooting

### Common Issues

#### "Chat service is currently unavailable"
**Cause**: OpenAI API key not configured
**Solution**: 
1. Set the `OPENAI_API_KEY` environment variable
2. Restart the backend server
3. Verify the API key is valid

#### "Failed to initialize chat service"
**Cause**: Network issues or API rate limits
**Solution**:
1. Check internet connection
2. Verify OpenAI API key has available credits
3. Try again after a few minutes

#### "Birth chart generation failed"
**Cause**: Invalid birth chart data
**Solution**:
1. Verify birth date and time format
2. Check latitude/longitude coordinates
3. Ensure timezone is correctly specified

### Debug Mode

Enable debug logging in `chat_service.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check

Test the service health:
```bash
curl http://localhost:8000/api/chat/health
```

## 📊 Performance & Scaling

### Current Limitations
- **Memory Storage**: Conversations stored in memory (not persistent)
- **Single Instance**: No load balancing or clustering
- **Rate Limits**: Subject to OpenAI API rate limits

### Production Recommendations
- **Redis**: Use Redis for conversation storage
- **Database**: Store conversation history in PostgreSQL
- **Load Balancer**: Use nginx or similar for multiple instances
- **Rate Limiting**: Implement per-user rate limiting
- **Monitoring**: Add logging and monitoring for chat usage

## 🎨 Customization

### Modify AI Personality
Edit the system prompt in `chat_service.py`:
```python
def get_system_prompt(self) -> str:
    return """You are an expert Vedic astrologer with [your modifications]..."""
```

### Add New Question Categories
Extend the `get_suggested_questions` method:
```python
def get_suggested_questions(self, birth_chart: BirthChartResponse) -> List[str]:
    # Add your custom question logic here
    suggestions.extend([
        "Your custom question here",
        "Another custom question"
    ])
```

### Customize Chat UI
Modify the React components in `starlight-astral-guide/src/components/`:
- `AstrologicalChat.tsx`: Main chat interface
- `AstrologicalChatPage.tsx`: Chat page layout

## 📝 API Documentation

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Next Steps

### Planned Features
- **Voice Chat**: Audio input/output support
- **Chart Visuals**: Display birth chart alongside chat
- **Export Conversations**: Download chat history
- **Scheduled Readings**: Set up recurring consultations
- **Multiple Languages**: Support for different languages

### Contributing
To contribute to the chat functionality:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

---

## 🌟 Conclusion

The Astrological Chat feature provides a powerful, personalized way for users to explore their birth charts and receive guidance. With proper setup and configuration, it offers an engaging, educational experience that combines ancient wisdom with modern AI technology.

For additional support or questions, please refer to the main project documentation or open an issue in the repository.

Happy chatting with the stars! ✨ 