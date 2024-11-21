
import os
import json
import logging
import platform

def get_chrome_profiles():
    """
    Dynamically fetches Chrome profiles and returns their names and folders.
    """
    # Determine the profiles path dynamically based on the OS
    system = platform.system()
    if system == 'Darwin':  # macOS
        profiles_path = os.path.expanduser('~/Library/Application Support/Google/Chrome')
    elif system == 'Windows':  # Windows
        profiles_path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
    elif system == 'Linux':  # Linux
        profiles_path = os.path.expanduser('~/.config/google-chrome')
    else:
        raise Exception(f"Unsupported platform: {system}")

    profiles = []

    if os.path.exists(profiles_path):
        for folder in os.listdir(profiles_path):
            # Skip common system folders
            if folder in ['System Profile', 'Crash Reports', 'Default', 'Guest Profile']:
                continue

            preferences_path = os.path.join(profiles_path, folder, 'Preferences')
            if os.path.exists(preferences_path):
                try:
                    with open(preferences_path, 'r', encoding='utf-8') as f:
                        preferences = json.load(f)
                        profile_name = preferences.get('profile', {}).get('name', folder)
                        profiles.append({'name': profile_name, 'folder': folder})
                except Exception as e:
                    logging.warning(f"Error reading profile {folder}: {e}")
    else:
        logging.warning(f"Profiles path does not exist: {profiles_path}")

    return profiles
