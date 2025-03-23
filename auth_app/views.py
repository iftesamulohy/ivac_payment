from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from auth_app.forms import LoginForm
from auth_app.models import IVACLoginInfo
from .selenium_login import submit_otp, login_to_ivac
import uuid
from asgiref.sync import sync_to_async

@csrf_exempt
def login_view(request):
    """Render login page"""
    form = LoginForm()
    return render(request, 'auth_app/login.html', {'form': form})

@csrf_exempt
def api_login(request):
    """Handle login form submission"""
    if request.method == "POST":
        mobile_no = request.POST.get("mobile_no")
        password = request.POST.get("password")
         # Generate a unique session ID
        session_id = str(uuid.uuid4())
        request.session['session_id'] = session_id

        # Store in database (encrypted)
        IVACLoginInfo.objects.update_or_create(mobile_no=mobile_no, defaults={"password": password},session_id=session_id)

       

        # Call Selenium function
        login_success = login_to_ivac(mobile_no, password, session_id)
        print("session id from number: ", session_id)
        if login_success:
            return JsonResponse({"status": "success", "message": "Login successful. Please enter OTP.", "session_id": session_id})
        return JsonResponse({"status": "error", "message": "Login failed. Please try again."})

    return JsonResponse({"status": "error", "message": "Invalid request method."})

@csrf_exempt
def submit_otp_api(request):
    """Handle OTP submission"""
    if request.method == "POST":
        otp = request.POST.get("otp")
        session_id = request.POST.get("session_id")

        if not session_id:
            return JsonResponse({"status": "error", "message": "Session expired. Please login again."})

        otp_success, cookie_dict = submit_otp(otp, session_id)  # Call Selenium function for OTP submission
        
        # Debug prints
        print("session id from otp: ", session_id)
        print(otp_success)
        print("Cookies from OTP: ", cookie_dict)

        if otp_success:
            try:
                # Retrieve the login information from the database using the session_id
                login_info = IVACLoginInfo.objects.get(session_id=session_id)

                # Update the cookies in the model
                login_info.set_cookies(cookie_dict)
                login_info.save()  # Save the updated record in the database

                return JsonResponse({"status": "success", "message": "OTP submitted successfully!"})
            except IVACLoginInfo.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Session not found. Please login again."})

        return JsonResponse({"status": "error", "message": "Failed to submit OTP. Please try again."})

    return JsonResponse({"status": "error", "message": "Invalid request method."})


# import json
# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from auth_app.models import IVACLoginInfo, PaymentInfo
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from django.views.decorators.csrf import csrf_exempt
# import time  # Import time module for pause
# @csrf_exempt
# def add_payment_info(request):
#     """View to add a new payment info."""
#     if request.method == "POST":
#         title = request.POST.get("title")
#         ivac_login_info_id = request.POST.get("ivac_login_info")

#         if not ivac_login_info_id:
#             return JsonResponse({"status": "error", "message": "Session expired. Please login again."})

#         try:
#             # Get the IVACLoginInfo instance based on the selected id
#             login_info = IVACLoginInfo.objects.get(id=ivac_login_info_id)

#             # Get the cookies as a dictionary
#             cookies = login_info.get_cookies()

#             # Extract the session cookie from the dictionary
#             session_cookie = cookies.get("ivac_session")

#             if not session_cookie:
#                 return JsonResponse({"status": "error", "message": "Session cookie not found."})

#             # Create a new PaymentInfo entry
#             payment_info = PaymentInfo.objects.create(
#                 title=title,
#                 ivac_login_info=login_info
#             )

#             # Initialize the WebDriver
#             chrome_options = Options()
#             service = Service(ChromeDriverManager().install())
#             driver = webdriver.Chrome(service=service, options=chrome_options)
#             driver.get("https://payment.ivacbd.com/")

#             # Add the session cookie from the PaymentInfo
#             cookie = {
#                 "name": "ivac_session",
#                 "value": session_cookie,  # Use the extracted session cookie
#                 "domain": "payment.ivacbd.com",
#                 "path": "/"
#             }
#             driver.add_cookie(cookie)

#             # Verify that the cookie is set
#             cookies_after_set = driver.get_cookies()
#             print("Cookies after setting:", cookies_after_set)

#             # Wait for a moment to ensure the cookie is set
#             time.sleep(2)

#             # Refresh the page using JavaScript
#             driver.execute_script("window.location.href = window.location.href;")

#             # Verify the cookies again after refresh
#             cookies_after_refresh = driver.get_cookies()
#             print("Cookies after refresh:", cookies_after_refresh)

#             # Wait for the page to fully load and verify login success
#             wait = WebDriverWait(driver, 10)
#             try:
#                 logout_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Logout')]")))
#                 print("✅ Login successful via session cookie!")
#             except:
#                 print("❌ Login failed, cookie might be expired or incorrect!")

#             # Keep the browser open
#             input("Press Enter to exit...")

#             # Close the browser
#             driver.quit()

#             return JsonResponse({"status": "success", "message": "Payment info created successfully!"})

#         except IVACLoginInfo.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Session not found. Please login again."})

#     # Fetch the IVACLoginInfo objects to display in the dropdown
#     ivac_login_info_list = IVACLoginInfo.objects.all()

