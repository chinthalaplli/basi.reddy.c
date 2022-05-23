from selenium import webdriver
import time

driver = webdriver.Chrome(r"C:\Users\user\Downloads\chromedriver.exe")
driver.get("https://reddit.com")
cookies = driver.get_cookies()
print(len(cookies))
cooki={'name':'cbr','value':'1234'}
driver.add_cookie(cooki)
cookies=driver.get_cookies()
print(len(cookies))
print(cookies)
"how to delete the cookie"
driver.delete_cookie('cbr')
cookies = driver.get_cookies()
print(len(cookies))


driver.delete_all_cookies()
cookies=driver.get_cookies()    
print(len(cookies))
