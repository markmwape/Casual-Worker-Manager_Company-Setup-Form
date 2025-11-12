"""
Translation Audit Script
Scans all templates and identifies hardcoded English strings that should be translated
"""

import re
import os
from pathlib import Path
from collections import defaultdict

# Patterns to identify translatable content
PATTERNS = {
    'text_nodes': r'>([^<]+)<',  # Text between HTML tags
    'placeholders': r'placeholder="([^"]+)"',
    'titles': r'title="([^"]+)"',
    'alt_text': r'alt="([^"]+)"',
    'button_text': r'<button[^>]*>([^<]+)<',
    'label_text': r'<label[^>]*>([^<]+)<',
    'h1_text': r'<h1[^>]*>([^<]+)<',
    'h2_text': r'<h2[^>]*>([^<]+)<',
    'h3_text': r'<h3[^>]*>([^<]+)<',
    'span_text': r'<span[^>]*>([^<]+)<',
    'a_text': r'<a[^>]*>([^<]+)<',
    'p_text': r'<p[^>]*>([^<]+)<',
}

# Strings to ignore (technical, numbers, special characters, etc.)
IGNORE_PATTERNS = [
    r'^[\s]*$',  # Empty or whitespace
    r'^[\d\-/:.,]+$',  # Numbers and punctuation only
    r'^[{%{]',  # Jinja2 variables
    r'^\{\{',  # Template variables
    r'^\.\.\.existing',  # Comments
    r'^[a-z0-9]+@[a-z0-9]+',  # Email patterns
    r'url_for',  # Flask functions
    r'session\.',  # Session objects
    r'^[a-f0-9]{32,}$',  # Hex strings
    r'material-icons',  # Icon names
]

def should_ignore(text):
    """Check if text should be ignored"""
    text = text.strip()
    if not text:
        return True
    
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # Ignore very short strings (single characters, short IDs)
    if len(text) < 2:
        return True
    
    return False

def extract_strings_from_html(content):
    """Extract translatable strings from HTML content"""
    strings = set()
    
    # Remove comments
    content = re.sub(r'{#.*?#}', '', content, flags=re.DOTALL)
    
    # Extract from various HTML elements
    # Text between tags (but not Jinja2)
    matches = re.findall(r'>([^<{%}]+)<', content)
    for match in matches:
        text = match.strip()
        if not should_ignore(text) and not '{{' in text and not '{%' in text:
            strings.add(text)
    
    # Placeholders
    matches = re.findall(r'placeholder="([^"]+)"', content)
    for match in matches:
        if not should_ignore(match):
            strings.add(match)
    
    # Button and link text
    matches = re.findall(r'<(button|a|span|label|h[1-3])[^>]*>([^<{%}]+)<', content)
    for tag, text in matches:
        text = text.strip()
        if not should_ignore(text) and not '{{' in text:
            strings.add(text)
    
    # Title attributes
    matches = re.findall(r'(?:title|aria-label)="([^"]+)"', content)
    for match in matches:
        if not should_ignore(match):
            strings.add(match)
    
    return strings

def scan_templates():
    """Scan all template files for translatable strings"""
    templates_dir = Path('templates')
    results = defaultdict(set)
    
    print("=" * 80)
    print("TRANSLATION AUDIT - Scanning Templates")
    print("=" * 80)
    print()
    
    for template_file in templates_dir.rglob('*.html'):
        # Skip components that are just includes
        if 'components' in str(template_file) and template_file.name != 'language_switcher.html':
            continue
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {template_file}: {e}")
            continue
        
        # Extract strings
        strings = extract_strings_from_html(content)
        
        if strings:
            rel_path = str(template_file.relative_to('templates'))
            results[rel_path] = strings
    
    return results

