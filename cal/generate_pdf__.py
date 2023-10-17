import requests
from playwright.sync_api import sync_playwright

# Define the API endpoint and parameters
api_url = "https://metropolis-api-captcha.p.rapidapi.com/solve"
api_headers = {
    "X-RapidAPI-Host": "metropolis-api-captcha.p.rapidapi.com",
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
    "Content-Type": "application/json",
}
api_data = {
    "captchaImage": "BASE64_ENCODED_IMAGE",  # Replace with the base64-encoded CAPTCHA image
}

# Make a POST request to the CAPTCHA solving API
response = requests.post(api_url, headers=api_headers, json=api_data)

if response.status_code == 200:
    captcha_solution = response.json().get("captchaSolution")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to the webpage with the CAPTCHA
        page.goto("https://example.com")
        
        # Fill in the CAPTCHA solution in the input field (adjust selector as needed)
        page.fill("input#captcha-input", captcha_solution)
        
        # Submit the form or perform other actions as needed
        page.click("button#submit-button")
        
        # Continue with the rest of your automation script
        
        browser.close()
else:
    print("CAPTCHA solving failed. Error:", response.status_code, response.text)
