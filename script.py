from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url, category):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('.product-title')[0].get_text().strip()
        stamp['title'] = title
    except: 
        stamp['title'] = None
        
    try:
        cat_price = html.select('.cat-price')[0].get_text().strip()
        cat_price = cat_price.replace('CAT Price:', '').strip()
        stamp['cat_price'] = cat_price
    except: 
        stamp['cat_price'] = None   
        
    try:
        scott_num = html.select('.cat-number')[0].get_text().strip()
        scott_num = scott_num.replace('CAT #:', '').strip()
        stamp['scott_num'] = scott_num
    except: 
        stamp['scott_num'] = None  
     
    try:
        stock_num = html.select('.stock .stock')[0].get_text().strip()
        stock_num = stock_num.replace(' in stock', '').strip()
        stamp['stock_num'] = stock_num
    except: 
        stamp['stock_num'] = None      
        

    try:
        price = html.select('.price .woocommerce-Price-amount')[0].get_text().strip()
        stamp['price'] = price.replace('$', '').strip()
    except: 
        stamp['price'] = None
        
    stamp['currency'] = 'CAD'
    stamp['category'] = category
    
     
    try:
        breadcrumb = html.select('.breadcrumbs')[0]
        breadcrumb_parts = str(breadcrumb).split('<i class="fa fa-angle-right"></i>')
        subcategory = breadcrumb_parts[2].replace('&amp;', '&').strip()
    except:
        subcategory = None
    
    stamp['subcategory'] = subcategory

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('.woocommerce-product-gallery__image a')
        for image_item in image_items:
            img_item = image_item.get('href')
            img_parts = img_item.split('?')
            img = img_parts[0]
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
    
    keywords = ''
    try:
        keyword_items = html.select('.tags a')
        for keyword_item in keyword_items:
            keyword = keyword_item.get_text().strip()
            if keywords:
                keywords += ','
            keywords += keyword
    except:
        pass
    
    stamp['keywords'] = keywords 
    
    try:
        raw_text = html.select('.description')[0]
        raw_text = raw_text.replace('Description ', '').strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title']
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('.product .lnk'):
            item_link = item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_url_elem = html.select('a.lnk-next-page')[0]
        if next_url_elem:
            next_url = next_url_elem.get('href')
    except:
        pass   
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_subcategories(category):
    
    items = []
    
    url = 'https://chrisgreen.ca/inventory/'

    try:
        html = get_html(url)
    except:
        return items

    try:
        for subcat_cont in html.select('ul.subcategories'):
            cat_item = subcat_cont.parent.select('a')[0]
            if cat_item:
                cat_item_name = cat_item.get_text().strip()
                if cat_item_name == category:
                    for subcat_item in  subcat_cont.select('li a'):
                        item_link = subcat_item.get('href') 
                        if item_link not in items:
                            items.append(item_link)
    except: 
        pass
    
    shuffle(items)
    
    return items

categories = {
    'British Commonwealth',
    'Canada & BNA',
    'Germany'
}
    
for category in categories:
    print(category) 

selection = input('Choose category: ')
           
subcategories = get_subcategories(selection)
for subcategory in subcategories:
    page_url = subcategory
    while(page_url):
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            stamp = get_details(page_item, selection)
