import json
import os
import time
import requests
import calendar
import json
from pyzbar import pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import fitz

from playwright.sync_api import sync_playwright

def run_playwright(rfc, password):

    checked_cookie_file = f'{rfc}.json'
    checked_cookie_file_path = os.path.join('Cookies', checked_cookie_file)

    if os.path.exists(checked_cookie_file_path):
        print(f"The file {checked_cookie_file} exists in the directory {checked_cookie_file_path}.")
        last_modified_time = os.path.getmtime(checked_cookie_file_path)
        print('elaspes time=', time.time() - last_modified_time)
        if time.time() - last_modified_time > 60 * 15 : 
            return generate_cookie_pdf(rfc, password)
        else:
            return generate_pdf(checked_cookie_file_path)
    else:
        print(f"The file {checked_cookie_file} does not exists in the directory {checked_cookie_file_path}.")
        return generate_cookie_pdf(rfc, password)


def generate_cookie_pdf(rfc, password):
    with sync_playwright() as p:
        profile_path = get_profile_path()
        browser = p.chromium.launch_persistent_context(
            profile_path,
            headless=False,
            chromium_sandbox=False,
            accept_downloads=True,
            devtools=False,
            ignore_default_args=["--enable-automation"]
        )

        page = browser.new_page()
        page.goto(os.environ.get('TARGET_URL'))

        page.fill('#rfc', rfc)
        page.fill('#password', password)

        img_url = page.locator("#divCaptcha").locator("img").get_attribute(name="src")

        captcha_time = time.time()
        captcha_code = pass_captcha(img_url)
        page.fill('#userCaptcha', captcha_code)
        page.click('#submit')
        print(f'Captcha {time.time() - captcha_time:.2f} seconds')
        time.sleep(1)

        cookie_time = time.time()
        cookies_file_name = f'{rfc}.json'
        cookies_file_path = os.path.join(os.getcwd(), 'Cookies/', cookies_file_name)
        with open(cookies_file_path, 'w') as cookies_file:
            json.dump(page.context.cookies(), cookies_file, indent=4)

        print(f'cookietime {time.time() - cookie_time:.2f} seconds')
        page.goto(os.environ.get('TARGET_URL'))
            
        current_GMT = time.gmtime()
        time_stamp = calendar.timegm(current_GMT)

        with page.expect_download() as download_info:
            page.get_by_text('Generar Constancia').click()
        download = download_info.value
        pdf_path = os.path.join('Downloads', str(time_stamp) + '.pdf')
        download.save_as(pdf_path)

        return process_pdf(page, pdf_path)

def get_profile_path():
    browser_folders_path = os.path.join(os.getcwd(), 'Browser')

    if os.path.exists(browser_folders_path):
        import shutil
        shutil.rmtree(browser_folders_path)

    profile_path = os.path.join(browser_folders_path, 'profile')

    if not os.path.exists(profile_path):
        os.makedirs(profile_path, exist_ok=True)
        tmp_dir = os.path.join(profile_path, 'Default')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, exist_ok=True)
            with open(os.path.join(tmp_dir, 'Preferences'), 'w') as pref_file:
                default_preferences = {
                    'plugins': {
                        'always_open_pdf_externally': True,
                    },
                }
                json.dump(default_preferences, pref_file)

            return profile_path

def pass_captcha(img_url):
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
    
    return  captcha_code

def generate_pdf(cookie_file_path):
    with sync_playwright() as p:
        profile_path = get_profile_path()
        browser = p.chromium.launch_persistent_context(
            profile_path,
            headless=False,
            chromium_sandbox=False,
            accept_downloads=True,
            devtools=False,
            ignore_default_args=["--enable-automation"]
        )

        page = browser.new_page()

        with open(cookie_file_path, 'r') as cookies_file:
            cookies = json.load(cookies_file)

        page.context.add_cookies(cookies)
        page.goto(os.environ.get('TARGET_URL'))

        current_GMT = time.gmtime()
        time_stamp = calendar.timegm(current_GMT)

        with page.expect_download() as download_info:
            page.get_by_text('Generar Constancia').click()
        download = download_info.value
        pdf_path = os.path.join('Downloads', str(time_stamp) + '.pdf')
        download.save_as(pdf_path)


        return process_pdf(page, pdf_path)
    
def process_pdf(page, pdf_path):
    doc = fitz.open(pdf_path)

    flag = 1
    for page_num in range(len(doc)):
        pa = doc[page_num]

        pix = pa.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        qr_codes = pyzbar.decode(img)

        for qr_code in qr_codes:
            code = qr_code.data.decode("utf-8")
            print("QR Code Data:", code)
            flag = 0
            break
        if flag == False: break

    doc.close()

    with open(pdf_path, "rb") as file:

        import base64

        encoded_pdf = base64.b64encode(file.read()).decode('utf-8')

    result = {
        'status': 'OK',
        'pdfbase64': str(encoded_pdf),
        'url': str(code),
        'data': {}
    }

    page.goto(result['url'])

    html = page.content()
    page.close()
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')

    td_elements = soup.find_all('td', attrs={'role': 'gridcell'})

    regi_value = ""
    fecha_de_value = ""
    reg_temp_arr = []
    for td in td_elements:
        span = td.find('span')

        if span is not None:
            if span.text:
                temp = str(span.text)
                temp = temp.replace(" ", "_")
                temp = temp.replace(":", "")
                temp = temp.lower()
        else:
            if td.text:
                if temp == 'régimen':
                    regi_value = td.text
                elif temp == 'fecha_de_alta':
                    fecha_de_value = td.text
                else:
                    result['data'][temp] = td.text

        if regi_value and fecha_de_value:
            reg_temp_arr.append({"régimen": regi_value, "fecha_de_alta": fecha_de_value})
            regi_value = ""
            fecha_de_value = ""
    result['data']['características_fiscales'] = reg_temp_arr

    return result