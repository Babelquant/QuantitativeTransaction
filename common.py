'''
the common function of project.
'''

import time,os,sys

back_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(back_directory) 

#时间格式年-月-日_时-分
def currentTime():
    return time.strftime('%Y-%m-%d_%H-%M',time.localtime(time.time()))