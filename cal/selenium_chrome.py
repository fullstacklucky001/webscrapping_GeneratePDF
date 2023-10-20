import requests
import base64
import fitz
import time
import os
import shutil
import calendar
from PIL import Image
from pyzbar import pyzbar
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from pyzbar.pyzbar import decode


class GeneratePdf():
    def __init__(self):

        create_instance_start_time = time.time()

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
        download_root_path = os.path.join(current_directory, download_directory)
        
        current_GMT = time.gmtime()

        time_stamp = calendar.timegm(current_GMT)

        download_full_path = os.path.join(download_root_path, str(time_stamp))
        self.download_full_path = download_full_path
        os.makedirs(self.download_full_path, exist_ok=True)

        try:
            options = Options()
            if os.name == 'nt':
                path = os.getcwd()+'\sat_gob'
            else:
                path = os.getcwd()+'/sat_gob'

            options.add_argument('--user-data-dir=' + path)
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-content-safety-policy")
            options.add_argument("--disable-features=CrossSiteDocumentBlockingIfIsolating")
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
            # driver = webdriver.Chrome(options=options)
            driver = webdriver.Chrome(options=options, service=service)
            driver.get(os.environ.get('TARGET_URL'))

            self.driver = driver
            print('driver=', driver)
        except:
            driver.close()
            driver.quit()
            print("Error: Driver loading failed")

        print(f"========= Create instance time : {time.time() - create_instance_start_time:.2f} seconds =======")

    def login(self, rfc, pwd):
        try:
            pass_captcha_start_time = time.time()

            self.driver.switch_to.frame("iframetoload")
            self.driver.find_element(By.ID, "rfc").send_keys(rfc)
            self.driver.find_element(By.ID, "password").send_keys(pwd)
            captcha_input = self.driver.find_element(By.ID, "userCaptcha")
            captcha_img_container = self.driver.find_element(By.ID, "divCaptcha")
            captcha_img = captcha_img_container.find_element(By.TAG_NAME, "img")
            img_url = captcha_img.get_attribute("src")
            submit = self.driver.find_element(By.ID, "submit")

            # CAPTCHA
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
            
            print("captcha", captcha_code)
            print(f"========= Captcha pass time : {time.time() - pass_captcha_start_time:.2f} seconds =======")

            captcha_input.send_keys(captcha_code)

            # SUBMIT
            self.end_pass_captcha_time = time.time()
            submit.click()
            
            return self.generatePDF()

        except:
            self.driver.quit()
            return self.result

    
    def generatePDF(self):
        
        downloaded_org_file = f"{self.download_full_path}/SAT.pdf"

        # Switch to main window
        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframetoload")))
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "formReimpAcuse:j_idt50"))).click()

        print(f"========= Loading potal page time : {time.time() - self.end_pass_captcha_time:.2f} seconds =======")

        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Wait download file
        time.sleep(3)

        processing_pdf_start_time = time.time()
        # Handle new pdf file
        doc = fitz.open(downloaded_org_file)


        flag = 1
        for page_num in range(len(doc)):
            page = doc[page_num]

            # Convert the PDF page to an image
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Decode QR codes in the image
            qr_codes = pyzbar.decode(img)

            # Process the detected QR codes
            for qr_code in qr_codes:
                code = qr_code.data.decode("utf-8")
                print("QR Code Data:", code)
                flag = 0
                break
            if flag == False: break

        doc.close()

        with open(downloaded_org_file, "rb") as file:
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

        try:
            shutil.rmtree(self.download_full_path)
            print(f"Directory '{self.download_full_path}' has been successfully deleted.")
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}")

        print(f"========= Processing PDF file time: {time.time() - processing_pdf_start_time:.2f} seconds=======")

        self.driver.close()
        self.driver.quit()
        return self.result