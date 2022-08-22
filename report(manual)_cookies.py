import os
import sys

from utils.navigator import Navigator
from utils.user import UserManager

def assert_input(msg, choices: list):
    while True:
        res = input(msg)
        if res in choices:
            return res
        print('输入内容错误！')

print('***********************************************')
print('***                                         ***')
print('***      UCAS Cronavirus Report Script      ***')
print('***                Manual                   ***')
print('***         Cookies Login - by ZZJ          ***')
print('***                                         ***')
print('***********************************************')

try:
    usermg = UserManager(True)
    user = usermg.get_user()
    nav = Navigator(user)
    nav.login()
    print('获取历史打卡记录中')
    old_data = nav.get_history_data()
    print('构造本次打卡记录中')
    new_data = nav.gen_report_data(old_data)
    print('请设置需修改的参数：')
    if len(sys.argv) > 1 and sys.argv[1] in ['y', 'Y', 'n', 'N']:
        res = sys.argv[1]
    else:
        res = assert_input('昨日是否接受核酸检测？[y/n]', ['y', 'Y', 'n', 'N'])
    sfjshsjc = 1 if res in ['y', 'Y'] else 0
    assert 'sfjshsjc' in new_data, '待提交数据内不含"sfjshsjc"参数！打卡系统可能有变动，则本脚本不再支持！'
    print('用户输入为 昨日' + ('已' if sfjshsjc else '未') + '接受核酸检测')
    new_data['sfjshsjc'] = sfjshsjc
    print('提交打卡记录中')
    resp = nav.do_report(new_data)
    if resp.json()['e']==0:
        print('打卡成功！')

except Exception as err:
    print(err)

os.system('pause')



