import configparser
import json
from math import e
import re
import os
import time
import Encrypt
import requests
import datetime
# =============================================================================================
# 获取路径
configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config = configparser.ConfigParser()
# 读取配置文件
config.read(configPath, encoding="utf-8")

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36',
}
# =============================================================================================
class Sign:
    def login():
        session = requests.Session()
        # ====================================================================获取登录页面
        print(datetime.datetime.now(),"开始获取登录页面...")
        # 再次定义的原因是，捕获异常后，重新请求cookie，header里面可能包含无效的cookie，所以需要清空字典
        headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36',
}
        req = session.get(config.get('url', "login_Url"), headers=headers)
        set_cookie = req.headers["SET-COOKIE"]
        route = re.findall("route=(.*?),", set_cookie)[0]
        JSESSIONID = re.findall("JSESSIONID=(.*?);", set_cookie)[0]
        html = req.text
        LT = re.findall('name="lt" value="(.*)"', html)[0]
        key = re.findall('var pwdDefaultEncryptSalt = "(.*?)"', html)[0]
        dllt = re.findall('name="dllt" value="(.*)"', html)[0]
        execution = re.findall('name="execution" value="(.*?)"', html)[0]
        rmShown = re.findall('name="rmShown" value="(.*?)"', html)[0]
        print("获取登录页面信息成功,下一步开始登录...")
        # =====================================================================开始登录
        print(datetime.datetime.now(),'正在进行登录前的准备...')
        body = {
            'username': config.get('user', "studentid"),
            'password': Encrypt.AESEncrypt_psw(config.get('user', "passWord"), key),
            'captchaResponse': '',
            'lt': LT,
            'dllt': dllt,
            'execution': execution,
            '_eventId': 'submit',
            'rmShown': rmShown
        }
        req = session.post(config.get('url', "login_Url"),
                           data=body, headers=headers)
        set_cookie = req.history[0].headers["SET-COOKIE"]
        CASTGC = re.findall("CASTGC=(.*?);", set_cookie)[0]
        CASPRIVACY = re.findall("CASPRIVACY=(.*?);", set_cookie)[0]
        iPlanetDirectoryPro = re.findall(
            "iPlanetDirectoryPro=(.*?);", set_cookie)
        print("登录成功,成功获取CASTGC,下一步获取HWWAFSESID和HWWAFSESTIME....")
        # =========================================================================================
        print(datetime.datetime.now(),'正在进行获取HWWAFSESID和HWWAFSESTIME...')
        req = session.get(config.get('url', "getHWW_url"), headers=headers)
        set_cookie = req.history[0].headers["SET-COOKIE"]
        HWWAFSESID = re.findall("HWWAFSESID=(.*?);", set_cookie)[0]
        HWWAFSESTIME = re.findall("HWWAFSESTIME=(.*?);", set_cookie)[0]
        print("获取HWWAFSESID和HWWAFSESTIME成功,下一步获取MOD_AUTH_CAS...")
        # =========================================================================================
        print(datetime.datetime.now(),'正在进行获取MOD_AUTH_CAS前的准备...')
        headers['Cookie'] = 'HWWAFSESID=' + \
            HWWAFSESID+'; HWWAFSESTIME='+HWWAFSESTIME
        headers['Host'] = 'huat.campusphere.net'
        req = session.post(config.get('url', "cas_url"), headers=headers)
        print('第一步...')
        headers['Host'] = 'cas.huat.edu.cn'
        headers['Cookie'] = 'CASTGC='+CASTGC+'; route='+route+'; JSESSIONID='+JSESSIONID + \
            '; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN'
        print('第二步...')
        req = session.post(req.history[0].headers["Location"], headers=headers)
        headers['Host'] = 'huat.campusphere.net'
        print('第三步...')
        req = session.post(req.history[0].headers["Location"], headers=headers)
        ticket = re.findall(
            "ticket=(.*)", req.history[0].headers['Location'])[0]
        print(datetime.datetime.now(),'成功获取MOD_AUTH_CAS,下一步保存数据...')
        # print(ticket)
        if(config.has_section('Cookie')):
            config.set('Cookie', 'HWWAFSESID', HWWAFSESID)
            config.set('Cookie', 'HWWAFSESTIME', HWWAFSESTIME)
            config.set('Cookie', 'ticket', ticket)
        else:
            config.add_section("Cookie")
            config.set('Cookie', 'HWWAFSESID', HWWAFSESID)
            config.set('Cookie', 'HWWAFSESTIME', HWWAFSESTIME)
            config.set('Cookie', 'ticket', ticket)
        config.write(open(configPath, 'w',encoding="UTF-8"))

    def getTasks():
        print(datetime.datetime.now(),'正在获取打卡任务...')
        params = {
            'pageSize': 10,
            'pageNumber': 10}
        headers['Host'] = 'huat.campusphere.net'
        headers['Content-Type'] = 'application/json;charset=UTF-8'
        headers['Cookie'] = 'HWWAFSESID='+config.get('Cookie', "HWWAFSESID")+'; HWWAFSESTIME='+config.get(
            'Cookie', "HWWAFSESTIME")+'; MOD_AUTH_CAS='+config.get('Cookie', "ticket")
        req = requests.post(config.get('url', "tasks_url"),
                            headers=headers, data=json.dumps(params))
        tasks = json.loads(req.text)
        # print(req.text)
        # 获取未打卡任务
        for n in tasks['datas']['unSignedTasks']:
            signInstanceWid = n['signInstanceWid']
            taskName = n['taskName']
            if taskName!="科院2021-2022学年第一学期学生安全日报":
                print(datetime.datetime.now(),"该任务不是疫情打卡，已跳过："+taskName)
                continue
                # TODO: write code...
            print(datetime.datetime.now(),"正在打卡："+taskName)
            extension = {
                "systemName": "android",
                "systemVersion": "11",
                "model": config.get('user', "model"),
                "deviceId": Encrypt.GenDeviceID(config.get('user', "studentid")),
                "appVersion": config.get('key', "appversion"),
                "lon": config.get('user', "lon"),
                "lat": config.get('user', "lat"),
                "userId": config.get('user', "studentid"), }
            # sign_headers = {
            #     'tenantld': 'huat',
            #     'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Premium Edition Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 okhttp/3.12.4 cpdaily/9.0.12 wisedu/9.0.12',
            #     'CpdailyStandAlone': '0',
            #     'extension': '1',
            #     'Cpdaily-Extension': Encrypt.DESEncrypt(json.dumps(extension)),
            #     'Content-Type': 'application/json; charset=utf-8',
            #     'Host': 'huat.campusphere.net',
            #     'Connection': 'Keep-Alive',
            #     'Accept-Encoding': 'gzip',
            #     'Cookie': 'MOD_AUTH_CAS='+config.get('Cookie', "ticket")+'; path=/; Httponly; Max-Age=21600'}
            form = {
                "longitude": config.get('user', "lon"),
                "latitude": config.get('user', "lat"),
                "isMalposition": '0',
                "abnormalReason": "",
                "signPhotoUrl": "",
                "isNeedExtra": '1',
                "position": config.get('user', "address"),
                "uaIsCpadaily": 'true',
                "signInstanceWid": signInstanceWid,
                "signVersion": "1.0.0",
                "extraFieldItems": [{"extraFieldItemValue": "是（已返校，走读学生填写此项）", "extraFieldItemWid": '1497912'}, {"extraFieldItemValue": "37.2° 及以下", "extraFieldItemWid": '1497914'}, {"extraFieldItemValue": "否", "extraFieldItemWid": '1497917'}, {"extraFieldItemValue": "否", "extraFieldItemWid": '1497920'}, {"extraFieldItemValue": "绿色", "extraFieldItemWid": '1497921'}]}
            body = {
                "appVersion": "9.0.12",
                "systemName": "android",
                "bodyString": Encrypt.GenBodyString(form),
                "model": config.get('user', "model"),
                "lon": config.get('user', "lon"),
                "calVersion": "firstv",
                "systemVersion": "11",
                "deviceId": Encrypt.GenDeviceID(config.get('user', "studentid")),
                "userId": config.get('user', "studentid"),
                "version": "first_v2",
                "lat": config.get('user', "lat")}
            body['sign'] = Encrypt.SignForm(body)
            r = json.loads(requests.post(config.get(
                'url', "sign_url"), data=json.dumps(body), headers=headers).text)
            print(datetime.datetime.now(),"打卡结果：", r)
            print('正在将打卡结果推送到微信...')
            url = "https://sctapi.ftqq.com/" + \
                config.get('user', "servesendkey")+".send"
            body = {
                "title": "今日校园"+taskName+"打卡结果",
                "desp": str(r)
            }
            res = requests.post(url=url, data=body)

    def test():
        print(datetime.datetime.now(),'正在获取打卡任务...')
        params = {
            'pageSize': 10,
            'pageNumber': 10}
        headers['Host'] = 'huat.campusphere.net'
        headers['Content-Type'] = 'application/json;charset=UTF-8'
        headers['Cookie'] = 'HWWAFSESID='+config.get('Cookie', "HWWAFSESID")+'; HWWAFSESTIME='+config.get(
            'Cookie', "HWWAFSESTIME")+'; MOD_AUTH_CAS='+config.get('Cookie', "ticket")
        req = requests.post(config.get('url', "tasks_url"),
                            headers=headers, data=json.dumps(params))
        tasks = json.loads(req.text)
        print(tasks)
        for n in tasks['datas']['unSignedTasks']:
            signInstanceWid = n['signInstanceWid']
            taskName = n['taskName']
            if taskName!="科院2021-2022学年第一学期学生安全日报":
                print(datetime.datetime.now(),"该任务不是疫情打卡，已跳过："+taskName)
                continue
                # TODO: write code...
            print(datetime.datetime.now(),"正在打卡："+taskName)
            form = {
                "longitude": config.get('user', "lon"),
                "latitude": config.get('user', "lat"),
                "isMalposition": '0',
                "abnormalReason": "",
                "signPhotoUrl": "",
                "isNeedExtra": '1',
                "position": config.get('user', "address"),
                "uaIsCpadaily": 'true',
                "signInstanceWid": signInstanceWid,
                "signVersion": "1.0.0",
                "extraFieldItems": [{"extraFieldItemValue": "是（已返校，走读学生填写此项）", "extraFieldItemWid": '1497912'}, {"extraFieldItemValue": "37.2° 及以下", "extraFieldItemWid": '1497914'}, {"extraFieldItemValue": "否", "extraFieldItemWid": '1497917'}, {"extraFieldItemValue": "否", "extraFieldItemWid": '1497920'}, {"extraFieldItemValue": "绿色", "extraFieldItemWid": '1497921'}]}
            body = {
                "appVersion": "9.0.12",
                "systemName": "android",
                "bodyString": Encrypt.GenBodyString(form),
                "model": config.get('user', "model"),
                "lon": config.get('user', "lon"),
                "calVersion": "firstv",
                "systemVersion": "11",
                "deviceId": Encrypt.GenDeviceID(config.get('user', "studentid")),
                "userId": config.get('user', "studentid"),
                "version": "first_v2",
                "lat": config.get('user', "lat")}
            body['sign'] = Encrypt.SignForm(body)
            start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '8:29', '%Y-%m-%d%H:%M')
            grab_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '8:30', '%Y-%m-%d%H:%M')
            now_time = datetime.datetime.now()
            if start_time < now_time<=grab_time:
                print("抢榜时间")
                while 1<2:
                    now_time = datetime.datetime.now()
                    if now_time>=grab_time:
                        print(datetime.datetime.now(),"\n开始打卡")
                        r = json.loads(requests.post(config.get('url', "sign_url"), data=json.dumps(body), headers=headers).text)
                        print(datetime.datetime.now(),"打卡结果：", r)
                        break
                    else:
                        time.sleep(0.05)
                        print("等待打卡，当前时间为",now_time)
            else:
                print(datetime.datetime.now(),"\n更新cookie")
                Sign.login()


