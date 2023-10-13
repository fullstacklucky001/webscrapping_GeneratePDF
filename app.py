from flask import Flask, request, jsonify
# from cal.index import calculate
import cal.generate_pdf as generate_pdf
from selenium import webdriver
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tabledef import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from flask_cors import CORS

application = Flask(__name__)
application.secret_key = 'web_app_for_scraping_mx_gov'

CORS(application)

engine = create_engine('sqlite:///user.db?check_same_thread=False', echo=True)
Session = sessionmaker(bind=engine)

# options = Options()
# options.add_argument("--ignore-certificate-errors")
# options.add_argument('disable-infobars')
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("prefs", {"download.prompt_for_download": False})
# # options.add_argument("--headless") # Ensure GUI is off
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")

# profile = {"plugins.plugins_list": [{ "enabled": False, "name": "Chrome PDF Viewer"}],
#     # 'profile.default_content_settings.popups': 0,
#     # 'profile.content_settings.exceptions.automatic_downloads.*.setting': 1,
#     "download.default_directory": "",
#     "download.extensions_to_open": "",
#     "plugins.always_open_pdf_externally": True
# }

# options.add_experimental_option("prefs", profile)
# driver = webdriver.Chrome(options = options)

@application.route('/')
def hello():
    print("hello world")
    return 'Welcome to Web Client!'

@application.route('/scraping',  methods=["POST"])
def scraping():
    print("get request")
    method = request.json
    rfc = method["rfc"]
    password = method["password"]

    s = Session()
    result = s.query(User).filter_by(rfc = rfc).first()
    print("--->result", result)

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    current_dt = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

    generate_pdf_intance = generate_pdf.GeneratePdf()

    if result:
        prev_dt = datetime.combine(result.created_date, datetime.min.time())

        # Get the difference in seconds
        difference_in_seconds = (current_dt - prev_dt).total_seconds()

        if difference_in_seconds <= 7 * 24 * 60 * 60:
            print("==pwd==", password)
            print("==result pwd==", result.password)
            if password == result.password:
                return jsonify(result.data)
            else: return jsonify({"status": "Claves incorrectas", "pdfbase64": "", "url": "1", "data": {}})
        else:
            if data['status'] != 'OK':
                return jsonify(data)    
            else:
                print('=======pdf result=======', data)
                result.data = data
                result.created_date = current_dt
                s.commit()
                return jsonify(s.query(User).filter_by(rfc = rfc).first().data)
    else:
        data = generate_pdf_intance.login(rfc, password)

        print('--------------- data result ---------------', data)
        if data['status'] != 'OK':
            return jsonify(data)
        else:
            print("rfc", rfc)
            print("password", password)
            print("current_dt", current_dt)
            user = User(rfc, password, data, current_dt)
            s.add(user)
            s.commit()

            print("sending result to client...")
            return jsonify(s.query(User).filter_by(rfc = rfc).first().data)

@application.route('/delete_user_cache/<rfc>')
def delete_user_cache(rfc):
    s = Session()
    s.query(User).filter_by(rfc = rfc).delete()
    s.commit()
    return "Success"

if __name__ == '__main__':
    application.run(host='0.0.0.0', port='5000')