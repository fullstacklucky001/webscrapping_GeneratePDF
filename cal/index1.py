from playwright.sync_api import sync_playwright
import requests
import base64
import fitz
from pyzbar import pyzbar
from PIL import Image
from bs4 import BeautifulSoup
import time
import requests
import urllib.request
def calculate(userName, userPwd):
    data = {
        "status": "claves incorrectas",
        "pdfbase64": "",
        "url": "4",
        "data": {}
    }
    try:
        with sync_playwright() as p:
            print("Starting")
            browser = p.chromium.launch(headless=False)
            print("==>2")
            page = browser.new_page()
            page.route('**/*.pdf', lambda route: route.continue_())
            page.set_default_navigation_timeout(600000)  # Timeout of 60 seconds
            page.goto("https://www.sat.gob.mx/aplicacion/login/53027/genera-tu-constancia-de-situacion-fiscal")
            print("==>3")

            iframe1 = page.query_selector('#iframetoload')
            frame = iframe1.content_frame()

            nameInput = frame.query_selector('#rfc')
            pwdInput = frame.query_selector('#password')
            captchaInput = frame.query_selector('#userCaptcha')
            submit = frame.query_selector('#submit')
            image_container = frame.query_selector('#divCaptcha')
            captcha_image = image_container.query_selector('img')
            img_url = captcha_image.get_attribute('src')

            url = "https://metropolis-api-captcha.p.rapidapi.com/solve"

            querystring = {"image": img_url}

            rapid_key = ["1b029f7bebmsh8f4d7158c2e53c4p1ec3cdjsn90e7c23929a9", 
                        "5d10341094mshd1b5b7c721aeb1bp13afbbjsndb2f7b388bea",
                        "dab759d9a5msh1308f96aedcabf5p113f87jsne21d78b4fd35",
                        "b8e83ed90bmsh94f9d07bd1d6534p11c4adjsn662fb0fc2217",
                        "8906cb5d84mshf935efec6c55168p11b99cjsn634fc5c2d963",
                        "272d06c69amsh5aa1736d50bef91p16068fjsnd0ea6f959383",
                        "67442fa9c7msh806839ab19f6ad0p1368b1jsnb4d255dd4d07",
                        "5cb81df867mshf203d18a905e6c7p1b7448jsn500250db89b1",
                        "04dce39de8mshe7d2a832209f6b8p16b517jsnce7c7000cb28",
                        "851e4be954msh83309512be5bc12p14661cjsn26bb348c05bf"]

            for i in rapid_key:
                try:
                    headers = {
                        "X-RapidAPI-Key": i,
                        "X-RapidAPI-Host": "metropolis-api-captcha.p.rapidapi.com"
                    }
                    response = requests.get(url, headers=headers, params=querystring)
                    captchaCode = response.json()["captcha"]
                    break;       
                except:
                    print(f"An error occurred")
            
            print("captcha", captchaCode)

            nameInput.fill(userName)
            pwdInput.fill(userPwd)
            captchaInput.fill(captchaCode)

            with page.expect_navigation():
                submit.click()

            time.sleep(0.5)
            try:
                error_msg = frame.query_selector("#msgError")

                print("error_msg", error_msg)
                if error_msg.query_selector("strong"):
                    return data
            except:
                pass
            
            # Switch to the iframe
            print("Load second frame")

            iframe2 = page.wait_for_selector('#iframetoload')
            frame2 = iframe2.content_frame()
            
            generator = frame2.wait_for_selector('#formReimpAcuse\\:j_idt50', state="visible")
            generator.click()
            
            print("click generator button")
            
            def handle_download(download):
                # Wait for the download to complete
                download.save_as('file.pdf')

            page.on('download', handle_download)

            # Wait for the popup and switch to it

            new_page = page.wait_for_event("popup")

            print("sucess to load new_page")

            url = new_page.url
            # page.goto(url)
            # page.wait_for_selector('.pdf-viewer')
            # print(url)

            # # Get the PDF viewer element
            # pdf_viewer = page.query_selector('.pdf-viewer')
            # print("url")

            # # Save the PDF content
            # pdf_content = pdf_viewer.inner_html()
            # print("==>url")
            # with open('file.pdf', 'w', encoding='utf-8') as file:
            #     file.write(pdf_content)

            # page.wait_for_load_state('networkidle')
            # time.sleep(5)
            # page.pdf(path="file.pdf")
            # print("url")

            # pdf_content = None
            # print("file")

            # def intercept_response(route, response):
            #     nonlocal pdf_content
            #     try:
            #         pdf_content = response.body()
            #     except Exception as e:
            #         print(f"Error occurred while intercepting response: {str(e)}")
            # print("pdf")

            # page.on('response', intercept_response)

            # page.goto(url)
            # print(url)

            # page.wait_for_load_state('networkidle')

            # # Set the path where you want to save the PDF file
            # pdf_path = 'file.pdf'
            # print("file.pdf")

            # # Save the PDF content to a file
            # if pdf_content:
            #     with open(pdf_path, 'wb') as file:
            #         file.write(pdf_content)
            #     print('PDF downloaded successfully!')
            # else:
            #     print('PDF content not intercepted.')
            # print("end")

            page.goto(url)
            print(url)

            with page.expect_download() as download_info:
                # Perform the action that initiates download
                page.get_by_text("Download file").click()
            download = download_info.value

            # Wait for the download process to complete and save the downloaded file somewhere
            download.save_as(download.suggested_filename)

            # with page.expect_download() as download_info:
            #     print("value", download_info.value)
            #     page.click("text=Extra Small File 5 MB A high quality 5 minute MP3 music file 30secs @ 2 Mbps 10s >> img")
            # download = download_info.value
            # print("download", download)
            # path = download.path()
            # download.save_as(download.suggested_filename)
            # print("path", path)


            browser.close()

            return data
    except:
        return data