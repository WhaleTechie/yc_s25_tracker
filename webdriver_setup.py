import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # add this

def create_driver():
    os.environ["CHROME_LOG_FILE"] = os.devnull if os.name != 'nt' else 'nul'
    os.environ["MOZ_DISABLE_RDD_SANDBOX"] = "1"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    options.add_experimental_option("prefs", {
        "webrtc.ip_handling_policy": "disable_non_proxied_udp",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False,
    })

    # Use webdriver_manager to install the correct ChromeDriver version automatically
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    return driver
