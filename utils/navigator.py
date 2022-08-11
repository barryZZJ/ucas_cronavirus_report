import time

import requests
from easydict import EasyDict as edict
from utils.user import User
from utils.httpRequestUtil import httpRequest

conf = edict(dict(
    auth_welcome=dict(url='https://app.ucas.ac.cn/uc/wap/login', method='get'),
    auth_check=dict(url='https://app.ucas.ac.cn/uc/wap/login/check', method='post'),
    history_data=dict(url='https://app.ucas.ac.cn/ucasncov/api/default/daily?xgh=0&app_id=ucas', method='get'),
    report=dict(url='https://app.ucas.ac.cn/ucasncov/api/default/save', method='post'),
))


class Navigator:
    REPORT_KEYS = ['date', 'realname', 'number', 'jzdz', 'zrzsdd', 'sfzx', 'dqszdd', 'geo_api_infot', 'szgj', 'szgj_select_info[id]', 'szgj_select_info[name]', 'geo_api_info', 'dqsfzzgfxdq', 'zgfxljs', 'tw', 'sffrzz', 'dqqk1', 'dqqk1qt', 'dqqk2', 'dqqk2qt', 'sfjshsjc', 'dyzymjzqk', 'dyzwjzyy', 'dyzjzsj', 'dezymjzqk', 'dezwjzyy', 'dezjzsj', 'dszymjzqk', 'dszwjzyy', 'dszjzsj', 'gtshryjkzk', 'extinfo', 'app_id']
    def __init__(self, user: User):
        self.s = requests.Session()
        self.user = user

    def login(self):
        # load user config from file
        if self.user.use_cookies:
            cookies = self.user.get_info()
            self.s.cookies.update(cookies)
        else:
            # authenticater user to get cookies (stored in session)
            self._authenticate(self.user)

    def _authenticate(self, user: User):
        # get first cookie eai-sess
        with httpRequest(self.s, **conf.auth_welcome) as resp:
            assert 'eai-sess' in self.s.cookies, self._err_msg('获取cookie eai-sess', 'cookie中不含eai-sess')

        # get second cookie UUkey
        payload = user.get_info()
        with httpRequest(self.s, **conf.auth_check, payload=payload) as resp:
            self._assert_json(resp, '获取cookie UUkey')
            assert 'UUkey' in self.s.cookies, self._err_msg('获取cookie UUkey', 'cookie中不含UUkey')

    def get_history_data(self):
        with httpRequest(self.s, **conf.history_data) as resp:
            self._assert_json(resp, '获取上次记录')
            res = resp.json()
            assert 'd' in res, self._err_msg('获取上次记录', '结果不含数据：{}'.format(res))
            return res['d']

    def gen_report_data(self, old_data):
        new_data = {key: old_data[key] for key in old_data if key in self.REPORT_KEYS}
        # 注意，经对比需要对数据做一下小调整，
        new_data.update({
            'date': time.strftime("%Y-%m-%d", time.localtime()),
            'geo_api_infot': '{"area":{"label":"","value":""},"city":{"label":"","value":""},"address":"","details":"","province":{"label":"","value":""}}',
            'szgj': '',
            'szgj_select_info[id]': '0',
            'szgj_select_info[name]': '',
            'app_id': 'ucas',
        })
        assert len(new_data) == len(self.REPORT_KEYS), self._err_msg('构造打卡数据', '构造的数据不完整！已有数据为：{}'.format(list(new_data.keys())))
        return new_data

    def do_report(self, data):
        with httpRequest(self.s, **conf.report, payload=data) as resp:
            self._assert_json(resp, '提交打卡数据')
            return resp

    @staticmethod
    def _assert_json(resp: requests.Response, msg=''):
        try:
            js = resp.json() # type: dict
        except requests.exceptions.JSONDecodeError as err:
            raise requests.exceptions.ContentDecodingError(f'{msg}失败！json解析错误，返回结果为：{resp.text}')
        assert 'e' in js, f'{msg}失败！json不含键"e"，返回结果为：{resp.text}'
        assert js['e'] == 0, f'{msg}失败！服务器报错信息为：{js["m"]}'

    @staticmethod
    def _err_msg(msg1, msg2=''):
        return f'{msg1}失败！{msg2}'