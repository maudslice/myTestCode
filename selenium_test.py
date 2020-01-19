from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("blink-settings-imagesEnabled-false")
browser = webdriver.Chrome(executable_path="D:/Chrome Driver/chromedriver.exe", chrome_options=chrome_options)
browser.get("https://bbs.csdn.net/")
print(browser.page_source)
