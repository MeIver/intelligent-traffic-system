# Intelligent Traffic System API Documentation System

This system provides automated generation and validation of API documentation for the Intelligent Traffic System. It supports multiple output formats and integrates with GitHub Actions for continuous documentation.

## Features

- **Automated Documentation Generation**: Convert OpenAPI specifications to Markdown, HTML, and PDF
- **Traffic-Specific Validation**: Validate API specs against traffic system requirements
- **Multiple Output Formats**: Generate documentation in Markdown, HTML, and PDF
- **GitHub Integration**: Automated workflows for CI/CD documentation generation
- **Quality Assurance**: Comprehensive validation and error reporting
- **Scheduled Updates**: Daily automatic documentation regeneration

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements-docs.txt

# Install system dependencies for PDF generation (optional)
sudo apt-get install wkhtmltopdf  # Ubuntu/Debian
# or
brew install wkhtmltopdf          # macOS
```

### Generate Documentation

```bash
# Generate all formats from OpenAPI spec
python scripts/traffic-api-docs-generator.py openapi/traffic-api.yaml

# Generate specific format only
python scripts/traffic-api-docs-generator.py openapi/traffic-api.yaml --format markdown
python scripts/traffic-api-docs-generator.py openapi/traffic-api.yaml --format html
python scripts/traffic-api-docs-generator.py openapi/traffic-api.yaml --format pdf

# Validate only without generating docs
python scripts/traffic-api-docs-generator.py openapi/traffic-api.yaml --validate-only
```

## File Structure

```
intelligent-traffic-system/
├── docs/
│   └── api/
│       ├── templates/
│       │   └── traffic-api-template.md    # Documentation template
│       └── generated/                     # Auto-generated docs
├── openapi/
│   └── traffic-api.yaml                   # OpenAPI specification
├── scripts/
│   └── traffic-api-docs-generator.py      # Main generator script
├── .github/
│   └── workflows/
│       └── traffic-api-docs.yml           # GitHub Actions workflow
├── requirements-docs.txt                  # Python dependencies
└── README-api-docs.md                     # This file
```

## API Documentation Template

The system uses `docs/api/templates/traffic-api-template.md` as a base template with the following sections:

1. **System Overview**: General API information and base URL
2. **API Authentication**: API key authentication details
3. **Traffic Endpoints**: Real-time traffic data, incidents, control endpoints
4. **Data Models**: TrafficFlow, TrafficIncident, TrafficSignal objects
5. **Rate Limiting**: Tier-based limits and best practices
6. **Error Handling**: HTTP status codes and error response format

## GitHub Actions Workflow

The automated workflow (`.github/workflows/traffic-api-docs.yml`) provides:

### Triggers
- **Scheduled**: Daily at 02:00 UTC
- **Pull Requests**: On changes to API specs or documentation files
- **Manual**: Via workflow_dispatch event

### Jobs
1. **generate-docs**: Generate documentation and validate OpenAPI spec
2. **quality-check**: Verify generated documentation quality
3. **deploy-docs**: (Optional) Deploy to hosting platform

### Artifacts
- Generated documentation (Markdown, HTML, PDF)
- Validation reports with detailed error information
- Quality check results

## OpenAPI Specification Requirements

The validation system checks for traffic-specific requirements:

### Required Endpoints
- `GET /traffic/real-time` - Real-time traffic data
- `POST /traffic/incidents` - Incident reporting
- `GET /control/signals/{signal_id}` - Signal status
- `PUT /control/signals/{signal_id}` - Signal control
- `POST /routes/calculate` - Route optimization

### Required Data Models
- `TrafficFlow` - Real-time traffic metrics
- `TrafficIncident` - Incident information
- `TrafficSignal` - Traffic signal configuration

### Authentication
- API key authentication scheme (`ApiKeyAuth`)
- Required security for all endpoints

## Customization

### Modifying the Template
Edit `docs/api/templates/traffic-api-template.md` to customize the documentation structure. Use placeholders like `{{endpoints}}` and `{{data_models}}` for auto-generated content.

### Adding New Validation Rules
Extend the `validate_traffic_spec` method in `traffic-api-docs-generator.py` to add custom validation rules for your traffic system requirements.

### Output Formats
The system supports multiple output formats. Add new format generators by extending the generator class with new methods following the existing pattern.

## Error Handling

The system provides detailed error reporting:

- **Validation Errors**: Specific issues with OpenAPI specification
- **Generation Errors**: Problems during documentation generation
- **Quality Warnings**: Issues with generated documentation quality

All errors are reported in the validation report and GitHub Actions logs.

## Contributing

1. Follow the existing code style and structure
2. Add tests for new functionality
3. Update documentation when making changes
4. Ensure all validations pass before submitting PRs

## License

MIT License - see LICENSE file for details.

## Support

For issues with the documentation system:
1. Check the validation report in `docs/api/generated/validation-report.json`
2. Review GitHub Actions workflow logs
3. Ensure all dependencies are properly installed
4. Verify OpenAPI specification compliance with traffic system requirements