# 🌟 Starlight Astrology API - Swagger Documentation

## Overview

Your FastAPI application already has comprehensive **Swagger documentation** built-in! This document explains how to access and use the interactive API documentation.

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   cd starlight_backend
   python3 start_server.py
   ```

2. **Access the documentation:**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📚 Available Documentation Formats

### 1. Swagger UI (`/docs`)
- **Interactive documentation** with "Try it out" functionality
- Test endpoints directly from the browser
- View request/response schemas
- Copy curl commands
- **Best for**: Development and testing

### 2. ReDoc (`/redoc`)
- **Beautiful, responsive documentation**
- Better for reading and sharing
- Clean, professional layout
- **Best for**: Documentation and client presentations

### 3. OpenAPI JSON (`/openapi.json`)
- **Machine-readable API specification**
- Can be imported into tools like Postman
- Used by code generators
- **Best for**: Integration and tooling

## 🔧 API Endpoints

### 🌟 Astrology Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/astrology/birth-chart` | Generate complete birth chart |
| `GET` | `/api/astrology/birth-chart` | Legacy birth chart endpoint |
| `GET` | `/api/astrology/planets/{planet_name}` | Get specific planet position |
| `GET` | `/api/astrology/houses` | Get house cusps |
| `GET` | `/api/astrology/aspects` | Get planetary aspects |
| `GET` | `/api/astrology/chart-summary` | Get chart summary |
| `GET` | `/api/astrology/health` | Astrology service health check |
| `GET` | `/api/astrology/supported-planets` | List supported planets |
| `GET` | `/api/astrology/supported-house-systems` | List supported house systems |
| `GET` | `/api/astrology/zodiac-signs` | List zodiac signs |

### 📋 General Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and welcome |
| `GET` | `/health` | General health check |

## 🔮 Example Usage

### 1. Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out" button
4. Fill in the required parameters
5. Click "Execute" to test the API

### 2. Sample Request (Birth Chart)
```json
{
  "name": "Albert Einstein",
  "birth_date": "1879-03-14",
  "birth_time": "11:30",
  "latitude": 48.3969,
  "longitude": 9.9918,
  "timezone": "Europe/Berlin",
  "house_system": "Placidus"
}
```

### 3. Using curl
```bash
curl -X POST "http://localhost:8000/api/astrology/birth-chart" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Albert Einstein",
    "birth_date": "1879-03-14",
    "birth_time": "11:30",
    "latitude": 48.3969,
    "longitude": 9.9918,
    "timezone": "Europe/Berlin"
  }'
```

## 🎯 Features Already Implemented

Your API already includes:

✅ **Complete OpenAPI 3.0 specification**
✅ **Comprehensive endpoint documentation**
✅ **Request/response schema validation**
✅ **Interactive testing interface**
✅ **Example requests and responses**
✅ **Error response documentation**
✅ **Authentication documentation** (if applicable)
✅ **Custom OpenAPI schema enhancements**
✅ **Professional branding and descriptions**

## 🌟 Advanced Features

### Custom OpenAPI Schema
The API includes enhanced OpenAPI schema with:
- Custom logo and branding
- Detailed tag descriptions
- Example data for testing
- External documentation links
- Professional contact information

### Built-in Examples
Pre-configured examples include:
- Albert Einstein's birth chart
- Modern birth chart example
- Various house system comparisons

### Error Handling
Comprehensive error responses with:
- Detailed error messages
- HTTP status codes
- Validation error descriptions
- Helpful debugging information

## 🛠️ Customization Options

### Adding New Examples
To add custom examples to the Swagger UI, edit the `custom_openapi()` function in `app/main.py`:

```python
openapi_schema["components"]["examples"]["YourExample"] = {
    "summary": "Your Example",
    "description": "Description of your example",
    "value": {
        # Your example data
    }
}
```

### Customizing Documentation
- Edit endpoint docstrings for detailed descriptions
- Update `app/main.py` for main API information
- Modify Pydantic models for schema documentation
- Add response examples using `response_model`

## 🎨 Themes and Styling

The Swagger UI uses the default theme but can be customized:
- Custom CSS can be added
- Logo and branding can be modified
- Color schemes can be changed
- Layout can be customized

## 📱 Integration

### Frontend Integration
The OpenAPI specification can be used with:
- **Code generators**: Generate client SDKs
- **API testing tools**: Postman, Insomnia
- **Documentation platforms**: Stoplight, Swagger Hub
- **Monitoring tools**: API monitoring services

### Export Options
- Export OpenAPI JSON for external tools
- Generate client libraries
- Import into API testing platforms
- Share with team members

## 🔍 Testing the API

### Using the Demo Script
```bash
cd starlight_backend
python3 demo_api.py
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Get API Information
```bash
curl http://localhost:8000/
```

## 🌍 Deployment Notes

For production deployment:
- Update server URLs in the OpenAPI config
- Configure proper CORS settings
- Set up authentication if needed
- Enable HTTPS for secure documentation access

## 🎉 Conclusion

Your Starlight Astrology API already has **world-class Swagger documentation** built-in! Simply start the server and visit `/docs` to access the interactive documentation interface.

The documentation is:
- ✨ **Comprehensive** - covers all endpoints
- 🔧 **Interactive** - test directly from the browser
- 📱 **Responsive** - works on all devices
- 🌟 **Professional** - ready for production use

**Ready to use! Just start the server and explore the documentation at http://localhost:8000/docs** 