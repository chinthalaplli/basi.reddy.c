from idlelib.multicall import r

import openpyxl
path=r"C:\Users\user\OneDrive\Desktop\testing\cbr.xlsx"
workbook=openpyxl.load_workbook(path)
sheet=workbook.active
for i in range(1,6):
	for c in range(1,4):
		sheet.cell(row=r,column=c).value='cbr'
workbook.save(path)
