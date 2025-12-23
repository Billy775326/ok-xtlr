from operator import truediv
import re
from time import sleep
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
            '用户游戏昵称': "樱岛麻衣",
            '长文字框选项': "默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字",
            'list选项': ['第一', '第二', '第3'],
        })
        self.config_type["体力本"] = {'type': "drop_down",
                                      'options': ['第一', '第二', '第3']}
        


    def run(self):
        self.log_info('日常任务开始运行!', notify=True)
        self.run_for_login(self)
        self.log_info('日常任务运行完成!', notify=True)

    def run_for_login(self):
        self.sleep(5)
        self.find_start_on_login()

        self.check_black_and_click()
        self.sleep(1)
        self.find_start_on_home()
        self.sleep(1)

    def find_start_on_login(self):#登录页面弹窗
        self.wait_click_ocr( box='login_click_start',match="点击任意区域进入游戏")
        self.sleep(0.5)
        self.log_info('点击任意区域进入游戏')
        if self.ocr(box="login_notice_feature", match="公告") :
            self.log_info('关闭公告弹窗后再次点击')
            self.wait_click_feature("login_closenotice_btn")
            self.sleep(0.5)#给一点缓冲时间让弹窗消失
            self.wait_click_ocr(box='login_click_start',match="点击任意区域进入游戏")
        #return self.wait_click_ocr( x=0.4, y=0.8, to_x=0.6, to_y=0.85,match="点击任意区域进入游戏",threshold = 0.9,raise_if_not_found=True)
    

    def find_start_on_home(self):#游戏主页弹窗
        """游戏主页弹窗处理：循环清理弹窗直到进入主界面"""
        self.log_info("开始清理主界面弹窗...")
        
        # 设定一个最大尝试次数，防止死循环
        for _ in range(3):
            # 1. 首先校验是否已经看到昵称（如果在主界面了，就直接结束）
            if self.check_player_nickname():
                self.log_info("已确认处于主界面。")
                break
                
            # 2. 检查并处理“获得道具”弹窗
            # 使用 wait_feature 检查图片特征或 OCR 检查文字
            if self.ocr(box="getprop", match="获得道具!"):
                self.log_info("检测到『获得道具』，点击空白处继续")
                # 使用我们之前算好的 1080p 坐标点击
                self.click(960, 870) 
                self.sleep(1.5) # 等待动画
                continue # 处理完一个弹窗后重新开始循环检查

            # 3. 检查并处理“每日签到”弹窗
            # 如果能看到签到页面的关闭按钮
            if self.find_one("checkin_closenotice_btn"):
                self.log_info("检测到『每日签到』，正在关闭...")
                self.wait_click_feature("checkin_closenotice_btn")
                self.sleep(1.5)
                continue

            # 4. 兜底逻辑：如果什么都没匹配到，但也没看到昵称，尝试点一下屏幕下方（防止未知的空白继续提示）
            self.log_info("未匹配到特定弹窗，尝试点击屏幕下方跳过潜在遮挡...")
            self.click(960, 870)
            self.sleep(2)


    def check_player_nickname(self):
        # 从配置中读取用户填写的昵称
        nickname = self.config.get('用户游戏昵称')
        self.log_info(f"正在匹配用户昵称: {nickname}")
        # 调用 OCR 在指定区域进行匹配
        # 动态将获取到的参数传给 match
        result = self.ocr(box="player_name_area", match=nickname)
        
        if result:
            self.log_info(f"成功校验昵称: {nickname}")
            return True
        else:
            # 获取实际识别到的文字用于调试
            actual_text = self.ocr(box="player_name_area")
            self.log_info(f"昵称校验失败！配置为: {nickname}, 实际看到: {actual_text}")
            return False
            
    def check_black_and_click(self):#跳过角色立绘展示
        """
        检查屏幕中心区域是否有黑色。
        如果黑色像素占比低于阈值（认为黑色消失），则点击中心区域。
        """
        # 1. 定义黑色的 RGB 范围
        # 纯黑是 (0,0,0)，这里给一点容差 (0-30) 以应对画质波动
        black_range = {
            'r': (0, 30), 
            'g': (0, 30), 
            'b': (0, 30)
        }
    
        # 2. 指定检测区域
        center_box = "loading_center_area" 
    
        # 3. 计算该区域内黑色的百分比
        black_percent = self.calculate_color_percentage(black_range, center_box)
        self.log_info(f"当前中心区域黑色占比: {black_percent:.2%}")
    
        # 4. 判断逻辑：如果黑色几乎没有了（比如占比低于 5%）
        if black_percent < 0.05:
            self.log_info("黑色已消失，执行点击")
            # 点击屏幕绝对中心点
            self.click(960, 540)
            return True
    
        return False

    #委托commission
    def start_commission(self):
        self.wait_click_ocr(box="dailyzone",match="委托")
        self.log_info("委托")
        sleep(0.5)
        self.wait_click_ocr(box="commission_get",match="一键领取")
        self.log_info("一键领取")
        status_msg = "委托未完成"
        
        if self.ocr(box="commission_fin",match="委托完成!"):
            self.wait_click_ocr(box="commission_again",match="再次委托")
            status_msg = "再次委托"

        sleep(0.5)
        self.wait_click_feature("home")
        self.log_info(f"{status_msg} 返回主页")
        
    #采购purchase
    def start_purchase(self):
        self.wait_click_ocr(box="dailyzone",match="采购")
        self.log_info("委托")

        if self.wait_click_ocr(box="dailygift",match="每日赠礼"):
            status_msg = "领取赠礼"
            self.wait_click_ocr(box="getprop", match="获得道具!")

        if self.wait_click_ocr(box="dailygift",match="已领取"):
            status_msg = "赠礼已领取"

        sleep(0.5)
        self.wait_click_feature("home")
        self.log_info(f"{status_msg} 返回主页")

#心链heartlink


#任务 missions

#基金grant