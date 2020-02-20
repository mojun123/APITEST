"""
------------------------------------
@Time : 2019/6/1 14:21
@Auth : linux超
@File : test_AddLoan_api.py
@IDE  : PyCharm
@Motto: Real warriors,dare to face the bleak warning,dare to face the incisive error!
------------------------------------
"""
import unittest
import inspect
from openpyxl.styles.colors import RED, GREEN

from libs.ddt import (data, ddt)
from base.base import Base
from business.LoginApi import login
from common.ParseExcel import do_excel
from common.DataReplace import add_parameters
from common.HandleJson import HandleJson
from common.ParseConfig import (do_conf, do_user)
from common.RecordLog import log
from common.SendRequests import request


@ddt
class TestAddApi(Base):
    """加标接口"""
    test_data = do_excel.get_name_tuple_all_value(do_conf('SheetName', 'add'))

    def setUp(self):
        # 管理员登录加标
        login.login_api(method='post',
                        url=do_conf('URL', 'Host_Url') + '/member/login',
                        data={"mobilephone": str(do_user('Admin', 'mobilephone')),
                              "pwd": (do_user('Admin', 'pwd'))}
                        )

    @data(*test_data)
    def test_add(self, value):
        row = value.CaseId + 1  # 用例ID所在行号
        precondition = value.Precondition  # excel用例的前置条件
        title = value.Title  # 用例标题
        url = do_conf('URL', 'Host_Url') + value.URL  # 用例url
        request_method = value.Method  # 请求方法
        request_value = value.Data  # 请求参数
        select_sql = value.Sql  # 查询数据库中不存在的member id
        add_expected = HandleJson.json_to_python(value.Expected)  # 期望结果
        if precondition == '借款人用户ID不存在':
            not_exist_loan_member_id = str(int(self.mysql(select_sql)['Id'])-1)
            request_value = add_parameters(not_exist_loan_member_id, request_value)
        else:
            request_value = add_parameters('', request_value)
        log.info('执行加标-测试用例"{}"开始'.format(title))
        response = request(request_method, url=url, data=request_value)
        actual_result = response.json()
        do_excel.write_cell(
            do_conf('SheetName', 'Add'),
            row,
            do_conf('ExcelNum', 'Actual_Column'),
            response.text
        )
        try:
            self.assertEqual(add_expected, actual_result, msg='测试{}失败'.format(title))
        except AssertionError as e:
            do_excel.write_cell(
                do_conf('SheetName', 'Add'),
                row,
                do_conf('ExcelNum', 'Result_Column'),
                do_conf('Result', 'Fail'),
                color=RED)
            log.error('{}-测试[{}] :Failed\nDetails:\n{}'.format(inspect.stack()[0][3], title, e))
            raise e
        else:
            do_excel.write_cell(
                do_conf('SheetName', 'Add'),
                row,
                do_conf('ExcelNum', 'Result_Column'),
                do_conf('Result', 'Pass'),
                color=GREEN)
            log.info('{}-测试[{}] :Passed'.format(inspect.stack()[0][3], title))
        log.info('执行加标-测试用例"{}"结束'.format(title))

    def tearDown(self):
        login.close()


if __name__ == '__main__':
    unittest.main()
