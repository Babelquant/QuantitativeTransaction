"""
scrape hot stocks
"""

from email.policy import default
import json,time,os
import pandas as pds
import math
import requests as rq
import common

#当DataFrame的列名含有中文时，pandas就无法准确的控制列宽，从而导致列名和列没有对齐
pds.set_option('display.unicode.ambiguous_as_wide', True)
pds.set_option('display.unicode.east_asian_width', True)

class HotRankStocks:
    def __init__(self):
        self.url = "https://eq.10jqka.com.cn/open/api/hot_list/v1/hot_stock/a/hour/data.txt"
        self.stocks_head = ['股票名','排名','排名变化','概念','人气','表现']
        self.date = time.strftime('%m-%d',time.localtime(time.time()))
        self.header ={
            'Host': 'eq.10jqka.com.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G9810 Build/QP1A.190711.020; wv) \
            AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 \
            Hexin_Gphone/10.13.02 (Royal Flush) hxtheme/0 innerversion/G037.08.462.1.32 userid/-640913281 hxNewFont/1',
            'Referer': 'https://eq.10jqka.com.cn/webpage/ths-hot-list/index.html?showStatusBar=true',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'com.hexin.plat.android'
        }

    #获取热度榜所有股票
    def getHotStocks(self):
        rsp = rq.get(url=self.url,headers=self.header)
        rsp_body = rsp.json()
        hot_list = parseHotStockPackage(rsp_body)
   
        #返回股票热度榜表单
        return pds.DataFrame(data=hot_list,columns=self.stocks_head) 

    #导出热度榜到excel
    def exportData(self,path='hot_stocks_'+common.currentTime()+'.xlsx'):
        try:
            with pds.ExcelWriter(path,mode='w') as writer: 
                self.getHotStocks().to_excel(writer,index=False,sheet_name=self.date)
        except:
            pass

#解析热度榜数据包
def parseHotStockPackage(body):
    if body['status_code'] == 0:
        rows = []
        infos = body['data']['stock_list']
        for info in infos:
            row = [ info['name'],info['order'],info['hot_rank_chg'],\
                    info['tag']['concept_tag'],info['rate'],info['tag'].get('popularity_tag',None)]
            rows.append(row)
        return rows
