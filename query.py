# coding: utf-8
import requests
from bs4 import BeautifulSoup
from stations import stations
import urllib3
from collections import OrderedDict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class QueryPassStation:
    root_url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?' \
               'train_no={}&' \
               'from_station_telecode={}&' \
               'to_station_telecode={}&' \
               'depart_date={}'
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

    def __init__(self, train_no, from_station, to_station, date):
        self.train_no = train_no
        self.from_station = from_station
        self.to_station = to_station
        self.date = date
        self.pass_train_infos = None

    def pass_station(self):
        src_encode = stations[self.from_station]
        dst_encode = stations[self.to_station]
        url = self.root_url.format(self.train_no, src_encode, dst_encode, self.date)
        response = requests.get(url, headers=self.headers, verify=False)
        response.encoding = 'utf-8'
        self.pass_train_infos = response.json()['data']['data']
        pass_station_names = []
        for station_info in self.pass_train_infos:
            pass_station_names.append(station_info['station_name'])
        return pass_station_names


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
        self.train_infos = []

    def query(self, src, dst, date):
        url = self.encode_url(src, dst, date)
        response = requests.get(url, headers=self.headers, verify=False)
        response.encoding = 'utf-8'
        return self.analysis_html(response)

    def analysis_html(self, response):
        try:
            available_trains = response.json()['data']['result']
        except Exception:
            print("please wait for moment, 12306 maybe happened a big bug.")
            exit(0)
        available_trains = [i.split('|') for i in available_trains]
        stations_re = dict(zip(stations.values(), stations.keys()))
        for raw_train in available_trains:
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

            train_info['business_seat'] = raw_train[32]
            train_info['first_seat'] = raw_train[31]
            train_info['second_seat'] = raw_train[30]
            train_info['advance_soft_sleep'] = raw_train[21]
            train_info['soft_sleep'] = raw_train[23]
            train_info['bullet_sleep'] = raw_train[33]
            train_info['hard_sleep'] = raw_train[28]
            train_info['soft_seat'] = raw_train[24]
            train_info['hard_seat'] = raw_train[29]
            train_info['no_seat'] = raw_train[26]
            train_info['others'] = raw_train[22]
            self.train_infos.append(train_info)
            break

    def encode_url(self, src, dst, date):
        src_encode = stations[src]
        dst_encode = stations[dst]
        url = self.root_url.format(date, src_encode, dst_encode)
        return url


if __name__ == '__main__':
    qt = QueryTrain()
    date = '2019-10-01'
    qt.query('北京西', '信阳', date)
    for train_info in qt.train_infos:
        train_name = train_info['train_name']
        start_time = train_info['start_time']
        from_station = train_info['from_station']
        to_station = train_info['to_station']
        train_no = train_info['train_no']
        qps = QueryPassStation(train_no, from_station, to_station, start_time)
        pass_stations = qps.pass_station()
        print("train_name: {}, pass station is {}".format(train_name, pass_stations))
