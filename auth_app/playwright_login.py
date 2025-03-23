import asyncio
from playwright.async_api import async_playwright
import time

# Dictionary to store active browser sessions
browser_sessions = {}

async def login_to_ivac(mobile_no, password, session_id):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Keep browser open
        context = await browser.new_context()
        page = await context.new_page()

        # Store the browser and page instance
        browser_sessions[session_id] = {"browser": browser, "page": page}

        await page.goto("https://payment.ivacbd.com/")

        # Close any popups
        await page.evaluate("""
            let popup = document.querySelector('.modal-content');
            if (popup) popup.remove();
        """)

        # Fill mobile number and submit
        await page.fill("input[name='mobile_no']", mobile_no)
        await page.click("#submitButton")

        # Wait for password field to appear
        await page.wait_for_selector("input[name='password']", timeout=10000)
        await page.fill("input[name='password']", password)
        await page.click("#submitButton")

        # Wait for OTP form to appear
        await page.wait_for_selector("input[name='otp']", timeout=10000)

        # Don't close the browser; return session ID
        return True

async def submit_otp(otp, session_id):
    """Submit OTP using an active browser session"""
    if session_id in browser_sessions:
        session_data = browser_sessions[session_id]
        page = session_data["page"]

        # Fill the OTP field and submit
        await page.fill("input[name='otp']", otp)
        await page.click("#submitButton")  # Submit OTP

        # Wait for the next page (or until some confirmation appears)
        await page.wait_for_timeout(5000)

        # Keep the browser open for a few seconds to ensure OTP submission
        await page.wait_for_timeout(5000)  # Wait for some confirmation or until next page loads

        return True
    return False
