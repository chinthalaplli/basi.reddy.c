from selenium import webdriver
from selenium.webdriver.firefox.options import Options
#object of Options class
op = Options()
#save file to path defined for recent download with value 2
op.set_preference("browser.download.folderList",2)
#disable display Download Manager window with false value
op.set_preference("browser.download.manager.showWhenStarting", False)
#download location
op.set_preference
("browser.download.dir","C:\\Users\\ghs6kor\\Documents\\Download")
#MIME set to save file to disk without asking file type to used to open file
op.set_preference
("browser.helperApps.neverAsk.saveToDisk",
"application/octet-stream,application/vnd.ms-excel")
#set geckodriver.exe path
driver = webdriver.Firefox(executable_path="C:\\geckodriver.exe",
firefox_options=op)
driver.maximize_window()
#launch URL
driver.get("https://the-internet.herokuapp.com/download");
#click download link
l = driver.find_element_by_link_text("xls-sample1.xls")
l.click()