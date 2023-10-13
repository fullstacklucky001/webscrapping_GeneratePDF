from PIL import Image
import requests
import base64
import fitz
from pyzbar import pyzbar
from PIL import Image
import base64
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# options = webdriver.ChromeOptions()

# profile = {"plugins.plugins_list": [{ "enabled": False, "name": "Chrome PDF Viewer"}],
#     "download.default_directory": "temp_pdf",
#     "download.extensions_to_open": "",
#     "plugins.always_open_pdf_externally": True
# }
# options.add_experimental_option("prefs", profile)

# driver = webdriver.Chrome(options = options)

def calculate(userName, userPwd):
    pdf_directory = "temp_pdf"

    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('disable-infobars')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("prefs", {"download.prompt_for_download": False})
    options.add_argument("--headless") # Ensure GUI is off
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    profile = {"plugins.plugins_list": [{ "enabled": False, "name": "Chrome PDF Viewer"}],
        # 'profile.default_content_settings.popups': 0,
        # 'profile.content_settings.exceptions.automatic_downloads.*.setting': 1,
        "download.default_directory": "temp_pdf",
        "download.extensions_to_open": "",
        "plugins.always_open_pdf_externally": True
    }

    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options = options)


    data = {
        "status": "claves incorrectas",
        "pdfbase64": "",
        "url": "",
        "data": {}
    }

    try:
        print("Starting")
        driver.get("https://www.sat.gob.mx/aplicacion/login/53027/genera-tu-constancia-de-situacion-fiscal")

        print("Sucess to run")
        iframe1 = driver.find_element("id", "iframetoload")
        driver.switch_to.frame(iframe1)
        nameInput = driver.find_element(By.ID, "rfc")
        pwdInput = driver.find_element(By.ID, "password")
        captchaInput = driver.find_element(By.ID, "userCaptcha")
        submit = driver.find_element(By.ID, "submit")
        imageContainer = driver.find_element(By.ID, "divCaptcha")
        captchaImage = imageContainer.find_element(By.TAG_NAME, "img")
        imgUrl = captchaImage.get_attribute("src")
        url = "https://metropolis-api-captcha.p.rapidapi.com/solve"

        print('iframe1=', iframe1)
        print('nameInput=', nameInput)
        print('pwdInput=', pwdInput)
        print('captchaInput=', captchaInput)
        print('submit=', submit)
        print('imageContainer=', imageContainer)
        print('captchaImage=', captchaImage)
        print('imgUrl=', imgUrl)

        querystring = {"image": imgUrl}

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
                break
            except:
                print(f"An error occurred")
        
        print("captcha", captchaCode)

        nameInput.clear()
        pwdInput.clear()
        captchaInput.clear()

        nameInput.send_keys(userName)
        pwdInput.send_keys(userPwd)
        captchaInput.send_keys(captchaCode)

        submit.click()

        time.sleep(0.5)
        try:
            error_msg = driver.find_element(By.ID, "msgError")
            if error_msg:
                data = {
                    "status": "claves incorrectas",
                    "pdfbase64": "",
                    "url": "",
                    "data": {}
                }
                return data
        except:
            pass

        try:
            os.remove(pdf_directory + "/SAT.pdf")
        except Exception as e:
            print("===Error===", e)

        driver.switch_to.default_content()

        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframetoload")))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "formReimpAcuse:j_idt50"))).click()

        driver.switch_to.window(driver.window_handles[-1])

        url = driver.current_url
        time.sleep(10)

        print("url", url)
        doc = fitz.open(pdf_directory + "/SAT.pdf")
        for page_num in range(len(doc)):
            page = doc[page_num]

            # Convert the PDF page to an image
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Decode QR codes in the image
            qr_codes = pyzbar.decode(img)

            # Process the detected QR codes
            flag = 1
            for qr_code in qr_codes:
                code = qr_code.data.decode("utf-8")
                print("QR Code Data:", code)
                flag = 0
                break
            if flag == False: break

        with open(pdf_directory + "/SAT.pdf", "rb") as file:
            encoded_pdf = base64.b64encode(file.read()).decode('utf-8')
        
        data["status"] = "OK"
        data["pdfbase64"] = str(encoded_pdf)
        data['url'] = str(code)

        print("Starting Scraping...")
        driver.get(data['url'])
        html = driver.page_source
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
                    if(temp == 'régimen'):
                        regi_value = td.text
                    elif(temp == 'fecha_de_alta'):
                        fecha_de_value = td.text
                    else:
                        data['data'][temp] = td.text

            if regi_value and fecha_de_value:
                reg_temp_arr.append({"régimen": regi_value, "fecha_de_alta": fecha_de_value})
                regi_value = ""
                fecha_de_value = ""
        data['data']['características_fiscales'] = reg_temp_arr

        driver.quit()

        return data
    except Exception as e:
        print("error0", e)
        data = {
            "status": e,
            "pdfbase64": "",
            "url": "",
            "data": {}
        }
        driver.quit()
        return data