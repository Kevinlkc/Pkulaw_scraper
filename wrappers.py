from ast import literal_eval  # convert string to list
import time
import random
import numpy as np
import re
import pandas as pd

# Get a list for provinces
provinces = [province.replace('省', '') for province in '河北省、山西省、辽宁省、吉林省、黑龙江省、江苏省、浙江省、安徽省、福建省、江西省、山东省、河南省、\
湖北省、湖南省、广东省、海南省、四川省、贵州省、云南省、陕西省、甘肃省、青海省、台湾省'.split('、')] + ['内蒙古', '广西', '西藏', '宁夏', '新疆']\
+ ['上海', '北京', '重庆', '天津', '香港', '澳门']
# len(provinces) = 34
key_word = ['试点']


def examine_n(dataset, all_text=False, index=-2):
    if index == -2:
        index = random.choice(range(np.shape(dataset)[0]))

    def print_related_text(text):
        for paragraph in text:
            if any([paragraph.find(key) != -1 for key in key_word]):
                print(paragraph)

    def print_all_text(text):
        for paragraph in text:
            print(paragraph)

    print(dataset.iloc[index]['标题'])
    print(dataset.iloc[index]['落地政策'], dataset.iloc[index]['试点范围'])
    print('')
    if isinstance(dataset.iloc[index]['正文'], str):
        if all_text:
            print_all_text(dataset.iloc[index]['正文'].split('\n'))
        else:
            print_related_text(dataset.iloc[index]['正文'].split('\n'))
    else:
        if all_text:
            print_all_text(dataset.iloc[index]['正文'])
        else:
            print_related_text(dataset.iloc[index]['正文'])


def filter_by_dept(dept, dataset):
    return dataset.loc[[dept in literal_eval(d) for d in dataset['发布部门']]]


def filter_by_year(value, dataset, key='year'):
    if key == 'year':
        yr = [time.strptime(d).tm_year for d in dataset['发布日期']]
        return dataset.loc[yr == value]
    elif key == 'month':
        month = [time.strptime(d).tm_mon for d in dataset['发布日期']]
        return dataset.loc[month == value]
    else:
        assert False, 'Unidentified Key'


def filter_by_effect(effect: list, dataset):
    return dataset.loc[[e in effect for e in dataset['效力级别']]]


def find_related(key: str, df):
    return df[df['标题'].find(key) != -1]


def get_paragraph(doc):
    """convert from raw text to a list containing paragraphs"""
    return doc.split('\n')


class Policy:
    """
    IMPORTANT: This Class is Defined Based on the .cn Website
    """
    def __init__(self, soup):
        self.title = self.get_title(soup)
        self.info = self.get_info(soup)
        self.text = self.get_text(soup)
        self.info['标题'] = self.title
        self.info['正文'] = self.get_rawtext()
        self.info['有效'] = self.mentioned()

    def get_title(self, soup):
        """Return Type: str"""
        assert len(soup.find_all('td', align="center", colspan="2", style="width:100%;")) == 1
        title = soup.find('td', align="center", colspan="2", style="width:100%;").text
        if re.search('[a-zA-Z]', title):
            title = title[:re.search('[a-zA-Z]', title).start()]
        if title.endswith('[失效]'):
            title = title[:-4]
        return title

    def get_info(self, soup):
        """Return Type: dict"""
        names = ['发布部门', '发文字号', '发布日期', '实施日期', '时效性', '效力级别', '法规类别']
        soups = soup.find_all('td', style="width:50%;")
        info = {}
        for name in names:
            flag = False
            for soup_ in soups:
                if soup_.text.find(name) != -1:
                    info[name] = soup_.text[6:].strip()
                    flag = True
            if not flag:
                info[name] = 'None'
        info['发布部门'] = info['发布部门'].split('，')
        return info

    def get_text(self, soup):
        """Return Type: list"""
        # return a list of strings, each paragraph is an entry in the list
        raw_text = soup.find('td', class_="Content", colspan="2", id="fulltext", style="width:100%;").text
        assert isinstance(raw_text, str)
        raw_text = raw_text.replace('\xa0', '').replace('\u3000', '')
        return [par for par in raw_text.split('\n') if par != '']

    def mentioned(self):
        # Check if keywords appear.
        for paragraph in self.text:
            if any([key in paragraph for key in key_word]):
                return True
        return False

    def get_rawtext(self):
        """Return Type: string"""
        rt = ''
        for paragraph in self.text:
            rt += paragraph
            rt += '\n'
        return rt


