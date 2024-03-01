import re
import requests
import base64
import json


class APP:
    def __init__(self):  # 初始化
        self.session = requests.session()
        self.url = 'http://qzjwxt.kjxy.nchu.edu.cn:800'
        self.courses = {}

        self.headers = {
            'Host': 'qzjwxt.kjxy.nchu.edu.cn:800',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Referer': 'http://qzjwxt.kjxy.nchu.edu.cn:800/jsxsd/',
        }

        self.login()

    def login(self):  # 登入平台
        url_login = f'{self.url}/jsxsd/xk/LoginToXk'
        data = {
            'userAccount': '',
            'userPassword': '',
            'encoded': base64.b64encode(str(username).encode()).decode() + '%%%' + base64.b64encode(str(password).encode()).decode(),
        }

        self.session.post(url_login, headers=self.headers, data=data)
        self.get_courses()

    def get_courses(self):  # 获取课表
        url_xklist = f'{self.url}/jsxsd/xsxk/xklc_list'  # 获取选课列表
        response = self.session.get(url_xklist, headers=self.headers).text

        try:
            url_jrxk = re.findall(r'<a href=\"(.*)\" target=\"blank\">进入选课</a>', response)[0]  # 获取进入选课链接
            url_jrxk = f'{self.url}{url_jrxk}'
            print('[+] 获取选课链接成功')

        except:
            print(
                '[-] 获取选课链接失败，请检查账号密码是否错误，若使用正确密码出现此问题，则为正则匹配失败，请手动修改匹配代码')
            exit(0)

        # 只有登入选课界面后，jsxsd/xsxkkc/xsxkBxxk 访问才有课程表，否则视为登入异常
        self.session.get(url_jrxk, headers=self.headers)  # 模拟进入选课页

        ''' 
        url_xk = f'{self.url}/jsxsd/xsxkkc/comeInBxxk'  # 选课界面 参数说明：
        response = self.session.get(url_xk, headers=self.headers).text
        "aoColumns": [
            {"mDataProp": "kch", "sTitle": "课程编号", "sWidth": "140px"},
            {"mDataProp": "kcmc", "sTitle": "课程名"},
            {"mDataProp": "fzmc", "sTitle": "分组名"},
            {"mDataProp": "ktmc", "sTitle": "合班名称"},
            {"mDataProp": "xf", "sTitle": "学分", "sWidth": "50px", sClass: "center"},
            {"mDataProp": "kcxzmc", "sTitle": "课程性质"},
            {"mDataProp": "skls", "sTitle": "上课老师"},
            {"mDataProp": "sksj", "sTitle": "上课时间"},
            {"mDataProp": "skdd", "sTitle": "上课地点"},
            {"mDataProp": "xqmc", "sTitle": "上课校区"},
            {"mDataProp": "ctsm", "sTitle": "时间冲突"},
            {"mDataProp": "czOper", "sTitle": "操作", "sWidth": "80px", sClass: "center"}
        ]
        '''

        url_xsxk = f'{self.url}/jsxsd/xsxkkc/xsxkBxxk'  # 获取选课列表
        data = {
            'sEcho': '0',
            'iColumns': '0',
            'sColumns': '',
            'iDisplayStart': '0',
            'iDisplayLength': '15',
            'mDataProp_0': 'kch',
            'mDataProp_1': 'kcmc',
            'mDataProp_2': 'fzmc',
            'mDataProp_3': 'ktmc',
            'mDataProp_4': 'xf',
            'mDataProp_5': 'skls',
            'mDataProp_6': 'sksj',
            'mDataProp_7': 'skdd',
            'mDataProp_8': 'xqmc',
            'mDataProp_9': 'ctsm',
            'mDataProp_10': 'czOper',
        }

        response = self.session.post(url_xsxk, headers=self.headers, data=data).text
        courses_xsxk = json.loads(response)

        try:
            for item in courses_xsxk['aaData']:
                if item['fzmc'] not in self.courses.keys():
                    self.courses[item['fzmc']] = [item['jx02id'], item['jx0404id']]
            print('[+] 载入课表成功  \n课表信息：')
            for item in self.courses:
                print('|', item, self.courses[item][0], self.courses[item][1], '|')
        except:
            print('[-] 获取课表失败，可能为字典键值与实际不同，请手动修改代码，返回信息：', courses_xsxk['aaData'])
            exit(0)

        self.course_select()

    def course_select(self):  # 抢课函数
        if not len(self.courses) and not len(courses):  # 判断课表与选课列表都不为空
            print('[-] 请输入至少一个选择的课程，如果已输入课程，则可能课表为空')
            exit(0)

        print('[+] 正在抢课中')
        while True:
            for item1 in courses:
                for item2 in self.courses.keys():
                    if item1 in item2:
                        url = f'http://qzjwxt.kjxy.nchu.edu.cn:800/jsxsd/xsxkkc/bxxkOper?kcid={self.courses[item2][0]}&cfbs=null&jx0404id={self.courses[item2][1]}'
                        response = json.loads(self.session.get(url, headers=self.headers).text)

                        if response['success']:
                            print('[+] 选课成功')
                            return


username = input('请输入学号：').strip()
password = input('请输入密码：').strip()

courses = input('请输入课程名称（多个课程请以空格隔开) :').strip().split(' ')
if '' in courses:
    print('[-] 请检查输入课程名称', courses)
    exit(0)

app = APP()
