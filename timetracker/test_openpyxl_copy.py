from openpyxl import Workbook
from copy import copy

wb = Workbook()
ws = wb.active
c = ws['A1']
try:
    c.font.copy()
    print("c.font.copy() worked")
except AttributeError:
    print("c.font.copy() failed")
except Exception as e:
    print(f"c.font.copy() failed with {e}")

try:
    copy(c.font)
    print("copy(c.font) worked")
except Exception as e:
    print(f"copy(c.font) failed with {e}")
