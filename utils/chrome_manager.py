import undetected_chromedriver as uc
import os
import logging


def create_chrome_driver(profile_folder):
    profiles_path = '/Users/dorperetz/Library/Application Support/Google/Chrome'
    profile_path = os.path.join(profiles_path)

    options = uc.ChromeOptions()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument(f"--profile-directory={profile_folder}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--log-path=/Users/dorperetz/Desktop/bot/chromedriver.log")
    options.add_argument("--verbose")  # להגדיל את הוורבליות
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")  # רמת לוגים


    logging.info(f"Starting ChromeDriver with profile: {profile_folder}")
    try:
        driver = uc.Chrome(options=options)
        logging.info("ChromeDriver started successfully")
        return driver
    except Exception as e:
        logging.error(f"Failed to create ChromeDriver session: {e}")
        raise
