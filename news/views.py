from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from .models import NewsPiece, Tag, ContentTag
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
import jieba
import datetime
import copy
import math
import operator
import time
from collections import Counter


def index(request):
    news_list = NewsPiece.objects.all()
    paginator = Paginator(news_list, 10)
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    return render(request, 'news/newslist.html', {'news_title_list': news, 'news_sum': len(NewsPiece.objects.all())})


def init_data(request):
    from selenium import webdriver
    browser = webdriver.Chrome()
    url = 'http://www.xinhuanet.com/local/index.htm'
    browser.get(url)
    print('hello')
    time.sleep(1)
    btn = browser.find_element_by_class_name("moreBtn")
    for i in range(0, 99):
        btn.click()
        time.sleep(0.8)
    titles = browser.find_elements_by_xpath("//ul[@id='showData0']/child::li/h3/a")
    # nums = browser.find_elements_by_xpath("//div[@class='ndi_main']/child::div/child::div/div[@class='share-join clearfix']/a/div/span[@class='post_recommend_tie_icon icons']")
    # return HttpResponse("start working.")
    print(len(titles))
    c = 0
    con_browser = webdriver.Chrome()
    flag = False
    d = -1
    for i in titles:
        d = d + 1
        href = i.get_attribute('href')
        title = i.text
        print(href + ' ' + title)
        con_browser.get(href)
        try:
            content = con_browser.find_element_by_xpath(
                "//div[@class='main']/div[@class='part part1 clearfix']/div[@class='p-right left']/div[@id='p-detail']")
            news_time = con_browser.find_element_by_class_name('h-time')
        except Exception as e:
            pass
        else:
            n = NewsPiece(news_title=title, news_content=content.text, pub_date=news_time.text)
            n.save()
            print(news_time.text)
            print(content.text)
            c = c + 1
        time.sleep(0.2)
    return HttpResponse("end working.")


def index_page(request, page_id):
    print('hello')
    news_from = page_id * 20
    news_to = page_id * 20 + 20
    news_title_list = NewsPiece.objects.all()[news_from:news_to]
    print('hello')
    context = {'news_title_list': news_title_list, 'news_from': news_from + 1, 'news_to': news_to,
               'page_id': page_id, 'news_sum': len(NewsPiece.objects.all())}
    return render(request, 'news/index.html', context)


def takeIdf(elem):
    return elem['tf_idf']


def detail(request, news_id):
    news_ins = NewsPiece.objects.get(pk=news_id)
    mod = copy.deepcopy(news_ins)
    c = 0
    ind = 0
    while ind < len(mod.news_content):
        ch = mod.news_content[ind]
        if ch == '。':
            c = c + 1
            if c == 3:
                str1 = mod.news_content[0:ind + 1]
                str2 = mod.news_content[ind + 1:]
                mod.news_content = str1 + "<br><br>" + str2
                c = 0
        ind = ind + 1

    title = news_ins.news_title
    print(title)
    title_ci = news_ins.tag_set.all()
    content_ci = news_ins.contenttag_set.all()
    r_title_ci = []
    r_content_ci = []
    for t in title_ci:
        r_title_ci.append(t.name)
    for t in content_ci:
        r_content_ci.append(t.name)
    # print(total_ci)
    all_con = news_ins.news_title + news_ins.news_content  # all content
    tot_sum = len(NewsPiece.objects.all())
    result = []
    print(r_title_ci)
    dict_max = {}
    _max = 0
    for ci in r_title_ci:
        c = 0
        p = 0
        _i = 0
        while _i != -1:
            _i = all_con.find(ci, p)
            # print(_i)
            p = _i + 1
            c = c + 1
        # print(c)
        dict = {}
        tot = len(NewsPiece.objects.filter(contenttag__name=ci))
        tf = (c - 1) / len(all_con) * 2
        idf = math.log(tot_sum / (tot + 1))
        tf_idf = tf * idf
        dict['ci'] = ci
        dict['times'] = c - 1
        dict['total'] = tot
        dict['tf'] = tf
        dict['idf'] = idf
        dict['tf_idf'] = tf_idf
        if (tf_idf > _max and tot != 0):
            _max = tf_idf
            dict_max = dict
        result.append(dict)

    result.sort(key=takeIdf, reverse=True)
    print(result)
    print(dict_max)
    related = NewsPiece.objects.filter(contenttag__name=dict_max['ci'])
    related |= NewsPiece.objects.filter(contenttag__name=result[1]['ci'])
    related_set = set(related)

    related_result = []
    for r in related_set:
        if r.news_title == news_ins.news_title:
            continue
        r_tags_raw = r.contenttag_set.all()
        r_tags_str = []
        for j in r_tags_raw:
            r_tags_str.append(j.name)
        r_tags_str_set = set(r_tags_str)
        jiao = r_tags_str_set & set(r_title_ci)
        bing = r_tags_str_set | set(r_title_ci)
        related_result.append((r, len(jiao) / len(bing)))

    # print(related)
    # print(related_result)
    sorted_related = sorted(related_result, key=operator.itemgetter(1), reverse=True)
    print(sorted_related)
    pass_related = []
    for p in sorted_related:
        pass_related.append(p[0])
    print(pass_related)
    context = {'news_ins': mod, 'related_news': pass_related[0:5]}
    return render(request, 'news/detail.html', context)


