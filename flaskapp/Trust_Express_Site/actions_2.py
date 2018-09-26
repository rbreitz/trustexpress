from flask import Flask, render_template, request
from Trust_Express_Site import app
from .trust_utils_2 import get_product_info, get_product_reviews, rate_my_product, get_top_reviews


#app = Flask(__name__)


@app.route('/')
@app.route('/index')
def pattern_input():
    return render_template("webpage5.html")


@app.route('/', methods=['GET', 'POST'])
def get_difficulty_prediction():

    try:

        # Get user input on webpage
        product_url = request.form['product_url']
        #changed pattern url to product url - B

        # Get the product_id from the url
        product_info = get_product_info(product_url)
        #changed 

        # Get authentications
        #Not needed until next week - B
        #auth_tuple = get_rav_credentials()

        # Scrape pattern data from the Ravelry API
        #Not needed until next week - B
        #pattern_data = get_pattern_data(pattern_permalink, auth_tuple)
        
        #For this week just need to get product reviews from all reviews
        product_reviews = get_product_reviews(product_info)
        
        #Find product ratings based on reviews
        product_ratings = rate_my_product(product_reviews)
        #Note: next week you'll have to actually

        # Get some great reviews
        top_reviews = get_top_reviews(product_reviews)
        helpful_review_1 = top_reviews.iloc[0]['buyerfeedback']
        helpful_score_1 = top_reviews.iloc[0]['help_prob']
        helpful_eval_1 = top_reviews.iloc[0]['buyereval']/20
        helpful_review_2 = top_reviews.iloc[1]['buyerfeedback']
        helpful_score_2 = top_reviews.iloc[1]['help_prob']
        helpful_eval_2 = top_reviews.iloc[1]['buyereval']/20
        negative_review_1 = top_reviews.iloc[2]['buyerfeedback']
        negative_score_1 = top_reviews.iloc[2]['help_prob']
        negative_eval_1 = top_reviews.iloc[2]['buyereval']/20
        #difficult_features = top_feature_dict['difficult_features']
        #easy_features = top_feature_dict['easy_features']
        #Find some features from the reviews and figure out 
        #how to display them - B

        # Get product info for display
        store_name = product_info.iloc[0]['store_name']
        product_name = product_info.iloc[0]['title']
        price = product_info.iloc[0]['price']
        main_rating = product_info.iloc[0]['stars']
        number_reviews = product_info.iloc[0]['votes']
        #need to update all of these - B
        try:
            product_photo_url = product_info.iloc[0]['primary_image_url']
        except:  # If something goes wrong with the photo, we can just display an empty photo.
            product_photo_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/240px-No_image_available.svg.png'
        return render_template("webpage5.html", 
                               number_reviews = number_reviews,
                               main_rating=main_rating,
                               english_reviews = product_ratings['number_english'],
                               helpful_reviews = product_ratings['number_helpful'],
                               helpful_rating = round(product_ratings['helpful_only_rating'],2),
                               store_name=store_name,
                               product_name=product_name,
                               price = price,
                               product_photo_url=product_photo_url,
                               helpful_review_1 = helpful_review_1,
                               helpful_score_1 = round(helpful_score_1,2),
                               helpful_eval_1 = helpful_eval_1,
                               helpful_review_2 = helpful_review_2,
                               helpful_score_2 = round(helpful_score_2,2),
                               helpful_eval_2 = helpful_eval_2,
                               negative_review_1 = negative_review_1,
                               negative_score_1 = round(negative_score_1,2),
                               negative_eval_1 = negative_eval_1
                               )

    # Don't tell the programmers :'(
    # I just need to be able to make one simple error message on my site when stuff goes wrong.
    except:
        print('exception')
        main_rating = -5
        return render_template("webpage5.html",
                               number_reviews = None,
                               main_rating=main_rating,
                               english_reviews = None,
                               helpful_reviews = None,
                               helpful_rating = None,
                               store_name=None,
                               product_name=None,
                               price = None,
                               product_photo_url=None,
                               helpful_review_1 = None,
                               helpful_score_1 = None,
                               helpful_eval_1 = None,
                               helpful_review_2 = None,
                               helpful_score_2 = None,
                               helpful_eval_2 = None,
                               negative_review_1 = None,
                               negative_score_1 = None,
                               negative_eval_1 = None
                               )

@app.errorhandler(404)
def page_not_found(e):
    #snip
    return render_template('flextest.html'), 404

#if __name__ == '__main__':
 #   app.run()
