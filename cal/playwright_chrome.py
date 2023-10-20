import requests
import time
import os
from playwright.sync_api import sync_playwright

result = {
    "status": "claves incorrectas",
    "pdfbase64": "",
    "url": "",
    "data": {}
}

def run_playwright(rfc, pwd):
    with sync_playwright() as p:
        start_time = time.time()
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(os.environ.get('TARGET_URL'))

        # Login with rfc, password, captcha
        login_frame = page.frame_locator('#iframetoload')
        login_frame.locator('#rfc').fill(rfc)
        login_frame.locator('#password').fill(pwd)
        captcha_input = login_frame.locator("#userCaptcha")
        captcha_img_container = login_frame.locator("#divCaptcha")
        captcha_img = captcha_img_container.locator('img')
        img_url = captcha_img.get_attribute('src')

        try:
            captcha_code = pass_captcha(img_url)
            captcha_input.fill(captcha_code)

            # Redirect portal page
            login_frame.locator('#submit').click()

            # Waiting portal page loading
            page.set_default_timeout(50000)
            # page.set_default_navigation_timeout(50000)

            page.wait_for_url(os.environ.get('PORTAL_URL'))
            # Handle portal iframe
            try:
                portal_iframe = page.wait_for_selector('#iframetoload').content_frame()
                print('portal_iframe=', portal_iframe)

                # Get generate PDF file button
                try:
                    # gen_pdf_btn = portal_iframe.locator(f'#{os.environ.get("GENERATE_PDF_BTN")}')
                    gen_pdf_btn = portal_iframe.locator('#formReimpAcuse\\:j_idt50')
                except Exception as e:
                    print('Generate PDF button not found : ', e)
                    return result
                
                if gen_pdf_btn:
                    gen_pdf_btn.click()


                    # input("Press Enter to close the browser...")    
                else:
                    print('Generate PDF button not found.')
                    return result

            except Exception as e:
                print('Get portal iframe error : ', e)
                return result

        except Exception as e:
            print('Pass captcha error : ', e)
            return result

def pass_captcha(img_url):
    start_time = time.time()

    captcha_url = os.environ.get('CAPTCHA_URL')
    querystring = {"image": img_url}
    rapid_keys = ["1b029f7bebmsh8f4d7158c2e53c4p1ec3cdjsn90e7c23929a9", 
                "5d10341094mshd1b5b7c721aeb1bp13afbbjsndb2f7b388bea",
                "dab759d9a5msh1308f96aedcabf5p113f87jsne21d78b4fd35",
                "b8e83ed90bmsh94f9d07bd1d6534p11c4adjsn662fb0fc2217",
                "8906cb5d84mshf935efec6c55168p11b99cjsn634fc5c2d963",
                "272d06c69amsh5aa1736d50bef91p16068fjsnd0ea6f959383",
                "67442fa9c7msh806839ab19f6ad0p1368b1jsnb4d255dd4d07",
                "5cb81df867mshf203d18a905e6c7p1b7448jsn500250db89b1",
                "04dce39de8mshe7d2a832209f6b8p16b517jsnce7c7000cb28",
                "851e4be954msh83309512be5bc12p14661cjsn26bb348c05bf"]
    
    for i in rapid_keys:
        try:
            headers = {
                "X-RapidAPI-Key": i,
                "X-RapidAPI-Host": "metropolis-api-captcha.p.rapidapi.com"
            }
            response = requests.get(captcha_url, headers=headers, params=querystring)
            captcha_code = response.json()["captcha"]
            break
        except:
            print(f"An error occurred")
    
    print("captcha code=", captcha_code)

    end_time = time.time()
    print('====== Pass captcha elapsed time ========', end_time - start_time)

    return  captcha_code