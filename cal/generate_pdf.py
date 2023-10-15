from PIL import Image
import requests
import base64
import fitz
from pyzbar import pyzbar
from PIL import Image
import base64
import time
from bs4 import BeautifulSoup
from re import fullmatch
from urllib.parse import quote
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

class GeneratePdf():
    def __init__(self):
        self.result = {
            "status": "claves incorrectas",
            "pdfbase64": "",
            "url": "",
            "data": {}
        }
        
        # Install Webdriver
        service = Service(ChromeDriverManager().install())

        current_directory = os.getcwd()
        download_directory = os.environ.get('DOWNLOAD_DIRECTORY')
        download_full_path = os.path.join(current_directory, download_directory)

        os.makedirs(download_full_path, exist_ok=True)

        try:
            options = Options()
            if os.name == 'nt':
                path = os.getcwd()+'\sat_gob'
            else:
                path = os.getcwd()+'/sat_gob'

            options.add_argument('--user-data-dir=' + path)
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-web-security")
            options.add_argument('disable-infobars')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("prefs", {"download.prompt_for_download": False})
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            profile = {
                "plugins.plugins_list": [{ "enabled": False, "name": "Chrome PDF Viewer"}],
                "download.default_directory": download_full_path,
                "download.extensions_to_open": "",
                "plugins.always_open_pdf_externally": True
            }

            options.add_experimental_option("prefs", profile)

            # Create Driver Instance
            driver = webdriver.Chrome(options=options, service=service)
            driver.get(os.environ.get('TARGET_URL'))

            self.driver = driver
            self.wait_10 = WebDriverWait(driver, 10)
            print('driver', driver)
            print('page loading...')
        except:
            driver.close()
            driver.quit()
            print("Error: Driver loading failed")

    def login(self, rfc, pwd, file_name):
        try:
            self.driver.switch_to.frame("iframetoload")
            rfc_input = self.driver.find_element(By.ID, "rfc")
            pwd_input = self.driver.find_element(By.ID, "password")
            captcha_input = self.driver.find_element(By.ID, "userCaptcha")
            captcha_img_container = self.driver.find_element(By.ID, "divCaptcha")
            captcha_img = captcha_img_container.find_element(By.TAG_NAME, "img")
            img_url = captcha_img.get_attribute("src")
            submit = self.driver.find_element(By.ID, "submit")

            # RFC 
            rfc_input.click()
            rfc_input.clear()
            rfc_input.send_keys(rfc)

            # PASSWORD
            pwd_input.click()
            pwd_input.clear()
            pwd_input.send_keys(pwd)

            # CAPTCHA
            captcha_url = os.environ.get('CAPTCHA_URL')
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
                    response = requests.get(captcha_url, headers=headers, params=querystring)
                    captcha_code = response.json()["captcha"]
                    break
                except:
                    print(f"An error occurred")
            
            print("captcha", captcha_code)

            captcha_input.click()
            captcha_input.clear()
            captcha_input.send_keys(captcha_code)

            # SUBMIT
            submit.click()
            
            time.sleep(1)

            # HANDLE ERROR
            try:
                error_msg = self.driver.find_element(By.ID, "msgError")
                if error_msg:
                    self.driver.quit()
                    return self.result
            except:
                return self.generatePDF(file_name)

        except:
            self.driver.quit()
            return self.result

    def generatePDF(self, file_name):
        pdf_path = os.environ.get('DOWNLOAD_DIRECTORY')
        downloaded_org_file = f"{pdf_path}/SAT.pdf"
        renamed_file = f"{pdf_path}/{file_name}.pdf"

        # HANDLE PDF
        # try:
        #     os.remove(downloaded_org_file)
        # except Exception as e:
        #     print("===Error===", e)

        # Switch to main window
        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframetoload")))
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "formReimpAcuse:j_idt50"))).click()

        self.driver.switch_to.window(self.driver.window_handles[-1])
        current_url = self.driver.current_url
        
        # Wait download file
        time.sleep(15)

        # Rename file
        os.rename(downloaded_org_file, renamed_file)

        # Handle new pdf file
        doc = fitz.open(renamed_file)

        print("pdf page len=", len(doc))
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

        with open(renamed_file, "rb") as file:
            encoded_pdf = base64.b64encode(file.read()).decode('utf-8')
        
        self.result["status"] = "OK"
        self.result["pdfbase64"] = str(encoded_pdf)
        self.result['url'] = str(code)

        print("Starting Scraping...")
        self.driver.get(self.result['url'])
        html = self.driver.page_source
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
                        self.result['data'][temp] = td.text

            if regi_value and fecha_de_value:
                reg_temp_arr.append({"régimen": regi_value, "fecha_de_alta": fecha_de_value})
                regi_value = ""
                fecha_de_value = ""
        self.result['data']['características_fiscales'] = reg_temp_arr

        self.driver.quit()
        return self.result