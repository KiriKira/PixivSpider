from bs4 import BeautifulSoup
import requests
import re
import time
from tomorrow import threads

class PixivSpider(object):
    url4GetLogIn = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    param4GetLogIn = {
        'lang': 'zh',
        'source': 'pc',
        'view_type': 'page',
        'ref': 'wwwtop_accounts_index',
    }
    url4LogIn = 'https://accounts.pixiv.net/api/login?lang=zh'
    datas4LogIn = {
        'pixiv_id': '',
        'password': '',
        'captcha': '',
        'g_recaptcha_response': '',
        'post_key': '',
        'source': 'pc',
        'ref': 'wwwtop_accounts_index',
        'return_to': 'https://www.pixiv.net/'
    }

    url4Daily = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust'
    param4Daily = {
        'mode': 'daily',
        'content': 'illust'
    }

    url4Page = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="

    url4Manga = "https://www.pixiv.net/member_illust.php?mode=manga&illust_id="

    head4Pic = {
        'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,en-US;q=0.2',
        'referer': '',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    def __init__(self, Username, Password, Path):
        self.username = Username
        self.password = Password
        self.path = Path
        self.datas4LogIn['pixiv_id'] = self.username
        self.datas4LogIn['password'] = self.password
        self.rq = requests.session()
        self.dataIDlist = []

    def log_in(self):
        res = self.rq.request('GET', url=self.url4GetLogIn, params=self.param4GetLogIn, headers=self.head)
        pattern = re.compile(r'name="post_key" value="(.*?)">')
        r = pattern.findall(res.text)
        self.datas4LogIn['post_key'] = r[0]

        self.rq.request('POST', url=self.url4LogIn, data=self.datas4LogIn, headers=self.head)

    def get_id(self):
        result = self.rq.request('GET', url=self.url4Daily, params=self.param4Daily, headers=self.head)
        bs = BeautifulSoup(result.text, 'lxml')
        for item in bs.find_all('section', class_="ranking-item"):
            self.dataIDlist.append(item['data-id'])
        print(self.dataIDlist)

    def pre(self):
        self.log_in()
        self.get_id()

    @threads(8)
    def download_One(self,originimgurl,headers):
        return requests.get(originimgurl,headers=headers)

    def get_pic(self):
        for ID in self.dataIDlist:
            time.sleep(2)
            page = self.rq.request("GET", url=self.url4Page + ID, headers=self.head)
            soup = BeautifulSoup(page.text, 'lxml')
            try:
                originimgurl = soup.find('img', class_="original-image")['data-src']
                header = self.head4Pic
                header['referer'] = self.url4Page + ID
                pic = self.download_One(originimgurl, headers=header)
                with open(self.path + ID + '.jpg', 'wb') as f:
                    f.write(pic.content)
                print("Succeed With " + ID)
            except:
                mangaList = []
                manga = self.rq.request("GET", url=self.url4Manga + ID, headers=self.head)
                soup = BeautifulSoup(manga.text, 'lxml')
                for item in soup.find_all('img',class_="image ui-scroll-view"):
                    mangaList.append(item['data-src'])
                header = self.head4Pic
                header['referer'] = self.url4Manga + ID
                for picture in mangaList :
                    pic = self.download_One(picture, headers=header)
                    with open(self.path + ID + '_p' + str(mangaList.index(picture)) + '.jpg', 'wb') as f:
                        f.write(pic.content)
                print("Succeed With " + ID + "(Manga)")

        print("Done Successfully!")




Username = input('输入用户名\n')
Password = input('输入密码\n')
Path = input('输入希望保存的路径(以\\或/结尾)(Windows系统记得用双反斜杠)\n')

ps = PixivSpider(Username, Password, Path)
ps.pre()
ps.get_pic()
