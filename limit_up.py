#coding=utf-8
"""
scrape limit up stocks
"""

from mitmproxy import ctx
from mitmproxy import http
import json

class LimitUp:
    #limit_up interface
    def response(self,flow:http.HTTPFlow):
        if 'https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool?page' in flow.request.url:
            if flow.response.status_code == 0:
                ctx.log.info("result status code:%i"%flow.response.status_code)
                print("0000000000")
                body = json.loads(flow.response.text)
                infos = body['data'].get('info',{})
                if infos != {}:
                    f= open("stock.txt",mode='w')
                    for info in infos:
                        ctx.log.info("stock name:%s"%info['name'])
                        f.write(info['name'])
                    f.close()
                else:
                    ctx.log.info("no info.")  
            else:
                ctx.log.warn("request failed.")  
                

addons = [LimitUp()]