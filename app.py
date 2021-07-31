from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


# route to show the review comments in a web UI
@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            search_string = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + search_string
            user_client = uReq(flipkart_url)
            flipkart_page = user_client.read()
            user_client.close()
            flipkart_html = bs(flipkart_page, "html.parser")
            bigboxes = flipkart_html.findAll(
                "div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            product_link = "https://www.flipkart.com" + \
                box.div.div.div.a['href']
            product_response = requests.get(product_link)
            product_response.encoding = 'utf-8'
            prod_html = bs(product_response.text, "html.parser")
            print(prod_html)
            comment_boxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = search_string + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for comment_box in comment_boxes:
                try:
                    # name.encode(encoding='utf-8')
                    name = comment_box.div.div.find_all(
                        'p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    # rating.encode(encoding='utf-8')
                    rating = comment_box.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    # comment_head.encode(encoding='utf-8')
                    comment_head = comment_box.div.div.div.p.text
                except:
                    comment_head = 'No Comment Heading'
                try:
                    customer_tag = comment_box.div.div.find_all(
                        'div', {'class': ''})
                    # customer_comment.encode(encoding='utf-8')
                    customer_comment = customer_tag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                my_dict = {"Product": search_string, "Name": name, "Rating": rating, "comment_head": comment_head,
                           "Comment": customer_comment}
                reviews.append(my_dict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
