import math
import os
import random
import re
import time
import traceback

import pymysql
import requests
from bs4 import BeautifulSoup


def callran(t):
    arr = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
           "W", "X", "Y", "Z",
           "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
           "w", "x", "y", "z"]
    # cal = "CAS"
    cal = ""
    for i in range(t):
        ran = math.ceil(51 * random.random())
        cal += arr[ran]
    return cal


def callran_cn(t):
    arr = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
           "W", "X", "Y", "Z",
           "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
           "w", "x", "y", "z"]
    cal = "CAS"
    # cal = ""
    for i in range(t):
        ran = math.ceil(51 * random.random())
        cal += arr[ran]
    return cal


def request_eleven(hotel, s, supplier_id, cookie):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "hotels.ctrip.com",

        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/63.0.3239.132 Safari/537.36",
        'Accept-Encoding': 'gzip, deflate',
        # 切换代理
    }
    if supplier_id == 209:
        cal_value = callran(17)
        url = "http://hotels.ctrip.com/international/Tool/cas-ocanball.aspx?callback=" + cal_value + "&_=" + \
              str(int(time.time() * 1000))
        headers["Referer"] = "http://hotels.ctrip.com/international/" + str(hotel) + ".html"
    elif supplier_id == 208:
        cal_value = callran_cn(15)
        headers['Referer'] = "http://hotels.ctrip.com/hotel/" + str(hotel) + ".html"
        url = "http://hotels.ctrip.com/domestic/cas/oceanball?callback=" + cal_value + "&_=" + \
              str(int(time.time() * 1000))
    else:
        return
    headers['Cookie'] = cookie
    req = s.get(url, headers=headers)
    return req.text


def eleven(response1, supplier_id):
    if supplier_id == 209:
        match = re.search('return res}\((.*),function\(it.*fromCharCode\(item-([0-9]{1,7})\)', response1)
        if match:
            num = match.groups()[1]
            num_arr = match.groups()[0]
        else:
            return 'error'
        result1 = "".join(map(lambda item: chr(int(item) - int(num)), eval(num_arr)))  # 翻译为字母组合
        result1 = re.sub('= \[32769,26495,32473,23567,', '== [32769,26495,32473,23567,', result1)
        result1 = re.sub('[a-zA-Z]{17}\(new Function\(\'return \"\' \+', 'console.log(', result1)
        result1 = re.sub('\+ \'\";\'\)\);', ');phantom.exit();', result1)
        match2 = re.search(r'(\"\/international\/.{4,8}\.html\")', result1)
        if match2:
            result1 = result1.replace('window.location.href', match2.groups()[0])
        else:
            return 'error'
        with open('runjs.js', 'w') as f:  # 写入文件中
            f.write(result1)
        result1 = os.popen('phantomjs runjs.js').read()  # 执行文件
        return result1[:-1]
    elif supplier_id == 208:
        match = re.search('return res}\((.*),function\(it.*fromCharCode\(item-([0-9]{1,7})\)', response1)
        if match:
            num = match.groups()[1]
            num_arr = match.groups()[0]
        else:
            return 'error'
        result1 = "".join(map(lambda item: chr(int(item) - int(num)), eval(num_arr)))  # 翻译为字母组合
        result1 = re.sub('= \[32769,26495,32473,23567,', '== [32769,26495,32473,23567,', result1)
        result1 = re.sub('CAS[a-zA-Z]{15}\(new Function\(\'return \"\' \+', 'console.log(', result1)
        result1 = re.sub('\+ \'\";\'\)\);', ');phantom.exit();', result1)
        match2 = re.search(r'(\"\/hotel\/.{4,8}\.html\")', result1)
        if match2:
            result1 = result1.replace('window.location.href', match2.groups()[0])
        else:
            return 'error'
        with open('runjs.js', 'w') as f:  # 写入文件中
            f.write(result1)
        result1 = os.popen('phantomjs runjs.js').read()  # 执行文件
        return result1[:-1]
    else:
        return "error"


def get_cookies_from_db(supplier_id):
    filename = "ctripcn_cookies.txt" if supplier_id == 208 else "ctripint_cookies.txt"
    path = os.path.join(os.getcwd(), "ctrip_cookies", filename)
    result = open(path, "r").read()
    return result


def get_city_id(url):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Host": "hotels.ctrip.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        'Accept-Encoding': 'gzip, deflate',
        # 切换代理
    }
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            res = soup.find("input", attrs={"id": "cityId"})['value']
            return res
        else:
            get_city_id(url)
    except:
        get_city_id(url)


