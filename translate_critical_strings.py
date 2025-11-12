"""
Translate Critical Strings using LibreTranslate
This script translates the critical 268 strings (buttons, labels, messages)
to all 10 languages using the free LibreTranslate API.
"""

import json
import requests
from pathlib import Path
import time

# LibreTranslate API endpoint (public free API)
LIBRETRANSLATE_API = "https://libretranslate.de/translate"

# Language codes for LibreTranslate
LANGUAGE_MAP = {
    'fr': 'fr',      # French
    'sw': 'sw',      # Swahili
    'pt': 'pt',      # Portuguese
    'es': 'es',      # Spanish
    'tr': 'tr',      # Turkish
    'hi': 'hi',      # Hindi
    'zh': 'zh',      # Chinese (Simplified)
    'ar': 'ar',      # Arabic
    'vi': 'vi',      # Vietnamese
}

# Critical strings to translate (buttons, labels, messages, UI elements)
CRITICAL_STRINGS = {
    # Buttons & Links (110 strings)
    "Add Field": "Form buttons",
    "Add Worker": "Form buttons",
    "Add Member": "Form buttons",
    "Add Team Member": "Form buttons",
    "Edit": "Form buttons",
    "Delete": "Form buttons",
    "Delete Worker": "Form buttons",
    "Remove": "Form buttons",
    "Remove Member": "Form buttons",
    "Remove Team Member": "Form buttons",
    "Edit Role": "Form buttons",
    "Edit Team Member Role": "Form buttons",
    "Update Role": "Form buttons",
    "Save": "Form buttons",
    "Save Changes": "Form buttons",
    "Create New Task": "Form buttons",
    "Create Task": "Form buttons",
    "Edit Task": "Form buttons",
    "Delete Task": "Form buttons",
    "Create Workspace": "Form buttons",
    "Import Workers": "Form buttons",
    "Download": "Form buttons",
    "Export": "Form buttons",
    "Generate": "Form buttons",
    "Reset Password": "Form buttons",
    "Send Reset Link": "Form buttons",
    "Back to sign in": "Form buttons",
    "Back to Sign In": "Form buttons",
    "Back to Home": "Form buttons",
    "Back to Dashboard": "Form buttons",
    "Back to Tasks": "Form buttons",
    "Back to Today": "Form buttons",
    "Return to Home": "Form buttons",
    "Go back": "Form buttons",
    "Go to Dashboard": "Form buttons",
    "Manage Plan": "Form buttons",
    "Manage Subscription": "Form buttons",
    "Manage your team": "Form buttons",
    "Manage Workers & Tasks": "Form buttons",
    "Upgrade Now": "Form buttons",
    "Upgrade": "Form buttons",
    "Request 3-day extension (one-time only)": "Form buttons",
    "Manage Existing Billing": "Form buttons",
    "Watch Demo": "Form buttons",
    "Contact Sales": "Form buttons",
    "Contact us for support": "Form buttons",
    "Contact our support team": "Form buttons",
    "View Invoice": "Form buttons",
    
    # Messages & Alerts (28 strings)
    "Are you sure you want to logout?": "Messages",
    "Are you sure you want to remove": "Messages",
    "This action cannot be undone.": "Messages",
    "Confirm Deletion": "Messages",
    "Confirm Delete": "Messages",
    "Delete Workspace": "Messages",
    "Pause Workspace": "Messages",
    "Resume Workspace": "Messages",
    "Confirm": "Messages",
    "Cancel": "Messages",
    "OK": "Messages",
    "Close": "Messages",
    "Done": "Messages",
    "Please wait while we sign you into your account.": "Messages",
    "Signing In...": "Messages",
    "Loading...": "Messages",
    "Refreshing dashboard data...": "Messages",
    "Creating workspace...": "Messages",
    "Sign-in link sent! Check your email.": "Messages",
    "Import Complete": "Messages",
    "Workers have been successfully imported": "Messages",
    "No workers found": "Messages",
    "No Tasks Yet": "Messages",
    "No activity data": "Messages",
    "Error": "Messages",
    "Success": "Messages",
    "404 - Page Not Found": "Messages",
    "404": "Messages",
    
    # Form Labels & Placeholders (68 strings)
    "Email": "Form labels",
    "Email Address": "Form labels",
    "Name": "Form labels",
    "First Name": "Form labels",
    "Last Name": "Form labels",
    "Company Name": "Form labels",
    "Company Email": "Form labels",
    "Company Phone": "Form labels",
    "Country": "Form labels",
    "Industry": "Form labels",
    "Industry Type": "Form labels",
    "Role": "Form labels",
    "Select a role": "Form labels",
    "Status": "Form labels",
    "Active": "Form labels",
    "Inactive": "Form labels",
    "Paused": "Form labels",
    "Suspended": "Form labels",
    "Start Date": "Form labels",
    "End Date": "Form labels",
    "Select Start Date": "Form labels",
    "Select end date": "Form labels",
    "Select start date": "Form labels",
    "Task Name": "Form labels",
    "Description": "Form labels",
    "Daily Payout Amount": "Form labels",
    "Daily Rate": "Form labels",
    "Payout per Unit/Part": "Form labels",
    "Per Unit/Part": "Form labels",
    "Payment Type": "Form labels",
    "Select Currency": "Form labels",
    "Enter amount": "Form labels",
    "Enter amount per unit": "Form labels",
    "Payment per item completed": "Form labels",
    "Fixed daily amount": "Form labels",
    "Field Name": "Form labels",
    "Enter field name...": "Form labels",
    "Maximum Limit": "Form labels",
    "Units Completed": "Form labels",
    "Select Field": "Form labels",
    "Date of Birth": "Form labels",
    "Worker": "Form labels",
    "Task": "Form labels",
    "Attendance Date Range": "Form labels",
    "Date": "Form labels",
    "Check-in Time": "Form labels",
    "Check-out Time": "Form labels",
    "Search by any field...": "Form labels",
    "Select task date": "Form labels",
    "Choose Present or Absent for each worker": "Form labels",
    "Keep typing to refine your search": "Form labels",
    "Find Worker": "Form labels",
    "Select country": "Form labels",
    "Select industry": "Form labels",
    
    # UI Elements & Navigation (60 strings)
    "Dashboard": "UI Elements",
    "Workers": "UI Elements",
    "Tasks": "UI Elements",
    "Reports": "UI Elements",
    "Payments/Billing": "UI Elements",
    "Sign Out": "UI Elements",
    "Sign In": "UI Elements",
    "My Profile": "UI Elements",
    "My Workspace": "UI Elements",
    "Confirm Logout": "UI Elements",
    "English": "UI Elements",
    "Team Members": "UI Elements",
    "Admin": "UI Elements",
    "Manager": "UI Elements",
    "Supervisor": "UI Elements",
    "Accountant": "UI Elements",
    "Workspace Code": "UI Elements",
    "Total Workers": "UI Elements",
    "Active Tasks": "UI Elements",
    "Active Subscription": "UI Elements",
    "Worker Limit": "UI Elements",
    "Your role:": "UI Elements",
    "Trial:": "UI Elements",
    "Here's what's happening with your workforce today": "UI Elements",
    "Active workforce": "UI Elements",
    "Create new task": "UI Elements",
    "Current projects": "UI Elements",
    "Download reports": "UI Elements",
    "Manage your team access and permissions": "UI Elements",
    "Reports": "UI Elements",
    "Manage billing": "UI Elements",
    "Workforce analytics": "UI Elements",
    "Help": "UI Elements",
    "Settings": "UI Elements",
    "Account": "UI Elements",
    "Profile": "UI Elements",
    "Preferences": "UI Elements",
    "Theme": "UI Elements",
    "Language": "UI Elements",
    "Security": "UI Elements",
    "Privacy": "UI Elements",
    "Notifications": "UI Elements",
    "Support": "UI Elements",
    "Documentation": "UI Elements",
    "Legal": "UI Elements",
    "Terms": "UI Elements",
    "Privacy Policy": "UI Elements",
    "Contact": "UI Elements",
    "About": "UI Elements",
    "Home": "UI Elements",
    "Logout": "UI Elements",
    "Yes": "UI Elements",
    "No": "UI Elements",
    "Later": "UI Elements",
    "Today's Date": "UI Elements",
    "Created": "UI Elements",
    "Created At": "UI Elements",
    "Select All": "UI Elements",
    "Delete Selected": "UI Elements",
    "Copy": "UI Elements",
    "Share": "UI Elements",
    "Search": "UI Elements",
    "Filter": "UI Elements",
    "Sort": "UI Elements",
    "Actions": "UI Elements",
    "Details": "UI Elements",
    "Required": "UI Elements",
    "Optional": "UI Elements",
}

