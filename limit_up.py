#coding=utf-8
"""
scrape limit up stocks
"""

from mitmproxy import ctx
from mitmproxy import http
import json,time
import pandas as pds

class ExportExcel:
    def __init__(self):
        self.columns = ['股票名','涨停价','流通值','涨停原因','涨停形态','几天几板','换手率']

    def exportData(self,data:list):
        t= time.strftime('%Y-%m-%d_%H-%M',time.localtime(time.time()))
        df = pds.DataFrame(data=data,columns=self.columns)
        ctx.log.info("start save...\n\n\n\n\n") 
        df.to_excel('C:\\Users\\Administrator\\Desktop\\test.xlsx',sheet_name='limit_up')
        #df.to_excel(os.path.join('limit_up_pool_',t,'.xlsx'),sheet_name='涨停池')
        ctx.log.info("save the data over...\n") 

class LimitUp:
    #limit_up interface
    def response(self,flow:http.HTTPFlow):
        if 'https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool?page' in flow.request.url:
            if flow.response.status_code == 200:
                body = json.loads(flow.response.text)
                infos = body['data'].get('info',{})
                if infos != {}:
                    export = ExportExcel()
                    rows = []
                    for info in infos:
                        #ctx.log.warn("stock name:%s"%info['name'])
                        row = [ info['name'],info['latest'],str(round(info['currency_value']/100000000,1))+"亿",\
                                info['reason_type'],info['limit_up_type'],info['high_days'],\
                                info['change_rate'] ]
                        rows.append(row)
                    export.exportData(rows)   
                else:
                    ctx.log.info("no info.")  
            else:
                ctx.log.warn("request failed.code:%i\n"%flow.response.status_code)  
                

addons = [LimitUp()]