#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 16:42:12 2018

@author: rebeccareitz
"""
import csv
import requests as rq
import pandas as pd
import numpy as np
import re
from sklearn.externals import joblib

def get_product_info(product_url):
    product_df = pd.read_csv('/Users/rebeccareitz/Desktop/Insight/AliExpress_Project/flaskapp/Trust_Express_Site/data/all_saved_product_info.csv', index_col=False, low_memory=False)
    product_info = product_df.loc[product_df['product_url']==product_url]
    return product_info.iloc[0]

def get_product_reviews(product_info):
    product_id = product_info['product_id']
    review_df = pd.read_csv('/Users/rebeccareitz/Desktop/Insight/AliExpress_Project/flaskapp/Trust_Express_Site/data/Ali_Express_English_Reviews_with_Amazon_Helpfulness.csv', index_col=False, low_memory=False)
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
    print(product_info.iloc[0]['product_id'])
    product_reviews = get_product_reviews(product_info)
    print(product_reviews.iloc[0]['buyerid'])
    product_ratings=rate_my_product(product_reviews)
    print(product_ratings)
    top_reviews = get_top_reviews(product_reviews)
    print(top_reviews.iloc[2]['buyerfeedback'])
    