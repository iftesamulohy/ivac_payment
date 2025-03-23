from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Dictionary to store active browser sessions
browser_sessions = {}

def login_to_ivac(mobile_no, password, session_id):
    """Login to IVAC and store the browser session"""
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser_sessions[session_id] = {"driver": driver}

    try:
        driver.get("https://payment.ivacbd.com/")
        wait = WebDriverWait(driver, 10)

        # Close the modal popup if exists
        try:
            modal = wait.until(EC.visibility_of_element_located((By.ID, "instructModal")))
            close_button = wait.until(EC.element_to_be_clickable((By.ID, "emergencyNoticeCloseBtn")))
            driver.execute_script("arguments[0].click();", close_button)
        except Exception as e:
            print("No modal popup found:", e)

        # Enter mobile number and password
        mobile_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile_no")))
        mobile_input.send_keys(mobile_no)
        mobile_input.send_keys(Keys.RETURN)

        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        # Wait for OTP form to appear
        otp_input = wait.until(EC.presence_of_element_located((By.NAME, "otp")))

        return True  # Successfully logged in, OTP can be submitted
    except Exception as e:
        print("Error during login:", e)
        return False

def submit_otp(otp, session_id):
    """Submit OTP using an active browser session and return session cookies."""
    if session_id in browser_sessions:
        driver = browser_sessions[session_id]["driver"]
        wait = WebDriverWait(driver, 10)

        try:
            otp_input = wait.until(EC.presence_of_element_located((By.NAME, "otp")))
            otp_input.send_keys(otp)
            otp_input.send_keys(Keys.RETURN)

            # Wait for redirection after OTP submission
            time.sleep(5)

            # Capture cookies after OTP submission
            cookies = driver.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            print(cookie_dict)
            return True, cookie_dict  # Return both success status and cookies
        except Exception as e:
            print("Error during OTP submission:", e)
            return False, {}
    
    return False, {}