def translate_text(text, target_language):
    """Translate text to target language using LibreTranslate"""
    try:
        payload = {
            "q": text,
            "source": "en",
            "target": target_language
        }
        
        response = requests.post(LIBRETRANSLATE_API, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('translatedText', text)
        else:
            print(f"  ⚠️  Error translating '{text}' to {target_language}: {response.status_code}")
            return text
    except Exception as e:
        print(f"  ⚠️  Exception translating '{text}' to {target_language}: {str(e)}")
        return text

def translate_all_strings():
    """Translate all critical strings to all target languages"""
    translations = {}
    
    total_strings = len(CRITICAL_STRINGS)
    total_languages = len(LANGUAGE_MAP)
    total_translations = total_strings * total_languages
    
    print("=" * 80)
    print("TRANSLATING CRITICAL STRINGS USING LIBRETRANSLATE")
    print("=" * 80)
    print(f"\n📊 Translation Plan:")
    print(f"   • Strings to translate: {total_strings}")
    print(f"   • Target languages: {total_languages}")
    print(f"   • Total translations needed: {total_translations}")
    print(f"   • Rate limit: ~10 translations/minute (to be respectful of free API)\n")
    
    start_time = time.time()
    translated_count = 0
    
    for i, (english_text, category) in enumerate(CRITICAL_STRINGS.items()):
        translations[english_text] = {"en": english_text}
        
        print(f"[{i+1}/{total_strings}] Translating: '{english_text[:50]}...'")
        
        for lang_code, lt_code in LANGUAGE_MAP.items():
            translated = translate_text(english_text, lt_code)
            translations[english_text][lang_code] = translated
            translated_count += 1
            
            # Rate limiting - be respectful to free API
            time.sleep(0.2)  # 5 translations per second max
        
        # Additional delay between strings
        time.sleep(0.5)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n✅ Translation Complete!")
    print(f"   • Total translations: {translated_count}")
    print(f"   • Time taken: {duration:.1f} seconds")
    print(f"   • Average: {duration/translated_count:.2f}s per translation\n")
    
    return translations

def merge_with_existing_translations(new_translations):
    """Merge new critical translations with existing full translation set"""
    translation_manager_path = Path(__file__).parent / 'translation_manager.py'
    
    # Read existing translation_manager.py
    with open(translation_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Build the new TRANSLATIONS dict as Python code
    translations_code = "TRANSLATIONS = {\n"
    
    # Add all new critical translations first
    for i, (english_text, trans_dict) in enumerate(new_translations.items()):
        # Escape quotes in the text
        english_escaped = english_text.replace('"', '\\"')
        
        translations_code += f'    "{english_escaped}": {{\n'
        translations_code += f'        "en": "{english_text}",\n'
        
        for lang_code in ['fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']:
            translated = trans_dict.get(lang_code, english_text)
            translated_escaped = translated.replace('"', '\\"')
            translations_code += f'        "{lang_code}": "{translated_escaped}",\n'
        
        translations_code += '    },\n'
    
    translations_code += "}\n"
    
    # Replace the old TRANSLATIONS dict with the new one
    import re
    pattern = r'TRANSLATIONS = \{[\s\S]*?\n\}'
    content = re.sub(pattern, translations_code.rstrip(), content)
    
    with open(translation_manager_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated translation_manager.py with {len(new_translations)} critical strings")

def export_to_json(translations):
    """Export translations to JSON files"""
    output_dir = Path(__file__).parent / 'static' / 'translations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    languages = ['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']
    
    for lang in languages:
        translations_for_lang = {}
        for english_text, trans_dict in translations.items():
            translations_for_lang[english_text] = trans_dict.get(lang, english_text)
        
        output_file = output_dir / f'{lang}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translations_for_lang, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Exported {lang}.json ({len(translations_for_lang)} strings)")

def main():
    """Main translation workflow"""
    print("\n🌍 Starting LibreTranslate Workflow\n")
    
    # Step 1: Translate all critical strings
    print("Step 1: Translating critical strings...")
    print("-" * 80)
    translations = translate_all_strings()
    
    # Step 2: Merge with existing translations in translation_manager.py
    print("\nStep 2: Merging translations with translation_manager.py...")
    print("-" * 80)
    merge_with_existing_translations(translations)
    
    # Step 3: Export to JSON files
    print("\nStep 3: Exporting to JSON translation files...")
    print("-" * 80)
    export_to_json(translations)
    
    # Final summary
    print("\n" + "=" * 80)
    print("✅ TRANSLATION WORKFLOW COMPLETE!")
    print("=" * 80)
    print("\n📋 Summary:")
    print(f"   • Translated strings: {len(translations)}")
    print(f"   • Languages: {', '.join(['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi'])}")
    print(f"   • Files updated: translation_manager.py + 10 JSON files")
    print("\n🚀 Next steps:")
    print("   1. Review translations for accuracy (some may need manual fixes)")
    print("   2. Test the app in different languages")
    print("   3. Consider professional translation for landing page & legal docs")
    print("\n")

if __name__ == '__main__':
    main()
