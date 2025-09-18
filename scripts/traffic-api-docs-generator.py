#!/usr/bin/env python3
"""
Intelligent Traffic System API Documentation Generator

This script generates API documentation from OpenAPI specifications
for the Intelligent Traffic System. Supports multiple output formats
and includes validation and error reporting.
"""

import json
import yaml
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import markdown
import pdfkit

class TrafficAPIDocsGenerator:
    def __init__(self):
        self.template_path = "docs/api/templates/traffic-api-template.md"
        self.output_dir = "docs/api/generated"
        self.validation_errors = []
        
    def load_openapi_spec(self, spec_path: str) -> Dict:
        """Load OpenAPI specification from file"""
        try:
            with open(spec_path, 'r') as f:
                if spec_path.endswith('.json'):
                    return json.load(f)
                elif spec_path.endswith(('.yaml', '.yml')):
                    return yaml.safe_load(f)
                else:
                    raise ValueError("Unsupported file format. Use .json, .yaml, or .yml")
        except Exception as e:
            self.validation_errors.append(f"Failed to load OpenAPI spec: {e}")
            raise
    
    def validate_traffic_spec(self, spec: Dict) -> bool:
        """Validate traffic-specific API requirements"""
        is_valid = True
        
        # Check required traffic endpoints
        required_paths = [
            '/traffic/real-time',
            '/traffic/incidents', 
            '/control/signals/{signal_id}',
            '/routes/calculate'
        ]
        
        for path in required_paths:
            if path not in spec.get('paths', {}):
                self.validation_errors.append(f"Missing required traffic endpoint: {path}")
                is_valid = False
        
        # Check authentication scheme
        security_schemes = spec.get('components', {}).get('securitySchemes', {})
        if 'ApiKeyAuth' not in security_schemes:
            self.validation_errors.append("Missing API key authentication scheme")
            is_valid = False
        
        # Check traffic-specific data models
        required_models = ['TrafficFlow', 'TrafficIncident', 'TrafficSignal']
        schemas = spec.get('components', {}).get('schemas', {})
        
        for model in required_models:
            if model not in schemas:
                self.validation_errors.append(f"Missing required data model: {model}")
                is_valid = False
        
        return is_valid
    
    def generate_markdown_docs(self, spec: Dict, output_path: str) -> None:
        """Generate Markdown documentation from OpenAPI spec"""
        try:
            # Load template
            with open(self.template_path, 'r') as f:
                template = f.read()
            
            # Generate endpoints documentation
            endpoints_md = self._generate_endpoints_section(spec)
            data_models_md = self._generate_data_models_section(spec)
            
            # Replace template placeholders
            docs_content = template.replace('{{endpoints}}', endpoints_md)
            docs_content = docs_content.replace('{{data_models}}', data_models_md)
            docs_content = docs_content.replace('{{generation_date}}', datetime.now().isoformat())
            docs_content = docs_content.replace('{{spec_version}}', spec.get('info', {}).get('version', '1.0.0'))
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(docs_content)
                
            print(f"✓ Markdown documentation generated: {output_path}")
            
        except Exception as e:
            self.validation_errors.append(f"Failed to generate Markdown docs: {e}")
            raise
    
    def generate_html_docs(self, markdown_path: str, output_path: str) -> None:
        """Convert Markdown to HTML"""
        try:
            with open(markdown_path, 'r') as f:
                md_content = f.read()
            
            html_content = markdown.markdown(md_content, extensions=['extra', 'tables'])
            
            # Add HTML styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Intelligent Traffic System API Documentation</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; border-bottom: 2px solid #3498db; }}
                    code {{ background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }}
                    pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .endpoint {{ background: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            with open(output_path, 'w') as f:
                f.write(styled_html)
                
            print(f"✓ HTML documentation generated: {output_path}")
            
        except Exception as e:
            self.validation_errors.append(f"Failed to generate HTML docs: {e}")
            raise
    
    def generate_pdf_docs(self, html_path: str, output_path: str) -> None:
        """Convert HTML to PDF"""
        try:
            # Check if pdfkit is available
            try:
                import pdfkit
            except ImportError:
                self.validation_errors.append("PDF generation requires pdfkit. Install with: pip install pdfkit")
                return
            
            pdfkit.from_file(html_path, output_path)
            print(f"✓ PDF documentation generated: {output_path}")
            
        except Exception as e:
            self.validation_errors.append(f"Failed to generate PDF docs: {e}")
    
    def _generate_endpoints_section(self, spec: Dict) -> str:
        """Generate endpoints documentation section"""
        endpoints_md = ""
        paths = spec.get('paths', {})
        
        for path, methods in paths.items():
            if path.startswith('/traffic') or path.startswith('/control') or path.startswith('/routes'):
                endpoints_md += f"### {path}\n\n"
                
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        endpoints_md += f"#### {method.upper()} {path}\n\n"
                        endpoints_md += f"{details.get('summary', 'No description')}\n\n"
                        
                        # Parameters
                        if 'parameters' in details:
                            endpoints_md += "**Parameters**:\n\n"
                            endpoints_md += "| Name | Type | Required | Description |\n"
                            endpoints_md += "|------|------|----------|-------------|\n"
                            for param in details['parameters']:
                                endpoints_md += f"| {param.get('name', '')} | {param.get('schema', {}).get('type', '')} | {param.get('required', False)} | {param.get('description', '')} |\n"
                            endpoints_md += "\n"
                        
                        # Request body
                        if 'requestBody' in details:
                            endpoints_md += "**Request Body**:\n\n"
                            content = details['requestBody'].get('content', {})
                            for content_type, schema_info in content.items():
                                if 'schema' in schema_info:
                                    endpoints_md += f"```json\n{schema_info['schema']}\n```\n\n"
                        
                        # Responses
                        if 'responses' in details:
                            endpoints_md += "**Responses**:\n\n"
                            for status_code, response in details['responses'].items():
                                endpoints_md += f"- **{status_code}**: {response.get('description', '')}\n"
                                if 'content' in response:
                                    for content_type, schema_info in response['content'].items():
                                        if 'schema' in schema_info:
                                            endpoints_md += f"  ```json\n{schema_info['schema']}\n  ```\n"
                        
                        endpoints_md += "\n"
        
        return endpoints_md
    
    def _generate_data_models_section(self, spec: Dict) -> str:
        """Generate data models documentation section"""
        models_md = ""
        schemas = spec.get('components', {}).get('schemas', {})
        
        for model_name, schema in schemas.items():
            if model_name in ['TrafficFlow', 'TrafficIncident', 'TrafficSignal']:
                models_md += f"### {model_name} Object\n\n"
                models_md += f"```json\n{json.dumps(schema, indent=2)}\n```\n\n"
                
                if 'description' in schema:
                    models_md += f"{schema['description']}\n\n"
                
                models_md += "\n"
        
        return models_md
    
    def generate_validation_report(self, output_path: str) -> None:
        """Generate validation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "errors": self.validation_errors,
            "error_count": len(self.validation_errors),
            "status": "PASS" if not self.validation_errors else "FAIL"
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Validation report generated: {output_path}")
        
        if self.validation_errors:
            print(f"\n❌ Validation failed with {len(self.validation_errors)} errors:")
            for error in self.validation_errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("✓ All validations passed!")

def main():
    parser = argparse.ArgumentParser(description='Generate Intelligent Traffic System API Documentation')
    parser.add_argument('spec_file', help='Path to OpenAPI specification file (JSON/YAML)')
    parser.add_argument('--format', choices=['markdown', 'html', 'pdf', 'all'], 
                       default='all', help='Output format(s)')
    parser.add_argument('--output-dir', default='docs/api/generated', 
                       help='Output directory for generated docs')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate the spec without generating docs')
    
    args = parser.parse_args()
    
    generator = TrafficAPIDocsGenerator()
    
    try:
        # Load and validate OpenAPI spec
        spec = generator.load_openapi_spec(args.spec_file)
        
        if not generator.validate_traffic_spec(spec):
            print("❌ OpenAPI specification validation failed!")
            generator.generate_validation_report(os.path.join(args.output_dir, 'validation-report.json'))
            sys.exit(1)
        
        if args.validate_only:
            print("✓ OpenAPI specification validation passed!")
            generator.generate_validation_report(os.path.join(args.output_dir, 'validation-report.json'))
            sys.exit(0)
        
        # Generate documentation in requested formats
        base_name = os.path.splitext(os.path.basename(args.spec_file))[0]
        
        if args.format in ['markdown', 'all']:
            md_path = os.path.join(args.output_dir, f'{base_name}.md')
            generator.generate_markdown_docs(spec, md_path)
        
        if args.format in ['html', 'all']:
            html_path = os.path.join(args.output_dir, f'{base_name}.html')
            generator.generate_html_docs(md_path, html_path)
        
        if args.format in ['pdf', 'all']:
            pdf_path = os.path.join(args.output_dir, f'{base_name}.pdf')
            generator.generate_pdf_docs(html_path, pdf_path)
        
        # Generate final validation report
        generator.generate_validation_report(os.path.join(args.output_dir, 'validation-report.json'))
        
        print("\n🎉 API documentation generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        generator.generate_validation_report(os.path.join(args.output_dir, 'validation-report.json'))
        sys.exit(1)

if __name__ == "__main__":
    main()