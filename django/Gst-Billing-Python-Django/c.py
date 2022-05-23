import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdrivermanager import ChromeDriverManager


class TestUntitled():
    def setup_method(self, method):
        self.driver = webdriver.Chrome("C:\\Users\\user\\OneDrive\\Desktop\\cbr\\selenium\\chromedriver.exe")
        self.vars = {}

    def teardown_method(self, method):

        self.driver.quit()

    def test_untitled(self):
        self.driver.get("https://www.vn2solutions.com:2096")
        self.driver.find_element(By.ID,"user").send_keys("basi.reddy@vn2solutions.com")
        self.driver.find_element(By.NAME,"pass").send_keys("Cbr@1122")
        self.driver.find_element(By.XPATH,"//button[@id='login_submit']").click()
