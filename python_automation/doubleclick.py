from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
#browser exposes an executable file
#Through Selenium test we will invoke the executable file which will then
#invoke actual browser
driver = webdriver.Chrome(executable_path="C:\\chromedriver.exe")
# to maximize the browser window
driver.maximize_window()
#get method to launch the URL
driver.get("https://www.tutorialspoint.com/index.htm")
#to refresh the browser
driver.refresh()
# identifying the source element
source= driver.find_element_by_xpath("//*[text()='GATE Exams']");
# action chain object creation
action = ActionChains(driver)
# double click operation and perform
action.double_click(source).perform()
#to close the browser
driver.close()