# -*- coding: utf-8 -*-
from getLoginInfo import *
test=getLoginInfo()
try:
    test.submitCollector()
except:
    print("打卡捕获到异常")
    test.login()
    test.getCollector()
    test.submitCollector()