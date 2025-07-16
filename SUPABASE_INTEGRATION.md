# 🗄️ Supabase Integration Guide

## Overview

The Starlight Astrology API now includes **comprehensive Supabase integration** for user profile management. This integration allows you to store and manage user birth chart information, enabling personalized astrological experiences.

## 🚀 Features

### ✨ User Profile Management
- **Complete CRUD Operations**: Create, Read, Update, Delete user profiles
- **Birth Chart Data Storage**: Store all necessary birth information for chart generation
- **Astrological Preferences**: Save user's preferred house system and ayanamsa
- **Location Information**: Store detailed birth location including coordinates and address
- **Secure Authentication**: Row-level security ensuring users can only access their own data

### 🎯 Key Benefits
- **Persistent Storage**: User profiles saved securely in PostgreSQL database
- **Fast Retrieval**: Optimized queries with proper indexing
- **Data Validation**: Comprehensive validation for all birth chart parameters
- **Scalable Architecture**: Built on Supabase's robust infrastructure
- **Real-time Updates**: Automatic timestamp tracking for all changes

## 🛠️ Setup Instructions

### 1. Database Schema Setup

Run the provided SQL schema in your Supabase project:

```sql
-- Execute the contents of supabase_schema.sql in your Supabase SQL Editor
-- This creates the user_profiles table with all necessary constraints and indexes
```

### 2. Environment Configuration

Create a `.env` file in your `starlight_backend` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# OpenAI Configuration (existing)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Default timezone is now set to IST (Asia/Kolkata)
```

### 3. Install Dependencies

```bash
cd starlight_backend
pip install -r requirements.txt
```

### 4. Start the Server

```bash
# Start the development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 📋 API Endpoints

### Base URL: `http://localhost:8000/api/profile`

### 1. Get User Profile

```http
GET /api/profile/profile/{user_id}
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "id": "profile-uuid",
    "user_id": "user-uuid",
    "name": "John Doe",
    "birth_date": "1990-01-15",
    "birth_time": "14:30",
       "latitude": 40.7128,
   "longitude": -74.0060,
   "timezone": "Asia/Kolkata",
   "city": "New York",
   "state": "NY",
   "country": "USA",
   "created_at": "2024-01-15T10:30:00Z",
   "updated_at": "2024-01-15T10:30:00Z"
 },
 "message": "Profile retrieved successfully"
}
```

### 2. Create User Profile