#     return render(request, 'auth_app/add_payment_info.html', {
#         'ivac_login_info_list': ivac_login_info_list
#     })

from django.shortcuts import render, redirect
from django.http import JsonResponse
from auth_app.models import IVACLoginInfo, PaymentInfo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from django.views.decorators.csrf import csrf_exempt
import time
from selenium.webdriver.support.ui import WebDriverWait
@csrf_exempt
def add_payment_info(request):
    """View to add a new payment info."""
    if request.method == "POST":
        title = request.POST.get("title")
        ivac_login_info_id = request.POST.get("ivac_login_info")
        email = request.POST.get("email")
        
        # Get the bgd and name fields
        bgd_data = [request.POST.get(f"bgd{i}") for i in range(1, 6)]
        name_data = [request.POST.get(f"name{i}") for i in range(1, 6)]

        if not ivac_login_info_id:
            return JsonResponse({"status": "error", "message": "Session expired. Please login again."})

        try:
            # Get the IVACLoginInfo instance based on the selected id
            login_info = IVACLoginInfo.objects.get(id=ivac_login_info_id)

            # Get the cookies as a dictionary
            cookies = login_info.get_cookies()
            session_cookie = cookies.get("ivac_session")

            if not session_cookie:
                return JsonResponse({"status": "error", "message": "Session cookie not found."})

            # Create a new PaymentInfo entry
            payment_info = PaymentInfo.objects.create(
                title=title,
                ivac_login_info=login_info,
                email=email,
                bgd1=bgd_data[0], name1=name_data[0],
                bgd2=bgd_data[1], name2=name_data[1],
                bgd3=bgd_data[2], name3=name_data[2],
                bgd4=bgd_data[3], name4=name_data[3],
                bgd5=bgd_data[4], name5=name_data[4],
            )

            # Initialize the WebDriver
            chrome_options = Options()
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get("https://payment.ivacbd.com/")

            # Add the session cookie
            cookie = {
                "name": "ivac_session",
                "value": session_cookie,
                "domain": "payment.ivacbd.com",
                "path": "/"
            }
            driver.add_cookie(cookie)

            # Wait for a moment to ensure the cookie is set
            time.sleep(2)

            # Refresh the page using JavaScript
            driver.execute_script("window.location.href = window.location.href;")

            # JavaScript code you want to execute after reload
            js_script = """
                const bgd1 = 'BGDRV1F41C25';
                const name1 = 'ANWAR+HOSSAIN';
                const mobileno = '01797418758';
                const email = 'himelenganwar@gmail.com';
                const tokenkey = csrf_token;

                const container = document.createElement('div');
                container.style.cssText = 'position:fixed;bottom:10px;right:10px;display:flex';

                const buttonPanel = document.createElement('div');
                buttonPanel.style.cssText = `
                    width:420px;
                    height:50px;
                    padding:4px 10px;
                    text-align:left;
                    border:5px solid red;
                    background-color:#10cff9;
                    box-shadow:0 8px #10f9f6;
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                `;

                const btnContainer = document.createElement('div');
                btnContainer.style.cssText = 'display:flex;justify-content:space-between;width:100%;height:100%;';

                btnContainer.innerHTML = `
                    <div id="MyClockDisplay" class="clock"></div><br></br>
                    <button style="cursor:pointer;" onclick="Application_Info()">Application Info</button>
                    <button style="background:rgb(255, 171, 0);cursor:pointer;" onclick="Personal_Info()">Personal Info</button>
                    <button style="cursor:pointer;" onclick="Overview()">Overview Info</button>
                    <button style="background:rgb(249, 16, 160);cursor:pointer;" onclick="stopinfo()">Stop</button>
                `;

                buttonPanel.appendChild(btnContainer);
                container.appendChild(buttonPanel);
                document.body.appendChild(container);

                // Define AJAX submission functions (Application_Info, Personal_Info, Overview, stopinfo)
                // This is just an example; you need to define these functions as per your logic.
                function Application_Info() {
                    console.log('Application Info submitted');
                }
                function Personal_Info() {
                    console.log('Personal Info submitted');
                }
                function Overview() {
                    console.log('Overview submitted');
                }
                function stopinfo() {
                    console.log('Stopped');
                }
            """

            # Execute the JavaScript in the browser
            driver.execute_script(js_script)

            # Allow some time to see the effect before closing
            time.sleep(5)


            # Wait for the page to fully load and verify login success
            time.sleep(5)  # Adjust sleep time as necessary

            # Verify the cookies after refresh
            cookies_after_refresh = driver.get_cookies()

            # Wait for the page to fully load and verify login success
            wait = WebDriverWait(driver, 10)
            try:
                logout_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Logout')]")))
                print("✅ Login successful via session cookie!")
            except:
                print("❌ Login failed, cookie might be expired or incorrect!")

            # Close the browser
            driver.quit()

            return JsonResponse({"status": "success", "message": "Payment info created successfully!"})

        except IVACLoginInfo.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Session not found. Please login again."})

    # Fetch the IVACLoginInfo objects to display in the dropdown
    ivac_login_info_list = IVACLoginInfo.objects.all()

    return render(request, 'auth_app/add_payment_info.html', {
        'ivac_login_info_list': ivac_login_info_list
    })
