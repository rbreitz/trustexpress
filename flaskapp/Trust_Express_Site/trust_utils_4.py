#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 16:42:12 2018

@author: rebeccareitz
"""
from lxml import html
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime
from bs4 import BeautifulSoup

from langdetect import detect

import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

import os


def scrape_product_info(product_url):
    session_requests = requests.session()
    #login_url = "https://login.aliexpress.com/"
    #result = session_requests.get(login_url)
    #tree = html.fromstring(result.text)
    #authenticity_token = tree.xpath("//input[@name='_csrf_token']/@value")
   
    #Load 
    #path = 'data/AliExpressSecret.txt'  # Path to the file that holds the keys
    #mode = 'r'  # read mode--I'll only need to read the username and password from the file

    #keys = []  # The list where I'll store my username and password
    #with open(path, mode) as f:  # Open the file
    #    for line in f:
    #        keys.append(line)  # The first line is the username, and the second line is the password--add each of these
            # lines to the keys list
    
    #payload = {
    #        'loginID': keys[0].rstrip(),
    #        'password': keys[1].rstrip()
    #        }
    #print(product_url)
    
    #login_result = session_requests.post(
    #    login_url, 
    #    data = payload, 
    #    headers = dict(referer=login_url)
    #    )
    
    result = session_requests.get(
        product_url,
        headers = dict(referer = product_url))
    print(result.ok)
    
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
    dirpath = os.getcwd()
    product_filename = os.path.join(dirpath,'Trust_Express_Site','data', 'all_saved_product_info.csv')
    print(os.listdir())
    print(product_filename)
    product_df = pd.read_csv(product_filename, index_col=False, low_memory=False)
    product_info = product_df.loc[product_df['product_url']==product_url]
    return product_info.iloc[0]

def find_english(product_reviews):
    lang_list = []
    for ind, row in product_reviews.iterrows():
        this_review = row['buyerfeedback']
        try:
            feedback_lang = detect(this_review)
            lang_dict = {
                'feedback_lang':feedback_lang,
                'ind':ind
                }
        except:
            continue
        lang_list.append(lang_dict)
    lang_df = pd.DataFrame(lang_list)
    product_reviews = product_reviews.join(lang_df.set_index('ind'))
    english_product_reviews = product_reviews.loc[product_reviews['feedback_lang']=='en']
    return english_product_reviews

def standardize_text(df, text_field):
    df[text_field] = df[text_field].str.replace(r"http\S+", "")
    df[text_field] = df[text_field].str.replace(r"http", "")
    df[text_field] = df[text_field].str.replace(r"@\S+", "")
    df[text_field] = df[text_field].str.replace(r"[^A-Za-z0-9(),!?@\'\`\"\_\n]", " ")
    df[text_field] = df[text_field].str.replace(r"@", "at")
    df[text_field] = df[text_field].str.lower()
    return df

def find_helpful(english_product_reviews):
    
    english_product_reviews = standardize_text(english_product_reviews, 'buyerfeedback')
    
    dirpath = os.getcwd()
    tfidf_vectorizer_pkl_filename = os.path.join(dirpath,'Trust_Express_Site','models', 'tfidf_vectorizer.pickle')
    tfidf_vectorizer_pkl = open(tfidf_vectorizer_pkl_filename, 'rb')
    tfidf_vectorizer = pickle.load(tfidf_vectorizer_pkl)
    X_tfidf = tfidf_vectorizer.transform(english_product_reviews['buyerfeedback'])
            
    clf_tfidf_pkl_filename = os.path.join(dirpath,'Trust_Express_Site','models', 'clf_tfidf.pickle')
    clf_tfidf_pkl = open(clf_tfidf_pkl_filename, 'rb')
    clf_tfidf = pickle.load(clf_tfidf_pkl)
    y = clf_tfidf.predict_proba(X_tfidf)
    y_df = pd.DataFrame(y, columns = ['unhelp_prob','help_prob'], index = english_product_reviews.index.values)    
    
    english_reviews_with_prob = pd.concat([english_product_reviews[:],y_df[:]],axis = 1)
    
    return english_reviews_with_prob

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
            'buyercountry': review['buyerCountry'],
            'buyereval': review['buyerEval'],
            'buyerfeedback': review['buyerFeedback'],
            'buyergender': review['buyerGender'] if 'buyerGender' in review else '',
            'buyerHeadPortrait': review['buyerHeadPortrait'] if 'buyerHeadPortrait' in review else '',
            'buyerid': review['buyerId'] if 'buyerId' in review else '',
            'buyername': review['buyerName'] if 'buyerName' in review else '',
            'evaldate': review['evalDate'],
            'image': review['images'][0] if 'images' in review and len(review['images']) > 0 else '',
            'logistics': review['logistics'] if 'logistics' in review else '',
            'skuInfo': review['skuInfo'] if 'skuInfo' in review else '',
            'thumbnail': review['thumbnails'][0] if 'thumbnails' in review and len(review['thumbnails']) > 0 else '',
        }
        filtered_reviews.append(data)

    product_reviews = pd.DataFrame(filtered_reviews)
    print(product_reviews.shape)
    english_product_reviews = find_english(product_reviews)
    print(english_product_reviews.shape)
    english_product_reviews_with_prob = find_helpful(english_product_reviews)
    print(english_product_reviews_with_prob.shape)
    return english_product_reviews_with_prob

def get_product_reviews(product_info):
    product_id = product_info['product_id']
    dirpath = os.getcwd()
    reviews_filename = os.path.join(dirpath,'Trust_Express_Site','data', 'smaller_pretrained_aliexpress_reviews.csv')
    review_df = pd.read_csv(reviews_filename, index_col=False, low_memory=False)
    product_reviews = review_df.loc[pd.to_numeric(review_df['product_id'], errors = 'coerce')==product_id]
    return product_reviews

def rate_my_product(product_reviews):
    number_reviews = product_reviews['buyerid'].count()
    helpful_only = product_reviews.loc[product_reviews['help_prob']>.5]
    number_helpful= helpful_only['buyerid'].count()
    helpful_only_rating = pd.to_numeric(helpful_only['buyereval']).mean()/20
    product_ratings = {
            'number_english':number_reviews,
            'number_helpful':number_helpful,
            'helpful_only_rating':helpful_only_rating,
            }
    return product_ratings

def get_top_reviews(product_reviews):
    helpful_sorted = product_reviews.sort_values(by='help_prob',ascending=False)
    helpful_sorted['buyereval']=pd.to_numeric(helpful_sorted['buyereval'], errors='coerce')
    top_reviews_list = []
    top_review_1 = {
            'buyerfeedback' : helpful_sorted.iloc[0]['buyerfeedback'],
            'help_prob':helpful_sorted.iloc[0]['help_prob'],
            'buyereval':helpful_sorted.iloc[0]['buyereval']
            }
    top_reviews_list.append(top_review_1)
    top_review_2 = {
            'buyerfeedback' : helpful_sorted.iloc[1]['buyerfeedback'],
            'help_prob':helpful_sorted.iloc[1]['help_prob'],
            'buyereval':helpful_sorted.iloc[1]['buyereval']
            }
    top_reviews_list.append(top_review_2)
    
    if helpful_sorted.buyereval.min() < 60:
        negative_reviews = helpful_sorted.loc[helpful_sorted['buyereval']<60]
    else:
        negative_reviews = helpful_sorted.loc[helpful_sorted['buyereval']==helpful_sorted.buyereval.min()]
    
    negative_review_1 = {
            'buyerfeedback' : negative_reviews.iloc[0]['buyerfeedback'],
            'help_prob':negative_reviews.iloc[0]['help_prob'],
            'buyereval':negative_reviews.iloc[0]['buyereval']
            }
    top_reviews_list.append(negative_review_1)
    
    top_reviews = pd.DataFrame(top_reviews_list)
    
    return top_reviews

if __name__ == '__main__':
    # Test the functions
    link = 'https://www.aliexpress.com/item/100pcs-bag-10mm-wholesale-silver-Plating-metal-Jump-Rings-Loop-Finding/1082836270.html?ws_ab_test=searchweb0_0,searchweb201602_3_10065_10068_10130_10547_10546_10059_10548_315_10545_10696_100031_5017615_531_10084_10083_10103_451_10618_452_10307_5017715,searchweb201603_55,ppcSwitch_3&algo_expid=89c3c219-2c61-4ec5-a633-13e752a31ec8-41&algo_pvid=89c3c219-2c61-4ec5-a633-13e752a31ec8&transAbTest=ae803_2&priceBeautifyAB=0'
    product_info = get_product_info(link)
    print(product_info['product_id'])
    product_reviews = get_product_reviews(product_info)
    print(product_reviews.iloc[0]['buyerid'])
    product_ratings=rate_my_product(product_reviews)
    print(product_ratings)
    
    link_2 = 'https://www.aliexpress.com/store/product/2017-Women-Summer-Casual-Cotton-Linen-V-neck-short-sleeve-tops-shorts-two-piece-set-Female/2056007_32808779921.html?spm=2114.search0103.3.56.503d1b09JWn3Kc&ws_ab_test=searchweb0_0,searchweb201602_5_10065_10068_10130_10547_10546_10059_10884_10548_315_10545_10887_10696_100031_10084_531_10083_10103_10618_10307_449,searchweb201603_60,ppcSwitch_7&algo_expid=69625d3c-df51-43ba-8dbf-232180987a7d-7&algo_pvid=69625d3c-df51-43ba-8dbf-232180987a7d&priceBeautifyAB=0'
    product_info = scrape_product_info(link_2)
    print(product_info['product_id'])
    product_reviews = extract_product_reviews(product_info['product_id'])
    print(product_reviews.iloc[0]['buyerid'])
    
    