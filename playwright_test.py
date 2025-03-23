from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options (remove headless if you want to see the browser)
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment if you want to run in headless mode

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the website to set the domain
driver.get("https://payment.ivacbd.com/")

# Add the session cookie
cookie = {
    "name": "ivac_session",
    "value": "eyJpdiI6IjFOQkUrd3hWNWl6cFI1dThqUjVRXC9RPT0iLCJ2YWx1ZSI6IkVPK1EzNDZOQXNIQndkNTdYXC9XcXVDb1VyXC91M1d2MzZTckZsWVZqTjAwb29rYkg1WkVJZ0JMVnBWS3RwWVhyYiIsIm1hYyI6ImFjYjA1NDAxN2Y5NmU5ZTQ3YWRhNzYwNDI5OTc1ZGRjZjEyNzdkNGYxNGJhOTQyODkyMzBmYWZiMzIyM2FkZTQifQ%3D%3D",
    "domain": "payment.ivacbd.com",
    "path": "/"
}
driver.add_cookie(cookie)

# Refresh the page to apply the cookie
driver.get("https://payment.ivacbd.com/")

# Verify if login was successful by checking a specific element
try:
    driver.find_element("xpath", "//a[contains(text(), 'Logout')]")  # Adjust if needed
    print("✅ Login successful via session cookie!")
except:
    print("❌ Login failed, cookie might be expired or incorrect!")

# Keep the browser open
input("Press Enter to exit...")

# Close the browser
driver.quit()
