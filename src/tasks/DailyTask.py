from operator import truediv
import re
from time import sleep
from tkinter import S

from cv2 import matchShapes
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
            '体力刷取': "纹章1",
            '领取邮件': True,
            '游戏昵称(非UID)': "星塔旅人大王",
            '邀约(1～5个)': ['菈露（圣夜）','冬香','花原','希娅','千都世'],
            #'送礼次数': 1,
             # '干员列表': ''' '菈露（圣夜）','冬香',  '花原','希娅','千都世', '卡西米拉', '鸢尾','琥珀', '尘沙', '师渺', '岭川', '璟麟', '科洛妮丝', '卡娜丝', '杏子', 
            #                 '苍兰', '紫槿', '特丽莎', '密涅瓦', '缇莉娅','夏花',  '雾语', '赤霞', '珂赛特', '焦糖','格芮','菈露','小禾' ''',
        })
        self.config_type["体力本"] = {'type': "drop_down",
                                      'options': [ '新活动','纹章1', '纹章2', "纹章3","秘纹经验" ,"技能1","技能2","技能3",'突破1','突破2','突破3']}
        self.add_text_fix({"拉露 (圣夜）": "菈露（圣夜）", "g0ld": "gold"})

    def test(self):
        #选择礼物
        settings_box = self.wait_ocr(box='gift_bar',match='礼物栏')
        if settings_box:
            self.wait_click_feature('gift_choose',threshold=0.5,after_sleep=0.5)
                        #成功送出礼物,获得默契值
        self.wait_click_ocr(box='gift_choose_confirm',match='送出礼物',after_sleep=2)
                        #礼物送出后获得回礼
        while self.wait_click_ocr(box='getprop',match='获得回礼!',after_sleep=2):
                        #默契值提升弹窗
            self.wait_click_ocr(box='tacitimprove',match='默契提升')
        #self.scroll_relative(0.22, 0.75, 50)
        # txt = self.wait_click_ocr(name='heartlink_trekker',match='菈露（圣夜）',after_sleep=1)
        # for box in txt:
        #     self.log_info(f"找到文本: {box.name} at {box.center()}")
        # txt_list = self.ocr(x=0.068, y=0.241, to_x=0.359, to_y=0.861)
        # self.log_info(f"区域内共识别到 {len(txt_list)} 个文本块：")
        # for box in txt_list:
        #     content = box.name 
        #     self.log_info(f"识别结果: 『{content}』")
    def run(self):
        self.log_info('日常任务开始运行!', notify=True)
        self.run_for_login()
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
        self.sleep(1.5)
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
        for _ in range(10):
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

        status_msg = "再次委托"
        self.wait_click_ocr(box="commission_get",match="一键领取",after_sleep=3)
        self.log_info("一键领取")
        status_msg = "委托未完成"
        
        while not self.ocr(box="commission_fin",match="委托完成!"):
            self.wait_click_ocr(box='commission_skip',match='跳过',after_sleep=1)
            self.wait_click_ocr(box='getprop',match='获得道具!')
            self.log_info("正在跳过动画...")
        self.wait_click_ocr(box="commission_again",match="再次委托")


        sleep(0.5)
        self.wait_click_feature("home")
        self.log_info(f"{status_msg} 返回主页")
        
    #采购purchase
    def start_purchase(self):
        self.wait_click_ocr(box="dailyzone",match="采购")
        self.log_info("委托")

        if self.wait_click_ocr(box="dailygift",match="每日赠礼",after_sleep=2):
            status_msg = "领取赠礼"
            self.wait_click_ocr(box="getprop", match="获得道具!")

        if self.wait_click_ocr(box="dailygift",match="已领取"):
            status_msg = "赠礼已领取"

        sleep(0.5)
        self.wait_click_feature("home")
        self.log_info(f"{status_msg} 返回主页")

