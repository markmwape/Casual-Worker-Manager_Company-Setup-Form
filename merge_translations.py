#!/usr/bin/env python3
"""
Merge critical translations into translation_manager.py
This script combines hand-crafted quality translations with the existing system
"""

import json
from pathlib import Path
from critical_translations import CRITICAL_TRANSLATIONS

def merge_translations():
    """Merge critical translations into translation_manager.py"""
    
    translation_manager_path = Path(__file__).parent / 'translation_manager.py'
    
    print("\n" + "=" * 80)
    print("MERGING CRITICAL TRANSLATIONS")
    print("=" * 80 + "\n")
    
    # Build Python dict as code
    dict_code = "TRANSLATIONS = {\n"
    
    for english_text, trans_dict in CRITICAL_TRANSLATIONS.items():
        # Escape special characters
        english_escaped = english_text.replace('"', '\\"').replace('\n', '\\n')
        
        dict_code += f'    "{english_escaped}": {{\n'
        dict_code += f'        "en": "{english_escaped}",\n'
        
        for lang_code in ['fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']:
            translated = trans_dict.get(lang_code, english_text)
            translated_escaped = translated.replace('"', '\\"').replace('\n', '\\n')
            dict_code += f'        "{lang_code}": "{translated_escaped}",\n'
        
        dict_code += '    },\n'
    
    dict_code += "}\n\n"
    
    # Read the rest of translation_manager.py (after the TRANSLATIONS dict)
    with open(translation_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where TRANSLATIONS dict ends and replace it
    import re
    pattern = r'TRANSLATIONS = \{[\s\S]*?\n\}\n\n'
    match = re.search(pattern, content)
    
    if match:
        new_content = content[:match.start()] + dict_code + content[match.end():]
    else:
        # Fallback: try simpler pattern
        pattern = r'TRANSLATIONS = \{[\s\S]*?\n\}\n'
        new_content = re.sub(pattern, dict_code, content)
    
    # Write back
    with open(translation_manager_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated translation_manager.py")
    print(f"   Total strings: {len(CRITICAL_TRANSLATIONS)}\n")

def export_to_json():
    """Export translations to JSON files"""
    output_dir = Path(__file__).parent / 'static' / 'translations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    languages = ['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']
    
    print("Exporting to JSON files...")
    print("-" * 80)
    
    for lang in languages:
        translations_for_lang = {}
        for english_text, trans_dict in CRITICAL_TRANSLATIONS.items():
            if lang == 'en':
                translations_for_lang[english_text] = english_text
            else:
                translations_for_lang[english_text] = trans_dict.get(lang, english_text)
        
        output_file = output_dir / f'{lang}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translations_for_lang, f, ensure_ascii=False, indent=2)
        
        status = "✅" if lang != 'en' else "✅"
        print(f"{status} {lang.upper():6} → {output_file.name:10} ({len(translations_for_lang):3} strings)")
    
    print("\n" + "=" * 80)
    print("✅ TRANSLATION MERGE COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   • Critical strings translated: {len(CRITICAL_TRANSLATIONS)}")
    print(f"   • Languages: {', '.join(['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi'])}")
    print(f"   • JSON files generated: 10")
    print(f"\n🚀 Next steps:")
    print(f"   1. Test the app in different languages")
    print(f"   2. Verify translations on critical pages")
    print(f"   3. Consider additional translations for other 863 strings")
    print(f"   4. Deploy to production\n")

if __name__ == '__main__':
    merge_translations()
    export_to_json()
