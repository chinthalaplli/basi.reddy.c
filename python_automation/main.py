import xlrd, unittest
from selenium import webdriver
from ddt import ddt, data, unpack


def get_data(cbr):
    # create an empty list to store rows
    rows = []
    # open the CSV file
    book = xlrd.open_workbook(cbr)
    # get the frist sheet
    sheet = book.sheet_by_index(0)
    # iterate through the sheet and get data from rows in list
    for row_idx in range(1, sheet.nrows):  # iterate 1 to maxrows
        rows.append(list(sheet.row_values(row_idx, 0, sheet.ncols)))
    return rows


@ddt
class SearchEXCLEDDT(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(r"C:\Users\user\Downloads\chromedriver.exe")
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.driver.get("https://www.baidu.com")

    # get test data from specified excle spreadsheet by using the get_data funcion
    @data(*get_data('TestData.xlsx'))
    @unpack
    def test_search(self, search_value, expected_result):
        search_text = self.driver.find_element_by_id('kw')
        search_text.clear()
        search_text.send_keys(search_value)

        search_button = self.driver.find_element_by_id('su')
        search_button.click()

        tag = self.driver.find_element_by_link_text("PyPI").text
        self.assertEqual(expected_result, tag)

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main(verbosity=2)
