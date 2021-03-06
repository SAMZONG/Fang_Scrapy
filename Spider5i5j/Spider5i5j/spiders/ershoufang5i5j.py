#!/usr/bin/env python
# coding=utf-8

import scrapy
import demjson

from Spider5i5j.items import Spider5I5JItem
from Spider5i5j.spiders.startURL import startURL

class ershoufang5i5j(scrapy.Spider):
    name = 'ershoufang5i5j'
    allowed_domains = ['5i5j.com']
    start_urls = startURL.ershoufangURL

    def parse(self, response):
        house_page_query = '//body/section/div/div/div/ul[@class="list-body"]/li'
        house_page_root = response.request.url.split('/')[2]
        for info in response.xpath(house_page_query):
            house_page_href = info.xpath('a/attribute::href').extract()[0]
            house_page_url = 'http://'+ house_page_root + house_page_href
            yield scrapy.Request(house_page_url,callback=self.parse_house_page)

    def parse_house_page(self,response):
        item = Spider5I5JItem()
        item['houseTitle'] = response.xpath('//html/head/title/text()').extract()[0].split('_')[0]

        #此XPath节点可以获得房屋的所有基本信息
        house_info_query = '//body/section/div/div/ul'

        area_query = 'li/ul/li[3]/text()'
        item['houseArea'] = response.xpath(house_info_query).xpath(area_query).extract()[0]

        name_query = 'li[3]/text()'
        item['houseName'] = response.xpath(house_info_query).xpath(name_query).extract()[0]

        #此XPath节点获得房屋的历史价格信息和最早发布时间
        #这里初始化房屋售价为一个字典
        item['housePrice'] = {}

        histroy_price_query = '//body/section/div/section/div/script/text()'
        histroy_price_json = response.xpath(histroy_price_query).extract()[0].split(';')[1].split('=')[1]
        histroy_price_dejson = demjson.decode(histroy_price_json)
        histroy_price_data = histroy_price_dejson['xAxis'][0]['data']
        histroy_time = len(histroy_price_data)
        i = 0
        while i < histroy_time :
            histroy_price_guapai = histroy_price_dejson['series'][0]['data'][i]
            histroy_price_chengjiao = histroy_price_dejson['series'][1]['data'][i]
            item['housePrice'][histroy_price_data[i]] = {
                'price_guapai' : histroy_price_guapai,
                'price_chengjiao' : histroy_price_chengjiao
            }
            i += 1

        #最早的历史时间就是发帖的时间
        item['housePublishedTime'] = histroy_price_data[0]

        #这里请求房屋的地址和城市
        item['houseAddress'] = response.xpath('//body/section/div/section/div[@class="xq-intro-info"]/ul/li[3]/text()').extract()[0]
        item['houseCity'] = response.xpath('//body').re(r'mapCityName.*;?')[0].split('\"')[-2]
        #这里请求房屋的地址和城市
        item['houseAddress'] = response.xpath('//body/section/div/section/div[@class="xq-intro-info"]/ul/li[3]/text()').extract()[0]
        item['houseCity'] = response.xpath('//body').re(r'mapCityName.*;?')[0].split('\"')[-2]
        item['houseBaiduLongitude'] = response.xpath('//body').re(r'mapY.*;?')[0].split('=')[-1].split(';')[0].replace('"','')
        item['houseBaiduLatitude'] = response.xpath('//body').re(r'mapX.*;?')[0].split('=')[-1].split(';')[0].replace('"','')

        yield item
        
