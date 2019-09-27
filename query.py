# coding: utf-8
import requests
from bs4 import BeautifulSoup
from stations import stations
import urllib3
from collections import OrderedDict
from openpyxl import Workbook
import time
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers_firefox = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "kyfw.12306.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Cookie": "JSESSIONID=F6868BDFDD826F11A72E4932119EF136; BIGipServerotn=1156579850.50210.0000; RAIL_EXPIRATION=1569796156959; RAIL_DEVICEID=nlIBK2z1jxKrLiRnOOa9nCkIAdqTldGiiaBLxqWQhP1qNscZdMowhjYKvyvyclrvFZkBtQVzNi7P6Q34_W_25ilA7X6VQY5-AFIgAWcFsjuN4HImZfqYBbOkhrXDfeNlsg7gn9EQWv-i_I3ZFvAXJna0gtCnpx_I; BIGipServerpool_passport=183304714.50215.0000; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_fromStation=%u5317%u4EAC%2CBJP; _jc_save_toStation=%u5E7F%u5DDE%2CGZQ; _jc_save_fromDate=2019-09-27; _jc_save_toDate=2019-09-27; _jc_save_wfdc_flag=dc; BIGipServerpassport=904397066.50215.0000"

}

headers_google = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;"
              "q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "kyfw.12306.cn",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    "Cookie": "JSESSIONID=27D34D0E07CF546A1997015F13D9BBC0; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_wfdc_flag=dc; RAIL_EXPIRATION=1569811344621; RAIL_DEVICEID=E9memzjv96LvvIx35PywH1XTeTcjd2r5mBx2GzPN833Ikco5hPPlS7N-nH3fUii7zRvMvOA_MIrAVZ7_cLo_slHqj9Crlh2aoUVS29798CSMFT5GUlgkM_n4ISARQqamK1s5ajEC8NHpFF9K_HHYxRRtch53-FLh; _jc_save_fromStation=%u5317%u4EAC%2CBJP; BIGipServerpool_passport=183304714.50215.0000; _jc_save_toDate=2019-09-27; BIGipServerotn=703595018.38945.0000; _jc_save_toStation=%u5929%u6D25%2CTJP; _jc_save_fromDate=2019-10-03"

}


class QueryPassStation:
    root_url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?' \
               'train_no={}&' \
               'from_station_telecode={}&' \
               'to_station_telecode={}&' \
               'depart_date={}'

    def __init__(self, train_no, from_station, to_station, date):
        self.train_no = train_no
        self.from_station = from_station
        self.to_station = to_station
        self.date = date
        self.pass_train_infos = None

    def pass_station(self, half=False):
        src_encode = stations[self.from_station]
        dst_encode = stations[self.to_station]
        url = self.root_url.format(self.train_no, src_encode, dst_encode, self.date)
        response = request_url(url)
        self.pass_train_infos = response['data']
        pass_station_names = []
        for station_info in self.pass_train_infos:
            pass_station_names.append(station_info['station_name'])
        start_indx = pass_station_names.index(self.from_station)
        end_indx = pass_station_names.index(self.to_station)
        if half:
            return pass_station_names[start_indx:end_indx + 1]
        else:
            return pass_station_names[start_indx:]


def request_url(url, verify=False):
    count = 1
    while count:
        try:
            headers = random.sample([headers_firefox, headers_google], 1)[0]
            response = requests.get(url, headers=headers, verify=verify)
            response.encoding = 'utf-8'
            available_trains = response.json()['data']
            count = 0
        except Exception:
            print("please wait for {} seconds, 12306 maybe happened a big bug.".format(2 * count))
            time.sleep(2 * count)
            count += 1
    return available_trains


