from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)
CORS(app)

url = "https://ruvuz.ru/barnaul"
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"
}

def formatEga(arg):
    s = arg.replace("Средний балл\nЕГЭ: ", "")
    if s == "None":
        return "Нету"
    else:
        return s

def formatRating(arg):
    s = arg.replace("Рейтинг: ", "")
    return s

@app.route('/unis', methods=['GET'])
def parse():
    try:
        page = requests.get(url, headers=headers)
        soup = bs(page.content, "html.parser")
        container = soup.find("div", class_="page-content__univers")
        items = container.findAll("div", class_="univer__item")

        unis = []

        for item in items:

            price_head = item.findAll("div", class_="univer__item__price-head")

            title = item.find("h3", class_='univer__item-head')
            uni_link = title.find('a')

            specialnosti_container = item.find("div", class_="univer__item-bottom-col-content__item")
            spec = specialnosti_container.find('b').get_text(strip = True)

            params = item.find("div", class_="univer__item__param-items")
            params_items = params.findAll("div", class_="univer__item__param-item")
            params_out = []

            for p in params_items:
                params_out.append( { 'param': p.get_text(strip = True) } )

            unis.append({
                'title': title.get_text(strip = True),
                'link': "https://ruvuz.ru" + uni_link.get('href'),
                'ega': formatEga(price_head[0].get_text(strip = True)),
                'rating': formatRating(price_head[1].get_text(strip = True)),
                'spec': params_out
                
            })

        return jsonify(unis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Page not found'}), 404

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=2365)