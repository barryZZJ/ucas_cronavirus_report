import os
import configparser

class User:
    def __init__(self, use_cookies):
        self.use_cookies = use_cookies
        self.info = None

    def get_info(self):
        return self.info

class User_pass(User):
    def __init__(self, username, password):
        super().__init__(False)
        self.info = dict(
            username=username,
            password=password
        )

class User_cookie(User):
    def __init__(self, eai_sess, UUKey):
        super().__init__(True)
        self.info = {
            'eai-sess': eai_sess,
            'UUKey': UUKey
        }


class UserManager:
    BASEPATH = os.path.dirname(os.path.dirname(__file__))
    CONFPATH = [os.path.join(BASEPATH, 'user.ini'), os.path.join(BASEPATH, 'user_cookies.ini')]
    def __init__(self, use_cookies):
        self.use_cookies = use_cookies
        self.config = {}
        self.check_new_user()
        self.load_config()

    def check_new_user(self):
        if not os.path.exists(self.CONFPATH[self.use_cookies]) or os.path.getsize(self.CONFPATH[self.use_cookies]) == 0:
            print('未检测到配置文件'+self.CONFPATH[self.use_cookies]+'，请输入', end='')
            if self.use_cookies:
                print('cookies\n（默认记住此配置，如需更新请删除或修改.ini文件）\n')
                eai_sess = input('eai-sess: ')
                UUKey = input('UUKey: ')
                self.config = {
                    'eai-sess': eai_sess,
                    'UUKey': UUKey
                }
            else:
                print('sep系统登录账号和密码\n（默认记住此配置，如需更新请删除或修改.ini文件）\n')
                print('说明：sep用户名一般为学校邮箱**@ucas.ac.cn。\n')
                username = input('sep账号：')
                password = input('sep密码：')
                self.config = dict(
                    username=username,
                    password=password
                )
            self.save_config()

    def save_config(self):
        parser = configparser.ConfigParser()
        if self.use_cookies:
            parser['user_cookies'] = self.config
        else:
            parser['user'] = self.config
        with open(self.CONFPATH[self.use_cookies], 'w') as conffile:
            parser.write(conffile)

    def load_config(self):
        parser = configparser.ConfigParser()
        parser.read(self.CONFPATH[self.use_cookies])
        if parser.has_section('user_cookies'):
            self.use_cookies = True
            config = parser['user_cookies']
            print('已读取cookies')
        elif parser.has_section('user'):
            self.use_cookies = False
            config = parser['user']
            print('已读取账号', config['username'])
        else:
            os.remove(self.CONFPATH[self.use_cookies])
            raise NotImplementedError('.ini配置文件已损坏，请重新配置')
        self.config = config

    def get_user(self):
        if self.use_cookies:
            return User_cookie(self.config['eai-sess'], self.config['UUKey'])
        else:
            return User_pass(self.config['username'], self.config['password'])
