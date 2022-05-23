from selenium import webdriver
from selenium.webdriver.common.by import By
#object of ChromeOptions
op = webdriver.ChromeOptions()
#set download directory path
p = ("download.default_directory": "C:\\Users""safebrowsing.enabled":"false")
#adding preferences to ChromeOptions
op.add_experimental_option("prefs", p)
driver = webdriver.Chrome(executable_path="C:\\chromedriver.exe", chrome_options=op)
driver.implicitly_wait(0.4)
driver.get("https://www.seleniumhq.org/download/");
#identify element
m = driver.find_element_by_link_text("32 bit Windows IE")
m.click()