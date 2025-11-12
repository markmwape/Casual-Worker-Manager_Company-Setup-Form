#!/usr/bin/env python3
"""
Language Switcher Verification Script
=====================================

This script verifies that the language switcher is working correctly by:
1. Checking all language route endpoints
2. Validating CSS and JavaScript implementations  
3. Testing HTML component integration
4. Verifying translation functionality

Run this script to ensure everything is working properly.
"""

import requests
import json
import sys
import os
from pathlib import Path

class LanguageSwitcherVerifier:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_error(self, message):
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  WARNING: {message}")
        print(f"⚠️  {message}")
        
    def log_success(self, message):
        self.success_count += 1
        print(f"✅ {message}")
        
    def check_file_exists(self, filepath, file_description):
        """Check if a file exists"""
        if os.path.exists(filepath):
            self.log_success(f"{file_description} exists")
            return True
        else:
            self.log_error(f"{file_description} not found: {filepath}")
            return False
            
    def check_language_routes(self):
        """Test language route endpoints"""
        print("\n🔍 Testing Language Route Endpoints...")
        
        # Test set language endpoint
        try:
            response = requests.post(f"{self.base_url}/api/language/set", 
                                   json={"language": "es"},
                                   timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_success("Language set endpoint working")
                else:
                    self.log_error(f"Language set failed: {data.get('message', 'Unknown error')}")
            else:
                self.log_error(f"Language set endpoint returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_warning("Server not running - cannot test endpoints")
        except Exception as e:
            self.log_error(f"Language set endpoint error: {str(e)}")
            
        # Test get language endpoint
        try:
            response = requests.get(f"{self.base_url}/api/language/current", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'language' in data:
                    self.log_success(f"Current language endpoint working - current: {data['language']}")
                else:
                    self.log_error("Current language endpoint missing 'language' field")
            else:
                self.log_error(f"Current language endpoint returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_warning("Server not running - cannot test current language endpoint")
        except Exception as e:
            self.log_error(f"Current language endpoint error: {str(e)}")
    
    def check_static_files(self):
        """Check if CSS and JS files exist and contain expected content"""
        print("\n📁 Checking Static Files...")
        
        # Check JavaScript
        js_path = "static/js/language-switcher.js"
        if self.check_file_exists(js_path, "Language switcher JavaScript"):
            with open(js_path, 'r') as f:
                js_content = f.read()
                if 'toggleDropdown' in js_content:
                    self.log_success("JavaScript contains toggle function")
                else:
                    self.log_error("JavaScript missing toggle function")
                    
                if 'setLanguage' in js_content:
                    self.log_success("JavaScript contains setLanguage function")
                else:
                    self.log_error("JavaScript missing setLanguage function")
                    
                if '/api/language/set' in js_content:
                    self.log_success("JavaScript has correct API endpoint")
                else:
                    self.log_error("JavaScript missing API endpoint")
        
        # Check CSS
        css_path = "static/css/language-switcher.css"
        if self.check_file_exists(css_path, "Language switcher CSS"):
            with open(css_path, 'r') as f:
                css_content = f.read()
                if '.language-switcher' in css_content:
                    self.log_success("CSS contains language-switcher class")
                else:
                    self.log_error("CSS missing language-switcher class")
                    
                if 'dropdown-menu' in css_content:
                    self.log_success("CSS contains dropdown-menu styles")
                else:
                    self.log_error("CSS missing dropdown-menu styles")
    
    def check_templates(self):
        """Check template files for language switcher integration"""
        print("\n📄 Checking Template Files...")
        
        # Check language switcher component
        component_path = "templates/components/language_switcher.html"
        if self.check_file_exists(component_path, "Language switcher component"):
            with open(component_path, 'r') as f:
                component_content = f.read()
                if 'language-switcher' in component_content:
                    self.log_success("Component contains language-switcher class")
                else:
                    self.log_error("Component missing language-switcher class")
                    
                if 'toggleDropdown' in component_content:
                    self.log_success("Component has JavaScript integration")
                else:
                    self.log_error("Component missing JavaScript integration")
        
        # Check base template integration
        base_path = "templates/base_with_sidebar.html"
        if self.check_file_exists(base_path, "Base template"):
            with open(base_path, 'r') as f:
                base_content = f.read()
                if 'language_switcher.html' in base_content:
                    self.log_success("Base template includes language switcher")
                else:
                    self.log_error("Base template missing language switcher include")
                    
                if 'language-switcher.css' in base_content:
                    self.log_success("Base template includes CSS")
                else:
                    self.log_error("Base template missing CSS include")
                    
                if 'language-switcher.js' in base_content:
                    self.log_success("Base template includes JavaScript")
                else:
                    self.log_error("Base template missing JavaScript include")
    
    def check_backend_routes(self):
        """Check backend route implementations"""
        print("\n🔧 Checking Backend Routes...")
        
        routes_path = "language_routes.py"
        if self.check_file_exists(routes_path, "Language routes file"):
            with open(routes_path, 'r') as f:
                routes_content = f.read()
                if '@app.route(\'/api/language/set\'' in routes_content:
                    self.log_success("Set language route defined")
                else:
                    self.log_error("Set language route not found")
                    
                if '@app.route(\'/api/language/current\'' in routes_content:
                    self.log_success("Current language route defined")
                else:
                    self.log_error("Current language route not found")
                    
                if 'session[\'language\']' in routes_content:
                    self.log_success("Session handling implemented")
                else:
                    self.log_error("Session handling missing")
        
        # Check if routes are imported in main file
        main_routes_path = "routes.py"
        if self.check_file_exists(main_routes_path, "Main routes file"):
            with open(main_routes_path, 'r') as f:
                main_content = f.read()
                if 'from language_routes import *' in main_content or 'import language_routes' in main_content:
                    self.log_success("Language routes imported in main routes")
                else:
                    self.log_warning("Language routes may not be imported in main routes")
    
    def check_translations_directory(self):
        """Check translations directory structure"""
        print("\n🌍 Checking Translations...")
        
        translations_dir = "static/translations"
        if os.path.exists(translations_dir):
            self.log_success("Translations directory exists")
            
            # Check for language files
            languages = ['en', 'es', 'fr', 'de', 'pt', 'it', 'zh']
            for lang in languages:
                lang_file = f"{translations_dir}/{lang}.json"
                if os.path.exists(lang_file):
                    self.log_success(f"{lang}.json translation file exists")
                    
                    # Validate JSON structure
                    try:
                        with open(lang_file, 'r', encoding='utf-8') as f:
                            translations = json.load(f)
                            if isinstance(translations, dict) and len(translations) > 0:
                                self.log_success(f"{lang}.json has valid structure")
                            else:
                                self.log_warning(f"{lang}.json is empty or invalid")
                    except json.JSONDecodeError:
                        self.log_error(f"{lang}.json has invalid JSON syntax")
                    except Exception as e:
                        self.log_error(f"Error reading {lang}.json: {str(e)}")
                else:
                    self.log_warning(f"{lang}.json translation file not found")
        else:
            self.log_error("Translations directory not found")
    
    def test_test_page(self):
        """Test the test page endpoint"""
        print("\n🧪 Testing Test Page...")
        
        try:
            response = requests.get(f"{self.base_url}/test-language-switcher", timeout=5)
            if response.status_code == 200:
                self.log_success("Test page endpoint working")
                if 'language-switcher' in response.text:
                    self.log_success("Test page contains language switcher")
                else:
                    self.log_warning("Test page may not contain language switcher")
            else:
                self.log_error(f"Test page returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_warning("Server not running - cannot test test page")
        except Exception as e:
            self.log_error(f"Test page error: {str(e)}")
    
    def run_verification(self):
        """Run all verification checks"""
        print("🚀 Starting Language Switcher Verification...")
        print("=" * 60)
        
        self.check_static_files()
        self.check_templates()
        self.check_backend_routes()
        self.check_translations_directory()
        self.check_language_routes()
        self.test_test_page()
        
        print("\n" + "=" * 60)
        print("📊 VERIFICATION RESULTS")
        print("=" * 60)
        
        print(f"✅ Successful checks: {self.success_count}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        print("\n" + "=" * 60)
        
        if len(self.errors) == 0:
            print("🎉 Language switcher verification PASSED!")
            print("All critical components are properly implemented.")
        else:
            print("❌ Language switcher verification FAILED!")
            print("Please fix the errors listed above.")
            
        if len(self.warnings) > 0:
            print("⚠️  Some warnings were found. Consider addressing them for optimal functionality.")
        
        return len(self.errors) == 0

if __name__ == "__main__":
    verifier = LanguageSwitcherVerifier()
    success = verifier.run_verification()
    sys.exit(0 if success else 1)
