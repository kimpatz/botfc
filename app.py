from flask import Flask, render_template, request, jsonify
from utils.profile_manager import get_chrome_profiles
from utils.post_publisher import publish_comments
import os
import logging

app = Flask(__name__)

# הגדרת לוגים
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    # טוען את רשימת הפרופילים הקיימים
    profiles = get_chrome_profiles()
    return render_template('index.html', profiles=profiles)

@app.route('/publish', methods=['POST'])
def publish():
    try:
        data = request.json
        logging.info(f"Received request data: {data}")
        post_url = data.get('post_url')
        profiles = data.get('profiles')

        if not post_url or not profiles:
            logging.warning("Missing post URL or profiles")
            return jsonify({'error': 'Missing post URL or profiles'}), 400

        results = publish_comments(post_url, profiles)
        logging.info("Publish results: %s", results)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        logging.error(f"Error publishing comments: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