def category(request, tag_string):
    news_list = NewsPiece.objects.filter(tag__name=tag_string)
    marked = news_list[:]  # copy it
    for m in marked:
        start = m.news_title.find(tag_string)
        end = start + len(tag_string)
        str1 = m.news_title[0:start]
        str2 = m.news_title[start:end]
        str3 = m.news_title[end:]
        m.news_title = str1 + '<em>' + str2 + '</em>' + str3
        print(m.news_title)

    marked = list(set(marked))  # get rid of duplicate items
    paginator = Paginator(marked, 10)
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    context = {'news_list': news, 'tag_string': tag_string, 'results_num': len(news_list)}
    return render(request, 'news/tag.html', context)


def get_abstract(request):
    all_news = NewsPiece.objects.all()[990:]
    c = 0
    for news in all_news:
        str = news.news_content[0:100]
        print(c)
        print(str)
        news.news_abstract = str
        news.save()
        c = c + 1
    return HttpResponse('hello')


def search(request):
    str = request.GET['tag']
    from_date = request.GET['fromdate']
    to_date = request.GET['todate']
    # print(from_date)
    # print(to_date)
    if not from_date:
        from_date = '2000-1-1'
    if not to_date:
        to_date = '2100-1-1'
    s_time = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    e_time = datetime.datetime.strptime(to_date + " 23:59:59", '%Y-%m-%d %H:%M:%S')
    print(s_time)
    print(e_time)
    # search start
    tag_list = str.split(' ')
    num_of_tags = len(tag_list)
    print(tag_list)
    time_start = time.time()
    news_list = NewsPiece.objects.filter(tag__name=tag_list[0])
    news_list_content = NewsPiece.objects.filter(contenttag__name=tag_list[0])
    news_list_2 = []
    news_list_content_2 = []
    time_end = time.time()
    if num_of_tags >= 2:
        news_list_2 = NewsPiece.objects.filter(tag__name=tag_list[1])
        news_list_content_2 = NewsPiece.objects.filter(contenttag__name=tag_list[1])
    print(news_list_2)
    print(news_list)
    news_list_list = list(news_list)
    news_list_content_list = list(news_list_content)
    news_list_list += list(news_list_2)
    news_list_content_list += list(news_list_content_2)

    if num_of_tags >= 2:
        yanqiu = set(list(news_list)) & set(news_list_2)
        both_news = (set(list(news_list)) & set(news_list_content_2)) | (set(list(news_list_content)) & set(news_list_2))
        print(both_news)
        #print(yanqiu)

    news_list_content_list = list(set(news_list_content_list) - set(news_list_list) & set(news_list_content_list))
    # print(news_list_content)
    marked = []
    if num_of_tags >= 2:
        for item in yanqiu:
            n_time = datetime.datetime.strptime(item.pub_date, '%Y-%m-%d %H:%M:%S')
            if n_time >= s_time and n_time <= e_time:
                marked.append(item)
        for item in both_news:
            n_time = datetime.datetime.strptime(item.pub_date, '%Y-%m-%d %H:%M:%S')
            if n_time >= s_time and n_time <= e_time:
                marked.append(item)
    for item in news_list_list:
        n_time = datetime.datetime.strptime(item.pub_date, '%Y-%m-%d %H:%M:%S')
        if n_time >= s_time and n_time <= e_time:
            marked.append(item)
    for item in news_list_content_list:
        n_time = datetime.datetime.strptime(item.pub_date, '%Y-%m-%d %H:%M:%S')
        if n_time >= s_time and n_time <= e_time:
            marked.append(item)
    # search end
    delta_time = time_end - time_start
    print(time_end - time_start)
    if num_of_tags >= 2:
        for m in marked:
            start = m.news_title.find(tag_list[1])
            if start != -1:
                end = start + len(tag_list[1])
                str1 = m.news_title[0:start]
                str2 = m.news_title[start:end]
                str3 = m.news_title[end:]
                m.news_title = str1 + '<em>' + str2 + '</em>' + str3

            start2 = m.news_content.find(tag_list[1])
            end2 = start2 + len(tag_list[1])
            str12 = m.news_content[(start2 - 50) if (start2 - 50) >= 0 else 0: start2]
            str22 = m.news_content[start2:end2]
            # print(str22)
            str32 = m.news_content[end2:(end2 + 50) if (end2 + 50) < len(m.news_content) else len(m.news_content)]
            m.news_abstract = str12 + '<em>' + str22 + '</em>' + str32

    for m in marked:
        start = m.news_title.find(tag_list[0])
        if start != -1:
            end = start + len(tag_list[0])
            str1 = m.news_title[0:start]
            str2 = m.news_title[start:end]
            str3 = m.news_title[end:]
            m.news_title = str1 + '<em>' + str2 + '</em>' + str3

        start2 = m.news_content.find(tag_list[0])
        end2 = start2 + len(tag_list[0])
        str12 = m.news_content[(start2 - 50) if (start2 - 50) >= 0 else 0: start2]
        str22 = m.news_content[start2:end2]
        # print(str22)
        str32 = m.news_content[end2:(end2 + 50) if (end2 + 50) < len(m.news_content) else len(m.news_content)]
        m.news_abstract = str12 + '<em>' + str22 + '</em>' + str32
    # print(m.news_title)

    # marked = list(set(marked))  # get rid of duplicate items
    paginator = Paginator(marked, 10)
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    context = {'news_list': news, 'tag_string': str, 'results_num': len(marked), 'from_date': from_date,
               'to_date': to_date, 'time': delta_time}
    return render(request, 'news/tag.html', context)


def fenci(request):
    i = 990
    for news in NewsPiece.objects.all()[990:]:
        i = i + 1
        print(i)
        for tag in news.tag_set.all():
            tag.delete()
        title_tag = jieba.lcut_for_search(news.news_title)
        content_tag = jieba.lcut(news.news_content)
        r_title_tag = []
        r_content_tag = []
        for t in title_tag:
            if len(t) < 2:
                continue
            r_title_tag.append(t)
        for t in content_tag:
            if len(t) < 2:
                continue
            r_content_tag.append(t)
        r_title_tag = list(set(r_title_tag))
        r_content_tag = list(set(r_content_tag))
        for r in r_title_tag:
            news.tag_set.create(name=r)
        for r in r_content_tag:
            news.contenttag_set.create(name=r)
    return HttpResponse('fin')
