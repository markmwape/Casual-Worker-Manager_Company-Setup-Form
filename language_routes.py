"""
Language switching routes for multi-language support
"""
from flask import session, request, jsonify
from app_init import app, db
from models import User
import logging

@app.route('/api/change-language', methods=['POST'])
def change_language():
    """Change user's language preference"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        language = data.get('language', '').lower().strip()
        
        # Validate language code
        valid_languages = ['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']
        if not language or language not in valid_languages:
            return jsonify({"error": "Invalid language code", "received": language}), 400
        
        # Store in session for immediate effect (highest priority)
        session['language'] = language
        session.modified = True  # Ensure session is saved
        logging.info(f"Language changed to {language} in session")
        
        # Update user's language preference in database if logged in
        if 'user' in session and 'user_email' in session['user']:
            try:
                user = User.query.filter_by(email=session['user']['user_email']).first()
                if user:
                    user.language_preference = language
                    db.session.commit()
                    logging.info(f"Updated database: language for user {user.email} set to {language}")
            except Exception as e:
                logging.warning(f"Could not update user language preference in database: {e}")
                db.session.rollback()
                # Continue anyway - session change is enough
        
        return jsonify({
            "success": True, 
            "language": language,
            "message": f"Language changed to {language}"
        }), 200
        
    except Exception as e:
        logging.error(f"Error changing language: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/languages')
def get_languages():
    """Get list of available languages"""
    try:
        from app_init import app
        languages = app.config.get('LANGUAGES', {
            'en': 'English',
            'fr': 'Français',
            'sw': 'Swahili',
            'pt': 'Português',
            'es': 'Español',
            'tr': 'Türkçe',
            'hi': 'हिंदी',
            'zh': '中文',
            'ar': 'العربية',
            'vi': 'Tiếng Việt'
        })
        
        # Get current user's language preference with fallback chain
        current_language = 'en'
        
        # Priority 1: Check session language (most recent preference)
        if 'language' in session:
            current_language = session['language']
            logging.info(f"Using language from session: {current_language}")
        # Priority 2: Check user database preference
        elif 'user' in session and 'user_email' in session['user']:
            try:
                user = User.query.filter_by(email=session['user']['user_email']).first()
                if user and user.language_preference:
                    current_language = user.language_preference
                    # Sync to session
                    session['language'] = current_language
                    logging.info(f"Using language from user preference: {current_language}")
            except Exception as e:
                logging.warning(f"Could not get user language preference: {e}")
        # Priority 3: Use browser language
        else:
            browser_lang = request.accept_languages.best_match(languages.keys())
            if browser_lang:
                current_language = browser_lang
                logging.info(f"Using browser language: {current_language}")
        
        logging.info(f"API returning current language: {current_language}")
        return jsonify({
            "languages": languages,
            "current_language": current_language,
            "success": True
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting languages: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        # Return fallback data with 200 status so UI still works
        return jsonify({
            "languages": {
                'en': 'English',
                'fr': 'Français',
                'es': 'Español',
                'pt': 'Português',
                'sw': 'Swahili'
            },
            "current_language": "en",
            "error": str(e),
            "success": False
        }), 200

@app.route('/api/language/set', methods=['POST'])
def set_language():
    """Set the user's language preference (alternative endpoint)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        language = data.get('language', '').lower().strip()
        
        # Validate language code
        valid_languages = ['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']
        if not language or language not in valid_languages:
            return jsonify({
                "success": False,
                "error": "Invalid language code", 
                "received": language
            }), 400
        
        # Store in session for immediate effect
        session['language'] = language
        session.modified = True  # Ensure session is saved
        logging.info(f"Language set to {language} via /api/language/set")
        
        # Update user's language preference in database if logged in
        if 'user' in session and 'user_email' in session['user']:
            try:
                user = User.query.filter_by(email=session['user']['user_email']).first()
                if user:
                    user.language_preference = language
                    db.session.commit()
                    logging.info(f"Updated database: language for user {user.email} set to {language}")
            except Exception as e:
                logging.warning(f"Could not update user language preference in database: {e}")
                db.session.rollback()
        
        return jsonify({
            "success": True, 
            "language": language,
            "message": f"Language set to {language}"
        }), 200
        
    except Exception as e:
        logging.error(f"Error setting language: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/language/current', methods=['GET'])  
def get_current_language():
    """Get the user's current language"""
    try:
        # Get current user's language preference with fallback chain
        current_language = 'en'
        
        # Priority 1: Check session language
        if 'language' in session:
            current_language = session['language']
            logging.info(f"Using language from session: {current_language}")
        # Priority 2: Check user database preference
        elif 'user' in session and 'user_email' in session['user']:
            try:
                user = User.query.filter_by(email=session['user']['user_email']).first()
                if user and user.language_preference:
                    current_language = user.language_preference
                    # Sync to session
                    session['language'] = current_language
                    logging.info(f"Using language from user preference: {current_language}")
            except Exception as e:
                logging.warning(f"Could not get user language preference: {e}")
        
        language_names = {
            'en': 'English',
            'fr': 'Français', 
            'sw': 'Swahili',
            'pt': 'Português',
            'es': 'Español',
            'tr': 'Türkçe',
            'hi': 'हिंदी',
            'zh': '中文',
            'ar': 'العربية',
            'vi': 'Tiếng Việt'
        }
        
        return jsonify({
            'language': current_language,
            'display_name': language_names.get(current_language, 'English'),
            'supported_languages': language_names
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting current language: {str(e)}")
        return jsonify({
            'language': 'en',
            'display_name': 'English',
            'error': str(e)
        }), 500
