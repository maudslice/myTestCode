import re
import ast
import requests
from spiderrrr.models import *
from urllib import parse
from selenium import webdriver
from scrapy import Selector
from datetime import datetime

from spiderrrr.models import Topic

url_list = []
domain = "https://bbs.csdn.net"


def get_comment(url, id):
    rest_text = get_html(url)
    sel = Selector(text=rest_text)
    all_divs = sel.xpath('//div[starts-with(@id, "post-")]')
    for answer_item in all_divs:
        answer = Answer()
        answer.topic_id = id
        author_info = answer_item.xpath('.//div[@class="nick_name"]//a[1]/@href').extract()[0]
        author_id = author_info.split("/")[-1]
        answer.author = author_id
        create_time_str = answer_item.xpath('.//label[@class="date_time"]/text()').extract()[0]
        create_time = datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
        answer.creat_time = create_time
        context = answer_item.xpath('.//div[@class="post_body post_body_min_h"]/text()').extract()[0]
        answer.content = context
        praised_num = answer_item.xpath('//label[@class="red_praise digg"]//em/text()').extract()[0]
        answer.parise_num = int(praised_num)
        answer.save()


def parse_author(url):
    follower_num = 0
    author_id = url.split("/")[-1]
    rest_text = get_html(url)
    sel = Selector(text=rest_text)
    name = sel.xpath('//p[@class="lt_title"]/text()').extract()[-1].strip()
    desc = sel.xpath('//div[@class="description clearfix"]/p/text()').extract()[0].strip()
    follower_num_str = sel.xpath('//div[@class="fans"]//span/text()').extract()[0].strip()
    following_num = sel.xpath('//div[@class="att"]//span/text()').extract()[0].strip()
    if "k" or "K" in follower_num_str:
        fn_match = re.search("(\d+)", follower_num_str)
        follower_num = int(float(fn_match.group(1)) * 1000)
    else:
        follower_num = int(follower_num)
    if "w" or "W" in follower_num_str:
        fn_match = re.search("(\d+)", follower_num_str)
        follower_num = int(float(fn_match.group(1)) * 10000)
    else:
        follower_num = int(follower_num)

    author = Author()
    author.id = author_id
    author.follower_num = int(follower_num)
    author.following_num = int(following_num)
    author.desc = desc
    author.name = name
    existed_topic = Author.select().where(Author.id == author.id)
    if existed_topic:
        author.save()
    else:
        author.save(force_insert=True)


def parse_topic(url):
    topic_id = url.split("/")[-1]
    rest_text = get_html(url)
    sel = Selector(text=rest_text)
    all_divs = sel.xpath('//div[starts-with(@id, "post-")]')
    topic_item = all_divs[0]
    content = topic_item.xpath('.//div[@class="post_body post_body_min_h"]').extract()[0]
    praised_num = topic_item.xpath('.//label[@class="red_praise digg"]//em/text()').extract()[0]
    jtl_str = topic_item.xpath('.//div[@class="close_topic"]/text()').extract()[0]
    jtl_match = re.search("\d+(\.\d+)?", jtl_str)
    # 期末考试1
    jtl = 0.0
    if jtl_match:
        jtl = jtl_match.group(0)
    existed_topics = Topic.select().where(Topic.id == topic_id)
    if existed_topics:
        topic = existed_topics[0]
        topic.content = content
        topic.parise_num = int(praised_num)
        topic.jtl = float(jtl)
        topic.save()
    for answer_item in all_divs[1:]:
        answer = Answer()
        answer.topic_id = topic_id
        author_info = answer_item.xpath('.//div[@class="nick_name"]//a[1]/@href').extract()[0]
        author_id = author_info.split("/")[-1]
        answer.author = author_id
        create_time_str = answer_item.xpath('.//label[@class="date_time"]/text()').extract()[0]
        create_time = datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
        answer.creat_time = create_time
        context = answer_item.xpath('.//div[@class="post_body post_body_min_h"]/text()').extract()[0]
        answer.content = context
        praised_num = topic_item.xpath('.//label[@class="red_praise digg"]//em/text()').extract()[0]
        answer.parise_num = int(praised_num)
        answer.save()
    page_num_str = all_divs.xpath('//div[@class="page_nav"]/em/text()')
    if page_num_str:
        page_num_match = re.search("\d", page_num_str.extract()[0])
        page_num = int(page_num_match.group(0))
        for temp in range(1, page_num + 1):
            if temp > 1:
                get_comment(url + "?page=" + str(temp), topic_id)


