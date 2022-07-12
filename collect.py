#coding=utf-8

from re import U
from socket import timeout
import uiautomator2 as u2
from mitmproxy import http
from mitmproxy import flow
import time

class HandleTonghuashun(object): 
    def __init__(self):
        #self.d = u2.connect_wifi("192.168.1.55")
        self.d = u2.connect()
        self.appname = "com.hexin.plat.android"
        self.watcher()

    def watcher(self):
        self.d.watcher.when('//*[@resource-id="com.hexin.plat.android:id/skip_tv"]').click()
        self.d.watcher.when('//*[@resource-id="com.hexin.plat.android:id/cancel_btn"]').click()
        self.d.watcher.start(1.0)

    def startApp(self):
        if self.appname not in self.d.app_list_running():
            self.d.app_start(self.appname)

    def tomystock(self):
        #if self.d.wait_activity(".Hexin",timeout=5):
        self.d(text="自选").click_exists(timeout=3)

    def UpLimitPool(self):
        self.d(text="涨停聚焦").click_exists(timeout=3)

    def HotList(self):
        self.d(text="同花顺热榜").click_exists(timeout=3)


def main():
    h = HandleTonghuashun()
    h.startApp()
    h.UpLimitPool()

if __name__ == "__main__":
    main()