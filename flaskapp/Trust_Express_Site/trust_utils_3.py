#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 16:42:12 2018

@author: rebeccareitz
"""
import csv
from lxml import html
import requests
import pandas as pd
import numpy as np
import re
from sklearn.externals import joblib
import json
from datetime import datetime
from bs4 import BeautifulSoup

#for gathering data
import requests
from lxml import html

def get_ali_credentials():
    # Open my Ravelry authentication values
    path = 'data/AliExpressSecret.txt'  # Path to the file that holds
    # my keys--the username and password given to me by Ravelry for my Basic Auth, read only app
    mode = 'r'  # read mode--I'll only need to read the username and password from the file

    keys = []  # The list where I'll store my username and password
    with open(path, mode) as f:  # Open the file
        for line in f:
            keys.append(line)  # The first line is the username, and the second line is the password--add each of these
            # lines to the keys list

    payload = {
            'loginID': keys[0].rstrip(),
            'password': keys[1].rstrip(),
            '_csrf_token':keys[2].rstrip()
            }

    return payload

def scrape_product_info(product_url):
    session_requests = requests.session()
    login_url = "https://login.aliexpress.com/"
    result = session_requests.get(login_url)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='_csrf_token']/@value")))[0]
   
    #Load 
    path = 'data/AliExpressSecret.txt'  # Path to the file that holds the keys
    mode = 'r'  # read mode--I'll only need to read the username and password from the file

    keys = []  # The list where I'll store my username and password
    with open(path, mode) as f:  # Open the file
        for line in f:
            keys.append(line)  # The first line is the username, and the second line is the password--add each of these
            # lines to the keys list
    
    payload = {
            'loginID': keys[0].rstrip(),
            'password': keys[1].rstrip(),
            '_csrf_token':authenticity_token
            }
    
    login_result = session_requests.post(
        login_url, 
        data = payload, 
        headers = dict(referer=login_url)
        )
    
    result = session_requests.get(
        product_url,
        headers = dict(referer = product_url))
    
    soup = BeautifulSoup(result.content, "html.parser")
    
    if soup.find('input', {'id': 'hid-product-id'})['value'] is not None:
        product_id = soup.find('input', {'id': 'hid-product-id'})['value']
    else:
        product_id = 1
    title = soup.find('h1', {'class': 'product-name'}).text
    price = float(soup.find('span', {'id': 'j-sku-price'}).text.split('-')[0])

    if soup.find('span', {'id': 'j-sku-discount-price'}):
        discount_price = float(soup.find('span', {'id': 'j-sku-discount-price'}).text.split('-')[0])
    else:
        discount_price = None

    properties = soup.findAll('li', {'class': 'property-item'})
    attrs_dict = {}
    for item in properties:
        name = item.find('span', {'class': 'propery-title'}).text[:-1]
        val = item.find('span', {'class': 'propery-des'}).text
        attrs_dict[name] = val
    description = json.dumps(attrs_dict)

    stars = float(soup.find('span', {'class': 'percent-num'}).text)
    votes = int(soup.find('span', {'itemprop': 'reviewCount'}).text)
    orders = int(soup.find('span', {'id': 'j-order-num'}).text.split()[0].replace(',', ''))
    wishlists = 0  # int(soup.find('span', {'id': 'j-wishlist-num'}).text.strip()[1:-1].split()[0])

    try:
        shipping_cost = soup.find('span', {'class': 'logistics-cost'}).text
        shipping_company = soup.find('span', {'id': 'j-shipping-company'}).text
    except Exception:
        shipping_cost = ''
        shipping_company = ''
    is_free_shipping = shipping_cost == 'Free Shipping'
    is_epacket = shipping_company == 'ePacket'

    primary_image_url = soup.find('div', {'id': 'magnifier'}).find('img')['src']

    store_id = soup.find('span', {'class': 'store-number'}).text.split('.')[-1]
    store_name = soup.find('span', {'class': 'shop-name'}).find('a').text
    store_start_date = soup.find('span', {'class': 'store-time'}).find('em').text
    store_start_date = datetime.strptime(store_start_date, '%b %d, %Y')

    if soup.find('span', {'class': 'rank-num'}):
        store_feedback_score = int(soup.find('span', {'class': 'rank-num'}).text)
        store_positive_feedback_rate = float(soup.find('span', {'class': 'positive-percent'}).text[:-1]) * 0.01
    else:
        try:
            driver.refresh()
            store_feedback_score = int(soup.find('span', {'class': 'rank-num'}).text)
            store_positive_feedback_rate = float(soup.find('span', {'class': 'positive-percent'}).text[:-1]) * 0.01
        except Exception:
            store_feedback_score = -1
            store_positive_feedback_rate = -1

    try:
        cats = [item.text for item in soup.find('div', {'class': 'ui-breadcrumb'}).findAll('a')]
        category = '||'.join(cats)
    except Exception:
        category = ''

    row = {
        'product_id': product_id,
        'title': title,
        'description': description,
        'price': price,
        'discount_price': discount_price,
        'stars': stars,
        'votes': votes,
        'orders': orders,
        'wishlists': wishlists,
        'is_free_shipping': is_free_shipping,
        'is_epacket': is_epacket,
        'primary_image_url': primary_image_url,
        'store_id': store_id,
        'store_name': store_name,
        'store_start_date': store_start_date,
        'store_feedback_score': store_feedback_score,
        'store_positive_feedback_rate': store_positive_feedback_rate,
        'category': category,
        'product_url': product_url
    }
    
    return row

def get_product_info(product_url):
    product_df = pd.read_csv('/Users/rebeccareitz/Desktop/Insight/AliExpress_Project/flaskapp/Trust_Express_Site/data/all_saved_product_info.csv', index_col=False, low_memory=False)
    product_info = product_df.loc[product_df['product_url']==product_url]
    return product_info

def extract_product_reviews(product_id, max_page=100):
    url_template = 'https://m.aliexpress.com/ajaxapi/EvaluationSearchAjax.do?type=all&index={}&pageSize=20&productId={}&country=US'
    initial_url = url_template.format(1, product_id)
    print(product_id)
    reviews = []

    s = requests.Session()

    resp = s.get(initial_url)
    if resp.status_code == 200:
        data = resp.json()
        total_page = data['totalPage']
        total_page = min([total_page, max_page])
        reviews += data['evaViewList']

        if total_page > 1:
            next_page = 2
            while next_page <= total_page:
                print('{}\t{}/{}'.format(product_id, next_page, total_page))
                next_url = url_template.format(next_page, product_id)
                resp = s.get(next_url)

                next_page += 1

                try:
                    data = resp.json()
                except Exception:
                    continue

                reviews += data['evaViewList']

    filtered_reviews = []
    for review in reviews:
        data = {
            'product_id': product_id,
            'anonymous': review['anonymous'],
            'buyerCountry': review['buyerCountry'],
            'buyerEval': review['buyerEval'],
            'buyerFeedback': review['buyerFeedback'],
            'buyerGender': review['buyerGender'] if 'buyerGender' in review else '',
            'buyerHeadPortrait': review['buyerHeadPortrait'] if 'buyerHeadPortrait' in review else '',
            'buyerId': review['buyerId'] if 'buyerId' in review else '',
            'buyerName': review['buyerName'] if 'buyerName' in review else '',
            'evalDate': review['evalDate'],
            'image': review['images'][0] if 'images' in review and len(review['images']) > 0 else '',
            'logistics': review['logistics'] if 'logistics' in review else '',
            'skuInfo': review['skuInfo'] if 'skuInfo' in review else '',
            'thumbnail': review['thumbnails'][0] if 'thumbnails' in review and len(review['thumbnails']) > 0 else '',
        }
        filtered_reviews.append(data)

    product_reviews = pd.DataFrame(filtered_reviews)
    return product_reviews

def get_product_reviews(product_info):
    product_id = product_info.iloc[0]['product_id']
    review_df = pd.read_csv('/Users/rebeccareitz/Desktop/Insight/AliExpress_Project/flaskapp/Trust_Express_Site/data/df_with_reviews_and_trust_and_all.csv', index_col=False, low_memory=False)
    product_reviews = review_df.loc[pd.to_numeric(review_df['product_id'], errors = 'coerce')==product_id]
    return product_reviews

def rate_my_product(product_reviews):
    number_reviews = product_reviews['buyerid'].count()
    current_rating = pd.to_numeric(product_reviews['buyereval']).mean()/10
    trusted_only = product_reviews.loc[product_reviews['final_trust']==1]
    number_trusted = trusted_only['buyerid'].count()
    trusted_only_rating = pd.to_numeric(trusted_only['buyereval']).mean()/10
    middling = product_reviews.loc[product_reviews['final_trust']!=0]
    number_middling = middling['buyerid'].count()
    middling_rating = pd.to_numeric(middling['buyereval']).mean()/10
    product_ratings = {
            'number_reviews':number_reviews,
            'current_rating':current_rating,
            'number_trusted':number_trusted,
            'trusted_only_rating':trusted_only_rating,
            'not_untrustworthy':number_middling,
            'not_untrustworthy_rating':middling_rating
            }
    return product_ratings

def get_top_reviews(product_reviews):
    trusted_only = product_reviews.loc[product_reviews['predicted_trust']==True]
    if trusted_only.empty:
        best_reviews = product_reviews.loc[product_reviews['final_trust']==0.5]
    else:
        best_reviews = trusted_only
    if best_reviews.shape[0]>3:
        top_reviews = best_reviews.sample(n=3)
    else:
        top_reviews = best_reviews
    return top_reviews

if __name__ == '__main__':
    # Test the functions
    payload = get_ali_credentials()
    link = 'https://www.aliexpress.com/item/100pcs-bag-10mm-wholesale-silver-Plating-metal-Jump-Rings-Loop-Finding/1082836270.html?ws_ab_test=searchweb0_0,searchweb201602_3_10065_10068_10130_10547_10546_10059_10548_315_10545_10696_100031_5017615_531_10084_10083_10103_451_10618_452_10307_5017715,searchweb201603_55,ppcSwitch_3&algo_expid=89c3c219-2c61-4ec5-a633-13e752a31ec8-41&algo_pvid=89c3c219-2c61-4ec5-a633-13e752a31ec8&transAbTest=ae803_2&priceBeautifyAB=0'
    product_info = get_product_info(link)
    print(product_info.iloc[0]['product_id'])
    product_reviews = get_product_reviews(product_info)
    print(product_reviews.iloc[0]['buyerid'])
    product_ratings=rate_my_product(product_reviews)
    print(product_ratings)
    
    