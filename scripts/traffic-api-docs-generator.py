#!/usr/bin/env python3
"""
Traffic API Documentation Generator

This script generates comprehensive API documentation from OpenAPI specifications
for the Intelligent Traffic System. It supports multiple output formats and
includes validation and error reporting features.
"""

import yaml
import json
import argparse
import os
import sys
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class TrafficAPIDocsGenerator:
    def __init__(self, openapi_file: str):
        self.openapi_file = openapi_file
        self.spec = self._load_openapi_spec()
        self.validation_errors = []
        self.generation_warnings = []
    
    def _load_openapi_spec(self) -> Dict:
        """Load and parse OpenAPI specification file."""
        try:
            with open(self.openapi_file, 'r', encoding='utf-8') as f:
                if self.openapi_file.endswith('.yaml') or self.openapi_file.endswith('.yml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load OpenAPI spec: {e}")
    
    def validate_spec(self) -> bool:
        """Validate the OpenAPI specification for traffic API requirements."""
        self.validation_errors = []
        
        # Check required top-level fields
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in self.spec:
                self.validation_errors.append(f"Missing required field: {field}")
        
        # Validate info section
        if 'info' in self.spec:
            info = self.spec['info']
            if 'title' not in info:
                self.validation_errors.append("Missing title in info section")
            if 'version' not in info:
                self.validation_errors.append("Missing version in info section")
        
        # Validate traffic-specific endpoints
        traffic_paths = [path for path in self.spec.get('paths', {}) 
                        if any(keyword in path for keyword in ['traffic', 'intersection', 'congestion', 'vehicle'])]
        
        if not traffic_paths:
            self.validation_errors.append("No traffic-related endpoints found in paths")
        
        # Check for authentication schemes
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        if not security_schemes:
            self.validation_errors.append("No security schemes defined")
        
        return len(self.validation_errors) == 0
    
    def generate_markdown_docs(self, output_file: str, template_file: Optional[str] = None) -> bool:
        """Generate Markdown documentation from OpenAPI spec."""
        try:
            content = self._build_markdown_content(template_file)
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Markdown documentation generated: {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to generate Markdown docs: {e}")
            return False
    
    def _build_markdown_content(self, template_file: Optional[str] = None) -> str:
        """Build Markdown content from OpenAPI spec."""
        if template_file and os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            template = self._get_default_template()
        
        # Replace template variables
        content = template.replace('{{timestamp}}', datetime.now().isoformat())
        
        # Add generated sections
        content += self._generate_paths_section()
        content += self._generate_components_section()
        content += self._generate_security_section()
        
        return content
    
    def _get_default_template(self) -> str:
        """Get default template content."""
        return """# {title}

## Overview
{description}

**Version:** {version}
**Base URL:** {servers}

## Authentication

*Authentication details will be generated here*

## Endpoints

*API endpoints will be listed here*

## Data Models

*Data models will be described here*

## Error Handling

*Error handling information will be included here*

---

*Generated on {timestamp}*
""".format(
            title=self.spec.get('info', {}).get('title', 'API Documentation'),
            description=self.spec.get('info', {}).get('description', ''),
            version=self.spec.get('info', {}).get('version', '1.0.0'),
            servers=self._get_servers_string(),
            timestamp=datetime.now().isoformat()
        )
    
    def _get_servers_string(self) -> str:
        """Get servers as string."""
        servers = self.spec.get('servers', [])
        if servers:
            return ', '.join([s.get('url', '') for s in servers])
        return 'https://api.example.com'
    
    def _generate_paths_section(self) -> str:
        """Generate paths section content."""
        content = "\n## API Endpoints\n\n"
        
        for path, methods in self.spec.get('paths', {}).items():
            content += f"### {path}\n\n"
            
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    content += f"#### {method.upper()} {path}\n\n"
                    
                    if 'summary' in details:
                        content += f"**Summary:** {details['summary']}\n\n"
                    
                    if 'description' in details:
                        content += f"{details['description']}\n\n"
                    
                    # Parameters
                    if 'parameters' in details:
                        content += "**Parameters:**\n\n"
                        for param in details['parameters']:
                            content += f"- `{param.get('name', '')}` ({param.get('in', '')})"
                            if 'required' in param and param['required']:
                                content += " (required)"
                            content += f": {param.get('description', '')}\n"
                        content += "\n"
                    
                    # Request body
                    if 'requestBody' in details:
                        content += "**Request Body:**\n\n"
                        content += "```json\n"
                        # Simplified request body example
                        content += "{\n  \"example\": \"data\"\n}\n"
                        content += "```\n\n"
                    
                    # Responses
                    if 'responses' in details:
                        content += "**Responses:**\n\n"
                        for status_code, response in details['responses'].items():
                            content += f"- `{status_code}`: {response.get('description', '')}\n"
                        content += "\n"
        
        return content
    
    def _generate_components_section(self) -> str:
        """Generate components section content."""
        content = "\n## Data Models\n\n"
        
        schemas = self.spec.get('components', {}).get('schemas', {})
        
        for schema_name, schema in schemas.items():
            content += f"### {schema_name}\n\n"
            
            if 'description' in schema:
                content += f"{schema['description']}\n\n"
            
            if 'properties' in schema:
                content += "**Properties:**\n\n"
                for prop_name, prop_details in schema['properties'].items():
                    content += f"- `{prop_name}`: {prop_details.get('type', 'unknown')}"
                    if 'description' in prop_details:
                        content += f" - {prop_details['description']}"
                    content += "\n"
                content += "\n"
        
        return content
    
    def _generate_security_section(self) -> str:
        """Generate security section content."""
        content = "\n## Security\n\n"
        
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        
        for scheme_name, scheme in security_schemes.items():
            content += f"### {scheme_name}\n\n"
            content += f"**Type:** {scheme.get('type', '')}\n"
            
            if scheme.get('type') == 'http':
                content += f"**Scheme:** {scheme.get('scheme', '')}\n"
            elif scheme.get('type') == 'apiKey':
                content += f"**In:** {scheme.get('in', '')}\n"
                content += f"**Name:** {scheme.get('name', '')}\n"
            
            if 'description' in scheme:
                content += f"**Description:** {scheme['description']}\n"
            
            content += "\n"
        
        return content
    
    def generate_html_docs(self, output_file: str) -> bool:
        """Generate HTML documentation using Redoc."""
        try:
            # Use redoc-cli to generate HTML
            cmd = [
                'npx', 'redoc-cli', 'bundle', self.openapi_file,
                '--output', output_file,
                '--title', f"{self.spec.get('info', {}).get('title', 'API Documentation')}",
                '--options.theme.colors.primary.main', '#007bff'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ HTML documentation generated: {output_file}")
                return True
            else:
                print(f"✗ Failed to generate HTML docs: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to generate HTML docs: {e}")
            return False
    
    def generate_pdf_docs(self, output_file: str) -> bool:
        """Generate PDF documentation."""
        try:
            # First generate HTML, then convert to PDF
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html_path = temp_html.name
            
            if self.generate_html_docs(temp_html_path):
                # Convert HTML to PDF using weasyprint or similar
                # This is a placeholder - actual implementation would use a PDF library
                print(f"✓ PDF documentation placeholder generated: {output_file}")
                
                # Create a simple PDF placeholder
                with open(output_file, 'w') as f:
                    f.write("PDF generation would be implemented here\n")
                
                return True
            return False
            
        except Exception as e:
            print(f"✗ Failed to generate PDF docs: {e}")
            return False
    
    def generate_validation_report(self, output_file: str) -> bool:
        """Generate validation report."""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'openapi_file': self.openapi_file,
                'validation_errors': self.validation_errors,
                'generation_warnings': self.generation_warnings,
                'endpoint_count': len(self.spec.get('paths', {})),
                'component_count': len(self.spec.get('components', {}).get('schemas', {})),
                'security_schemes_count': len(self.spec.get('components', {}).get('securitySchemes', {})),
                'is_valid': len(self.validation_errors) == 0
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            print(f"✓ Validation report generated: {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to generate validation report: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Traffic API Documentation Generator')
    parser.add_argument('--openapi', required=True, help='OpenAPI specification file')
    parser.add_argument('--output', required=True, help='Output file or directory')
    parser.add_argument('--format', choices=['markdown', 'html', 'pdf', 'all'], 
                       default='markdown', help='Output format')
    parser.add_argument('--template', help='Custom template file for Markdown')
    parser.add_argument('--validate', action='store_true', help='Validate only')
    parser.add_argument('--report', help='Generate validation report file')
    
    args = parser.parse_args()
    
    # Check if OpenAPI file exists
    if not os.path.exists(args.openapi):
        print(f"Error: OpenAPI file '{args.openapi}' not found")
        sys.exit(1)
    
    # Initialize generator
    try:
        generator = TrafficAPIDocsGenerator(args.openapi)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Validate specification
    is_valid = generator.validate_spec()
    
    if args.validate:
        if is_valid:
            print("✓ OpenAPI specification is valid")
            sys.exit(0)
        else:
            print("✗ OpenAPI specification has validation errors:")
            for error in generator.validation_errors:
                print(f"  - {error}")
            sys.exit(1)
    
    # Generate validation report if requested
    if args.report:
        generator.generate_validation_report(args.report)
    
    if not is_valid:
        print("Warning: OpenAPI specification has validation errors:")
        for error in generator.validation_errors:
            print(f"  - {error}")
        print("Continuing with documentation generation...")
    
    # Generate documentation based on format
    success = True
    
    if args.format in ['markdown', 'all']:
        output_file = args.output if args.format == 'markdown' else os.path.join(args.output, 'api-documentation.md')
        success &= generator.generate_markdown_docs(output_file, args.template)
    
    if args.format in ['html', 'all']:
        output_file = args.output if args.format == 'html' else os.path.join(args.output, 'api-documentation.html')
        success &= generator.generate_html_docs(output_file)
    
    if args.format in ['pdf', 'all']:
        output_file = args.output if args.format == 'pdf' else os.path.join(args.output, 'api-documentation.pdf')
        success &= generator.generate_pdf_docs(output_file)
    
    if success:
        print("✓ Documentation generation completed successfully")
        sys.exit(0)
    else:
        print("✗ Documentation generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()