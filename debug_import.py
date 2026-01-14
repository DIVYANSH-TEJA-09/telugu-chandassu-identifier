import sys
import os
sys.path.insert(0, os.getcwd())
try:
    import telugu_chandas.constants as c
    print("Files in telugu_chandas:", os.listdir('telugu_chandas'))
    print("Attributes in constants:", dir(c))
except Exception as e:
    print(e)
