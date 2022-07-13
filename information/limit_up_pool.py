#coding=utf-8
"""
scrape limit up stocks
"""
import json,time,os,sys
import pandas as pds
import math
import requests as rq
import common

#当DataFrame的列名含有中文时，pandas就无法准确的控制列宽，从而导致列名和列没有对齐
pds.set_option('display.unicode.ambiguous_as_wide', True)
pds.set_option('display.unicode.east_asian_width', True)

class LimitUpStocks:
    def __init__(self):
        self.url = "https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool"
        self.stocks_head = ['股票名','涨停价','流通值','涨停原因','涨停形态','几天几板','换手率']
        self.reason_head = ['涨停股票数','占比','相关股票']
        self.date = time.strftime('%m-%d',time.localtime(time.time()))
        self.header = {
                'Host': 'data.10jqka.com.cn',
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; HD1900 Build/QKQ1.190716.003; wv) \
                AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.92 Mobile \
                Safari/537.36 Hexin_Gphone/10.40.10 (Royal Flush) hxtheme/1 innerversion/\
                G037.08.577.1.32 followPhoneSystemTheme/1 userid/475543965 \
                hxNewFont/1 isVip/0 getHXAPPFontSetting/normal getHXAPPAdaptOldSetting/0',
                'Sec-Fetch-Mode': 'cors',
                'X-Requested-With': 'com.hexin.plat.android',
                'Sec-Fetch-Site': 'same-origin',
                'Referer': 'https://data.10jqka.com.cn/datacenterph/limitup/limtupInfo.html',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                }

        self.limit_up_stocks = self.getLimitUpStocks()

    def requestParam(self,page=1):
        return  {'page': page,'limit': 15,'field': '199112,10,9001,330323,330324,330325,9002,330329,\
                133971,133970,1968584,3475914,9003,9004','filter': 'HS,GEM2STAR','order_field': 330324,\
                'order_type': 0,'data': '','_': 1657151054188}

    #获取涨停所有股票
    def getLimitUpStocks(self):
        rsp = rq.get(url=self.url,headers=self.header,params=self.requestParam())
        rsp_body = rsp.json()
        one_page_data = parseLimitUpStockPackage(rsp_body)
        page = rsp_body['data']['page']
        page_count = math.ceil(page['total']/page['limit'])

        #获取翻页全量数据
        full_stocks = []
        for i in range(2,page_count+1):
            rsp = rq.get(url=self.url,headers=self.header,params=self.requestParam(i))
            one_page_data.extend(parseLimitUpStockPackage(rsp.json()))        

        #返回股票详情表单
        self.limit_up_stocks = pds.DataFrame(data=one_page_data,columns=self.stocks_head)
        return self.limit_up_stocks

    #获取涨停原因统计表
    def getReasonStatistics(self):
        reasons = []
        for row in self.limit_up_stocks.itertuples(index=False):
            try:
                reason = getattr(row,'涨停原因').split('+')
            except:
                reason ="--"
            reasons.extend(reason)
        reason_type_num = pds.value_counts(reasons)

        concept_stock = {}
        for reason_type_name,_ in reason_type_num.iteritems():
            related_stocks = "" 
            for row in self.limit_up_stocks.itertuples(index=False):
                try:
                    if reason_type_name in getattr(row,'涨停原因'):
                        related_stocks = related_stocks + getattr(row,'股票名') + " "
                except:
                    pass
            concept_stock[reason_type_name] = related_stocks

        reason_type = {'涨停股票数': reason_type_num,\
                     '占比': reason_type_num.apply(lambda x:str(round(x/len(reasons)*100,1))+"%"),\
                     '相关股票': pds.Series(concept_stock)}
        
        #涨停原因表单
        return pds.DataFrame(data=reason_type,columns=self.reason_head)

    #导出涨停池及原因统计到excel
    def exportData(self,path='limit_up_stocks_'+common.currentTime()+'.xlsx'):
        try:
            with pds.ExcelWriter(path,mode='w') as writer: 
                self.limit_up_stocks.to_excel(writer,index=False,sheet_name=self.date)
                self.getReasonStatistics.to_excel(writer,sheet_name=self.date,startcol=8)
        except:
            pass

#解析涨停池数据包
def parseLimitUpStockPackage(body):
    if body['status_code'] == 0:
        rows = []
        infos = body['data']['info']
        for info in infos:
            #ctx.log.warn("stock name:%s"%info['name'])
            row = [ info['name'],info['latest'],str(round(info['currency_value']/100000000,1))+"亿",\
                    info['reason_type'],info['limit_up_type'],info['high_days'],\
                    round(info['change_rate'],1) ]
            rows.append(row)
        return rows