def categorize_strings(results):
    """Categorize strings by priority"""
    categories = {
        'UI Elements': [],
        'Form Labels & Placeholders': [],
        'Messages & Alerts': [],
        'Table Headers & Data': [],
        'Buttons & Links': [],
        'Other': []
    }
    
    ui_keywords = ['dashboard', 'home', 'workers', 'tasks', 'reports', 'settings', 'profile', 'menu', 'sidebar']
    form_keywords = ['name', 'email', 'password', 'search', 'filter', 'enter', 'type here', 'select', 'choose']
    message_keywords = ['error', 'success', 'warning', 'confirm', 'delete', 'confirm', 'are you', 'please', 'invalid', 'required']
    table_keywords = ['name', 'date', 'status', 'action', 'id', 'email', 'phone', 'amount', 'total']
    button_keywords = ['save', 'submit', 'cancel', 'delete', 'edit', 'add', 'download', 'export', 'import', 'logout', 'login', 'sign']
    
    all_strings = set()
    for strings in results.values():
        all_strings.update(strings)
    
    for string in sorted(all_strings):
        lower = string.lower()
        
        if any(kw in lower for kw in button_keywords):
            categories['Buttons & Links'].append(string)
        elif any(kw in lower for kw in form_keywords):
            categories['Form Labels & Placeholders'].append(string)
        elif any(kw in lower for kw in message_keywords):
            categories['Messages & Alerts'].append(string)
        elif any(kw in lower for kw in table_keywords):
            categories['Table Headers & Data'].append(string)
        elif any(kw in lower for kw in ui_keywords):
            categories['UI Elements'].append(string)
        else:
            categories['Other'].append(string)
    
    return categories

def generate_report(results):
    """Generate a translation audit report"""
    print("\n" + "=" * 80)
    print("AUDIT RESULTS BY FILE")
    print("=" * 80)
    
    total_strings = 0
    total_files = len(results)
    
    for file_path in sorted(results.keys()):
        strings = results[file_path]
        total_strings += len(strings)
        print(f"\n📄 {file_path}")
        print(f"   Found {len(strings)} translatable string(s):")
        for string in sorted(strings):
            print(f"   • {string}")
    
    print("\n" + "=" * 80)
    print("SUMMARY BY CATEGORY")
    print("=" * 80)
    
    categories = categorize_strings(results)
    
    for category, strings in categories.items():
        if strings:
            print(f"\n🏷️  {category} ({len(strings)})")
            for string in sorted(set(strings))[:5]:  # Show first 5
                print(f"   • {string}")
            if len(strings) > 5:
                print(f"   ... and {len(strings) - 5} more")
    
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"\n✓ Templates scanned: {total_files}")
    print(f"✓ Unique translatable strings: {len(set(s for strings in results.values() for s in strings))}")
    print(f"✓ Total string occurrences: {total_strings}")
    
    all_strings = set(s for strings in results.values() for s in strings)
    
    print(f"\n📊 Breakdown by category:")
    for category, strings in categories.items():
        count = len(set(strings))
        if count > 0:
            percentage = (count / len(all_strings)) * 100
            print(f"   {category}: {count} ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print(f"""
✓ Total unique strings to translate: {len(all_strings)}

Priority Order:
1. Buttons & Links ({len(set(categories['Buttons & Links']))}) - High impact
2. Messages & Alerts ({len(set(categories['Messages & Alerts']))}) - Important for UX
3. Form Labels ({len(set(categories['Form Labels & Placeholders']))}) - Important for usability
4. UI Elements ({len(set(categories['UI Elements']))}) - Navigation
5. Table Headers ({len(set(categories['Table Headers & Data']))}) - Data display
6. Other ({len(set(categories['Other']))}) - Miscellaneous

Next Steps:
1. Add these strings to translation_manager.py
2. Run: python3 translation_manager.py
3. Test each page in different languages
4. Deploy to production

Current Translation Coverage:
Already translated: ~16 strings (Navigation, basic UI)
Needs translation: {len(all_strings)} strings
Coverage: {(16 / (16 + len(all_strings))) * 100:.1f}%
""")

def export_for_translation(results):
    """Export strings in a format easy to add to translation_manager.py"""
    all_strings = set(s for strings in results.values() for s in strings)
    
    print("\n" + "=" * 80)
    print("EXPORT FOR TRANSLATION_MANAGER.PY")
    print("=" * 80)
    print("""
Add these strings to the TRANSLATIONS dictionary in translation_manager.py:

""")
    
    for string in sorted(all_strings)[:10]:  # Show first 10 as example
        print(f'''    "{string}": {{
        "fr": "[French translation]",
        "sw": "[Swahili translation]",
        "pt": "[Portuguese translation]",
        "es": "[Spanish translation]",
        "tr": "[Turkish translation]",
        "hi": "[Hindi translation]",
        "zh": "[Chinese translation]",
        "ar": "[Arabic translation]"
    }},''')
    
    print(f"\n    # ... and {len(all_strings) - 10} more strings\n")

if __name__ == '__main__':
    results = scan_templates()
    
    if results:
        generate_report(results)
        export_for_translation(results)
    else:
        print("No translatable strings found or templates directory not found.")
        print(f"Looking in: {Path('templates').absolute()}")
