import pickle
from selenium import webdriver
import time

# browser = webdriver.Firefox()


# def get_cookies():
#     browser.get("https://login.aliexpress.com/buyer.htm?return=https%3A%2F%2Fwww.aliexpress.com%2F&random=CEA73DF4D81D4775227F78080B9B6126")
#     print('input your username and password in Firefox and hit Submit')
#     input('Hit Enter here if you have summited the form: <Enter>')
#     cookies = browser.get_cookies()
#     pickle.dump(cookies, open("cookies.pickle", "wb"))


# def set_cookies():
#     browser.get("https://aliexpress.com")
#     cookies = pickle.load(open("cookies.pickle", "rb"))
#     for cookie in cookies:
#         browser.add_cookie(cookie)
#     browser.get("https://bestselling.aliexpress.com/en")


# if __name__ == '__main__':
#     get_cookies()

from selenium import webdriver
import pickle
import time


# driver = webdriver.Firefox()
# driver.get("https://aliexpress.com")
# cookies = pickle.load(open("cookies.pickle", "rb"))
# for cookie in cookies:
#     driver.add_cookie(cookie)


# def extract_product_urls_from_list_page(list_page_url):
#     driver.get(list_page_url)
#     time.sleep(5)
#     cats = driver.find_elements_by_css_selector('span.title')

#     all_links = set()
#     for ind, cat in enumerate(cats):
#         print(cat.text)
#         try:
#             cat.click()
#         except Exception:
#             continue
#         if ind == 0:
#             items = driver.find_elements_by_class_name('item-desc')
#             links = [item.get_attribute('href') for item in items]
#         else:
#             items = driver.find_elements_by_css_selector('div.title > a')
#             links = [item.get_attribute('href') for item in items]
#         for link in links:
#             all_links.add(link)
#         time.sleep(2)
#     return all_links


# if __name__ == '__main__':
#     extract_product_urls_from_list_page('https://sale.aliexpress.com/__pc/bestselling.htm')

from selenium import webdriver
import json
import pickle
from datetime import datetime
from bs4 import BeautifulSoup


driver = webdriver.Firefox()
# driver.get("https://aliexpress.com")
# cookies = pickle.load(open("cookies.pickle", "rb"))
# for cookie in cookies:
#     driver.add_cookie(cookie)


def extract_product_info(product_url):
    driver.get(product_url)
    content = driver.page_source

    soup = BeautifulSoup(content, "html.parser")
    #print(soup.find('input', {'id': 'hid-product-id'})['value']) #ID is the CSS selector and hid-product-id is the name. We want to extract the value
    #print(type(soup.find('h1', {'class': 'product-name'})))
    #print(soup.find('h1', {'class': 'product-name'}))
    #print(soup.find('h1', class_ = 'product-name').string)
    

    product_id = soup.find('input', {'id': 'hid-product-id'})['value']
    #print(product_id)
    #print(soup.find('input', {'id': 'skucustomAttr'})['name'])
    title = soup.find('h1', {'class': 'product-name'}).text
    price = float(soup.find('span', {'id': 'j-sku-price'}).text.split('-')[0])

    if soup.find('span', {'id': 'j-sku-discount-price'}):
        discount_price = float(soup.find('span', {'id': 'j-sku-discount-price'}).text.split('-')[0])
        #print(discount_price)
    else:
        discount_price = None

    properties = soup.findAll('li', {'class': 'property-item'})
    attrs_dict = {}
    for item in properties:
        name = item.find('span', {'class': 'propery-title'}).text[:-1]
        val = item.find('span', {'class': 'propery-des'}).text
        attrs_dict[name] = val
        print('Key is: ' + name + '--- Value is: ' + attrs_dict[name])

    description = json.dumps(attrs_dict)

    stars = float(soup.find('span', {'class': 'percent-num'}).text)
    votes = int(soup.find('span', {'itemprop': 'reviewCount'}).text)
    orders = int(soup.find('span', {'id': 'j-order-num'}).text.split()[0].replace(',', ''))
    wishlists = 0  # int(soup.find('span', {'id': 'j-wishlist-num'}).text.strip()[1:-1].split()[0])

    try:
        shipping_cost = soup.find('span', {'class': 'logistics-cost'}).text
        shipping_company = soup.find('span', {'id': 'j-shipping-company'}).text

        print(shipping_cost)
        print(shipping_company)
    except Exception:
        shipping_cost = ''
        shipping_company = ''
    is_free_shipping = shipping_cost == 'Free Shipping' #Checks the default shipping method if its free and epacket
    is_epacket = shipping_company == 'ePacket'
    print(is_epacket)

    primary_image_url = soup.find('div', {'id': 'magnifier'}).find('img')['src']

    store_id = soup.find('span', {'class': 'store-number'}).text.split('.')[-1]
    store_name = soup.find('span', {'class': 'shop-name'}).find('a').text
    store_start_date = soup.find('span', {'class': 'store-time'}).find('em').text
    store_start_date = datetime.strptime(store_start_date, '%b %d, %Y')

    print(soup.find('span', {'itemprop':'ratingValue'}).string)
    # OR print(soup.find('span', class_ = 'ui-rating-star').find('span', {'itemprop':'ratingValue'}).string)

    if soup.find('span', {'class': 'rank-num'}):
        store_feedback_score = int(soup.find('span', {'class': 'rank-num'}).text)
        store_positive_feedback_rate = float(soup.find('span', {'class': 'positive-percent'}).text[:-1]) * 0.01
    else:
        driver.refresh()
        try:
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

