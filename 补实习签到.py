import requests
import re
import sys
import time
import tkinter
from tkinter import messagebox

class show_information():
    def __init__(self):
        tkinter.Tk().withdraw()
        self.mine ='流沙则 v1.1'

    def normal(self,message):
        messagebox.showinfo(self.mine,message)

    def warning(self,message):
        messagebox.showwarning(self.mine,message)

def system_get_time():
    tim = time.localtime()
    time_dict = {
        'year': tim.tm_year, 'month': tim.tm_mon,
        'day': tim.tm_mday, 'hour': tim.tm_hour,
        'min': tim.tm_min, 'sec': tim.tm_sec}
    for x, y in time_dict.items():  # 格式化字典,长度小于2,前面补0
        time_dict[x] = y if len(str(y)) > 1 else f'0{y}'
    return time_dict

def get_address(address):
    """
    获取地址经纬度
    :return:
    """
    url = f'http://api.map.baidu.com/geocoder?address={address}'
    this_res = requests.get(url)
    this = re.findall('>.*.<', this_res.text)
    this = [i.replace('>', '').replace('<', '') for i in this]
    x, y = this[1], this[2]
    return x, y


class web_all_round:
    def __init__(self,username,passwd,address):
        self.username = username
        self.passwd = passwd
        self.address = address
        self.hearder = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'http://gzdk.gzisp.net',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; MI 8 SE Build/PKQ1.181121.001; wv) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile '
                          'Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://gzdk.gzisp.net/vueApp/dist/index.html',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,en-US;',
            'X-Requested-With': 'com.tentcoo.dkeducation'
        }
        self.host = 'http://58.215.9.164:8189'
        self.url = {
              'login':f'{self.host}/jsxx_new/mobile/login'
            , 'internshipId':f'{self.host}/jsxx_new/mobile/process/stu-location/getMylistByDate'
            , 'qiandao':f'{self.host}/jsxx_new/mobile/process/stu-location/save'
        }
        self.schoolId = 104
        self.req = requests.session()
        self.info =show_information()
        self.login()
        self.get_internshipId()
        self.checkin()
    def send_data_post(self,url,data):
        return self.req.post(url,data).text

    def send_data_get(self,url,data):
        return self.req.get(url,params=data).text

    def login(self):
        post_data = {'loginName': self.username,
                     'password': self.passwd,
                     'schoolId': self.schoolId}
        url = self.url['login']
        login_result = self.send_data_post(url,post_data)
        msg = re.findall('msg":.*,', login_result)[0].replace(',', '').split(':')[-1]
        if msg == 'null':
            session_id = re.findall(r'"sessionId":"[\w\W]{0,44}"', login_result)
            self.session_id = session_id[0].split(':')[-1].replace('"', '')
            self.student_id = re.findall(r'"student":{"id":[\d]{0,10}', login_result)[0].split(':')[-1]
        else:
            self.info.warning(f'用户: {self.username}\n状态: 签到失败!\n原因: 用户名或密码错误!')
            sys.exit()

    def get_internshipId(self):
        url = self.url['internshipId']
        year = system_get_time()['year']
        start_time = f'{year}-09-01'
        end_time = f'{year}-09-30'
        while True:
            post_data = {
                'token': self.session_id,
                'startDate': start_time,
                'endDate': end_time,
            }
            res = self.send_data_post(url, post_data)
            result = re.findall('"internshipId":[\w\W]{0,5},', res)
            if len(result) < 1:
                start_time = f'{year}-10-01'
                end_time = f'{year}-10-31'
            else:
                break
        self.internshipId =  int(result[0].replace(',', '').split(':')[-1])

    def checkin(self):
        x,y = get_address(self.address)
        post_data = {
            'token': self.session_id,
            'isAbnormal': 0,
            'checkType': 'CHECKIN',
            'studentId': self.student_id,
            'locationX': x,
            'locationY': y,
            'scale': 16,
            'label': self.address,
            'mapType': 'baidu',
            'content': '',
            'isEvection': 0,
            'internshipId': self.internshipId,
            'attachIds': ''

        }
        url = self.url['qiandao']
        result = self.send_data_post(url, post_data)
        result = result.split(',')
        false_or_sccess = result[0].split(':')[-1]
        msg = result[-2].split(':')[-1]
        if false_or_sccess != 'false':
            self.info.normal(f'用户 :{self.username}\n状态: 签到成功!')
        else:
            msg = msg.replace('"', '')
            self.info.warning(f'用户 :{self.username}\n状态: 签到失败!\n原因 :重复签到!')


#  使用示范
web_all_round('1717213108','liushaze@123','江苏省无锡市惠山区钱藕路1号')