class CentralPolicy(Policy):
    def __init__(self, soup):
        Policy.__init__(self, soup)
        self.scope = self.get_scope()
        self.validity = self.is_valid()
        self.info['试点范围'] = self.scope
        self.info['落地政策'] = self.validity

    def get_scope(self):
        scope = []
        for paragraph in self.text:
            if any([province in paragraph for province in provinces]) \
                    and any([key in paragraph for key in key_word]):
                scope.extend([province for province in provinces if province in paragraph])
        return list(set(scope))

    def is_valid(self):
        # Check if it's a general statement or a binding policy. If True, extract its scope
        # Exclude normative documents
        if self.info['效力级别'].find('规范') != -1:
            return False
        # Exclude general statements
        if self.title.endswith('的意见') or self.title.endswith('的意见[失效]') or self.title.endswith('的若干意见'):
            return False
        if self.title.find('的报告') != -1 and self.title.find('关于') != -1:
            return False
        # Exclude approval for bond/equity/insurance-issuing
        if (self.title.startswith('中国证券监督管理委员会') or self.title.startswith('中国证监会')
            or self.title.startswith('中国保险监督管理委员会') or self.title.startswith('中国银监会')) \
                and self.title.endswith('批复'):
            return False
        if self.title.find('国债') != -1:
            return False
        # Exclude response to proposals
        if self.title.endswith('答复') and self.title.find('会议') != -1:
            return False
        # Extract the scope
        flag = False
        for paragraph in self.text:
            if any([province in paragraph for province in provinces]) \
                    and any([key in paragraph for key in key_word]):
                flag = True
        return flag


def get_keyword(title):
    """
    :param title: policy title (str)
    :return: keyword (str)
    """
    matchObj = re.match('(.*)关于(.*)的(.*)', title)
    if matchObj:
        title = matchObj.group(2)
    matchObj2 = re.match(r'(.*)“(.*)”(.*)', title)
    if matchObj2:
        title =  matchObj2.group(2)
    matchObj3 = re.match('(.*)《(.*)》(.*)', title)
    if matchObj3:
        title =  matchObj3.group(2)
    title = re.sub(u"\\(.*?\\)", "", title)
    prefix = ['印发', '开展', '支持', '加强', '做好', '公布', '设立', '完善', '推进']
    suffix = ['试点', '工作', '暂行']
    year = [str(x)+'年度' for x in range(1970, 2020)] + [str(x)+'年' for x in range(1970, 2020)] + [str(x) for x in range(1970, 2020)]
    for y in year:
        if title.find(y) != -1:
            title = title.replace(y, '')
    start, end = 0, len(title)
    for p in prefix:
        if title.find(p) != -1:
            start = max(start, title.find(p)+2)
    for s in suffix:
        if title.rfind(s) != -1:
            end = min(end, title.rfind(s))
    title = title[start: end]
    return title


class CentralPolicy_V6:
    names = ['发布部门', '发文字号', '发布日期', '实施日期', '时效性', '效力级别', '法规类别', '失效依据']

    def __init__(self, soup):
        self.info = {}
        try:
            self.info['标题'] = soup.find('h2', class_='title').text.strip()
        except:
            pass
        try:
            self.info['gid'] = soup.find('h2', class_='title').find('a')['audiogid']
        except:
            pass

        try:
            for subsoup in soup.find('div', class_='fields').find_all('li'):
                try:
                    result = subsoup['title']
                except KeyError:
                    result = subsoup.find('span')['title']
                self.info[subsoup.find('strong').text[:-1]] = result
        except:
            pass

        try:
            self.text = soup.find('div', id="divFullText", class_="fulltext").text.replace('\u3000', '').strip()
        except:
            self.text = 'Missing'
        self.info['正文'] = self.text

        try:
            self.info['失效依据'] = soup.find('div', class_='fields').find('a', class_='alink').text
        except:
            pass
        try:
            self.info['后续文件'] = str(self.get_expiration(soup))
        except:
            pass
        try:
            self.info['url'] = soup.find('input', id="ArticleUrl", type="hidden")['value']
        except:
            pass
        self.info['引用'] = []
        self.info['被引用'] = []
        try:
            cor_info = soup.find_all('div', class_="correlation-info")
            for part in cor_info:
                if part.find('span', anchor='anchor').find('a')['name'] == 'association_1':
                    it = part.find_all('li')
                    for item in it:
                        self.info['引用'].append(
                            [item.find('a', target = '_blank').text.strip(), 
                            item.find('a', target = '_blank')['href']]
                        )
                elif part.find('span', anchor='anchor').find('a')['name'] == 'association_2':
                    it = part.find_all('li')
                    for item in it:
                        self.info['被引用'].append(
                            [item.find('a', target = '_blank').text.strip(), 
                            item.find('a', target = '_blank')['href']]
                        )
        except:
            pass

    def get_expiration(self, soup):
        time = [x.text.strip() for x in soup.find_all('span', class_='time')]
        titles = [x.text for x in soup.find_all('a', class_='lawChange', target='_blank') if x.text != '比对']
        hrefs = [x['href'] for x in soup.find_all('a', class_='lawChange contrast', target='_blank')]
        title = soup.find('h2', class_='title').text.strip()
        title = title[:title.find('\r')]
        titles.append(title)
        return [time, titles, hrefs]



