import re
import os
import sys
import time
import random
import logging
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

#print(sys.getdefaultencoding())
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(filename)s[line:%(lineno)d] %(message)s', datefmt='%a %d/%m/%Y %H:%M:%S', filename='myapp.log', filemode='w')


page_start = 6
page_end = 10

g_cookie = {}


def format(str):
    return '"' + str + '",'


def set_cookie(set_cookie):
    logging.info("receive cookie:%s", set_cookie)
    global g_cookie
    aliyungf_tc = re.match(r'.*aliyungf_tc=(.*?;)', set_cookie)
    if aliyungf_tc:
        g_cookie["aliyungf_tc"] = aliyungf_tc.group(1)
        logging.info("update Cookie aliyungf_tc:%s", g_cookie["aliyungf_tc"])

    csrfToken = re.match(r'.*csrfToken=(.*?;)', set_cookie)
    if csrfToken:
        g_cookie["csrfToken"] = csrfToken.group(1)
        logging.info("update Cookie csrfToken:%s", g_cookie["csrfToken"])

    _csrf = re.match(r'.*_csrf=(.*?;)', set_cookie)
    if _csrf:
        g_cookie["_csrf"] = _csrf.group(1)
        logging.info("update Cookie _csrf:%s", g_cookie["_csrf"])

    OA = re.match(r'.*OA=(.*?;)', set_cookie)
    if OA:
        g_cookie["OA"] = OA.group(1)
        logging.info("update Cookie OA:%s", g_cookie["OA"])

    _csrf_bk = re.match(r'.*_csrf_bk=(.*?;)', set_cookie)
    if _csrf_bk:
        g_cookie["_csrf_bk"] = _csrf_bk.group(1)
        logging.info("update Cookie _csrf_bk:%s", g_cookie["_csrf_bk"])

    TYCID = re.match(r'.*TYCID=(.*?;)', set_cookie)
    if TYCID:
        g_cookie["TYCID"] = TYCID.group(1)
        logging.info("update Cookie TYCID:%s", g_cookie["TYCID"])

    uccid = re.match(r'.*uccid=(.*?;)', set_cookie)
    if uccid:
        g_cookie["uccid"] = uccid.group(1)
        logging.info("update Cookie uccid:%s", g_cookie["uccid"])



def get_cookie():
    aliyungf_tc = "aliyungf_tc=" + g_cookie["aliyungf_tc"] + " "
    csrfToken = "csrfToken=" + g_cookie["csrfToken"] + " "
    _csrf = "_csrf=" + g_cookie["_csrf"] + " "
    OA = "OA=" + g_cookie["OA"] + " "
    _csrf_bk = "_csrf_bk=" + g_cookie["_csrf_bk"] + " "
    TYCID = "TYCID=" + g_cookie["TYCID"] + " "
    uccid = "uccid=" + g_cookie["uccid"] + " "
    Hm_lvt = "Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1505217802," + str(int(time.time())) + "; "
    Hm_lpvt = "Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=" + str(int(time.time())+8)
    cookie = aliyungf_tc + csrfToken + _csrf + OA + _csrf_bk + TYCID + uccid + Hm_lvt + Hm_lpvt
    logging.info("get cookie:%s", cookie)
    return cookie


def get_one_page(page_url):
    logging.info("正在获取数据(%s)...", page_url)
    headers = {}
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Accept-Language"] = "zh-CN,zh;q=0.8"
    headers["Connection"] = "keep-alive"
    headers["Host"] = "shenzhen.tianyancha.com"
    headers["Upgrade-Insecure-Requests"] = "1"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"

    global g_cookie
    if g_cookie:
        headers["Cookie"] = get_cookie()

    try:
        time.sleep(random.randint(5, 8))
        g_response = requests.get(page_url, headers=headers)
        set_cookie(g_response.headers["Set-Cookie"])

        logging.info("g_response.status_code:%d", g_response.status_code)

        if g_response.status_code == 200:
            return g_response.text
    except RequestException:
        logging.info("RequestException")
    exit()