try:
    Sign.test()
except:
    print("定时打卡捕获到异常\n")
    Sign.login()
    Sign.test()

# # 范围时间
# start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '8:29', '%Y-%m-%d%H:%M')
# grab_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '8:30', '%Y-%m-%d%H:%M')
# end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '19:00', '%Y-%m-%d%H:%M')
# # 当前时间
# now_time = datetime.datetime.now()
# # 判断当前时间是否在范围时间内
# if start_time < now_time < end_time:
#     # 若在当前时间范围，则进行打卡操作
#     if start_time < now_time<=grab_time:
#         print("抢榜时间")
#         while 1<2:
#             now_time = datetime.datetime.now()
#             if now_time>=grab_time:
#                 print(datetime.datetime.now(),"\n开始打卡")
#                 try:
#                     Sign.getTasks()
#                 except:
#                     print("定时打卡捕获到异常\n")
#                     Sign.login()
#                     Sign.getTasks()
#                 print(datetime.datetime.now(),"\n结束打卡")
#                 break
#             else:
#                 time.sleep(0.05)
#                 print("等待打卡，当前时间为",now_time)
#     else:
#         try:
#             # 打卡
#             print(datetime.datetime.now(),"\n开始打卡")
#             Sign.getTasks()
#             print(datetime.datetime.now(),"\n结束打卡")
#         except:
#             print("捕获到异常\n")
#             # 可能是cookie过期，重新获取cookie并打卡
#             print(datetime.datetime.now(),"\n开始打卡")
#             Sign.login()
#             Sign.getTasks()
#             print(datetime.datetime.now(),"\n结束打卡")
# else:
#     # 若不在打卡时间范围内，则更新cookie
#     print(datetime.datetime.now(),"\n更新cookie")
#     Sign.login()
