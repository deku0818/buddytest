
import grequests
import json
import datetime
import time
import pymysql
import requests


def conn_mysql():
    '''京东云自动化测试数据库'''

    db = pymysql.connect(host="mysql-internet-cn-east-2-5025a215c9e84419.rds.jdcloud.com", user="auto_test_root",
                         password="huFJQu6YCg",
                         db="auto_test")
    return db

def get_configid_and_update_proconfig(config_name,project_name):
    '''根据配置名称获取配置id并且更改项目的configid'''

    db = conn_mysql()
    cursor = db.cursor()
    selecct_sql = "SELECT id FROM testcaseinfo WHERE name=%s"
    cursor.execute(selecct_sql,config_name)
    txId = cursor.fetchall()
    config_id = txId[0][0]
    update_sql = "UPDATE projectinfo SET config_id=%s WHERE project_name=%s"
    cursor.execute(update_sql, (config_id,project_name))
    db.commit()
    db.close()


def sss(config_id,project_name):
    db = conn_mysql()
    cursor = db.cursor()

    update_sql = "UPDATE projectinfo SET config_id=%s WHERE project_name=%s"
    cursor.execute(update_sql, (config_id, project_name))
    db.commit()
    db.close()


def get_moduleinfo(project_id):
    '''获取项目的模块id'''

    db = conn_mysql()
    cursor = db.cursor()

    selecct_sql = "SELECT module_name, id FROM moduleinfo where belong_project_id=%s"
    cursor.execute(selecct_sql%(project_id))
    txId = cursor.fetchall()
    db.close()
    # moduleinfo = {}
    moduleidList = []
    for i in txId:
        # moduleinfo[i[0]] = i[1]
        moduleidList.append(i[1])
    return moduleidList


def get_autotestmanager_sessionid(user,pwd):
    "登录测试平台，获取sessionid"

    url = "http://116.239.33.32:8000/api/login/"
    payload = {"account": user,
               "password": pwd}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }

    response = requests.post(url, data=payload, headers=headers)
    sessionid = response.headers["Set-Cookie"].split(';')[0].split('=')[1]
    return sessionid


def post_buddy_Test(sessionid, env_name, type, idList):
    """
    请求测试平台 模块运行用例接口
    使用grequests并发请求 后端接口
    后端接口请求
    """

    url = "http://116.239.33.32:8000/api/run_test/"
    headers = {
        "Cookie": "sessionid={0}".format(sessionid),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
        # "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }

    start = time.time()
    req_list = [grequests.post(url, headers=headers,
                               json = {"id": id,
                                        "env_name": env_name,
                                        "type": type,
                                        "report_name": ""}) for id in idList]
    res_list = grequests.map(req_list,  exception_handler=err_handler)
    # print(res_list[0].text())
    print(time.time() - start)


def err_handler(request, exception):
    print("请求出错")


def list_of_groups(init_list, children_list_len):
    list_of_groups = zip(*(iter(init_list),) *children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count !=0 else end_list
    return end_list


def run_buddytest2(user,pwd, env_name, type, idList):
    """运行测试"""
    sessionid = get_autotestmanager_sessionid(user,pwd)
    post_buddy_Test(sessionid, env_name, type, idList)


if __name__ == '__main__':

    config_name = "linde_正式环境_weifanglinde测试账号_全局变量"
    project_name="林德智联"
    get_configid_and_update_proconfig(config_name,project_name)
    time.sleep(10)


    user = "buddytest"
    pwd = "123456"
    type = "module"
    env_name = "https://smartlink.lindemh-cn.com"  # 腾讯云正式环境

    # 获取 林德智联 项目的模块id
    init_idList = get_moduleinfo(1)
    print(len(init_idList))

    idList_list = list_of_groups(init_idList,5)
    print(idList_list)
    for idlist in idList_list:
        run_buddytest2(user, pwd, env_name,type, idlist)
        time.sleep(10)
