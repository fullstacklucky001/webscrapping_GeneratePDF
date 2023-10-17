# PDF Generating and downloading

Generate PDF file and download it with desired name using web scrapping

<ul>
<h6>Requirement</h6>
    <li>Python 3.x required</li>
    <li>Python selenium</li>
    <li>Chrome webdriver</li>
</ul>
<ul>
    <li>Session will be stored in your local system</li>
</ul>

# How to run
1. Install virtual env module by `pip install virtualenv`.
2. Create virtual environment named `env` by `python -m venv env`
3. Activate virtual environment by `cd whatsappenv/Scripts`, `activate`
4. Install required modules by `pip install -r requirements.txt`.
5. Run Python scripts by `python app.py`.

# How to test
Make the POST request with below JSON and send to 127.0.0.1:5000/scraping using POSTMAN
    {
        "rfc": "SAEC8307099E1",
        "password": "Walesca1",
        "filename": "Name_AsYouWant_test1"
    }
    
    "filename" is the desired name