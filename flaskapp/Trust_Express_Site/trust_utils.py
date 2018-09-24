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
    product_df = pd.read_csv('all_saved_product_info.csv', index_col=False, low_memory=False)
    product_info = product_df.loc[product_df['product_url']==product_url]
    return product_info

def get_product_reviews(product_info):
    product_id = product_info.iloc[0]['product_id']
    review_df = pd.read_csv('df_with_reviews_and_trust_and_all.csv', index_col=False, low_memory=False)
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
    product_info = get_product_info('https://www.aliexpress.com/item/Free-Shipping-Magic-Sponge-Eraser-Melamine-Cleaner-multi-functional-sponge-for-Cleaning100x60x20mm-50pcs-lot/683078212.html?ws_ab_test=searchweb0_0,searchweb201602_4_10065_10068_10130_10547_10546_10059_10884_10548_315_10545_10887_10696_100031_531_10084_10083_10103_451_10618_452_10307,searchweb201603_54,ppcSwitch_5&algo_expid=bc821ff7-d9d4-47c3-8285-22877b125992-46&algo_pvid=bc821ff7-d9d4-47c3-8285-22877b125992&priceBeautifyAB=0')
    print(product_info.iloc[0]['product_id'])
    product_reviews = get_product_reviews(product_info)
    print(product_reviews.iloc[0]['buyerid'])
    product_ratings=rate_my_product(product_reviews)
    print(product_ratings)
    