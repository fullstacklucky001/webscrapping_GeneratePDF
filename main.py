import json
import os
import time
import shutil

import fitz
import pyzbar
from PIL import Image
from playwright.sync_api import sync_playwright


def get_profile_path():
    browser_folders_path = os.path.join(os.getcwd(), 'Browser')

    if os.path.exists(browser_folders_path):
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


with sync_playwright() as p:
    start = time.time()
    print('start')

    profile_path = get_profile_path()
    print(profile_path)

    browser = p.chromium.launch_persistent_context(
        profile_path,
        headless=False,
        chromium_sandbox=False,
        accept_downloads=True,
        devtools=False,
        ignore_default_args=["--enable-automation"]
    )

    page = browser.new_page()

    from cookies_file import cookies

    page.context.add_cookies(cookies)
    page.goto(
        "https://rfcampc.siat.sat.gob.mx/app/seg/SessionBroker?url=/PTSC/IdcSiat/autc/ReimpresionTramite/ConsultaTramite.jsf&parametro=c&idSessionBit=&idSessionBit=null")

    print('Ok')
    '''# time.sleep(30)
    # page.reload()
        
    15110187034_SAEC8307099E1
    rfc = "SAEC8307099E1"
    password = "Walesca1"

    page.fill('#rfc', rfc)
    page.fill('#password', password)

    captcha_img_container = page.locator("#divCaptcha")
    captcha_img = captcha_img_container.locator("img")
    img_url = captcha_img.get_attribute(name="src")

    print(img_url)

    solver = TwoCaptcha("b94fc1d7d4b74a73594521840373d010")
    captcha_code = None

    try:
        result = solver.normal(img_url)
        captcha_code = result['code']
        print(captcha_code.upper())
    except:
        pass

    if captcha_code:
        page.fill('#userCaptcha', captcha_code.upper())
        page.click('#submit')
        time.sleep(5)
        print(page.context.cookies())'''

    script = """
        PrimeFaces.ab({source:'formReimpAcuse:j_idt50',oncomplete:function(xhr,status,args){
            window.open('/PTSC/IdcSiat/IdcGeneraConstancia.jsf');
        }});
        
        """

    with page.expect_download() as download_info:
        page.evaluate(script)
    download = download_info.value

    download.save_as(os.path.join('Downloads', download.suggested_filename))
    time.sleep(1)
    print(time.time() - start)
    exit()

    '''with page.context.expect_page() as tab:
        page.evaluate(script)
        time.sleep(10)

    new_tab = tab.value
    with page.expect_download() as download_info:
        
    download = download_info.value

    # Wait for the download process to complete and save the downloaded file somewhere
    download.save_as("./Downloads" + download.suggested_filename)


    image_path = './Downloads/screenshot.png'
    new_tab.screenshot(path=image_path)
    new_tab.pdf()

    from pyzbar.pyzbar import decode
    from PIL import Image

    with Image.open(image_path) as img:
        qr_codes = decode(img)
        qr_data = None
        if qr_codes:
            qr_data = qr_codes[0].data.decode('utf-8')

        print(qr_data)
        print(time.time() - start)

    time.sleep(10000)
    browser.close()'''
