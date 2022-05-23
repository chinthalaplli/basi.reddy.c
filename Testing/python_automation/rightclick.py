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
driver.get("https://www.tutorialspoint.com/about/about_careers.htm")
#to refresh the browser
driver.refresh()
# identifying the source element
source= driver.find_element_by_xpath("//*[text()='Company']");
# action chain object creation
action = ActionChains(driver)
# right click operation and then perform
action.context_click(source).perform()
#to close the browser
driver.close()
raja
Debomita Bhattacharjee