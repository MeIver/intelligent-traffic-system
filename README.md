# Intelligent Traffic System

A comprehensive intelligent traffic management system providing real-time traffic monitoring, optimization, and control capabilities for smart cities.

## Features

- **Real-time Traffic Monitoring**: Live traffic data collection and analysis
- **Incident Management**: Traffic incident reporting and response coordination
- **Signal Control**: Adaptive traffic signal optimization
- **Route Optimization**: Intelligent routing based on current conditions
- **API Integration**: RESTful API for system integration
- **Automated Documentation**: Self-updating API documentation system

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+

### Installation

```bash
# Clone the repository
git clone https://github.com/MeIver/intelligent-traffic-system.git
cd intelligent-traffic-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

## API Documentation

This project includes an automated API documentation system. See [README-api-docs.md](README-api-docs.md) for details.

### Generate Documentation

```bash
# Install documentation dependencies
pip install -r requirements-docs.txt

# Generate API documentation
python scripts/traffic-api-docs-generator.py openapi/traffic-api.yaml
```

### Automated Workflows

The documentation system includes GitHub Actions workflows that:
- Generate documentation daily at 02:00 UTC
- Validate API specifications on pull requests
- Produce multiple output formats (Markdown, HTML, PDF)
- Provide detailed validation reports

## Project Structure

```
intelligent-traffic-system/
├── api/                 # API application code
├── core/               # Core system functionality
├── docs/               # Documentation
│   └── api/           # API documentation
├── openapi/            # OpenAPI specifications
├── scripts/            # Utility scripts
├── .github/           # GitHub Actions workflows
├── requirements.txt   # Main dependencies
├── requirements-docs.txt  # Documentation dependencies
└── README.md          # This file
```

## API Endpoints

### Traffic Data
- `GET /api/v1/traffic/real-time` - Get real-time traffic data
- `POST /api/v1/traffic/incidents` - Report traffic incidents
- `GET /api/v1/traffic/history` - Historical traffic data

### Traffic Control
- `GET /api/v1/control/signals` - List traffic signals
- `PUT /api/v1/control/signals/{id}` - Update signal configuration
- `GET /api/v1/control/status` - System status

### Route Planning
- `POST /api/v1/routes/calculate` - Calculate optimal routes
- `GET /api/v1/routes/alternatives` - Get route alternatives

## Development

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting
- Pytest for testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_traffic_api.py

# Run with coverage
pytest --cov=.
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure all tests pass and documentation is updated.

## Deployment

### Production Setup

1. Set up production database and cache
2. Configure environment variables
3. Run migrations
4. Set up reverse proxy (nginx)
5. Configure SSL certificates
6. Set up monitoring and logging

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Run specific services
docker-compose up api worker
```

## Monitoring

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus metrics endpoint
- **Logging**: Structured JSON logging
- **Alerting**: Integration with monitoring systems

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Open an issue on GitHub
- Check the documentation
- Review API specifications

## Acknowledgments

- Traffic data providers and APIs
- Open source libraries and frameworks
- Contributing developers and researchers