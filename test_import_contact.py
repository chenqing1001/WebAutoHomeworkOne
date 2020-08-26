import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


class TestCookie:

    def setup(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://work.weixin.qq.com")
        self.driver.implicitly_wait(5)

    def teardown(self):
        self.driver.quit()

    #获取特定页面的cookie信息并存入json文件
    def test_get_cookie(self):
        time.sleep(10)
        #获取当前页面的cookie内容
        cookie = self.driver.get_cookies()
        # print(cookie) #即使没登录，也会有cookie信息，这个cookie不保存任何账号信息
        #因为如果只是return cookie，则只能在当前代码运行时使用一次，所以可以将cookie存放到文件里进行持久化
        with open("cookie.json","w") as f:
            # f.write(cookie) #这种写法会报错，write要传str类型，cookie是list类型，所以下面可以使用json文件保存
            #将cookie存入一个json文件中
            json.dump(obj=cookie,fp=f)

    #使用读取json文件中cookie的方式登录
    def login_with_json_cookie(self):
        time.sleep(5)
        #从json文件中读取cookie信息
        cookies = json.load(open("cookie.json"))
         #循环cookies列表，将cookie添加到浏览器中
        for cookie in cookies:
            if "expiry" in cookie: #如果cookie中有"expiry"key,则从列表中移除此键值对
                cookie.pop("expiry")
            self.driver.add_cookie(cookie) #每次只加一个cookie到driver里
        time.sleep(2) #cookie植入需要一点时间
        # self.driver.refresh()
        ##备注：企业微信的cookie有效期是1天，登录后1天不用重新登录，中间扫过码的话，cookie就会失效
        self.driver.get("https://work.weixin.qq.com/wework_admin/frame#index")

    def test_import_contact(self):
        #使用cookie跳过登录
        self.login_with_json_cookie()
        # 点击导入通讯录
        self.driver.find_element(By.CSS_SELECTOR, ".index_service_cnt_itemWrap:nth-child(2)").click()
        # 获取当前文件的绝对路径
        dir_better = os.path.dirname(__file__)
        self.driver.find_element(By.ID, "js_upload_file_input").send_keys(dir_better + "/contact.xlsx")
        # 断言上传文件的名称是否正确
        actual_file_name = self.driver.find_element(By.ID, "upload_file_name").text
        assert actual_file_name == "contact.xlsx"
        # 点击确认导入
        self.driver.find_element(By.ID, "submit_csv").click()
        # 验证导入成功，提示"新增导入1人"
        actual_tip = self.driver.find_element(By.CSS_SELECTOR, ".import_succStage_resultShow").text
        assert actual_tip == "新增导入1人"

