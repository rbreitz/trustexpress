from flask import Flask, render_template, request
from flaskapp.PatternDifficultyPredictor.trust_utils import get_product_info, get_product_reviews, \
    rate_my_product, get_top_reviews


app = Flask(__name__)


@app.route('/')
# @app.route('/index')
def pattern_input():
    return render_template("webpage5.html")


@app.route('/', methods=['GET', 'POST'])
def get_difficulty_prediction():

    try:

        # Get user input on webpage
        product_url = request.form['product url']
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
        #difficult_features = top_feature_dict['difficult_features']
        #easy_features = top_feature_dict['easy_features']
        #Find some features from the reviews and figure out 
        #how to display them - B

        # Get product info for display
        store_name = product_info.iloc[0]['store_name']
        product_name = product_info.iloc[0]['title']
    #need to update all of these - B
        try:
            product_photo_url = product_info.iloc[0]['primary_image_url']
        except:  # If something goes wrong with the photo, we can just display an empty photo.
            product_photo_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/240px-No_image_available.svg.png'
#you need to figure out what you want to pass to this page too - B
        return render_template("webpage5.html", 
                               main_rating=product_ratings['current_rating'],
                               store_name=store_name,
                               product_name=product_name, 
                               product_photo_url=product_photo_url,
                               top_reviews=top_reviews)

    # Don't tell the programmers :'(
    # I just need to be able to make one simple error message on my site when stuff goes wrong.
    except:
        print('exception')
        main_rating = -5
        return render_template("webpage5.html",
                               main_rating=difficulty_prediction,
                               store_name=None,
                               product_name=None,
                               product_photo_url=None,
                               top_reviews=None)

if __name__ == '__main__':
    app.run()
