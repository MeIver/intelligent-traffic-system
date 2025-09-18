#!/usr/bin/env python3
"""
Traffic API Documentation Generator

This script generates comprehensive API documentation from OpenAPI specifications
for the Intelligent Traffic System. It supports multiple output formats and
includes validation and error reporting features.
"""

import argparse
import json
import yaml
import os
import sys
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import tempfile
import re

class TrafficAPIDocsGenerator:
    def __init__(self, openapi_path: str, output_dir: str):
        self.openapi_path = openapi_path
        self.output_dir = output_dir
        self.spec = None
        self.errors = []
        self.warnings = []
        
    def load_openapi_spec(self) -> bool:
        """Load and validate OpenAPI specification"""
        try:
            with open(self.openapi_path, 'r', encoding='utf-8') as f:
                if self.openapi_path.endswith('.yaml') or self.openapi_path.endswith('.yml'):
                    self.spec = yaml.safe_load(f)
                else:
                    self.spec = json.load(f)
            
            # Basic validation
            if not self.validate_openapi_spec():
                return False
                
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to load OpenAPI spec: {str(e)}")
            return False
    
    def validate_openapi_spec(self) -> bool:
        """Validate OpenAPI specification structure"""
        required_fields = ['openapi', 'info', 'paths']
        
        for field in required_fields:
            if field not in self.spec:
                self.errors.append(f"Missing required field: {field}")
                return False
        
        # Validate info section
        info_required = ['title', 'version']
        for field in info_required:
            if field not in self.spec['info']:
                self.errors.append(f"Missing required info field: {field}")
                return False
        
        # Validate traffic-specific endpoints
        self.validate_traffic_endpoints()
        
        return len(self.errors) == 0
    
    def validate_traffic_endpoints(self):
        """Validate traffic-specific API endpoints"""
        expected_endpoints = [
            '/traffic/flow',
            '/traffic-lights/{intersection_id}',
            '/congestion/alerts',
            '/routes/optimize'
        ]
        
        found_endpoints = []
        for path in self.spec.get('paths', {}):
            found_endpoints.append(path)
            
            # Validate path parameters for traffic endpoints
            if '{intersection_id}' in path:
                methods = self.spec['paths'][path]
                for method in methods.values():
                    if 'parameters' in method:
                        has_intersection_param = any(
                            param.get('name') == 'intersection_id' and 
                            param.get('in') == 'path'
                            for param in method['parameters']
                        )
                        if not has_intersection_param:
                            self.warnings.append(
                                f"Path {path} should have intersection_id path parameter"
                            )
        
        # Check for missing expected endpoints
        for expected in expected_endpoints:
            if expected not in found_endpoints:
                self.warnings.append(f"Expected endpoint not found: {expected}")
    
    def generate_markdown_docs(self) -> bool:
        """Generate Markdown documentation"""
        try:
            template_path = Path('docs/api/templates/traffic-api-template.md')
            if not template_path.exists():
                self.errors.append("Template file not found")
                return False
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Replace template variables
            content = template.replace(
                '{{timestamp}}', 
                datetime.datetime.now().isoformat()
            )
            
            # Add generated endpoints section
            endpoints_content = self._generate_endpoints_section()
            content = content.replace('## Traffic Endpoints', endpoints_content)
            
            # Add data models section
            models_content = self._generate_models_section()
            content = content.replace('## Data Models', models_content)
            
            # Save generated documentation
            output_path = Path(self.output_dir) / 'traffic-api-documentation.md'
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Markdown documentation generated: {output_path}")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to generate Markdown docs: {str(e)}")
            return False
    
    def generate_html_docs(self) -> bool:
        """Generate HTML documentation using redoc-cli"""
        try:
            # Check if redoc-cli is available
            try:
                subprocess.run(['npx', '--yes', 'redoc-cli', '--version'], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.warnings.append("redoc-cli not available, skipping HTML generation")
                return False
            
            # Generate HTML using redoc-cli
            html_output = Path(self.output_dir) / 'traffic-api-documentation.html'
            
            result = subprocess.run([
                'npx', '--yes', 'redoc-cli', 'bundle', self.openapi_path,
                '--output', str(html_output),
                '--title', 'Intelligent Traffic System API Documentation',
                '--options.theme.colors.primary.main', '#2c5aa0'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.errors.append(f"redoc-cli failed: {result.stderr}")
                return False
            
            print(f"HTML documentation generated: {html_output}")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to generate HTML docs: {str(e)}")
            return False
    
    def generate_pdf_docs(self) -> bool:
        """Generate PDF documentation"""
        try:
            # First generate HTML, then convert to PDF
            if not self.generate_html_docs():
                return False
            
            # Check if we have tools for PDF conversion
            try:
                # This would require additional tools like puppeteer
                # For now, we'll just note that PDF generation requires setup
                self.warnings.append(
                    "PDF generation requires additional setup with puppeteer "
                    "or similar tools. HTML documentation was generated successfully."
                )
                return True
                
            except Exception as e:
                self.warnings.append(f"PDF generation setup incomplete: {str(e)}")
                return False
                
        except Exception as e:
            self.errors.append(f"Failed to generate PDF docs: {str(e)}")
            return False
    
    def _generate_endpoints_section(self) -> str:
        """Generate endpoints section from OpenAPI spec"""
        if not self.spec or 'paths' not in self.spec:
            return "## Traffic Endpoints\n\nNo endpoints defined in OpenAPI specification.\n"
        
        content = "## Traffic Endpoints\n\n"
        
        for path, methods in self.spec['paths'].items():
            content += f"### {path}\n\n"
            
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    content += f"#### {method.upper()} {path}\n\n"
                    
                    if 'summary' in details:
                        content += f"**Summary**: {details['summary']}\n\n"
                    
                    if 'description' in details:
                        content += f"{details['description']}\n\n"
                    
                    # Parameters
                    if 'parameters' in details:
                        content += "**Parameters**:\n\n"
                        content += "| Name | In | Type | Required | Description |\n"
                        content += "|------|----|------|----------|-------------|\n"
                        
                        for param in details['parameters']:
                            param_type = param.get('schema', {}).get('type', 'string')
                            content += f"| {param['name']} | {param['in']} | {param_type} | {param.get('required', False)} | {param.get('description', '')} |\n"
                        content += "\n"
                    
                    # Request body
                    if 'requestBody' in details:
                        content += "**Request Body**:\n\n"
                        content += "```json\n"
                        # Simplified example - in real implementation, would generate from schema
                        content += "{\n  \"example\": \"request body\"\n}\n"
                        content += "```\n\n"
                    
                    # Responses
                    if 'responses' in details:
                        content += "**Responses**:\n\n"
                        for status_code, response in details['responses'].items():
                            content += f"- **{status_code}**: {response.get('description', '')}\n"
                        content += "\n"
                    
                    content += "---\n\n"
        
        return content
    
    def _generate_models_section(self) -> str:
        """Generate data models section from OpenAPI spec"""
        if not self.spec or 'components' not in self.spec or 'schemas' not in self.spec['components']:
            return "## Data Models\n\nNo data models defined in OpenAPI specification.\n"
        
        content = "## Data Models\n\n"
        
        for model_name, model_schema in self.spec['components']['schemas'].items():
            content += f"### {model_name} Object\n\n"
            content += "```yaml\n"
            content += f"{model_name}:\n"
            
            if 'type' in model_schema:
                content += f"  type: {model_schema['type']}\n"
            
            if 'properties' in model_schema:
                content += "  properties:\n"
                for prop_name, prop_schema in model_schema['properties'].items():
                    content += f"    {prop_name}:\n"
                    if 'type' in prop_schema:
                        content += f"      type: {prop_schema['type']}\n"
                    if 'format' in prop_schema:
                        content += f"      format: {prop_schema['format']}\n"
                    if 'description' in prop_schema:
                        content += f"      description: {prop_schema['description']}\n"
                    if 'enum' in prop_schema:
                        content += f"      enum: {prop_schema['enum']}\n"
            
            content += "```\n\n"
        
        return content
    
    def generate_validation_report(self) -> str:
        """Generate validation report"""
        report = "# Traffic API Documentation Validation Report\n\n"
        report += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        
        report += "## Summary\n\n"
        report += f"- Errors: {len(self.errors)}\n"
        report += f"- Warnings: {len(self.warnings)}\n"
        report += f"- OpenAPI File: {self.openapi_path}\n\n"
        
        if self.errors:
            report += "## Errors\n\n"
            for error in self.errors:
                report += f"- ❌ {error}\n"
            report += "\n"
        
        if self.warnings:
            report += "## Warnings\n\n"
            for warning in self.warnings:
                report += f"- ⚠️ {warning}\n"
            report += "\n"
        
        if not self.errors and not self.warnings:
            report += "✅ All validations passed successfully!\n\n"
        
        return report
    
    def save_validation_report(self, report: str):
        """Save validation report to file"""
        report_path = Path(self.output_dir) / 'validation-report.md'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Validation report generated: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='Traffic API Documentation Generator')
    parser.add_argument('--openapi', '-i', required=True, 
                       help='Path to OpenAPI specification file')
    parser.add_argument('--output', '-o', default='./docs/api/generated',
                       help='Output directory for generated documentation')
    parser.add_argument('--format', '-f', choices=['markdown', 'html', 'pdf', 'all'], 
                       default='all', help='Output format')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate OpenAPI spec without generating docs')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    generator = TrafficAPIDocsGenerator(args.openapi, args.output)
    
    # Load and validate OpenAPI spec
    if not generator.load_openapi_spec():
        print("❌ Failed to load OpenAPI specification")
        for error in generator.errors:
            print(f"  - {error}")
        sys.exit(1)
    
    if args.validate_only:
        report = generator.generate_validation_report()
        generator.save_validation_report(report)
        print("\nValidation completed.")
        sys.exit(0 if not generator.errors else 1)
    
    # Generate documentation based on format
    success = True
    
    if args.format in ['markdown', 'all']:
        if not generator.generate_markdown_docs():
            success = False
    
    if args.format in ['html', 'all']:
        if not generator.generate_html_docs():
            success = False
    
    if args.format in ['pdf', 'all']:
        if not generator.generate_pdf_docs():
            success = False
    
    # Generate validation report
    report = generator.generate_validation_report()
    generator.save_validation_report(report)
    
    if success:
        print("\n✅ Documentation generation completed successfully!")
        if generator.warnings:
            print("\nWarnings:")
            for warning in generator.warnings:
                print(f"  ⚠️ {warning}")
    else:
        print("\n❌ Documentation generation completed with errors:")
        for error in generator.errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()