'''
the main of project
'''

import sys,os

back_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(back_directory) 

from information import limit_up_pool as lup
from information import hot_list as hl

def main():
    #收集数据
    limit_up_stocks = lup.LimitUpStocks()
    hot_stocks = hl.HotRankStocks()
    #limit_up_stocks.exportData()
    #print(limit_up_stocks.getReasonStatistics())
    print(hot_stocks.getHotStocks())

if __name__ == "__main__":
    main()