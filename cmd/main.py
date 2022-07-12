'''
the main of project
'''
import sys

sys.path.append(r'D:\project\QuantitativeTransaction') 

from information import limit_up_pool as lup


def main():
    #收集数据
    limit_up_stocks = lup.LimitUpStocks()
    print(limit_up_stocks.limit_up_stocks)

if __name__ == "__main__":
    main()