def printReviews(productUrl):
    #Open up FireFox & extract the page source code
    driver.get(productUrl)
    pageSource = driver.page_source
    soup = BeautifulSoup(pageSource, "html.parser")
    
    # We will save each User/Buyer's info into an array.
    # The User information will come in as an object, grouped together, hence the name "userInfoGroup"

    userInfoGroup = []
    i = 0
    # If the element that allows you to paginate to the next page is found, then we'll loop
    # *******PENDING PROBLEM: If it's not found, it'll throw an error. Come back and handle it.
    while (soup.find('div', {'id': 'complex-pager'})
    .find('div', class_ = 'ui-pagination ui-pagination-front ui-pagination-body util-clearfix')
    .find('div', class_ = 'ui-pagination-navi util-left')
    .find('a', class_ = 'ui-pagination-next ui-goto-page')):

        pageSource = driver.page_source
        #print(driver.page_source)
        soup = BeautifulSoup(pageSource, "html.parser")

        error_page_title_found = soup.find('title').string == "AliExpress.com - Maintaining"
        print(error_page_title_found)
            
            #Try to find buyer information
        if not (error_page_title_found):

            buyerInfo = soup.find('div', class_ = 'feedback-container').find('div', class_ = 'feedback-list-wrap').find_all('div', class_ = "feedback-item clearfix")
            userInfoGroup.append(buyerInfo)
            for feedbackItem in userInfoGroup[i]:
                print(feedbackItem.find('div', class_ = 'fb-main').find('div', class_ = 'f-content').find('dl', class_ = 'buyer-review').find('dt', 'buyer-feedback').find('span').string)
            
            #Try to find pagination
            button = driver.find_element_by_xpath('/html/body/div/div[5]/div/div/a[4]')
            button.click()

        error_page_title_found = soup.find('title').string == "AliExpress.com - Maintaining"

        if(error_page_title_found): 
            #AliExpress has kicked you out. Go back 1 page to resume
            print("Error. AliExpress has kicked you out.")
            error_page_title = soup.find('title').string
            print(error_page_title)
            driver.execute_script("window.history.go(-1)") #Go back to the last webpage you visited
            time.sleep(1)

            pageSource = driver.page_source
            soup = BeautifulSoup(pageSource, "html.parser")
            i-=1

           # driver.refresh()
        i+=1
            
    
    print('Look above')
    buyerInfo = soup.find('div', class_ = 'feedback-container').find('div', class_ = 'feedback-list-wrap').find_all('div', class_ = "feedback-item clearfix")
    for feedbackItem in buyerInfo:
        print(feedbackItem.find('div', class_ = 'fb-main').find('div', class_ = 'f-content').find('dl', class_ = 'buyer-review').find('dt', 'buyer-feedback').find('span').string)
    return 


