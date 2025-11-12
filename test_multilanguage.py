"""
Test script to verify multi-language setup
Run this to test all language features
"""

import os
import json
import sys
from pathlib import Path

def test_translations_exist():
    """Test that all translation files exist"""
    print("Testing translation files...")
    translations_dir = Path(__file__).parent / 'static' / 'translations'
    
    languages = ['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar']
    all_exist = True
    
    for lang in languages:
        file_path = translations_dir / f'{lang}.json'
        if file_path.exists():
            print(f"  ✅ {lang}.json exists")
            # Verify it's valid JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"     └─ Contains {len(data)} translations")
            except json.JSONDecodeError as e:
                print(f"  ❌ {lang}.json is not valid JSON: {e}")
                all_exist = False
        else:
            print(f"  ❌ {lang}.json does NOT exist")
            all_exist = False
    
    return all_exist


def test_config_files():
    """Test that config files exist"""
    print("\nTesting configuration files...")
    
    files_to_check = [
        'babel.cfg',
        'language_routes.py',
        'translation_manager.py',
    ]
    
    all_exist = True
    for filename in files_to_check:
        file_path = Path(__file__).parent / filename
        if file_path.exists():
            print(f"  ✅ {filename} exists")
        else:
            print(f"  ❌ {filename} does NOT exist")
            all_exist = False
    
    return all_exist


def test_template_files():
    """Test that template files exist"""
    print("\nTesting template files...")
    
    files_to_check = [
        'templates/components/language_switcher.html',
    ]
    
    all_exist = True
    for filename in files_to_check:
        file_path = Path(__file__).parent / filename
        if file_path.exists():
            print(f"  ✅ {filename} exists")
        else:
            print(f"  ❌ {filename} does NOT exist")
            all_exist = False
    
    return all_exist


def test_javascript_files():
    """Test that JavaScript files exist"""
    print("\nTesting JavaScript files...")
    
    files_to_check = [
        'static/js/i18n.js',
    ]
    
    all_exist = True
    for filename in files_to_check:
        file_path = Path(__file__).parent / filename
        if file_path.exists():
            print(f"  ✅ {filename} exists")
        else:
            print(f"  ❌ {filename} does NOT exist")
            all_exist = False
    
    return all_exist


def test_requirements():
    """Test that Flask-Babel is in requirements.txt"""
    print("\nTesting requirements.txt...")
    
    req_file = Path(__file__).parent / 'requirements.txt'
    if req_file.exists():
        with open(req_file, 'r') as f:
            content = f.read()
            if 'Flask-Babel' in content:
                print("  ✅ Flask-Babel is in requirements.txt")
                return True
            else:
                print("  ❌ Flask-Babel is NOT in requirements.txt")
                return False
    else:
        print("  ❌ requirements.txt does NOT exist")
        return False


def test_models():
    """Test that User model has language_preference field"""
    print("\nTesting models...")
    
    try:
        from models import User
        
        # Check if language_preference column exists in the model definition
        if hasattr(User, 'language_preference'):
            print("  ✅ User model has language_preference field")
            return True
        else:
            print("  ❌ User model does NOT have language_preference field")
            return False
    except Exception as e:
        print(f"  ❌ Error checking User model: {e}")
        return False


def test_app_init():
    """Test that app_init has Babel configured"""
    print("\nTesting app_init configuration...")
    
    try:
        with open(Path(__file__).parent / 'app_init.py', 'r') as f:
            content = f.read()
            
            checks = [
                ('Flask-Babel import', 'from flask_babel import Babel'),
                ('LANGUAGES config', "app.config['LANGUAGES']"),
                ('Babel initialization', 'babel = Babel(app)'),
                ('Locale selector', '@babel.localeselector'),
            ]
            
            all_good = True
            for check_name, check_string in checks:
                if check_string in content:
                    print(f"  ✅ {check_name} found")
                else:
                    print(f"  ❌ {check_name} NOT found")
                    all_good = False
            
            return all_good
    except Exception as e:
        print(f"  ❌ Error checking app_init: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Multi-Language Setup Verification")
    print("=" * 60)
    
    results = {
        'Translation Files': test_translations_exist(),
        'Configuration Files': test_config_files(),
        'Template Files': test_template_files(),
        'JavaScript Files': test_javascript_files(),
        'Requirements': test_requirements(),
        'Models': test_models(),
        'App Initialization': test_app_init(),
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Your multi-language setup is ready!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Update database: python3 -c \"from app_init import app, db; app.app_context().push(); db.create_all()\"")
        print("3. Start your app: python3 main.py")
        print("4. Open the app and click the globe icon 🌐 to test language switching")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
