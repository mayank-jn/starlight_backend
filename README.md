# 🌟 Starlight Astrology API

A comprehensive REST API for astrological birth chart generation with planets, houses, aspects, and interpretations.

## Features

✨ **Complete Birth Chart Generation**
- Planet positions in zodiac signs and houses
- House cusps with multiple house systems
- Planetary aspects with orbs
- Chart summary and interpretations

🤖 **AI-Powered Detailed Reports** (NEW!)
- **OpenAI Integration**: GPT-powered personalized astrological reports
- **5 Comprehensive Sections**: Personality, Career, Relationships, Health, Spiritual
- **Vedic Astrology Focus**: Traditional Indian astrology interpretations
- **Fallback System**: Graceful degradation to template-based reports
- **Customizable**: Configure models, enable/disable AI features

🪐 **Supported Planets**
- Traditional: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
- Modern: Uranus, Neptune, Pluto
- Lunar Nodes: Rahu (North Node), Ketu (South Node)

🏠 **House Systems**
- Placidus (default)
- Koch
- Equal House
- Whole Sign

🔄 **Planetary Aspects**
- Major: Conjunction, Opposition, Trine, Square, Sextile
- Minor: Quincunx, Semisextile, Semisquare, Sesquiquadrate

## Installation

### Prerequisites
- Python 3.8+
- Swiss Ephemeris data files

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Swiss Ephemeris data (optional for better accuracy):**
```bash
# On Ubuntu/Debian
sudo apt-get install libswe-dev

# On macOS
brew install swisseph

# Or download ephemeris files manually to /usr/share/swisseph/
```

3. **Run the API:**
```bash
# Development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. **Configure OpenAI (Optional but Recommended):**
```bash
# Copy the environment example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

5. **Test the API:**
```bash
python test_api.py
```

6. **Test OpenAI Integration:**
```bash
python demo_openai_integration.py
```

## API Endpoints

### 📍 Base URL: `http://localhost:8000`

### 🌟 Primary Endpoints

#### Generate Birth Chart (POST)
```
POST /api/astrology/birth-chart
```

#### Generate Detailed Report (POST) - NEW!
```
POST /api/astrology/detailed-report
```

**Request Body:**
```json
{
  "name": "John Doe",
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York",
  "house_system": "Placidus"
}
```

**Response:**
```json
{
  "name": "John Doe",
  "birth_datetime": "1990-01-15T14:30:00",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "julian_day": 2447893.1042,
  "house_system": "Placidus",
  "planets": [
    {
      "planet": "Sun",
      "longitude": 294.85,
      "latitude": 0.0,
      "distance": 0.983,
      "speed": 1.02,
      "sign": "Capricorn",
      "degree": 24.85,
      "house": 5,
      "retrograde": false
    }
  ],
  "houses": [
    {
      "number": 1,
      "cusp": 45.2,
      "sign": "Taurus",
      "ruler": "Venus"
    }
  ],
  "aspects": [
    {
      "planet1": "Sun",
      "planet2": "Moon",
      "aspect_type": "Trine",
      "angle": 120.5,
      "orb": 0.5,
      "applying": true
    }
  ],
  "chart_summary": {
    "sun_sign": "Capricorn",
    "moon_sign": "Virgo",
    "ascendant_sign": "Taurus",
    "dominant_sign": "Capricorn",
    "retrograde_planets": 2
  }
}
```

#### Generate Birth Chart (GET - Legacy)
```
GET /api/astrology/birth-chart?date=1990-01-15&time=14:30&lat=40.7128&lon=-74.0060
```

### 🪐 Individual Data Endpoints

#### Get Planet Position
```
GET /api/astrology/planets/{planet_name}?date=1990-01-15&time=14:30&lat=40.7128&lon=-74.0060
```

#### Get House Cusps
```
GET /api/astrology/houses?date=1990-01-15&time=14:30&lat=40.7128&lon=-74.0060&house_system=Placidus
```

#### Get Planetary Aspects
```
GET /api/astrology/aspects?date=1990-01-15&time=14:30&lat=40.7128&lon=-74.0060
```

#### Get Chart Summary
```
GET /api/astrology/chart-summary?date=1990-01-15&time=14:30&lat=40.7128&lon=-74.0060
```

### 📋 Info Endpoints

#### Health Check
```
GET /api/astrology/health
```

#### Supported Planets
```
GET /api/astrology/supported-planets
```

#### Supported House Systems
```
GET /api/astrology/supported-house-systems
```

#### Zodiac Signs
```
GET /api/astrology/zodiac-signs
```

## Usage Examples

### Python Example
```python
import requests

# Generate birth chart
data = {
    "name": "Jane Smith",
    "birth_date": "1985-12-25",
    "birth_time": "09:15",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "house_system": "Placidus"
}

response = requests.post("http://localhost:8000/api/astrology/birth-chart", json=data)
chart = response.json()

print(f"Sun Sign: {chart['chart_summary']['sun_sign']}")
print(f"Moon Sign: {chart['chart_summary']['moon_sign']}")
print(f"Ascendant: {chart['chart_summary']['ascendant_sign']}")
```

### JavaScript Example
```javascript
const generateBirthChart = async (birthData) => {
  const response = await fetch('http://localhost:8000/api/astrology/birth-chart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(birthData)
  });
  
  const chart = await response.json();
  return chart;
};

// Usage
const birthData = {
  name: "Alex Johnson",
  birth_date: "1992-07-04",
  birth_time: "16:45",
  latitude: 34.0522,
  longitude: -118.2437,
  timezone: "America/Los_Angeles",
  house_system: "Placidus"
};

generateBirthChart(birthData).then(chart => {
  console.log('Birth Chart:', chart);
});
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/astrology/birth-chart" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "birth_date": "1990-01-01",
    "birth_time": "12:00",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "house_system": "Placidus"
  }'
```

## Data Models

### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | No | Full name of the person |
| birth_date | string | Yes | Date in YYYY-MM-DD format |
| birth_time | string | Yes | Time in HH:MM format |
| latitude | float | Yes | Latitude (-90 to 90) |
| longitude | float | Yes | Longitude (-180 to 180) |
| timezone | string | No | Timezone (e.g., 'UTC', 'America/New_York') |
| house_system | string | No | House system (default: Placidus) |

### Response Structure

- **Planet Position**: longitude, latitude, distance, speed, sign, degree, house, retrograde
- **House**: number, cusp, sign, ruler
- **Aspect**: planet1, planet2, aspect_type, angle, orb, applying
- **Chart Summary**: dominant signs/houses, sun/moon/ascendant signs, retrograde count

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (validation errors)
- **404**: Not Found (invalid planet name)
- **500**: Internal Server Error

Error responses include:
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation with interactive testing.

## Development

### Running Tests
```bash
python test_api.py
```

### Code Structure
```
starlight_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app configuration
│   ├── models/
│   │   └── __init__.py      # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── astrology.py     # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── birth_chart.py   # Core astrological calculations
│   └── utils/
│       └── __init__.py
├── requirements.txt
├── test_api.py
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
- Create an issue in the repository
- Check the interactive documentation at `/docs`
- Run the test suite to verify functionality 