# Intelligent Traffic System API Documentation

## System Overview

The Intelligent Traffic System API provides real-time traffic data management, traffic flow optimization, and intelligent routing capabilities for smart city infrastructure. This RESTful API enables integration with traffic sensors, cameras, and control systems to optimize urban mobility.

**Base URL**: `https://api.traffic.example.com/v1`
**Protocol**: HTTPS
**Content-Type**: `application/json`

## API Authentication

### API Key Authentication
All endpoints require authentication via API key. Include your API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Obtaining API Keys
1. Register at the Traffic Management Portal
2. Generate API keys with appropriate permissions
3. Keys are rate-limited based on subscription tier

### Token Refresh
Long-lived operations may require token refresh:
```http
POST /auth/refresh
Authorization: Bearer EXPIRED_TOKEN
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

## Traffic Endpoints

### Traffic Data Collection

#### Get Real-time Traffic Data
```http
GET /traffic/real-time
```

**Parameters**:
- `location` (required): Geographic coordinates or area ID
- `radius` (optional): Search radius in meters (default: 1000)
- `sensor_types` (optional): Comma-separated sensor types

**Response**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "area_id": "NYC_DT"
  },
  "traffic_flow": {
    "vehicle_count": 1250,
    "average_speed": 45.2,
    "congestion_level": "MODERATE"
  },
  "sensor_data": [
    {
      "sensor_id": "cam_001",
      "type": "CAMERA",
      "status": "ACTIVE",
      "data": {
        "vehicle_types": {"CAR": 800, "TRUCK": 150, "BUS": 50},
        "lane_occupancy": [0.75, 0.68, 0.82]
      }
    }
  ]
}
```

#### Submit Traffic Incident
```http
POST /traffic/incidents
Content-Type: application/json

{
  "type": "ACCIDENT",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "severity": "HIGH",
  "description": "Multi-vehicle collision on main road",
  "affected_lanes": [1, 2]
}
```

### Traffic Control

#### Adjust Traffic Signals
```http
PUT /control/signals/{signal_id}
Content-Type: application/json

{
  "pattern": "EMERGENCY",
  "duration": 300,
  "priority": "HIGH"
}
```

#### Get Signal Status
```http
GET /control/signals/{signal_id}
```

### Route Optimization

#### Calculate Optimal Route
```http
POST /routes/calculate
Content-Type: application/json

{
  "origin": {"latitude": 40.7128, "longitude": -74.0060},
  "destination": {"latitude": 40.7589, "longitude": -73.9851},
  "vehicle_type": "CAR",
  "preferences": {
    "avoid_tolls": true,
    "minimize_time": true
  }
}
```

## Data Models

### TrafficFlow Object
```json
{
  "vehicle_count": 1250,
  "average_speed": 45.2,
  "congestion_level": "MODERATE",
  "timestamp": "2024-01-15T10:30:00Z",
  "predicted_trend": "INCREASING"
}
```

### TrafficIncident Object
```json
{
  "id": "inc_001",
  "type": "ACCIDENT",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "street": "Main Street",
    "intersection": "5th Avenue"
  },
  "severity": "HIGH",
  "description": "Multi-vehicle collision",
  "start_time": "2024-01-15T10:25:00Z",
  "estimated_clearance": "2024-01-15T11:30:00Z",
  "affected_lanes": [1, 2],
  "status": "ACTIVE"
}
```

### TrafficSignal Object
```json
{
  "id": "signal_001",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "intersection": "Main St & 5th Ave"
  },
  "current_pattern": "NORMAL",
  "phase_timings": {
    "green": 30,
    "yellow": 5,
    "red": 25
  },
  "status": "OPERATIONAL",
  "last_maintenance": "2024-01-10T08:00:00Z"
}
```

## Rate Limiting

### Tier-based Limits
- **Free Tier**: 100 requests/hour
- **Basic Tier**: 1,000 requests/hour  
- **Professional Tier**: 10,000 requests/hour
- **Enterprise Tier**: Custom limits

### Rate Limit Headers
Responses include rate limit information:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 850
X-RateLimit-Reset: 1705312800
```

### Best Practices
- Implement exponential backoff for retries
- Cache responses when appropriate
- Monitor rate limit headers
- Use webhooks for real-time updates instead of polling

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Maintenance |

### Error Response Format
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit of 1000 requests per hour exceeded",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset_in": 3598
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes
- `INVALID_API_KEY`: Authentication failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INVALID_LOCATION`: Geographic coordinates invalid
- `SENSOR_UNAVAILABLE`: Requested sensor not operational
- `ROUTE_UNAVAILABLE`: No valid route found
- `MAINTENANCE_MODE`: System undergoing maintenance

### Retry Recommendations
- 429 errors: Wait for reset time + random jitter
- 5xx errors: Exponential backoff with max 3 retries
- Network errors: Immediate retry with circuit breaker