class QueryTrain:
    root_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?' \
               'leftTicketDTO.train_date={}' \
               '&leftTicketDTO.from_station={}' \
               '&leftTicketDTO.to_station={}' \
               '&purpose_codes=ADULT'

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "kyfw.12306.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Cookie": "JSESSIONID=C4502AA3D6A080A952510B96F4CF15CB; BIGipServerotn=1156579850.50210.0000; RAIL_EXPIRATION="
                  "1569796156959; RAIL_DEVICEID=nlIBK2z1jxKrLiRnOOa9nCkIAdqTldGiiaBLxqWQhP1qNscZdMowhjYKvyvyclrvFZkBtQV"
                  "zNi7P6Q34_W_25ilA7X6VQY5-AFIgAWcFsjuN4HImZfqYBbOkhrXDfeNlsg7gn9EQWv-i_I3ZFvAXJna0gtCnpx_I; "
                  "BIGipServerpool_passport=183304714.50215.0000; route=c5c62a339e7744272a54643b3be5bf64; "
                  "_jc_save_fromStation=%u5317%u4EAC%2CBJP; _jc_save_toStation=%u5E7F%u5DDE%2CGZQ; "
                  "_jc_save_fromDate=2019-09-26; _jc_save_toDate=2019-09-26; _jc_save_wfdc_flag=dc; "
                  "BIGipServerpassport=904397066.50215.0000"

    }

    def __init__(self):
        self.stations_re = dict(zip(stations.values(), stations.keys()))

    def query_train_information(self, from_station, to_station, date, train_name=None):
        train_infos = []
        url = self.encode_url(from_station, to_station, date)
        response = request_url(url)
        available_trains = response['result']

        available_trains = [i.split('|') for i in available_trains]
        for raw_train in available_trains:
            if train_name is not None:
                if train_name != raw_train[3]:
                    continue
            train_infos.append(self.train_information(raw_train, self.stations_re))
        return train_infos

    @staticmethod
    def train_information(raw_train, stations_re):
        train_info = OrderedDict()
        train_info['train_no'] = raw_train[2]
        train_info['train_name'] = raw_train[3]
        train_info['start_station'] = stations_re.get(raw_train[4])
        train_info['end_station'] = stations_re.get(raw_train[5])
        train_info['from_station'] = stations_re.get(raw_train[6])
        train_info['to_station'] = stations_re.get(raw_train[7])
        temp = raw_train[13]
        train_info['start_time'] = temp[:4] + '-' + temp[4:6] + '-' + temp[6:]
        train_info['departure_time'] = raw_train[8]
        train_info['arrive_time'] = raw_train[9]
        train_info['cost_time'] = raw_train[10]

        train_info['type_business_seat'] = raw_train[32]
        train_info['type_first_seat'] = raw_train[31]
        train_info['type_second_seat'] = raw_train[30]
        train_info['type_advance_soft_sleep'] = raw_train[21]
        train_info['type_soft_sleep'] = raw_train[23]
        train_info['type_bullet_sleep'] = raw_train[33]
        train_info['type_hard_sleep'] = raw_train[28]
        train_info['type_soft_seat'] = raw_train[24]
        train_info['type_hard_seat'] = raw_train[29]
        train_info['type_no_seat'] = raw_train[26]
        train_info['others'] = raw_train[22]
        return train_info

    def query_ticket_number(self, from_station, to_station, date, train_name=None):
        train_info = self.query_train_information(from_station, to_station, date, train_name)[0]
        ticket_info = OrderedDict()
        for key in train_info.keys():
            if 'type_' not in key:
                continue
            ticket_info[key] = train_info[key]
            if train_info[key].isdigit() or '有' == train_info[key]:
                print("================ train_no: {}, from {} to {}, type: {}, num: {} =================".
                      format(train_name, from_station, to_station, key, train_info[key]))
        return ticket_info

    def encode_url(self, src, dst, date):
        src_encode = stations[src]
        dst_encode = stations[dst]
        url = self.root_url.format(date, src_encode, dst_encode)
        return url


def get_all_infos(from_station, to_station, date):
    all_tickets_infos = []

    qt = QueryTrain()
    all_trains_infos = qt.query_train_information(from_station, to_station, date)
    for train_info in all_trains_infos:
        ticket_info = {}
        train_name = train_info['train_name']
        start_time = train_info['start_time']
        from_station = train_info['from_station']
        to_station = train_info['to_station']
        train_no = train_info['train_no']
        qps = QueryPassStation(train_no, from_station, to_station, start_time)
        pass_stations = qps.pass_station()
        print("train_name: {}, pass station is {}".format(train_name, pass_stations))
        # query ticket information
        for pass_station in pass_stations[1:]:
            try:
                ticket = qt.query_ticket_number(from_station, pass_station, date, train_name)
                train_info[pass_station] = ticket
            except Exception:
                continue
        ticket_info['train_name'] = train_info['train_name']
        ticket_info['departure_time'] = train_info['departure_time']
        ticket_info['arrive_time'] = train_info['arrive_time']
        ticket_info['cost_time'] = train_info['cost_time']
        ticket_info['pass_station'] = pass_stations
        all_tickets_infos.append(ticket_info)


if __name__ == '__main__':
    date1 = '2019-10-01'
    from_station1 = '北京西'
    to_station1 = '信阳'
    get_all_infos(from_station1, to_station1, date1)
