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
driver.get("https://jqueryui.com/droppable/")
#to refresh the browser
driver.refresh()
# identifying the source and target elements
source= driver.find_element_by_id("draggable");
target= driver.find_element_by_id("droppable");
# action chain object creation
action = ActionChains(driver)
# drag and drop operation and the perform
action.drag_and_drop(source, target).perform()
driver.close()