def get_html(url):
    brower = webdriver.Chrome(executable_path="D:/Chrome Driver/chromedriver.exe")
    brower.get(url)
    return brower.page_source


def get_nodes_list():
    left_menu_text = requests.get("https://bbs.csdn.net/dynamic_js/left_menu.js?csdn").text
    nodes_str_match = re.search("forumNodes: (.*])", left_menu_text)

    if nodes_str_match:
        nodes_str = nodes_str_match.group(1).replace("null", "None")
        nodes_list = ast.literal_eval(nodes_str)
        return nodes_list
    return []


def process_nodes_list(nodes_list):
    # 将转换的node_list提取里面的url
    for item in nodes_list:
        if "url" in item and item["url"]:
            url_list.append(item["url"])
            if "children" in item:
                process_nodes_list(item["children"])


def get_level1_list(nodes_list):
    level1_list = []
    for item in nodes_list:
        if "url" in item and item["url"]:
            level1_list.append(item["url"])
    return level1_list


def get_last_url():
    node_list = get_nodes_list()
    process_nodes_list(node_list)
    level1_urls = get_level1_list(node_list)
    last_urls = []
    for url in url_list:
        if url not in level1_urls:
            last_urls.append(parse.urljoin(domain, url))
            last_urls.append(parse.urljoin(domain, url + "/recommend"))
            last_urls.append(parse.urljoin(domain, url + "/closed"))
    return last_urls


def parse_list(url):
    rest_text = get_html(url)
    sel = Selector(text=rest_text)
    all_trs = sel.xpath('//table[@class="forums_tab_table"]//tbody//tr')
    for tr in all_trs:
        status = tr.xpath('.//td[1]/span/text()').extract()[0]
        topic_url = parse.urljoin(domain, tr.xpath('.//td[3]/a[last()]/@href').extract()[0])
        topic_title = tr.xpath('.//td[3]/a[last()]/text()').extract()[0]
        score = int(tr.xpath('.//td[2]/em/text()').extract()[0])
        author_url = tr.xpath('.//td[4]/a/@href').extract()[0]
        author_id = author_url.split("/")[-1]
        create_time_str = tr.xpath('.//td[4]/em/text()').extract()[0]
        create_time = datetime.strptime(create_time_str, "%Y-%m-%d %H:%M")
        answer_info = tr.xpath('.//td[5]/span/text()').extract()[0]
        answer_nums = int(answer_info.split("/")[0])
        click_nums = int(answer_info.split("/")[1])
        last_time_str = tr.xpath('.//td[6]/em/text()').extract()[0]
        last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M")

        topic = Topic()
        topic.status = status
        topic.score = score
        topic.title = topic_title
        topic.author = author_id
        topic.creat_time = create_time
        topic.last_time = last_time
        topic.click_num = click_nums
        topic.id = int(topic_url.split("/")[-1])
        topic.answer_num = answer_nums

        existed_topic = Topic.select().where(Topic.id == topic.id)
        if existed_topic:
            topic.save()
        else:
            topic.save(force_insert=True)

        # parse_topic(topic_url)
        parse_author("https:" + author_url)


if __name__ == "__main__":
    # list_urls = get_last_url()
    # parse_list(list_urls[0])
    # parse_author("https://me.csdn.net/qq_40881680")
    parse_topic("https://bbs.csdn.net/topics/393558574")