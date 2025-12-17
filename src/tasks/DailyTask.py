from operator import truediv
import re
from tkinter import S

from qfluentwidgets import FluentIcon

from src.tasks.MyBaseTask import MyBaseTask


class DailyTask(MyBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Daily Task"
       # self.group_name = "Daily"
        self.description = "用户点击时调用run方法1"
        self.icon = FluentIcon.CAR
        self.default_config.update({
            '体力本': "第一",
            '自动登录': False,
            'int选项': 1,
            '文字框选项': "默认文字",
            '长文字框选项': "默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字",
            'list选项': ['第一', '第二', '第3'],
        })
        self.config_type["体力本"] = {'type': "drop_down",
                                      'options': ['第一', '第二', '第3']}
        


    def run(self):
        self.log_info('日常任务开始运行!', notify=True)
        self.sleep(10)
        self.find_start_on_login()
        self.sleep(1)
        self.click(0.5,0.5)
        #self.find_start_on_home()
        self.log_info('日常任务运行完成!', notify=True)

    def find_start_on_login(self):#登录页面弹窗
        self.wait_click_ocr( box='login_click_start',match="点击任意区域进入游戏")
        self.log_info('点击任意区域进入游戏')
        if self.ocr(box="login_notice_feature", match="公告") :
            self.log_info('关闭公告弹窗后再次点击')
            self.wait_click_feature(box="login_closenotice_btn")
            self.sleep(0.5)#给一点缓冲时间让弹窗消失
            self.wait_click_ocr(box='login_click_start',match="点击任意区域进入游戏")
        #return self.wait_click_ocr( x=0.4, y=0.8, to_x=0.6, to_y=0.85,match="点击任意区域进入游戏",threshold = 0.9,raise_if_not_found=True)
    

    def find_start_on_home(self):#游戏主页弹窗
        popup_on_home = ["点击空白处继续", "获得道具","奖励信息"]
        while self.ocr(match="出发",threshold = 0.9) :
            self.wait_click_ocr(match = "点击空白处继续",threshold = 0.9)
            self.wait_click_feature(self.close_btn,time_out=3,threshold = 0.9)
        
        self.wait_click_ocr( x=0.4, y=0.8, to_x=0.6, to_y=0.85,match="点击空白处继续",threshold = 0.9,raise_if_not_found=True,time_out=5)






