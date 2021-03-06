#coding=utf-8
"""
scrape limit up stocks
"""

from operator import index
import re
from mitmproxy import ctx
from mitmproxy import http
import json,time,os
import pandas as pds
import math
import requests as rq

class ExportExcel:
    def __init__(self):
        self.stocks_head = ['股票名','涨停价','流通值','涨停原因','涨停形态','几天几板','换手率']
        self.reason_head = ['涨停股票数','占比','相关股票']
        self.save_path = "C:\\Users\\Administrator\\Desktop\\test.xlsx"
        self.date = time.strftime('%m-%d',time.localtime(time.time()))

    def exportData(self,stocks:list):
        t= time.strftime('%Y-%m-%d_%H-%M',time.localtime(time.time()))

        #构建股票详情表单
        stocks_list = pds.DataFrame(data=stocks,columns=self.stocks_head)

        #涨停原因统计
        reasons = []
        for row in stocks_list.itertuples(index=False):
            try:
                reason = getattr(row,'涨停原因').split('+')
            except:
                reason ="--"
            reasons.extend(reason)
        reason_type_num = pds.value_counts(reasons)

        concept_stock = {}
        for reason_type_name,_ in reason_type_num.iteritems():
            related_stocks = "" 
            for row in stocks_list.itertuples(index=False):
                try:
                    if reason_type_name in getattr(row,'涨停原因'):
                        related_stocks = related_stocks + getattr(row,'股票名') + " "
                except:
                    pass
            concept_stock[reason_type_name] = related_stocks

        reason_type = {'涨停股票数': reason_type_num,\
                     '占比': reason_type_num.apply(lambda x:str(round(x/len(reasons)*100,1))+"%"),\
                     '相关股票': pds.Series(concept_stock)}
        
        #构建涨停原因表单
        reason_list = pds.DataFrame(data=reason_type,columns=self.reason_head)
        ctx.log.info("start save...\n\n\n") 

        f = open(self.save_path,'a')
        with pds.ExcelWriter(self.save_path,mode='w') as writer: 
            stocks_list.to_excel(writer,index=False,sheet_name=self.date)
            reason_list.to_excel(writer,sheet_name=self.date,startcol=8)
            ctx.log.info("save path:%s"%os.path.join('C:\\Users\\Administrator\\Desktop\\limit_up_pool_',t,'.xlsx'))
            #df.to_excel(os.path.join('C:\\Users\\Administrator\\Desktop\\limit_up_pool_',t,'.xlsx'),sheet_name='limit_up')
            ctx.log.info("save the data over...\n") 
            f.close()

class LimitUp:
    def __init__(self) -> None:
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
    #limit_up interface
    def response(self,flow:http.HTTPFlow):
        if 'https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool?page' in flow.request.url:
            if flow.response.status_code == 200:
                body = json.loads(flow.response.text)
                page = body['data']['page']

                page_count = math.ceil(page['total']/page['limit'])
                #获取翻页全量数据
                export = ExportExcel()
                rows = []

                for i in range(1,page_count+1):
                    args = {'page': i,'limit': 15,'field': '199112,10,9001,330323,330324,330325,9002,330329,\
                            133971,133970,1968584,3475914,9003,9004','filter': 'HS,GEM2STAR','order_field': 330324,\
                            'order_type': 0,'data': '','_': 1657151054188}
                    rsp = rq.get(url="https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool",headers=self.header,params=args)
                    rsp_body = rsp.json()

                    if rsp_body['status_code'] == 0:
                        infos = rsp_body['data']['info']
                        for info in infos:
                            #ctx.log.warn("stock name:%s"%info['name'])
                            row = [ info['name'],info['latest'],str(round(info['currency_value']/100000000,1))+"亿",\
                                    info['reason_type'],info['limit_up_type'],info['high_days'],\
                                    round(info['change_rate'],1) ]
                            rows.append(row)
                    else:
                        ctx.log.warn("response failed.code:%i\n"%rsp_body['status_code'])  
                        

                export.exportData(rows)    
            else:
                ctx.log.warn("request failed.code:%i\n"%flow.response.status_code)  
                

addons = [LimitUp()]