import undetected_chromedriver as uc

def test_chrome_navigation():
    options = uc.ChromeOptions()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    options.add_argument("--user-data-dir=/Users/dorperetz/Library/Application Support/Google/Chrome")
    options.add_argument("--profile-directory=Profile 53")

    driver = uc.Chrome(options=options)
    driver.get("https://www.facebook.com")
    print("Navigation successful. Current URL:", driver.current_url)
    driver.quit()

if __name__ == '__main__':
    test_chrome_navigation()
