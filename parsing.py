import requests
from bs4 import BeautifulSoup as BS

res = {}


def collect_data():
    for offset in (0, 30):
        page_html = requests.get(
            fr'https://news.sportbox.ru/Vidy_sporta/Hokkej/KHL?page_size=30&page_offset={offset}&plain_content=1')

        soup = BS(page_html.content, 'lxml')

        block = soup.find_all(
            'div', class_="_Sportbox_Spb2015_Components_TeazerBlock_TeazerBlock")
        for number, item in enumerate(block, offset + 1):
            title = item.find('div', class_='title').find(
                'span', class_='text').text
            link = f"https://news.sportbox.ru{item.find('a', class_='').get('href')}"
            res[number] = [title, link]
    return res


def main():
    collect_data()


if __name__ == '__main__':
    main()
