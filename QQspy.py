from selenium import webdriver
import os, time, re, random, cv2, datetime, pymysql
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
import numpy as np
import pandas as pd
from selenium.webdriver.chrome.options import Options


class Login(object): #登录类
    """
    腾讯防水墙滑动验证码破解
    使用OpenCV库
    成功率大概90%左右：在实际应用中，登录后可判断当前页面是否有登录成功才会出现的信息：比如用户名等。循环
    https://open.captcha.qq.com/online.html
    破解 腾讯滑动验证码
    腾讯防水墙
    python + seleniuum + cv2
    """

    def __init__(self):
        # 如果是实际应用中，可在此处账号和密码
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.url = "https://qzone.qq.com/"
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.user = ''#QQ账号
        self.ipass = ''#QQ密码

    def open(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.switch_to.frame('login_frame')
        self.driver.find_element_by_id("switcher_plogin").click()
        time.sleep(1)
        self.driver.find_element_by_id('u').clear()
        self.driver.find_element_by_id('u').send_keys(self.user)
        self.driver.find_element_by_id('p').clear()
        self.driver.find_element_by_id('p').send_keys(self.ipass)
        self.driver.find_element_by_id('login_button').click()
        time.sleep(5)
        try:
            self.driver.switch_to.frame('tcaptcha_iframe')
        except:
            self.driver.find_element_by_id('login_button').click()
            time.sleep(2)
            self.driver.switch_to.frame('tcaptcha_iframe')

    @staticmethod
    def show(name):
        cv2.imshow('Show', name)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def webdriverwait_send_keys(dri, element, value):
        """
        显示等待输入
        :param dri: driver
        :param element:
        :param value:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).send_keys(value)

    @staticmethod
    def webdriverwait_click(dri, element):
        """
        显示等待 click
        :param dri: driver
        :param element:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).click()

    @staticmethod
    def get_postion(chunk, canves):
        """
        判断缺口位置
        :param chunk: 缺口图片是原图
        :param canves:
        :return: 位置 x, y
        """
        otemp = chunk
        oblk = canves
        target = cv2.imread(otemp, 0)
        template = cv2.imread(oblk, 0)
        # w, h = target.shape[::-1]
        temp = 'temp.jpg'
        targ = 'targ.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        template = cv2.imread(temp)
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        return x, y
        # # 展示圈出来的区域
        # cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
        # cv2.imwrite("yuantu.jpg", template)
        # show(template)

    @staticmethod
    def get_track(distance):
        """
        模拟轨迹 假装是人在操作
        :param distance:
        :return:
        """
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
            else:
                a = -random.randint(3, 5)  # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    @staticmethod
    def urllib_download(imgurl, imgsavepath):
        """
        下载图片
        :param imgurl: 图片url
        :param imgsavepath: 存放地址
        :return:
        """
        from urllib.request import urlretrieve
        urlretrieve(imgurl, imgsavepath)

    def login_main(self):
        # ssl._create_default_https_context = ssl._create_unverified_context
        driver = self.driver
        self.open()
        time.sleep(1)
        bk_block = driver.find_element_by_xpath('//img[@id="slideBg"]')  # 大图
        web_image_width = bk_block.size
        web_image_width = web_image_width['width']
        bk_block_x = bk_block.location['x']

        slide_block = driver.find_element_by_xpath('//img[@id="slideBlock"]')  # 小滑块
        slide_block_x = slide_block.location['x']

        bk_block = driver.find_element_by_xpath('//img[@id="slideBg"]').get_attribute('src')  # 大图 url
        slide_block = driver.find_element_by_xpath('//img[@id="slideBlock"]').get_attribute('src')  # 小滑块 图片url
        slid_ing = driver.find_element_by_xpath('//div[@id="tcaptcha_drag_thumb"]')  # 滑块

        os.makedirs('./image/', exist_ok=True)
        self.urllib_download(bk_block, './image/bkBlock.png')
        self.urllib_download(slide_block, './image/slideBlock.png')
        time.sleep(0.5)
        img_bkblock = Image.open('./image/bkBlock.png')
        real_width = img_bkblock.size[0]
        width_scale = float(real_width) / float(web_image_width)
        position = self.get_postion('./image/bkBlock.png', './image/slideBlock.png')
        real_position = position[1] / width_scale
        real_position = real_position - (slide_block_x - bk_block_x)
        track_list = self.get_track(real_position + 4)

        ActionChains(driver).click_and_hold(on_element=slid_ing).perform()  # 点击鼠标左键，按住不放
        time.sleep(0.2)
        # print('第二步,拖动元素')
        for track in track_list:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
            time.sleep(0.002)
        # ActionChains(driver).move_by_offset(xoffset=-random.randint(0, 1), yoffset=0).perform()   # 微调，根据实际情况微调
        time.sleep(1)
        # print('第三步,释放鼠标')
        ActionChains(driver).release(on_element=slid_ing).perform()
        time.sleep(5)
        try:
            WebDriverWait(browser, 5).until(EC.text_to_be_present_in_element((By.ID, 'guideText'), '拖动下方滑块完成拼图'))
        except:
            print('验证成功')
            return None
        else:
            self.driver.find_element_by_id('e_reload').click()
            self.login_main()


