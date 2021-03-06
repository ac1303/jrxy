# -*- coding: utf-8 -*-
import configparser
import json
from math import e
import re
import os

import requests
import Encrypt
import requests
import datetime
# =============================================================================================
class getLoginInfo:
    def __init__(self):
        # 获取路径
        configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config = configparser.ConfigParser()
        # 读取配置文件
        config.read(configPath, encoding="utf-8")
        self.config=config
        self.configPath=configPath
        self.head = {}
        self.studentId=config.get('user', "studentid")
        self.password=config.get('user', "passWord")
        self.session=requests.Session()

    def pushDeer(self,text):
        key=self.config.get('user','pushDeer')
        if(len(key)==40):
            print(datetime.datetime.now(),"开始推送数据到手机")
            url=self.config.get('url', "pushDeer_url")+"?pushkey="+key+"&text="+text
            req = json.loads(requests.get(url=url).text)
            if(req['content']['result']==False):
                print(datetime.datetime.now(),"密钥不正确")
            else:
                for list in req['content']['result']:
                    print(datetime.datetime.now(),"设备："+list['trace_id'],"推送"+list['description'])
        else:
            print(datetime.datetime.now(),"PushDeer的推送密钥不正确，请重新填写")

    def login(self):
        print(datetime.datetime.now(),"开始获取登录页面...")
        # 清空字典，避免出现无效cookie
        self.head.clear()
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36',
            }
        req = self.session.get(self.config.get('url', "login_Url"), headers=self.head)
        set_cookie = req.headers["SET-COOKIE"]
        route = re.findall("route=(.*?),", set_cookie)[0]
        JSESSIONID = re.findall("JSESSIONID=(.*?);", set_cookie)[0]
        html = req.text
        LT = re.findall('name="lt" value="(.*)"', html)[0]
        key = re.findall('var pwdDefaultEncryptSalt = "(.*?)"', html)[0]
        dllt = re.findall('name="dllt" value="(.*)"', html)[0]
        execution = re.findall('name="execution" value="(.*?)"', html)[0]
        rmShown = re.findall('name="rmShown" value="(.*?)"', html)[0]
        print(datetime.datetime.now(),'获取登录页面信息成功,正在进行登录前的准备...')
        body = {
            'username': self.studentId,
            'password': Encrypt.AESEncrypt_psw(self.password, key),
            'captchaResponse': '',
            'lt': LT,
            'dllt': dllt,
            'execution': execution,
            '_eventId': 'submit',
            'rmShown': rmShown
        }
        req = self.session.post(self.config.get('url', "login_Url"),data=body, headers=self.head)
        set_cookie = req.history[0].headers["SET-COOKIE"]
        CASTGC = re.findall("CASTGC=(.*?);", set_cookie)[0]
        CASPRIVACY = re.findall("CASPRIVACY=(.*?);", set_cookie)[0]
        iPlanetDirectoryPro = re.findall(
            "iPlanetDirectoryPro=(.*?);", set_cookie)
        print(datetime.datetime.now(),"登录成功,成功获取CASTGC,下一步获取HWWAFSESID和HWWAFSESTIME....")
        req = self.session.get(self.config.get('url', "getHWW_url"), headers=self.head)
        set_cookie = req.history[0].headers["SET-COOKIE"]
        HWWAFSESID = re.findall("HWWAFSESID=(.*?);", set_cookie)[0]
        HWWAFSESTIME = re.findall("HWWAFSESTIME=(.*?);", set_cookie)[0]
        print(datetime.datetime.now(),'获取HWWAFSESID和HWWAFSESTIME成功，正在进行获取MOD_AUTH_CAS前的准备...')
        self.head['Cookie'] = 'HWWAFSESID=' + \
            HWWAFSESID+'; HWWAFSESTIME='+HWWAFSESTIME
        self.head['Host'] = 'huat.campusphere.net'
        req = self.session.post(self.config.get('url', "cas_url"), headers=self.head)
        print(datetime.datetime.now(),'第一步完成...')
        self.head['Host'] = 'cas.huat.edu.cn'
        self.head['Cookie'] = 'CASTGC='+CASTGC+'; route='+route+'; JSESSIONID='+JSESSIONID + \
            '; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN'
        print(datetime.datetime.now(),'第二步完成...')
        req = self.session.post(req.history[0].headers["Location"], headers=self.head)
        self.head['Host'] = 'huat.campusphere.net'
        print(datetime.datetime.now(),'第三步完成...')
        req = self.session.post(req.history[0].headers["Location"], headers=self.head)
        ticket = re.findall(
            "ticket=(.*)", req.history[0].headers['Location'])[0]
        print(datetime.datetime.now(),'成功获取MOD_AUTH_CAS,保存数据后结束该函数！')
        if(self.config.has_section('Cookie')!=True):
            self.config.add_section("Cookie")
        self.config.set('Cookie', 'HWWAFSESID', HWWAFSESID)
        self.config.set('Cookie', 'HWWAFSESTIME', HWWAFSESTIME)
        self.config.set('Cookie', 'ticket', ticket)
        self.config.write(open(self.configPath, 'w',encoding="UTF-8"))

    def getTasks(self):
        print(datetime.datetime.now(),'正在获取打卡任务...')
        self.head.clear()
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36',
            }
        params = {
            'pageSize': 10,
            'pageNumber': 10}
        self.head['Host'] = 'huat.campusphere.net'
        self.head['Content-Type'] = 'application/json;charset=UTF-8'
        self.head['Cookie'] = 'HWWAFSESID='+self.config.get('Cookie', "HWWAFSESID")+'; HWWAFSESTIME='+self.config.get(
            'Cookie', "HWWAFSESTIME")+'; MOD_AUTH_CAS='+self.config.get('Cookie', "ticket")
        req = requests.post(self.config.get('url', "tasks_url"),
                            headers=self.head, data=json.dumps(params))
        tasks = json.loads(req.text)
        print(tasks)

    def getCollector(self):
        print(datetime.datetime.now(),'开始获取学校收集信息任务')
        self.head.clear()
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36',}
        params = {
            'pageSize': 20,
            'pageNumber': 1}
        self.head['Host'] = 'huat.campusphere.net'
        self.head['Content-Type'] = 'application/json;charset=UTF-8'
        self.head['Cookie'] = 'HWWAFSESID='+self.config.get('Cookie', "HWWAFSESID")+'; HWWAFSESTIME='+self.config.get(
            'Cookie', "HWWAFSESTIME")+'; MOD_AUTH_CAS='+self.config.get('Cookie', "ticket")
        req = requests.post(self.config.get('url', "collector_url"),
                            headers=self.head, data=json.dumps(params))
        tasks = json.loads(req.text)
        for task in tasks['datas']['rows']:
            # 判断是不是需要填写
            if(task['subject'] =="科技学院2022年寒假学生健康安全日报"):
                print(datetime.datetime.now(),'存在需要打卡的任务！')
                data={
                    "collectorWid":task['wid'],
                    "instanceWid":task['instanceWid']
                }
                req=requests.post(self.config.get('url', "collector_detail_url"),
                            headers=self.head, data=json.dumps(data))
                tasks = json.loads(req.text)
                print(datetime.datetime.now(),'开始保存数据到配置文件 ，然后结束该函数')
                if(self.config.has_section('collector')!=True):
                    self.config.add_section("collector")
                self.config.set('collector', 'collectWid', task['wid'])
                self.config.set('collector', 'instanceWid', str(task['instanceWid']))
                self.config.set('collector', 'formWid', tasks['datas']['collector']['formWid'])
                self.config.set('collector', 'schoolTaskWid', tasks['datas']['collector']['schoolTaskWid'])
                self.config.write(open(self.configPath, 'w',encoding="UTF-8"))

                # data['formWid']= tasks['datas']['collector']['formWid']
                # data['pageSize']=9999
                # data['pageNumber']=1
                # req = requests.post(self.config.get('url', "collector_form_url"),
                #             headers=self.head, data=json.dumps(data))
                # print(req.text)
            else:
                continue

    def submitCollector(self):
        print(datetime.datetime.now(),'开始读取数据并填充')
        form = {
                "longitude": self.config.get('user', "lon"),
                "latitude": self.config.get('user', "lat"),
                "address": self.config.get('user', "address"),
                "uaIsCpadaily": True,
                "formWid": self.config.get('collector','formwid'),
                "collectWid": self.config.get('collector','collectwid'),
                # "schoolTaskWid": "",
                "schoolTaskWid": self.config.get('collector','schooltaskwid'),
                "instanceWid": self.config.get('collector','instancewid'),
                "form":[{'wid':'33394','formWid':'3088','fieldType':'7','title':'今天你的所在地是？','sort':1,'value': self.config.get('user', "address_Province")+'/'+self.config.get('user', "address_City")+'/'+self.config.get('user', "address_Region"),'show':True,'formType':'0','sortNum':'1'},{'wid':'33395','formWid':'3088','fieldType':'2','title':'你是否已经安全抵达目的地？','sort':2,'fieldItems':[{'itemWid':'78251','content':'是，已抵达','isOtherItems':False,}],'value':'78251','show':True,'formType':'0','sortNum':'2'},{'wid':'33396','formWid':'3088','fieldType':'2','title':'今天你的体温是多少？','sort':3,'fieldItems':[{'itemWid':'78254','content':'37.2℃及以下','isOtherItems':False,}],'value':'78254','show':True,'formType':'0','sortNum':'3'},{'wid':'33397','formWid':'3088','fieldType':'2','title':'今天你的身体状况是？','sort':4,'fieldItems':[{'itemWid':'78256','content':'健康','isOtherItems':False,}],'value':'78256','show':True,'formType':'0','sortNum':'4'},{'wid':'33398','formWid':'3088','fieldType':'2','title':'截至打卡当日，你所在地区是否为中、高风险地区？','sort':5,'fieldItems':[{'itemWid':'78262','content':'否','isOtherItems':False,}],'value':'78262','show':True,'formType':'0','sortNum':'5'},{'wid':'33399','formWid':'3088','fieldType':'2','title':'近14天你或你的共同居住人是否有疫情中、高风险区域人员接触史？','sort':6,'fieldItems':[{'itemWid':'78264','content':'否','isOtherItems':False,}],'value':'78264','show':True,'formType':'0','sortNum':'6'},{'wid':'33400','formWid':'3088','fieldType':'2','title':'近14天你或你的共 同居住人是否和确诊、疑似病人接触过？','sort':7,'fieldItems':[{'itemWid':'78266','content':'否','isOtherItems':False,}],'value':'78266','show':True,'formType':'0','sortNum':'7'},{'wid':'33401','formWid':'3088','fieldType':'2','title':'近14天你或你的共同居住人是否是确诊、疑似病例 ？','sort':8,'fieldItems':[{'itemWid':'78268','content':'否','isOtherItems':False,}],'value':'78268','show':True,'formType':'0','sortNum':'8'},{'wid':'33402','formWid':'3088','fieldType':'2','title':'你或你的共同居住人目前是否被医学隔离？','sort':9,'fieldItems':[{'itemWid':'78270','content':'否','imageUrl':'','isOtherItems':False,}],'value':'78270','show':True,'formType':'0','sortNum':'9'},{'wid':'33403','formWid':'3088','fieldType':'2','title':'今天你当地的健康码颜色是？','sort':10,'fieldItems':[{'itemWid':'78271','content':'绿色','isOtherItems':False,}],'value':'78271','show':True,'formType':'0','sortNum':'10'},{'wid':'33404','formWid':'3088','fieldType':'2','title':'本人是否承诺以上所填报的全部内容均属实、准确，不存在任何隐瞒与不实的情况，更无遗漏之处','sort':11,'fieldItems':[{'itemWid':'78274','content':'是','isOtherItems':False,}],'value':'78274','show':True,'formType':'0','sortNum':'11'}]
                }
        body = {
                "appVersion": self.config.get('key', "appversion"),
                "systemName": "android",
                "bodyString": Encrypt.GenBodyString(form),
                "model": self.config.get('user', "model"),
                "lon": self.config.get('user', "lon"),
                "calVersion": "firstv",
                "systemVersion": "11",
                "deviceId": Encrypt.GenDeviceID(self.config.get('user', "studentid")),
                "userId": self.config.get('user', "studentid"),
                "version": "first_v2",
                "lat": self.config.get('user', "lat")}
        body['sign'] = Encrypt.SignForm(body)
        extension = {
            "lon": self.config.get('user', "lon"),
            "lat": self.config.get('user', "lat"),
            "model": self.config.get('user', "model"),
            "appVersion":self.config.get('key', "appversion"),
            "systemVersion": "11",
            "userId": self.config.get('user', "studentid"),
            "systemName": "android",
            "deviceId": Encrypt.GenDeviceID(self.config.get('user', "studentid")),
        }
        self.head.clear()
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36',
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'}
        self.head['Host'] = 'huat.campusphere.net'
        self.head['Cpdaily-Extension']=Encrypt.DESEncrypt(json.dumps(extension))
        self.head['Content-Type'] = 'application/json;charset=UTF-8'
        self.head['Cookie'] = 'HWWAFSESID='+self.config.get('Cookie', "HWWAFSESID")+'; HWWAFSESTIME='+self.config.get('Cookie', "HWWAFSESTIME")+'; MOD_AUTH_CAS='+self.config.get('Cookie', "ticket")
        # print(json.dumps(body))
        r = json.loads(requests.post(self.config.get('url', "collector_submitForm_url"), data=json.dumps(body), headers=self.head).text)
        print(datetime.datetime.now(),"任务打卡数据为：",r,"\n")
        self.pushDeer("今日校园打卡："+r['message'])