if __name__ == '__main__':
    #extract_product_info('https://www.aliexpress.com/item/Baseus-Lightning-For-iPhone-Cable-2-0A-Fast-Data-Sync-Charger-USB-Cable-For-iPhone-6/32718277406.html?spm=a2g01.8286187.3.1.44b525c4mnXiw0&scm=1007.14594.99248.0&scm_id=1007.14594.99248.0&scm-url=1007.14594.99248.0&pvid=7ad5dd56-a817-462e-890d-793673a3deca')
    printReviews('https://feedback.aliexpress.com/display/productEvaluation.htm?productId=32718277406&ownerMemberId=221071036&companyId=231015615&memberType=sellerstartValidDate=i18n=true')

import csv
import requests


def extract_product_reviews(product_id, max_page=100):
    url_template = 'https://m.aliexpress.com/ajaxapi/EvaluationSearchAjax.do?type=all&index={}&pageSize=20&productId={}&country=US'
    initial_url = url_template.format(1, product_id)
    reviews = []

    s = requests.Session()
    #res = requests.get('https://feedback.aliexpress.com/display/productEvaluation.htm?productId=32718277406&ownerMemberId=221071036&companyId=231015615&memberType=sellerstartValidDate=i18n=true')
    
    
    ###res = requests.get('https://feedback.aliexpress.com/display/productEvaluation.htm#feedback-list')
    ###print(res.content)

    resp = s.get(initial_url)
    #res = s.get(https://feedback.aliexpress.com/display/productEvaluation.htm?productId=32718277406&amp;ownerMemberId=221071036&amp;companyId=231015615&amp;memberType=seller&amp;startValidDate=&amp;i18n=true)
    #https://feedback.aliexpress.com/display/productEvaluation.htm?productId=32718277406&ownerMemberId=221071036&companyId=231015615&memberType=sellerstartValidDate=i18n=true
    if resp.status_code == 200:
        data = resp.json()
        print(resp.text)
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
            'anonymous': review['anonymous'],
            'buyerCountry': review['buyerCountry'],
            'buyerEval': review['buyerEval'],
            'buyerFeedback': review['buyerFeedback'],
            'buyerGender': review['buyerGender'] if 'buyerGender' in review else '',
            'buyerHeadPortrait': review['buyerHeadPortrait'] if 'buyerHeadPortrait' in review else '',
            'buyerId': review['buyerId'] if 'buyerId' in review else '',
            'buyerName': review['buyerName'],
            'evalDate': review['evalDate'],
            'image': review['images'][0] if 'images' in review and len(review['images']) > 0 else '',
            'logistics': review['logistics'] if 'logistics' in review else '',
            'skuInfo': review['skuInfo'] if 'skuInfo' in review else '',
            'thumbnail': review['thumbnails'][0] if 'thumbnails' in review and len(review['thumbnails']) > 0 else '',
        }
        filtered_reviews.append(data)

    keys = filtered_reviews[0].keys()
    with open('reviews.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(filtered_reviews)
    return filtered_reviews


if __name__ == '__main__':
    extract_product_reviews('32718277406') ###this line
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
matplotlib.style.use('ggplot')

df = pd.read_csv('reviews.csv')
df['evalDate'] = pd.to_datetime(df['evalDate'])

vc = df['evalDate'].value_counts()
ax = vc.plot()
ax.set_xlabel("date")
ax.set_ylabel("review count")
plt.savefig('aliexpress-plot-review.png')

vc = df['buyerCountry'].value_counts()[:10]
ax = vc.plot(kind='pie')
ax.set_ylabel("top 10 buyer countries")
plt.savefig('aliexpress-plot-countries.png')


vc = df['logistics'].value_counts()[:5]
ax = vc.plot(kind='pie')
ax.set_ylabel("top 5 logistics")
plt.savefig('aliexpress-plot-logistics.png')


vc = df['skuInfo'].value_counts()
ax = vc.plot(kind='pie')
ax.set_ylabel("skuInfo")
plt.savefig('aliexpress-plot-skuinfo.png')