class Spy(object):
    def __init__(self):
        global db, cursor
        today = datetime.date.today() #调用datetime模块，获取今天的日期
        self.today = today
        self.yesterday = today - datetime.timedelta(days=1)
        self.earlyday = today - datetime.timedelta(days=2)
        db = pymysql.connect(host='',
                             port='',
                             user='',
                             passwd='',
                             db='',
                             charset='utf8mb4')   #填写数据库，请预先建立好数据库，并在该数据库下建立一个表格
        cursor = db.cursor()

    def sqlinsert(self, data):   #数据库写入函数
        table = ''#表格名称
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = 'insert into {table}({keys}) values({values})'.format(table=table, keys=keys, values=values)
        try:
            db.ping(reconnect=True)
            cursor.execute(sql, tuple(data.values()))
            print('写入成功')
            db.commit()
        except:
            db.ping(reconnect=True)
            print('写入失败')
            db.rollback()

    def timedefine(self, eachinfo):   #查询时间是否为昨天
        try:
            timeinfo = eachinfo.find_element_by_class_name('ui-mr8.state').get_attribute('textContent')
        except:
            return False
        else:
            try:
                timeinfo.index('昨天')
            except:
                return False
            else:
                return True

    def timedefine2(self, eachinfo):    #查询时间是否为前天
        timeinfo = eachinfo.find_element_by_class_name('ui-mr8.state').get_attribute('textContent')
        try:
            timeinfo.index('前天')
        except:
            return False
        else:
            return True

    def timedefine3(self, eachinfo):     #查询时间是否为昨天或前天
        try:
            timeinfo = eachinfo.find_element_by_class_name('ui-mr8.state').get_attribute('textContent')
        except:
            return False
        else:
            try:
                timeinfo.index('天')
            except:
                return False
            else:
                return True

    def timechange(self, timeinit):    #将昨天更改为具体时间
        try:
            timeinit.index('天')
        except:
            sttime = str(self.today) + timeinit
        else:
            try:
                timeinit.index('昨天')
            except:
                sttime = str(self.earlyday) + ' ' + timeinit[3:] + ':00'
            else:
                sttime = str(self.yesterday) + ' ' + timeinit[3:] + ':00'
        return sttime

    def commentinfo(self, eachinfo):     #获取评论函数
        commentlist = eachinfo.find_elements_by_xpath(".//*[@data-type='commentroot']")  #获取每一个评论分块
        if len(commentlist) == 0:
            return '无评论'
        else:
            all_comment = ''
            for eachcom in commentlist:
                init_comment = eachcom.find_element_by_xpath("./div[@class='comments-item-bd']/div[1]") #获取评论分块的第一条评论
                init_comment_info = self.reset_comment(init_comment)
                reply = eachcom.find_elements_by_xpath(".//*[@data-type='replyroot']")  #获取评论分块的回复
                if len(reply) == 0:
                    all = init_comment_info + '\n'
                else:
                    reply_list = []
                    for eachreply in reply:
                        reply_list.append(self.reset_comment(eachreply))
                    reply_info = '\n'.join(reply_list)
                    all = init_comment_info + '\n' + '\t' + reply_info + '\n'
                all_comment += all
            return all_comment

    def reset_comment(self, eachcom):    #对评论的进行格式的转换
        qqnum_info = eachcom.find_element_by_class_name("nickname.name.c_tx.q_namecard")
        qqnum_link = qqnum_info.get_attribute('link')
        qqnum = re.findall('\d+', qqnum_link)[0]
        com_info = eachcom.find_element_by_class_name('comments-content').get_attribute('textContent')[:-2]
        info=com_info[:-8]
        time1=com_info[-8:]
        time2=time1.replace('昨天',str(self.yesterday))
        com_info=info+' '+'['+time2+']'
        try:  #获取评论中的图片链接
            pic = eachcom.find_element_by_xpath(".//*[@class='comments-thumbnails']")
        except:
            pic_info = ''
        else:
            pic_info = self.get_pic(pic)

        return '[' + qqnum + ']' + com_info + pic_info

    def getindex(self, eachinfo):    #获取说说内容的主干函数
        name = eachinfo.find_element_by_class_name("f-name.q_namecard").get_attribute('textContent')
        qqnum_link = eachinfo.find_element_by_class_name("f-name.q_namecard").get_attribute('link')
        qqnum = re.findall('\d+', qqnum_link)[0]
        put_time = eachinfo.find_element_by_class_name('ui-mr8.state').get_attribute('textContent')
        info_time = self.timechange(put_time)
        init_info = self.init_index(eachinfo)
        init_pic = self.pic_box(eachinfo)
        init_video = self.get_video(eachinfo)
        link = self.findherf(eachinfo)
        ct = self.is_ct(eachinfo)
        turn_id = ct[0]
        turn_info = ct[1]
        turn_qqnum = ct[2]
        likenum_st = eachinfo.find_element_by_class_name('f-like-cnt').get_attribute('textContent')
        likenum_int = int(re.findall('\d+', likenum_st)[0])
        comment = self.commentinfo(eachinfo)
        return {'name': name,
                'qqnum': qqnum,
                'info_time': info_time,
                'likenum': likenum_int,
                'init_info_text': init_info,
                'init_info_pic': init_pic,
                'init_info_video': init_video,
                'link': link,
                'turn_id': turn_id,
                'turn_qqnum': turn_qqnum,
                'turn_info': turn_info,
                'comment': comment}

    def is_ct(self, eachinfo):    #判断是否含有转发内容
        try:
            turninfo = eachinfo.find_element_by_class_name('fui-txtimg-bg')
        except:
            turn_id = 0
            turn_info = '无转发内容'
            turn_qqnum = ''
        else:
            turn_id = 1
            turn_all = self.ct_index(turninfo)
            turn_qqnum = turn_all[0]
            turn_info = turn_all[1]
        return [turn_id, turn_info, turn_qqnum]

    def findherf(self, eachinfo):      #判断是否含有链接，例如微信内容分享
        try:
            link = eachinfo.find_element_by_xpath(".//*[contains(@data-clicklog,'pic_jump')]")
        except:
            return ''
        else:
            linki = link.get_attribute('href')
            return linki

    def init_index(self, eachinfo):    #获取说说原创内容
        try:
            init_info1 = eachinfo.find_element_by_class_name('f-info')
        except:
            init_info = '无原创内容'
        else:
            try:
                unfolf_info = eachinfo.find_element_by_class_name('f-info.qz_info_complete')
            except:
                init_info = init_info1.get_attribute('textContent')
            else:
                init_info = unfolf_info.get_attribute('textContent')[:-2]
        return init_info

    def ct_index(self, eachinfo):     #获取转发部分的内容
        try:
            textbox = eachinfo.find_element_by_class_name('txt-box').get_attribute('textContent').replace('\t','')
        except:
            imgbox = eachinfo.find_element_by_class_name('img-item')
            imglink = self.get_pic(imgbox)
            return imglink
        else:
            try:
                unfold = eachinfo.find_element_by_class_name("txt-box.qz_info_complete")
            except:
                pass
            else:
                textbox = unfold.get_attribute('textContent')[:-2]

            qqnum_link = eachinfo.find_element_by_class_name("nickname.name.c_tx.q_namecard").get_attribute('link')
            qqnum = re.findall('\d+', qqnum_link)[0]
            imgbox = eachinfo.find_element_by_class_name('img-box')
            imglink = self.get_pic(imgbox)
            return [qqnum, textbox + '\n' + imglink]

    def get_pic(self, img):    #获取图片链接
        imglist = img.find_elements_by_tag_name('img')
        srclist = []
        for i in imglist:
            imglink = i.get_attribute('src')
            srclist.append(imglink)
        return '\n'.join(srclist)

    def get_video(self, vid): #获取视频链接
        videolist = vid.find_elements_by_tag_name('video')
        if len(videolist) == 0:
            return ''
        else:
            srclist = []
            for i in videolist:
                vidlink = i.get_attribute('src')
                srclist.append(vidlink)
            return '\n'.join(srclist)

    def pic_box(self, eachinfo):  #获取好友原创内容的图片
        srclist = []
        picbox = eachinfo.find_elements_by_xpath(
            ".//*[contains(@class,'fui-txtimg') and not(contains(@class,'fui-txtimg-bg'))]/div[contains(@class,'img-box')]/a")
        if len(picbox) == 0:
            return ''
        else:
            for i in picbox:
                ii = i.find_element_by_tag_name('img')
                imglink = ii.get_attribute('src')
                srclist.append(imglink)
            return '\n'.join(srclist)

    def page(self): #获取网页源码中当前的页数
        pagelist = browser.find_element_by_xpath(".//*[@class='feed_page_container']/ul[@data-page]")
        pageint = int(pagelist.get_attribute('data-page'))
        return pageint

    def fresh(self):  #刷新页面
        li1 = self.page()
        li2 = li1 + 3
        while True:
            li1 = self.page()
            browser.execute_script("window.scrollBy(0, 1000)")
            time.sleep(3)
            if li1 == li2:
                break

    def main(self):
        while True:
            fold = browser.find_elements_by_xpath("//a[@data-cmd='qz_toggle']")
            if len(fold) != 0:
                for eachfold in fold:
                    browser.execute_script("arguments[0].click();", eachfold)
                    time.sleep(2)

            infolist = browser.find_element_by_class_name('feed_page_container').find_elements_by_xpath(
                ".//*[contains(@class,'f-s-s') and not(contains(@class,'f-single-biz'))]")
            if self.timedefine3(infolist[-1]) == False:
                self.fresh()
                time.sleep(2)
                continue

            for i in range(len(infolist)):
                eachinfo = infolist[i]
                if self.timedefine(eachinfo) == True:
                    alli = self.getindex(eachinfo)
                    self.sqlinsert(alli)
                    # infolist = browser.find_element_by_class_name('feed_page_container').find_elements_by_xpath(
                    #     "//*[contains(@class,'f-s-s') and not(contains(@class,'f-single-biz'))]")

            if not self.timedefine2(infolist[-1]):
                self.fresh()
                time.sleep(2)
                continue
            else:
                break
        cursor.close()
        db.close()


c = Login()
c.login_main()
time.sleep(5)
browser = c.driver
browser.execute_script("window.scrollBy(0, 800)")
q = Spy()
q.main()
print('Finish!')