def get_price_by_eleven(hotel, room_num, nights, checkin, checkout, supplier_id, person_num, child_num, child_age):
    try:
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Host": "hotels.ctrip.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            'Accept-Encoding': 'gzip, deflate',
            # 切换代理

        }
        cookie = get_cookies_from_db(supplier_id)
        s = requests.session()
        if str(supplier_id) == "209":
            eleven_ = eleven(request_eleven(hotel, s, supplier_id, cookie), supplier_id)
            child_age_list = child_age.split(",")
            childNum = person_num if child_num == 0 else str(person_num) + "-" + "-".join(child_age_list)
            dt = {'City': '73', 'Hotel': hotel, 'EDM': 'F', 'ep': '', 'StartDate': checkin,
                  'DepDate': checkout, 'RoomNum': str(person_num), 'RoomQuantity': '1', 'UserUnicode': '',
                  'requestTravelMoney': 'F', 'promotionid': '', 'Coupons': '', 'CCoupons': '', 'PageLoad': 'false',
                  't': str(int(time.time() * 1000)), 'childNum': childNum, 'FixSubHotel': 'F', 'allianceid': '', 'sid': '',
                  'Currency': '', 'Exchange': '1', 'Shadowid': '0', 'AvgPrice': '', 'Cashbackamount': '',
                  'Couponamount': '', 'TotalCouponamount': '', 'Reductionamount': '', 'TotalReductionamount': '',
                  'ShowType': '', 'TotalCashbackAmount': '', 'AverageTaxFee': '', 'TotalTaxFee': '', 'BedType': '-1',
                  'Breakfast': '0', 'Broadnet': '0', 'timestamp': '0', 'Childs': '',
                  'eleven': eleven_}
            headers['Referer'] = "http://hotels.ctrip.com/international/" + str(hotel) + ".html"
            headers['Cookie'] = cookie
            url = 'http://hotels.ctrip.com/international/Tool/AjaxHotelRoomInfoDetailPart.aspx'
            # 切换代理
            r = s.get(url, headers=headers, params=dt)
            # r = s.get(url, headers=headers, params=dt)
            if r.status_code == 200:
                return r.text
            else:
                return "error"
        elif str(supplier_id) == "208":
            city_id = get_city_id(hotel)
            eleven_ = eleven(request_eleven(hotel, s, supplier_id, cookie), supplier_id)
            headers['Referer'] = "http://hotels.ctrip.com/hotel/" + str(hotel) + ".html"
            url = 'http://hotels.ctrip.com/Domestic/tool/AjaxHote1RoomListForDetai1.aspx?'
            dt1 = {'psid': '',
                   'MasterHotelID': hotel,
                   'hotel': hotel,
                   'EDM': 'F',
                   'roomId': '',
                   'IncludeRoom': '',
                   'city': city_id,
                   'supplier': '',
                   'showspothotel': 'T',
                   'IsDecoupleSpotHotelAndGroup': 'F',
                   'contrast': '0',
                   'brand': '110',
                   'startDate': checkin,
                   'depDate': checkout,
                   'IsFlash': 'F',
                   'RequestTravelMoney': 'F',
                   'hsids': '',
                   'IsJustConfirm': '',
                   'contyped': '0',
                   'priceInfo': '-1',
                   'equip': '',
                   'filter': 'bed|0,bf|0,networkwifi|0,networklan|0,policy|0,hourroom|0,reserve|0,pay|0,triple|0,addbed|0,chooseroom|0,ctrip|0,hotelinvoice|0,CtripService|0',
                   'productcode': '',
                   'couponList': '',
                   'abForHuaZhu': '',
                   'defaultLoad': 'F',
                   'esfiltertag': '',
                   'estagid': '',
                   'Currency': '',
                   'Exchange': '',
                   'RoomGuestCount': '1,' + str(person_num) + ',' + str(child_num) + "," + str(child_age),
                   'promotionf': 'null,',
                   'eleven': eleven_,
                   'callback': callran_cn(15),
                   '_': str(int(time.time() * 1000))}
            # 切换代理
            # r = requests.get(url, headers=headers, params=dt1)
            r = requests.get(url, headers=headers, params=dt1)
            if r.status_code == 200:
                return r.text
            else:
                return "error"
        else:
            return "error"

    except:
        traceback.print_exc()
        return "error"
