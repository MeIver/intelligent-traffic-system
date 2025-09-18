#!/usr/bin/env python3
"""
Test script for the Traffic API Documentation Generator

This script tests the basic functionality of the documentation generator
without requiring full OpenAPI specification validation.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the generator
sys.path.insert(0, os.path.dirname(__file__))

try:
    from traffic_api_docs_generator import TrafficAPIDocsGenerator
    
    def test_basic_functionality():
        """Test basic generator functionality"""
        print("🧪 Testing Traffic API Documentation Generator...")
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = TrafficAPIDocsGenerator()
            
            # Create a minimal test OpenAPI spec
            test_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "Test Traffic API",
                    "version": "1.0.0",
                    "description": "Test specification for traffic system"
                },
                "paths": {
                    "/traffic/real-time": {
                        "get": {
                            "summary": "Get real-time traffic data",
                            "responses": {
                                "200": {
                                    "description": "Successful response"
                                }
                            }
                        }
                    }
                },
                "components": {
                    "securitySchemes": {
                        "ApiKeyAuth": {
                            "type": "apiKey",
                            "in": "header",
                            "name": "Authorization"
                        }
                    },
                    "schemas": {
                        "TrafficFlow": {
                            "type": "object",
                            "properties": {
                                "vehicle_count": {"type": "integer"},
                                "average_speed": {"type": "number"}
                            }
                        }
                    }
                }
            }
            
            # Save test spec to temporary file
            spec_path = os.path.join(temp_dir, "test-spec.yaml")
            with open(spec_path, 'w') as f:
                import yaml
                yaml.dump(test_spec, f)
            
            print("✅ Test OpenAPI specification created")
            
            # Test validation
            spec = generator.load_openapi_spec(spec_path)
            is_valid = generator.validate_traffic_spec(spec)
            
            if is_valid:
                print("✅ OpenAPI specification validation passed")
            else:
                print("❌ OpenAPI specification validation failed")
                for error in generator.validation_errors:
                    print(f"   - {error}")
                return False
            
            # Test markdown generation
            output_path = os.path.join(temp_dir, "test-output.md")
            generator.generate_markdown_docs(spec, output_path)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Markdown documentation generated ({file_size} bytes)")
                
                # Verify content
                with open(output_path, 'r') as f:
                    content = f.read()
                    
                if "Traffic API Documentation" in content and "System Overview" in content:
                    print("✅ Documentation content verified")
                else:
                    print("❌ Documentation content missing expected sections")
                    return False
            else:
                print("❌ Markdown documentation not generated")
                return False
            
            # Test validation report
            report_path = os.path.join(temp_dir, "validation-report.json")
            generator.generate_validation_report(report_path)
            
            if os.path.exists(report_path):
                print("✅ Validation report generated")
                
                with open(report_path, 'r') as f:
                    report = json.load(f)
                    
                if report['status'] == 'PASS':
                    print("✅ Validation report indicates success")
                else:
                    print("❌ Validation report indicates failure")
                    return False
            else:
                print("❌ Validation report not generated")
                return False
            
            print("🎉 All tests passed!")
            return True
            
    if __name__ == "__main__":
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install pyyaml markdown")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)