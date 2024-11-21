from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .chrome_manager import create_chrome_driver
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

LOGGER.setLevel(logging.DEBUG)  # הצג דיבאג מורחב של Selenium


def navigate_to_post(driver, post_url, max_retries=3):
    logging.info("Starting navigate_to_post function")
    retries = 0
    while retries < max_retries:
        try:
            logging.info(f"Navigating to {post_url}, attempt {retries + 1}")
            driver.get(post_url)

            # המתן לטעינת גוף העמוד
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logging.info("Page loaded successfully")
            time.sleep(5)  # המתנה נוספת כדי לוודא שכל האלמנטים נטענו
            current_url = driver.current_url
            logging.info(f"Current URL after navigation: {current_url}")

            # אם הכתובת הנוכחית לא תואמת, ננסה שוב
            if current_url != post_url:
                logging.warning(f"Navigation failed. Expected URL: {post_url}, but got: {current_url}. Retrying navigation.")
                retries += 1
                continue

            # בדיקה לטעינת אלמנטים ספציפיים מהפוסט
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@role, 'article')]"))
            )
            logging.info("Post element located successfully")

            # שימוש ב-JavaScript לוודא טעינת עמוד מלאה
            page_state = driver.execute_script('return document.readyState;')
            logging.info(f"Page state after navigation: {page_state}")
            if page_state != 'complete':
                raise Exception("Page did not reach 'complete' state")

            # בדיקת חלונות קופצים או בקשות אישור
            try:
                dismiss_button = driver.find_element(By.XPATH, "//button[contains(text(), 'לא תודה')]")
                dismiss_button.click()
                logging.info("Dismissed pop-up successfully.")
            except NoSuchElementException:
                logging.info("No pop-up found to dismiss.")

            return True
        except (TimeoutException, Exception) as e:
            logging.error(f"Attempt {retries + 1} failed: {e}")
            retries += 1
            time.sleep(5)  # המתנה בין ניסיונות

    logging.error(f"Failed to navigate to {post_url} after {max_retries} attempts.")
    return False


def publish_comments(post_url, profiles):
    logging.info("Starting publish_comments function")
    results = []
    for profile in profiles:
        profile_name = profile['profile']
        comment = profile.get('comment', '').strip()
        media_path = profile.get('media_path', '').strip()

        if not comment and not media_path:
            logging.info(f"Skipping profile {profile_name} - no comment or media provided.")
            results.append({'profile': profile_name, 'status': 'Skipped (empty comment and media)'})
            continue

        driver = None
        try:
            logging.info(f"Creating Chrome driver for profile: {profile_name}")
            try:
                driver = create_chrome_driver(profile_name)
                logging.info(f"Chrome driver created successfully for profile: {profile_name}")
            except WebDriverException as e:
                logging.error(f"Failed to create Chrome driver for profile {profile_name}: {e}")
                results.append({'profile': profile_name, 'status': f'Failed to create Chrome driver: {e}'})
                continue

            # ניווט לפוסט
            if not navigate_to_post(driver, post_url):
                raise Exception(f"Failed to navigate to {post_url}")

            # הוספת תגובה
            logging.info("Navigated to post successfully. Attempting to add comment.")
            try:
                # ניסיון לזהות את תיבת התגובה במספר דרכים
                try:
                    comment_box = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Write a comment')]/following-sibling::form//textarea"))
                    )
                    logging.info("Comment box located successfully using updated XPath.")
                except TimeoutException:
                    logging.warning("Failed to locate comment box using updated XPath. Trying alternative methods.")
                    try:
                        comment_box = WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label*='comment']"))
                        )
                        logging.info("Comment box located successfully using CSS_SELECTOR.")
                    except TimeoutException as e:
                        logging.error(f"Failed to locate comment box using all methods: {e}")
                        results.append({'profile': profile_name, 'status': 'Failed to locate comment box'})
                        driver.quit()
                        continue
                
                time.sleep(2)  # המתנה נוספת לפני הוספת תגובה
            except Exception as e:
                logging.error(f"Unexpected error while locating comment box: {e}")
                results.append({'profile': profile_name, 'status': 'Failed to locate comment box'})
                driver.quit()
                continue

            # ניסיון להוסיף את התגובה
            try:
                logging.info(f"Attempting to add comment for profile {profile_name}")
                comment_box.send_keys(comment)
                time.sleep(1)  # המתנה לפני השליחה
                comment_box.submit()
                logging.info(f"Comment published for profile {profile_name}.")
            except Exception as e:
                logging.warning(f"Failed to submit comment normally: {e}. Trying JavaScript.")
                driver.execute_script("arguments[0].value = arguments[1];", comment_box, comment)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", comment_box)
                try:
                    submit_button = driver.find_element(By.XPATH, "//button[contains(@type, 'submit')]")
                    submit_button.click()
                    logging.info(f"Comment published for profile {profile_name} using JavaScript.")
                except NoSuchElementException as e:
                    logging.error(f"Failed to locate submit button for profile {profile_name}: {e}")
                    results.append({'profile': profile_name, 'status': 'Failed to locate submit button'})
                    driver.quit()
                    continue

            results.append({'profile': profile_name, 'status': 'Comment published'})

        except Exception as e:
            logging.error(f"Failed to publish comment for profile {profile_name}: {e}")
            results.append({'profile': profile_name, 'status': f'Failed: {e}'})
        finally:
            if driver:
                logging.info(f"Quitting driver for profile {profile_name}")
                driver.quit()

    logging.info("Finished publishing comments")
    return results
