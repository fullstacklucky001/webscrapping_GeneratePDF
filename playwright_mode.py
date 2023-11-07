import json
import os
import time
import requests
import calendar
import json
import base64
from pyzbar import pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import fitz
from playwright.sync_api import sync_playwright

def load_cookies(page, rfc, password):

    page.fill('#rfc', rfc)
    page.fill('#password', password)

    img_url = page.locator("#divCaptcha").locator("img").get_attribute(name="src")

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
    
    page.fill('#userCaptcha', captcha_code.upper())
    page.click('#submit')
    time.sleep(1)

    cookies_file_name = f'./Cookies/{rfc}.json'
    with open(cookies_file_name, 'w') as cookies_file:
        cookies = page.context.cookies()
        json.dump(cookies, cookies_file, indent=4)


def save_and_get_pdf_path(page):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    with page.expect_download() as download_info:
        page.get_by_text('Generar Constancia').click()
    download = download_info.value
    pdf_path = os.path.join('Downloads', str(time_stamp) + '.pdf')
    download.save_as(pdf_path)

    return pdf_path

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

def run_playwright(rfc, password):
    with sync_playwright() as p:
        start = time.time()
        profile_path = get_profile_path()

        browser = p.chromium.launch_persistent_context(
            profile_path,
            headless=True,
            chromium_sandbox=False,
            accept_downloads=True,
            devtools=False,
            ignore_default_args=["--enable-automation"]
        )

        page = browser.new_page()

        cookies_file_path = f"./Cookies/{rfc}.json"
        if os.path.exists(f'{cookies_file_path}'):
            
            with open(cookies_file_path, 'r') as cookies_file:
                cookies = json.load(cookies_file)

            page.context.add_cookies(cookies)
            page.goto(os.environ.get('TARGET_URL'))

            captcha_element = None
            try:
                captcha_element = page.query_selector('#divCaptcha')

            except:
                pass

            if captcha_element:
                load_cookies(page, rfc, password)

        else:
            page.goto(os.environ.get('TARGET_URL'))
            load_cookies(page, rfc, password)

        pdf_path = save_and_get_pdf_path(page)
        
        doc = fitz.open(pdf_path)

        flag = 1
        for page_num in range(len(doc)):
            pa = doc[page_num]

            pix = pa.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            qr_codes = pyzbar.decode(img)

            for qr_code in qr_codes:
                code = qr_code.data.decode("utf-8")
                flag = 0
                break
            if flag == False: break

        doc.close()

        with open(pdf_path, "rb") as file:
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

        try:
            files = os.listdir(os.getenv('DOWNLOAD_PATH'))
            for file in files:
                file_path = os.path.join(os.getenv('DOWNLOAD_PATH'), file)
                os.remove(file_path)

            os.makedirs('Downloads', exist_ok=True)
        except OSError as e:
            print('Error: ', e)

        print(time.time() - start)

        return result