#心链heartlink  chat invite mail
    def start_heartlink(self):
        # 进入心链界面
        self.wait_click_ocr(box="dailyzone",match="心链",after_sleep=1)
        self.log_info("心链")
        #进入邀约界面
        self.wait_click_ocr(box='heartlink_invite',match='邀约',after_sleep=1)
        self.log_info("邀约")
        #从配置中获取用户勾选的邀约名单
        invite_list = self.config.get('邀约(1～5个)', [])
        if not invite_list:
            self.log_info("配置中未选择任何邀约对象，跳过此步骤")
            return
        #循环识别并点击名单中的每一个值
        for name in invite_list:
            self.log_info(f"正在尝试邀约: {name}")
            found = False
            last_frame = None # 用于存储滚动前的画面
            # 设定最大翻页次数，防止死循环
            for retry in range(5): 
                # 尝试在当前画面寻找
                result = self.wait_click_ocr(x=0.068, y=0.241, to_x=0.359, to_y=0.861,match=name) #x=0.068, y=0.241, to_x=0.359, to_y=0.861,         name='heartlink_trekker',
                if result:
                    self.log_info(f"成功点击角色: {name}")
                    current_frame = self.frame
                    if last_frame is not None:
                        pass
                    last_frame = current_frame
                    #复位
                    self.scroll_relative(0.22, 0.75, 50)
                    self.heartlink_invite()
                    # 完成后回到列表页并等待加载，进行下一个人的识别
                    found = True
                    break # 找到并处理完，跳出当前的翻页循环
                else:
                    self.log_info(f"当前页面未找到 {name}，尝试上滑...")
                    # 2. 检查是否已经滑不动了（触底检测）
                    current_frame = self.frame
                    if last_frame is not None:
                        pass
                    last_frame = current_frame
                    # 执行滑动操作：从下往上滑 (向上滚动列表)
                    # 在屏幕中心向下滚动 11 个单位
                    self.scroll_relative(0.22, 0.75, -11)
                    #self.sleep(1) # 等待滑动动画停止

            # if self.wait_click_ocr(box='heartlink_trekker',match=name, after_sleep=1):
            #     self.log_info(f"成功点击角色: {name}")
            #     self.heartlink_invite()
            if not found:
                self.log_error(f"未能在屏幕上找到角色: {name}，可能需要提issue或者抽卡")
        #心链任务结束返回
        self.wait_click_feature("heartlink_close")
        self.log_info("心链邀约任务结束，返回主页")
#心链邀约程序(选择完毕人物)
    def heartlink_invite(self):
        #点击右侧邀约按钮
        if self.wait_click_ocr(box="heartlink_invite_rightbtn",match='邀约'):
            #开始邀约的弹窗确认
            while self.wait_ocr(box='start_invite_verify',match='开始邀约'):
                self.wait_click_ocr(box='confirmbtn',match='确认')
                #选择约会地点,默认第一个
                while self.wait_ocr(box='choose_date_location',match='选择约会地点'):
                    self.wait_click_ocr(box='choose_date_location_btn',match='选择' )
                    #跳过调情对话按钮
                    while self.wait_click_feature('dating_interface_nextbtn'):
                        #送出礼物和离开选项  选择送出礼物
                        self.wait_click_ocr(box='dating_givegift_btn',match='送出礼物')
                        #选择礼物
                        settings_box = self.wait_ocr(box='gift_bar',match='礼物栏')
                        if settings_box:
                            self.wait_click_feature('gift_choose',threshold=0.5,after_sleep=0.5)
                        #成功送出礼物,获得默契值
                        self.wait_click_ocr(box='gift_choose_confirm',match='送出礼物',after_sleep=2)
                        #礼物送出后获得回礼
                        while self.wait_click_ocr(box='getprop',match='获得回礼!'):
                            #默契值提升弹窗
                            self.wait_click_ocr(box='tacitimprove',match='默契提升')


                        # #选择礼物
                        # self.wait_click_feature('gift_choose')
                        # #成功送出礼物,获得默契值
                        # self.wait_click_ocr(box='gift_choose_confirm',match='送出礼物')
                        # #礼物送出后获得回礼
                        # self.wait_click_ocr(box='getprop',match='获得回礼!',after_sleep=2)
                        # #默契值提升弹窗
                        # self.wait_click_ocr(box='tacitimprove',match='默契提升')
        #点击右侧邀约按钮,发现已经完成过了,直接跳过
        if self.wait_click_ocr(box="heartlink_invite_rightbtn",match=['今日已邀约','默契等级达到6解锁']):
                return True
#任务 missions

#基金grant
#每日任务daily affairs