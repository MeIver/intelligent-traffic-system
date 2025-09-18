# Intelligent Traffic System API Documentation

## System Overview

The Intelligent Traffic System API provides comprehensive access to real-time traffic data, traffic light control, congestion monitoring, and traffic analytics services. This RESTful API enables developers to integrate traffic management capabilities into their applications.

**Key Features:**
- Real-time traffic flow monitoring
- Traffic light control and synchronization
- Congestion detection and alerts
- Historical traffic data analysis
- Intersection management
- Vehicle counting and classification

**Base URL:** `https://api.traffic.example.com/v1`

## API Authentication

### API Key Authentication
All API requests require authentication using an API key. Include your API key in the `X-API-Key` header:

```http
GET /traffic/intersections HTTP/1.1
Host: api.traffic.example.com
X-API-Key: your-api-key-here
```

### OAuth 2.0 Authentication
For advanced applications, OAuth 2.0 is supported:

```http
POST /oauth/token HTTP/1.1
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret
```

### Rate Limit Headers
Responses include rate limit information:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: UTC timestamp when limit resets

## Traffic Endpoints

### Traffic Flow Monitoring

#### Get Real-time Traffic Flow
```http
GET /traffic/flow/{intersection_id}
```

**Parameters:**
- `intersection_id` (string): Unique intersection identifier
- `time_window` (optional, string): Time window for data (e.g., "5m", "1h")

**Response:**
```json
{
  "intersection_id": "int_12345",
  "timestamp": "2024-01-15T10:30:00Z",
  "vehicle_count": 45,
  "average_speed": 28.5,
  "congestion_level": "moderate",
  "lane_data": [
    {
      "lane_id": "lane_1",
      "vehicle_count": 12,
      "average_speed": 32.1
    }
  ]
}
```

### Traffic Light Control

#### Update Traffic Light Timing
```http
PUT /traffic/lights/{intersection_id}/timing
```

**Request Body:**
```json
{
  "green_duration": 30,
  "yellow_duration": 5,
  "red_duration": 25,
  "pattern": "standard",
  "emergency_override": false
}
```

### Congestion Management

#### Get Congestion Alerts
```http
GET /traffic/congestion/alerts
```

**Query Parameters:**
- `severity` (optional): Filter by severity level (low, medium, high, critical)
- `area` (optional): Geographic area filter
- `time_range` (optional): Time range for alerts

## Data Models

### TrafficFlow Data Model
```yaml
TrafficFlow:
  type: object
  properties:
    intersection_id:
      type: string
      description: Unique intersection identifier
    timestamp:
      type: string
      format: date-time
      description: Data collection timestamp
    vehicle_count:
      type: integer
      description: Total vehicles detected
    average_speed:
      type: number
      format: float
      description: Average vehicle speed in km/h
    congestion_level:
      type: string
      enum: [low, moderate, high, severe]
      description: Current congestion level
    lane_data:
      type: array
      items:
        $ref: '#/components/schemas/LaneData'
```

### LaneData Data Model
```yaml
LaneData:
  type: object
  properties:
    lane_id:
      type: string
      description: Lane identifier
    vehicle_count:
      type: integer
      description: Vehicles in this lane
    average_speed:
      type: number
      format: float
      description: Average speed in this lane
    vehicle_types:
      type: object
      description: Count by vehicle type
      properties:
        car:
          type: integer
        truck:
          type: integer
        bus:
          type: integer
        motorcycle:
          type: integer
```

### TrafficLight Data Model
```yaml
TrafficLight:
  type: object
  properties:
    intersection_id:
      type: string
    current_state:
      type: string
      enum: [red, yellow, green]
    state_duration:
      type: integer
      description: Seconds in current state
    next_change:
      type: string
      format: date-time
      description: Scheduled state change time
```

## Rate Limiting

### Standard Limits
- **Free Tier:** 100 requests/hour
- **Basic Tier:** 1,000 requests/hour
- **Professional Tier:** 10,000 requests/hour
- **Enterprise Tier:** Custom limits

### Endpoint-specific Limits
- Traffic flow endpoints: 60 requests/minute
- Traffic light control: 30 requests/minute
- Historical data: 20 requests/minute

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
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Maintenance or overload |

### Error Response Format
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 58 seconds.",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset": "2024-01-15T11:30:00Z"
    }
  }
}
```

### Common Error Codes
- `INVALID_API_KEY`: API key is invalid or expired
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INVALID_INTERSECTION`: Invalid intersection identifier
- `PERMISSION_DENIED`: Insufficient permissions for operation
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

### Retry Recommendations
- For 429 errors: Wait until reset time
- For 5xx errors: Implement exponential backoff
- For network errors: Retry with increasing delays

---

*This documentation is automatically generated from the OpenAPI specification. Last updated: {{timestamp}}*