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
        main_rating=round(product_ratings['current_rating'],2)
        #Note: next week you'll have to actually

        # Get some great reviews
        top_reviews = get_top_reviews(product_reviews)
        trusted_review = top_reviews.iloc[0]['buyerfeedback']
        predicted_tag = top_reviews.iloc[0]['predicted_tag']
        basic_trust_tag = top_reviews.iloc[0]['basic_trust_tag']
        #difficult_features = top_feature_dict['difficult_features']
        #easy_features = top_feature_dict['easy_features']
        #Find some features from the reviews and figure out 
        #how to display them - B

        # Get product info for display
        store_name = product_info.iloc[0]['store_name']
        product_name = product_info.iloc[0]['title']
        price = product_info.iloc[0]['price']
        #need to update all of these - B
        try:
            product_photo_url = product_info.iloc[0]['primary_image_url']
        except:  # If something goes wrong with the photo, we can just display an empty photo.
            product_photo_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/240px-No_image_available.svg.png'
        return render_template("webpage5.html", 
                               number_reviews = product_ratings['number_reviews'],
                               main_rating=main_rating,
                               trusted_reviews = product_ratings['number_trusted'],
                               trusted_rating = round(product_ratings['trusted_only_rating'],2),
                               not_untrusted_reviews = product_ratings['not_untrustworthy'],
                               not_untrusted_rating = product_ratings['not_untrustworthy_rating'],
                               store_name=store_name,
                               product_name=product_name,
                               price = price,
                               product_photo_url=product_photo_url,
                               trusted_review = trusted_review,
                               predicted_tag = predicted_tag,
                               basic_trust_tag = basic_trust_tag
                               )

    # Don't tell the programmers :'(
    # I just need to be able to make one simple error message on my site when stuff goes wrong.
    except:
        print('exception')
        main_rating = -5
        return render_template("webpage5.html",
                               number_reviews = None,
                               main_rating=main_rating,
                               trusted_reviews = None,
                               trusted_rating = None,
                               not_untrusted_reviews = None,
                               not_untrusted_rating = None,
                               store_name=None,
                               product_name=None,
                               product_photo_url=None,
                               top_reviews=None)

@app.errorhandler(404)
def page_not_found(e):
    #snip
    return render_template('flextest.html'), 404

#if __name__ == '__main__':
 #   app.run()