```http
POST /api/profile/profile
```

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "name": "John Doe",
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "Asia/Kolkata",
  "city": "New York",
  "state": "NY",
  "country": "USA"
}
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "id": "profile-uuid",
    "user_id": "user-uuid",
    "name": "John Doe",
    "birth_date": "1990-01-15",
    "birth_time": "14:30",
    "latitude": 40.7128,
    "longitude": -74.0060,
         "timezone": "Asia/Kolkata",
     "city": "New York",
     "state": "NY",
     "country": "USA",
     "created_at": "2024-01-15T10:30:00Z",
     "updated_at": "2024-01-15T10:30:00Z"
   },
   "message": "Profile created successfully"
}
```

### 3. Update User Profile

```http
PUT /api/profile/profile/{user_id}
```

**Request Body (Partial Update):**
```json
{
  "name": "John Smith",
  "city": "Los Angeles",
  "state": "CA"
}
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "id": "profile-uuid",
    "user_id": "user-uuid",
    "name": "John Smith",
    "birth_date": "1990-01-15",
    "birth_time": "14:30",
    "latitude": 40.7128,
    "longitude": -74.0060,
         "timezone": "Asia/Kolkata",
     "city": "Los Angeles",
     "state": "CA",
     "country": "USA",
     "created_at": "2024-01-15T10:30:00Z",
     "updated_at": "2024-01-15T11:45:00Z"
  },
  "message": "Profile updated successfully"
}
```

### 4. Delete User Profile

```http
DELETE /api/profile/profile/{user_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile deleted successfully"
}
```

### 5. Check Profile Exists

```http
GET /api/profile/profile/{user_id}/exists
```

**Response:**
```json
{
  "success": true,
  "exists": true,
  "user_id": "user-uuid"
}
```

### 6. Get All Profiles (Admin)

```http
GET /api/profile/profiles?limit=100&offset=0
```

**Response:**
```json
{
  "success": true,
  "profiles": [
    {
      "id": "profile-uuid-1",
      "user_id": "user-uuid-1",
      "name": "John Doe",
      "birth_date": "1990-01-15",
      "birth_time": "14:30",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "timezone": "America/New_York",
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1,
  "limit": 100,
  "offset": 0,
  "message": "Retrieved 1 profiles"
}
```

### 7. Health Check

```http
GET /api/profile/health
```

**Response:**
```json
{
  "service": "Profile Management API",
  "version": "1.0.0",
  "status": "healthy",
  "database": {
    "status": "healthy",
    "database": "connected",
    "total_profiles": 5,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "endpoints": {
    "get_profile": "GET /profile/{user_id}",
    "create_profile": "POST /profile",
    "update_profile": "PUT /profile/{user_id}",
    "delete_profile": "DELETE /profile/{user_id}",
    "check_exists": "GET /profile/{user_id}/exists",
    "get_all_profiles": "GET /profiles",
    "health_check": "GET /health"
  }
}
```

## 🔧 Data Models

### UserProfile Model

```python
class UserProfile(BaseModel):
    id: Optional[str] = Field(None, description="Profile ID")
    user_id: str = Field(..., description="User ID from Supabase Auth")
    name: Optional[str] = Field(None, description="User's full name")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")
    timezone: Optional[str] = Field(default="Asia/Kolkata", description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")
    city: Optional[str] = Field(None, description="Birth city")
    state: Optional[str] = Field(None, description="Birth state/province")
    country: Optional[str] = Field(None, description="Birth country")
    created_at: Optional[datetime] = Field(None, description="Profile creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Profile update timestamp")
```

### Validation Rules

- **birth_date**: Must be in YYYY-MM-DD format
- **birth_time**: Must be in HH:MM format
- **latitude**: Must be between -90 and 90
- **longitude**: Must be between -180 and 180

## 🔐 Security Features

### Row Level Security (RLS)
- Users can only access their own profiles
- Automatic user_id validation on all operations
- Secure policies prevent unauthorized access

### Data Validation
- Comprehensive validation for all input fields
- Type checking and constraint validation
- Error handling with detailed messages

### Connection Security
- Secure connection to Supabase
- Environment variable configuration
- API key protection

## 🚀 Usage Examples

### Python Client Example

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/profile"

# Create a new profile
profile_data = {
    "user_id": "user-uuid",
    "name": "John Doe",
    "birth_date": "1990-01-15",
    "birth_time": "14:30",
    "latitude": 40.7128,
    "longitude": -74.0060,
         "timezone": "Asia/Kolkata",
     "city": "New York",
     "state": "NY",
     "country": "USA"
 }

 response = requests.post(f"{BASE_URL}/profile", json=profile_data)
print(response.json())

# Get the profile
user_id = "user-uuid"
response = requests.get(f"{BASE_URL}/profile/{user_id}")
print(response.json())

# Update the profile
update_data = {
    "name": "John Smith",
    "city": "Los Angeles",
    "state": "CA"
}

response = requests.put(f"{BASE_URL}/profile/{user_id}", json=update_data)
print(response.json())
```

### JavaScript/Frontend Integration

```javascript
// Profile API client
class ProfileAPI {
  constructor(baseURL = 'http://localhost:8000/api/profile') {
    this.baseURL = baseURL;
  }

  async createProfile(profileData) {
    const response = await fetch(`${this.baseURL}/profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });
    return response.json();
  }

  async getProfile(userId) {
    const response = await fetch(`${this.baseURL}/profile/${userId}`);
    return response.json();
  }

  async updateProfile(userId, updateData) {
    const response = await fetch(`${this.baseURL}/profile/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    });
    return response.json();
  }

  async deleteProfile(userId) {
    const response = await fetch(`${this.baseURL}/profile/${userId}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  async checkProfileExists(userId) {
    const response = await fetch(`${this.baseURL}/profile/${userId}/exists`);
    return response.json();
  }
}

// Usage example
const profileAPI = new ProfileAPI();

// Create a new profile
const newProfile = {
  user_id: 'user-uuid',
  name: 'John Doe',
  birth_date: '1990-01-15',
  birth_time: '14:30',
  latitude: 40.7128,
  longitude: -74.0060,
  timezone: 'Asia/Kolkata',
  city: 'New York',
  state: 'NY',
  country: 'USA'
};

profileAPI.createProfile(newProfile)
  .then(response => console.log('Profile created:', response))
  .catch(error => console.error('Error:', error));
```

## 🐛 Troubleshooting

### Common Issues

1. **"SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required"**
   - Make sure you have created a `.env` file with the correct Supabase credentials

2. **"Profile already exists for user_id"**
   - Use the PUT endpoint to update existing profiles instead of POST

3. **"No profile found for user_id"**
   - Check that the user_id exists and the profile was created successfully

4. **"Database error"**
   - Verify your Supabase connection and table schema
   - Check the server logs for detailed error messages

### Debug Steps

1. **Check Server Health**:
   ```bash
   curl http://localhost:8000/api/profile/health
   ```

2. **Verify Database Connection**:
   ```bash
   curl http://localhost:8000/api/profile/health
   ```

3. **Test Profile Creation**:
   ```bash
   curl -X POST http://localhost:8000/api/profile/profile \
     -H "Content-Type: application/json" \
     -d '{"user_id":"test-user","name":"Test User","birth_date":"1990-01-01","birth_time":"12:00","latitude":40.7128,"longitude":-74.0060}'
   ```

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

Feel free to contribute to this integration by:
- Adding new features
- Improving documentation
- Reporting bugs
- Suggesting enhancements

## 📄 License

This integration is part of the Starlight Astrology API project and follows the same license terms. 