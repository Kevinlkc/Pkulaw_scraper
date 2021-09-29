import requests
from bs4 import BeautifulSoup
import re
import random
# import opencv-python
import json
import time
import base64
from PIL import Image
import pandas as pd

# =========================== Please read ===============================
# Academic purpose only. Please comply with the relevant laws and regulations.
# Prepared by Kaicheng Luo @ Harvard Econ, latest update 24 Sep 2021
# For a demo of how to use the scraper, check out demo.ipynb
# =========================== Instructions ends =========================

class PkuScraper:
    # Update this cookie whenever you use it, you can also get it updated by calling __self__.set_cookie(_str)
    Cookies_V6 = 'xCloseNew=8; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1630066629,1631060463; pkulaw_v6_sessionid=0zwgpxbk10jpsexxknqg4mm1; authormes=5f8e703755203640a7baa1c56e09ce5616c7268dca732f3b39028526dff6560a10f8eedcbd05b937bdfb; Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1631061484'
    # EDITS end here!

    def __init__(self, input_t='', output_t='', version='V6'):
        assert input_t in self.input_types, 'Invalid Input Type'
        self.input_type = input_t
        assert output_t in self.output_types, 'Invalid Output Type'
        self.output_type = output_t
        assert version in self.versions, 'Invalid Version'
        self.version = version
        self.library = 'chl'
        self.keyword = ''
        self.url = []
        self.type = []
        self.dept = []
        self.effective = []
        self.class_code_key = []
        self.max_page = 100000
        self.s = requests.Session()
        self.bg = '/Users/kevin/Desktop/temp.jpg'
        self.slide = '/Users/kevin/Desktop/temp2.jpg'
        self.cd = '/Users/kevin/Desktop/temp.zip'
        self.update_dic = {}

    User_Agents = [
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
        'Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
        'Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
        'Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10',
        'Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13',
        'Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+',
        'Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0',
        'Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)',
        'UCWEB7.0.2.37/28/999',
        'NOKIA5700/ UCWEB7.0.2.37/28/999',
        'Openwave/ UCWEB7.0.2.37/28/999',
        'Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999',
        'UCWEB7.0.2.37/28/999',
        'NOKIA5700/ UCWEB7.0.2.37/28/999',
        'Openwave/ UCWEB7.0.2.37/28/999',
        'Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999'
    ]

    input_types = ['url', 'keyword', '']
    output_types = ['name', 'gid', 'titles', 'soups', '']
    versions = ['V5', 'V6']
    filters = ['central', 'local', 'laws', 'regulations', 'interpretations', 'rules',
               'local regulations', 'local government rules', 'local regulatory documents']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Host': 'www.pkulaw.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.pkulaw.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8',
        'User-Agent': random.choice(User_Agents)
    }

    lib_dict = {
        'central': 'chl',
        'local': 'lar'
    }

    type_dict = {
        '法律': 'XA01',
        '行政法规': 'XC02',
        '司法解释': 'XG04',
        '部门规章': 'XE03',
        'unspecified': '',
        '地方性法规': 'XM07',
        '地方政府规章': 'XO08',
        '地方规范性文件': 'XP08',
        '地方工作文件': 'XP10',
        '行政许可批复': 'XP11',
        '部门规范性文件': 'XE0302'
    }
    dept_dict = {
        '全国人民代表大会': '1',
        '全国人大常委会': '2',
        '国务院': '5',
        '国务院各机构': '6',
        '党中央部门机构': 'a',
        'unspecified': ''
    }
    effective_dict = {
        '现行有效': '01',
        '失效': '02',
        '已被修改': '03',
        '尚未生效': '04',
        '部分失效': '05',
        'unspecified': ''
    }

    # Debug section starts here
    headers = {
        'Cookie': Cookies_V6,
        'Origin': 'https://www.pkulaw.com',
        'Host': 'www.pkulaw.com',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': random.choice(User_Agents),
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.pkulaw.com/law/chl?Keywords=%E8%AF%81%E7%85%A7%E5%88%86%E7%A6%BB',
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-mobile': '?0'
    }

    data = {
        'Menu': 'law',
        'SearchKeywordType': 'Title',
        'MatchType': 'Exact',
        'RangeType': 'Piece',
        'Library': 'chl',
        'Pager.PageIndex': 0,
        'Keywords': '',
        'ClassCodeKey': ',,,,,,',
        'ShowType': 'Default',
        'Pager.PageSize': 10,
        'RecordShowType': 'List',
        'QueryOnClick': 'False',
        'AfterSearch': 'True',
        'GroupByIndex': 0,
        'newPageIndex': 0,
        'OrderByIndex': 4,
        'isEng': 'chinese',
        'IsSynonymSearch': "true"
    }
    # debug section ends here


    def set_input_type(self, input_t):
        assert input_t in self.input_types, 'Invalid Input Type'
        self.input_type = input_t

    def set_output_type(self, output_t):
        assert output_t in self.output_types, 'Invalid Output Type'
        self.output_type = output_t

    def set_version(self, version):
        assert version in self.versions, 'Invalid Version'
        self.version = version

    def set_filters(self, lib_, type_, dept_, effective_):
        self.library, self.type, self.dept, self.effective = lib_, type_, dept_, effective_

        def set_class_code(type, dept, effe):
            return ',' + self.type_dict[type] + ',' + self.dept_dict[dept] + ',' + self.effective_dict[effe] + ',,'

        for t in self.type:
            for d in self.dept:
                for e in self.effective:
                    self.class_code_key.append(set_class_code(t, d, e))

    def set_cookies(self, s):
        self.Cookies_V6 = s

    def set_ouput_directory(self, s):
        self.cd = s

    def edit_postform(self, dic):
        self.update_dic = dic

    def decode_page_v6(self, url):
        """
        DOCUMENT PAGE
        URL -> Soup Object
        Version: https://www.PKULaw.com.
        Scraper Detection: time.sleep(2) if the number of requests exceeds 100.
        Access Requirement: Cookies, Headers
        Output: soupObj that can be decoded by the CentralPolicy_V6 class
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'Host': 'www.pkulaw.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.pkulaw.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8',
            'Cookie': self.Cookies_V6,
            'User-Agent': random.choice(self.User_Agents)
        }
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            assert not soup.find('title').text.startswith('法律法规_北大法宝法律数据库'), 'Homepage Redirected'
            return soup
        except:
            response = requests.get(url, headers=headers)
            return BeautifulSoup(response.text, 'lxml')


    def search_page_V6(self, keyword, _debug=False, SearchKeywordType='DefaultSearch'):
        """
        SEARCH PAGE
        class_code_key
        :return: [Titles, Time, Gids, Urls]
        """
        assert self.input_type == 'keyword', 'Please specify input type: keyword'
        self.keyword = keyword
        names, times, gids, urls = [], [], [], []



        def get_one_page(page_index=0, class_code=',,,,,'):
            url = 'https://www.pkulaw.com/law/search/RecordSearch'
            headers = {
                'Cookie': self.Cookies_V6,
                'Origin': 'https://www.pkulaw.com',
                'Host': 'www.pkulaw.com',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Agent': random.choice(self.User_Agents),
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.pkulaw.com/law/chl?Keywords=%E8%AF%81%E7%85%A7%E5%88%86%E7%A6%BB',
                'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
                'sec-ch-ua-platform': '"macOS"',
                'sec-ch-ua-mobile': '?0'
            }
            data = {
                'Menu': 'law',
                'SearchKeywordType': 'Title',
                'MatchType': 'Exact',
                'RangeType': 'Piece',
                'Library': self.library,
                'Pager.PageIndex': page_index,
                'Keywords': keyword,
                'ClassCodeKey': class_code,
                'ShowType': 'Default',
                'Pager.PageSize': 10,
                'RecordShowType': 'List',
                'QueryOnClick': 'False',
                'AfterSearch': 'True',
                'GroupByIndex': 0,
                'newPageIndex': page_index,
                'OrderByIndex': 4,
                'isEng': 'chinese',
                'IsSynonymSearch': "true"
            }
            data.update(self.update_dic)
            response = requests.post(url, headers=headers, data=data)
            return BeautifulSoup(response.text, 'lxml')

        def get_count(soup):
            try:
                return int(soup.find("span" ,class_="total").find('strong').text)
            except:
                return 0

        def extract_info(soup):
            for a in soup.find_all('div', class_='block'):
                try:
                    content = a.find('a', target="_blank", flink="true")
                    names.append(content.text)
                    matchObj = re.match(r'/' + self.library + '/(.*).html(.*)', content['href'])
                    if matchObj:
                        gids.append(matchObj.group(1))
                        urls.append('https://www.pkulaw.cn/fulltext_form.aspx?Db=chl&Gid=' + matchObj.group(1))
                except:
                    pass

        for class_code_key in self.class_code_key:
            temp_soup = get_one_page(page_index=0, class_code=class_code_key)
            if _debug == True:
                return temp_soup

            max_page = (get_count(temp_soup)-1) // 10 + 1
            if max_page > 20:
                print(min(max_page, self.max_page))
                print(self.keyword)
                break
            for page in range(min(max_page, self.max_page)):
                soup = get_one_page(page_index=page, class_code=class_code_key)
                extract_info(soup)

        return [names, times, urls, gids]

    # Step 2. Download the files according to their id's.
    # You can download up to 10, at least. Their id's shall be joined with commas. E.g. "aaxx11,bbyy22,cczz33" No blank space needed.
    def download(self, gids):
        '''
            将给定的文本压缩包下载到给定位置
            :param gids: 待下载文本的gids
        '''
        # 下载链接
        url = 'https://www.pkulaw.com/Tool/BatchDownloadFulltext'

        headers = {
            #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            #'Accept-Encoding': 'gzip, deflate, br',
            #'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8',
            #'Cache-Control': 'max-age=0',
            #'Connection': 'keep-alive',
            #'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.Cookies_V6,
            #'Host': 'v6downloadservice.pkulaw.com',
            #'Upgrade-Insecure-Requests': '1',
            #'Sec-Fetch-Dest': 'document',
            #'Sec-Fetch-Mode': 'navigate',
            #'Sec-Fetch-Site': 'same-origin',
            #'Sec-Fetch-User':'?1',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999'}

        form_data = {
            'typeName': "fullHyper",
            'keepFields': "true",
            'keepFblxInFulltext': "true",
            'keepRelatedFile': "true",
            'library': self.library,
            'flag': "undefined",
            'gids': gids,
            'curLib': self.library,
            'downloadType': 'DownloadFullText',
            'currentUrl': "https://pkulaw.com"
        }

        # 下载并存储压缩包
        resp = requests.post(url=url, data=form_data, headers=headers)
        with open(self.cd, 'wb') as f:
            f.write(resp.content)

    def get_time_distribution(self, keyword, begin_year):
        # 1. 首先，get_one_page() 成员函数返回给定关键词、页数、年份后，全文搜索的soup对象。
        # 2. 再调用 get_count() 成员函数返回页数与条目数量。
        # 3. 将这一数据存储在list中返回
        years_list = range(begin_year, 2021)

        def get_one_page(page_index=0, class_code=',,,,,', year=2020):
            url = 'https://www.pkulaw.com/law/search/RecordSearch'
            headers = {
                'Cookie': self.Cookies_V6,
                'Origin': 'https://www.pkulaw.com',
                'Host': 'www.pkulaw.com',
                'User-Agent': random.choice(self.User_Agents),
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.pkulaw.com/law/chl?Keywords=%E8%AF%81%E7%85%A7%E5%88%86%E7%A6%BB'
            }
            data = {
                'Menu': 'law',
                'SearchKeywordType': 'Fulltext',
                'MatchType': 'Exact',
                'RangeType': 'Piece',
                'Library': self.library,
                'Pager.PageIndex': page_index,
                'Keywords': keyword,
                'ClassCodeKey': class_code + str(year),
                'ShowType': 'Default',
                'Pager.PageSize': 10,
                'QueryOnClick': 'False',
                'AfterSearch': 'True',
                'GroupByIndex': 0,
                'newPageIndex': page_index,
                'OrderByIndex': 4,
                'IsSynonymSearch': "true"
            }
            response = requests.post(url, headers=headers, data=data)
            return BeautifulSoup(response.text, 'html5lib')

        def get_count(soup):
            try:
                return int(soup.find('h3').find('span').text)
            except:
                return 0

        final_lst = []

        for year in years_list:
            time.sleep(1)
            num = 0
            num += get_count(get_one_page(0, ',,,,,', year))
            final_lst.append([year, num])

        return final_lst
    

    def get_locality_id(self):
        url = "https://pkulaw.com/Tool/SingleClassResult"
        headers = self.headers
        data = {
            'library': 'lar',
            'className': 'IssueDepartment',
            'Aggs': '{"RelatedPrompted":"","EffectivenessDic":"","SpecialType":"","IssueDepartment":"","TimelinessDic":"","Category":"","IssueDate":""}',
            'keyword': '',
            'ClassFlag': 'lar',
            'KeywordType': 'Title',
            'MatchType': 'Exact'
        }
        response = requests.post(url, headers=headers, data=data)
        return response

    def get_category_dist(self, _debug=False):
        url = "https://pkulaw.com/Tool/SingleClassResult"
        headers = self.headers
        data = {
            'library': 'lar',
            'className': 'Category',
            'Aggs': '{"RelatedPrompted":"","EffectivenessDic":"","SpecialType":"","IssueDepartment":"","TimelinessDic":"","Category":"","IssueDate":""}',
            'keyword': '',
            'ClassFlag': 'lar',
            'KeywordType': 'Title',
            'MatchType': 'Exact'
        }
        if _debug:
            data.update(self.update_dic)

        response = requests.post(url, headers=headers, data=data)
        return response

    def search_largescale(self, keyword):
        # The idea is: first ask for a json response regarding what are the entities that issued those documents; then do searchings.
        # Step 1:
        url = "https://pkulaw.com/Tool/SingleClassResult"
        headers = self.headers
        data = {
            'library': 'lar',
            'className': 'IssueDepartment',
            'Aggs': '{"RelatedPrompted":"","EffectivenessDic":"","SpecialType":"","IssueDepartment":"","TimelinessDic":"","Category":"","IssueDate":""}',
            'keyword': keyword,
            'ClassFlag': 'lar',
            'KeywordType': 'Title',
            'MatchType': 'Exact'
        }
        response = requests.post(url, headers=headers, data=data)
        jsonString = response.text.replace(r'\r', '').replace(r'\n', '')
        dict_list = json.loads(jsonString)
        dict_list = pd.DataFrame(dict_list)
        id_list = dict_list['id'].unique()
        id_list = [x for x in id_list if len(x) <= 3] # Breaking it down into provincial searches shall be enough
        print(id_list)
        # Step 2:
        lst = [[], [], [], []]
        for id_ in id_list:
            self.edit_postform({'Aggs.IssueDepartment': id_})
            templst = self.search_page_V6(keyword)
            lst = [lst[x] + templst[x] for x in range(0, 4)]
            if len(lst[0]) > 0:
                print('Success')
            else:
                print('Failed to scrape')
        return lst

# =========================== Dividing line for testing functions ===========================
    # Those are the beta version that still cannot run. 
    def find_position(self):
        slider = cv2.imread(self.slide, 0)
        captcha = cv2.imread(self.bg, 0)

        result = cv2.matchTemplate(captcha, slider, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        return max_loc[0]

    def _generate_track(self, target: int) -> str:
        """
        根据拿到的答案生成相应的轨迹
        :param target: 想要生成的轨迹的横坐标
        :return str: 返回计算好的轨迹
        """
        template_track = [1, 3, 4, 6, 7, 9, 10, 11, 12, 13, 15, 16, 17, 18,
                          19, 20, 21, 23, 23, 25, 26, 27, 28, 29, 30, 31,
                          32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47]
        threshold = max(template_track)
        scale = target // threshold
        if target > threshold:
            num_track = template_track[:3] + [t * scale for t in template_track]
        else:
            num_track = [t for t in template_track if t < target]

        # 经过上面处理的轨迹最后停下来的位置如果不是目标点，调整到终点
        last_num = num_track[-1]
        if target != last_num:
            gap = target - last_num
            num_track.append(last_num + gap // 2)
            num_track.append(target)

        # 数字轨迹处理好了以后就开始处理时间戳了
        start_time = int(time.time() * 1000)
        time_track = [start_time] * len(num_track)
        for index in range(1, len(num_track)):
            time_track[index] = time_track[index - 1] + random.randint(17, 27)

        # 拼接数字轨迹和时间轨迹
        result = ""
        for i, t in zip(num_track, time_track):
            if result:
                result += "|"
            result += f"{i},{t}"

        return result

    def _get_captcha(self):
        """
        向服务器发送请求拿到一张验证码
        """
        url = "https://www.pkulaw.com/VerificationCode/GetVerifiCodeResult"
        form_data = {
            'act': 'getcode',
            'spec': '300*200'
        }

        headers = self.headers.copy()
        headers.update({
            'Host': 'www.pkulaw.com',
            'Origin': 'https://www.pkulaw.com',
            'Referer': 'https://www.pkulaw.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': random.choice(self.User_Agents),
            'Cookies': self.Cookies_V6
        })

        resp = json.loads(self.s.post(url=url, headers=headers, data=form_data).json())

        with open(self.slide, "wb") as f:
            f.write(base64.b64decode(resp.get("small")[21:]))
        with open(self.bg, "wb") as f:
            f.write(base64.b64decode(resp.get("normal")[21:]))
        print("成功地从服务器获取到验证码！")

        # 从服务拿到的图片是错位的图片，要进行复原
        # Todo： 直接使用IO流读取图片，不存盘减少IO
        bg = Image.open(self.bg, 'r')
        img_x, img_y = bg.size
        new_img = Image.new('RGB', (img_x, img_y))
        split_width = img_x // 10
        split_height = img_y // 2

        # 代码转换自`VerificationCode.js`
        order_array = [int(t) for t in resp['array'].split(",")]

        for index in range(len(order_array)):
            # index代表拼接后图片上的序号
            # num代表拼接前图片上的序号
            num = order_array.index(index)

            # 还原后的坐标点
            y = split_height if index > 9 else 0
            x = split_width * (index - 10) if index > 9 else split_width * index

            # 还原前的坐标点
            origin_y = split_height if num > 9 else 0
            origin_x = split_width * (num - 10) if num > 9 else split_width * num

            # 从还原前的坐标点处切图像，拼接到还原后的坐标点上
            new_img.paste(bg.crop((origin_x, origin_y, origin_x + split_width, origin_y + split_height)),
                          (x, y, x + split_width, y + split_height))

        new_img.save(self.bg)

    def validate(self):
        self._get_captcha()
        final_position = self.find_position()
        track = self._generate_track(final_position)
        form_data = {
            'act': 'check',
            'point': final_position,
            'timespan': '1856',
            'datelist': track
        }

        headers = self.headers.copy()
        headers.update({
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        url = 'https://www.pkulaw.com/VerificationCode/GetVerifiCodeResult'
        requests.post(url=url, headers=headers, data=form_data)
        return final_position