def get_search_page(page_index):
    logging.info("正在获取第 %d 页数据...", page_index)
    search_url_start = "https://shenzhen.tianyancha.com/search"
    search_url_end = "?key=%E6%95%99%E8%82%B2%E5%9F%B9%E8%AE%AD"
    if page_index == 1:
        return get_one_page(search_url_start + search_url_end)
    return get_one_page(search_url_start + "/p" + str(page_index) + search_url_end)


def get_company_url_list(search_page_content):
    soup = BeautifulSoup(search_page_content, "html.parser")
    element = soup.find_all(href=re.compile('https://www.tianyancha.com/company/'), target=True)
    company_url_list = []
    for link in element:
        href = link.get("href")
        company_url_list.append(href)
        logging.info("company_url:%s", href)
    if not company_url_list:
        logging.info("company_url_list为空，退出")
        exit()
    return company_url_list


def get_company_detail_page(company_url):
    return get_one_page(company_url)


def get_company_info(company_page_content):
    soup = BeautifulSoup(company_page_content, "html.parser")

    company_info_1 = soup.find_all("div", class_="company_header_width")[0]
    company_name = re.match(r'.*<span class="f18 in-block vertival-middle">(.*?)</span>', str(company_info_1)).group(1)
    company_human_phone = re.match(r'.*<span>电话：</span><span>(.*?)</span>', str(company_info_1)).group(1)
    company_address = re.match(r'.*<span .*?>地址：</span><span .*?>(.*?)</span>', str(company_info_1)).group(1)
    company_website_tmp = re.match(r'.*<span>网址：</span><span>(.*?)</span>', str(company_info_1))
    if not company_website_tmp:
        company_website_tmp = re.match(r'.*<span>网址：</span><a .*?>(.*?)</a>', str(company_info_1))
    company_website = company_website_tmp.group(1)

    company_info_2 = soup.find_all("div", class_="human-top")[0]
    company_human_name = re.match(r'.*<a .*?>(.*?)</a>', str(company_info_2)).group(1)

    company_info_3 = soup.find_all("td", style="padding: 0;")[0]
    company_register_capital = re.match(r'.*注册资本.*<div .*?getRegCapitalWithUnit.*?>(.*?)</div>', str(company_info_3)).group(1)
    company_regiter_time = re.match(r'.*注册时间.*?<div .*?"baseinfo-module-content-value".*?>(.*?)</div>', str(company_info_3)).group(1)

    company_info_4 = soup.find_all("span", class_="js-shrink-container")[0]
    company_business_scope = re.match(r'.*<span .*?"showDetail".*?>(.*?)</span>', str(company_info_4)).group(1)

    content = format(company_name) + format(company_human_name) + format(company_human_phone) + format(company_regiter_time) + format(company_register_capital) + format(company_website) + format(company_address) + format(company_business_scope) + "\n"

    logging.info("result:%s", content)
    return content


def save_to_file(content=None, file_path=None, access_mode="a"):
    logging.info("file_path:%s", file_path)
    if (content) and (file_path):
        fsock = open(file_path, access_mode, encoding='utf-8')
        fsock.write(content)
        fsock.close()


def save_page(content=None, page_index=0, page_url=None):
    dst_path = os.path.abspath('.') + "/page" + str(page_index)
    isExists=os.path.exists(dst_path)
    if not isExists:
        os.makedirs(dst_path)
    file_path = ""
    if page_url == None:
        file_path = dst_path + "/page" + str(page_index) + ".html"
    else:
        company_flag = re.match(r"https://www.tianyancha.com/company/(.*)", page_url).group(1)
        file_path = dst_path + "/" + company_flag + ".html"
    save_to_file(content, file_path)


def save_result(content=None):
    file_path = os.path.abspath('.') + "/result.csv"
    save_to_file(content, file_path)


def Process():
    global page_start
    global page_end
    for page_index in range(page_start, page_end + 1):
        search_page_content = get_search_page(page_index)
        save_page(content=search_page_content, page_index=page_index)
        company_url_list = get_company_url_list(search_page_content)
        for company_url in company_url_list:
            company_page_content = get_company_detail_page(company_url)
            save_page(content=company_page_content, page_index=page_index, page_url=company_url)
            company_info = get_company_info(company_page_content)
            save_result(company_info)

if __name__ == "__main__":
    Process()
