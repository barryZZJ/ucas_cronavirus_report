import os

from utils.navigator import Navigator
from utils.user import UserManager


print('***********************************************')
print('***                                         ***')
print('***      UCAS Cronavirus Report Script      ***')
print('***            Cookies Login                ***')
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
    print('提交打卡记录中')
    resp = nav.do_report(new_data)
    if resp.json()['e']==0:
        print('打卡成功！')

except Exception as err:
    print(err)

os.system('pause')



