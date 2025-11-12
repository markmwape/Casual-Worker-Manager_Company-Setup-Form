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
        language = data.get('language', 'en').lower()
        
        # Validate language code
        valid_languages = ['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']
        if language not in valid_languages:
            return jsonify({"error": "Invalid language code"}), 400
        
        # Update user's language preference if logged in
        if 'user' in session and 'user_email' in session['user']:
            try:
                user = User.query.filter_by(email=session['user']['user_email']).first()
                if user:
                    user.language_preference = language
                    db.session.commit()
                    logging.info(f"Changed language for user {user.email} to {language}")
            except Exception as e:
                logging.warning(f"Could not update user language preference: {e}")
                db.session.rollback()
        
        # Store in session for immediate effect
        session['language'] = language
        
        return jsonify({"success": True, "language": language})
    except Exception as e:
        logging.error(f"Error changing language: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
        
        # First try to get from session (most recent preference)
        if 'language' in session:
            current_language = session['language']
            logging.info(f"Using language from session: {current_language}")
        # Then try user database preference
        elif 'user' in session and 'user_email' in session['user']:
            try:
                user = User.query.filter_by(email=session['user']['user_email']).first()
                if user and user.language_preference:
                    current_language = user.language_preference
                    logging.info(f"Using language from user preference: {current_language}")
            except Exception as e:
                logging.warning(f"Could not get user language preference: {e}")
        
        logging.info(f"Returning current language: {current_language}")
        return jsonify({
            "languages": languages,
            "current_language": current_language
        })
    except Exception as e:
        logging.error(f"Error getting languages: {str(e)}")
        return jsonify({
            "languages": {
                'en': 'English',
                'fr': 'Français',
                'es': 'Español'
            },
            "current_language": "en",
            "error": str(e)
        }), 200  # Return 200 with fallback data
