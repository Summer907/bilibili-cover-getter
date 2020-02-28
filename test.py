from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as BS
import time, requests, os, sys

print("--------bilibili视频信息获取----------")
search = input('请输入关键字：')
wanted_pages = int(input('请输入爬取的页数，每页20个视频（默认为1）：'))
print('--请把浏览器窗口拖到右边以获得最佳体验--\n'*3)
time.sleep(3)

# 启动驱动
driver = webdriver.Chrome(executable_path='chromedriver')

# 声明页面
first_url = 'https://www.bilibili.com/'
driver.get(url=first_url)

# 搜索关键字
tag = driver.find_element_by_xpath('//*[@id="nav_searchform"]/input')
tag.clear()
tag.send_keys(search)
action = ActionChains(driver)
action.send_keys(Keys.ENTER).perform()
time.sleep(5)

# 切换到新标签页
n = driver.window_handles
driver.switch_to.window(n[1])

page = 1
success = 0
fail = 0


# 定义爬取函数
def get_info(m):
    global success, fail

    # 滚屏
    height = 0
    for i in range(1, 10):
        js = 'var q=document.documentElement.scrollTop=%d' % height
        height += 800
        driver.execute_script(js)
        time.sleep(0.1)

    soup = BS(driver.page_source, 'html.parser')
    results = soup.find_all('li', class_='video-item matrix')
    for index, i in enumerate(results):
        print('*' * 100)
        print('第%d页第' % m + str(index + 1) + '个视频：')

        # 获取各种属性
        info = i.find('div', class_='info')
        headline = info.find('div', class_='headline clearfix')
        tags = info.find('div', class_='tags')

        video_type = headline.span.text
        plays = tags.find('span', title="观看").text.split()[0]
        danmus = tags.find('span', title="弹幕").text.split()[0]
        date = tags.find('span', title="上传时间").text.split()[0]
        up = tags.find('span', title="up主").a.text
        up_link = 'https:' + tags.find('span', title="up主").a.attrs['href'].split('?')[0]
        title = i.a.attrs['title']
        video_link = 'https:' + i.a.attrs['href'].split('?')[0]
        img_src = 'http:' + i.a.div.div.img.attrs['src'].split('@')[0]
        av = video_link.split('video/')[1]

        # 打印各种属性
        print('类型：' + video_type)
        print('标题：' + title)
        print('播放量：' + plays)
        print('弹幕数：' + danmus)
        print('上传时间：' + date)
        print('UP主：' + up + '，个人空间：' + up_link)
        print('视频链接：' + video_link)
        print('视频封面：' + img_src)

        # 保存封面
        try:
            link = requests.get(img_src).content
            with open(str(index+20*(m-1)+1) + '--' + av + '.jpg', 'wb') as f:
                f.write(link)
                time.sleep(0.5)
                print('封面已保存到本地')
                success += 1
        except Exception as e:
            print('保存封面出错')
            print(e)
            fail += 1


# 爬取第一页
get_info(page)

# 如果要爬取的多于一页，要注意到第一页和后面的页中“下一页”按钮的Xpath是不一样的
if wanted_pages > 1:
    driver.find_element_by_xpath('//*[@id="all-list"]/div[1]/div[3]/div/ul/li[9]/button').click()
    time.sleep(1)
    page += 1
    get_info(page)

for j in range(wanted_pages-2):
    driver.find_element_by_xpath('//*[@id="all-list"]/div[1]/div[2]/div/ul/li[10]/button').click()
    time.sleep(1)
    page += 1
    get_info(page)

# 打印结果
print('*'*100)
print('成功%d个，失败%d个' % (success, fail))

# 退出驱动
driver.quit()
