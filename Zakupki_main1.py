#!/usr/bin/python3

import requests
from lxml.html import fromstring
from bs4 import BeautifulSoup
from datetime import date, timedelta
import xlwt
import argparse
import time
import logging

VERBOSITY_TO_LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}
SITE = "http://www.zakupki.gov.ru"
SEARCH_URL = "http://www.zakupki.gov.ru/epz/order/extendedsearch/results.html"
DEAL_URL = "http://www.zakupki.gov.ru/epz/order/" \
           "notice/ea44/view/supplier-results.html"
KEY_WORDS = ["Льговское сельское поселение"]
DELAY = 10

#формируем URL запрос для поиска необходимой информации
def create_url(searchString, updateDateFrom, params, pageNumber = 1):

    if params == 'n':
        #задаем фильтры для поиска
        payload = {"searchString": searchString,
                   "pageNumber": pageNumber,
                   "fz44": "on",
                   "ppRf615": "on", "af": "on", "ca": "on",
                   "priceFromGeneral": "500000", "recordsPerPage": "_50",
                   "updateDateFrom": updateDateFrom,
                   "updateDateTo": date.today().strftime('%d.%m.%Y')#,
                   #"districts": "5277336"
                   }
    if params == 'o':
        payload = {"searchString": searchString,
                   "pageNumber": pageNumber,
                   "fz44": "on",
                   "ppRf615": "on", "pc": "on",
                   "priceFromGeneral":  "500000", "recordsPerPage": "_50",
                   "updateDateFrom": updateDateFrom,
                   "updateDateTo": date.today().strftime('%d.%m.%Y'),
                   "districts": "5277336"}
    #логирование в консоль заданных фильтров
    logging.debug('payload is \n{}'.format(payload))
    #присвоение переменной адреса и фильтров
    url = requests.get(SEARCH_URL, params=payload)
    url.encoding = 'UTF-8'
    return url.url

#задаем параметры метаданных
def get_page(search_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url=search_url, headers=headers)
    response.encoding = 'UTF-8' #кодировка с поддержкой кириллицы
    return response

#сохранение спарсенных данных в файл
def save(text):
    with open('test.html', 'w') as f:
        f.write(text)

#
def get_info(response):
    response = response.text
    html = BeautifulSoup(response, 'html.parser')
    #записываем в переменную расположение блока(div) (DOM - модель) где хранится требуемая информация для парсинга
    deals = html.find_all('div',
                          class_='search-registry-entry-block')
    #записываем в переменную расположение блока(div) (DOM - модель) где хранятся информация о количестве найденных записей
    all_records = html.find('div', class_="search-results__total")
    #конвертируем в строку записанное кол-во записей
    all_records = fromstring(str(all_records)).xpath('//div/text()')[0]

    print('Найдено записей:', all_records)

    #проверка на пустое значение переменной, если пустое, то выводит сообщение "ничего не найдено",
    #в противном случае выводит полученные данные
    if all_records is None:
        logging.debug("Ничего не найдено")
        return None, None
    else:
        #all_records = fromstring(str(all_records)).xpath('//div/text()')#[0]
        all_records = 50
        logging.debug(
            "total numbers of all_records {}".format(all_records))
    info = [{"Deal": ["Price", "FZ", "Status",
                      "Customer", "Create", "Update", "Link"]}]
    #цикл проходит по DOM-модели и записывает в переменные по указанному пути значения
    for deal in deals:
        zakupka_str = fromstring(str(deal))

        #номер закупки. Ищет div (блок) с классом N и берет из него только текстовое значение (с помощью функции text())
        #это осуществялется благодаря подключенной библиотеке xpath.
        number = zakupka_str.xpath(
            '//div[contains(@class, "registry-entry__header-top__number")]'
            '//a/text()')[0].strip()
        number = ''.join(c for c in number if c.isdigit())

        #ссылка на закупку. Берет значение по аналогии с номером
        href = zakupka_str.xpath(
            '//div[contains(@class, "registry-entry__header-top__number")]//a/@href')[0]
        #проверка если переменная содержит в себе строку, которая начинается с  "/",
        #то переменная href дополняется адресом закупок
        if  href[0] == '/':
            href = SITE + href

        #try - попытка воспроизвести код ниже до except, если код не воспроизводится корректно (нет цены закупки),
        #то осуществялется переход сразу к except
        try:
            #цена. по аналогии
            price = zakupka_str.xpath(
                '//div[contains(@class, "price-block__value")]'
                '/text()')[0].strip()
            #проверка переменной на содержание числовых значений
            price = ''.join(c for c in price if c.isdigit())
            #конвертация в целочисленный вид
            price = int(price)
        #если цену не удалось получить, то выполняем дальше
        except IndexError:
            price = None
        #получаем ФЗ
        fz = zakupka_str.xpath(
            '//span[contains(@class, "registry-entry__header-mid__fz")]/text()')[0].strip()
        #получаем статус закупки
        status = zakupka_str.xpath('//div[contains(@class, "registry-entry__header-top__title") ]'
                                   '/text()')[0].strip()[:-2]
        #получаем заказчика
        customer = zakupka_str.xpath(
            '//div[contains(@class, "registry-entry__body-href")]'
            '/a/text()')[0].strip()
        #дата создания
        create = zakupka_str.xpath('//div[contains(@class, "data-block__value")]'
                                   '/text()')[0].strip()
        #дата обновления
        update = zakupka_str.xpath('//div[contains(@class, "data-block__value")]'
                                   '/text()')[0].strip()
        #в переменную info добавить в конец (append) следующие значения переменных
        info.append({number: [price, fz, status,
                              customer, create, update, href]})
    return info, all_records

#функция, которая позволяет спарсить данные исполнителя закупки
def extract_distributor(deals_info):
    #начало цикла
    for deal in deals_info[1::]:
        #cоздание списка с ключами
        deal_number = list(deal.keys())[0]
        #присвоение переменной 1-го элемента массива
        fz = deal[deal_number][1]
        # если фз=44, то формируется запрос
        if fz == "44-ФЗ":
            url = requests.Request('GET',
                                   DEAL_URL,
                                   params={"regNumber": deal_number}).prepare()
            deal_page = get_page(url.url)
            logging.debug("Извлечение информации о поставщике из \n {} \n".format(url.url))
            time.sleep(DELAY)
            print(deal_page)
            try:
                #используя DOM модель обращаемся к блоку div с классом noticetabBox и извлекаем текст
                player_1 = fromstring(str(deal_page.text)).xpath(
                    '//div[contains(@class, "noticeTabBox")'
                    ' and '
                    'contains(@class, "padBtm20")]'
                    '/div/div/table/tr[2]/td[3]/text()')[0].strip()
            except IndexError:
                player_1 = None
         #   try:
                #
           #     player_2 = fromstring(str(deal_page.text)).xpath(
            #        '//div[contains(@class, "noticeTabBox") '
            #       'and contains(@class, "padBtm20")]'
              #      '/div/div/table/tr[3]/td[1]/text()')[0].strip()
            #except IndexError:
              #  player_2 = None
            #изменяем формат
            players = "{}".format(player_1)#, player_2)
            print(players)
            #логирование
            logging.debug('Победители {}'.format(players))
            deal[deal_number].append(players)
    return deals_info


def create_report(wb, deals_info, searchString, type):
    #cоздает страницу в книге (excel)
    ws = wb.add_sheet(searchString)
    #задание параметров для колонок в таблице и задание стилей
    ws.col(0).width = 256 * 20
    ws.col(3).width = 256 * 20
    ws.col(4).width = 256 * 60
    ws.col(5).width = 256 * 10
    ws.col(6).width = 256 * 10
    ws.col(7).width = 256 * 20
    ws.col(8).width = 256 * 60
    style = xlwt.XFStyle()
    style.alignment.wrap = 1
    #проверка условия заданного параметра запуска
    if type == 'o':
    #добавляет в массив победителей закупок
        deals_info[0]["Закупка"].append("Победители")
    for (j, deal_info) in enumerate(deals_info):
        #возвращает номер элемента из списка
        deal_number = list(deal_info.keys())[0]
        ws.write(j, 0, deal_number, style)
        for (k, info) in enumerate(deal_info[deal_number]):
            ws.write(j, 1 + k, info, style)

#функция, которая отправляет поисковый запрос в ЕИС
def search(word, dateFrom, mode, pageNumber=1):
    url = create_url(word, dateFrom, mode, pageNumber)
    logging.info('Отправка URL \n {}'.format(url))
    response = get_page(url)
    logging.info("Ожидание {} секунд.....\n".format(DELAY))
    return response


def create_parser():
    #записывает в переменную дату (сегодня мину 2 недели)
    week_ago = date.today() - timedelta(weeks=2)
    #
    parser = argparse.ArgumentParser(description='zakupki')
    #добавляет аргумент "-s"
    parser.add_argument('-s', default=KEY_WORDS,
                        type=str, help="searchString")
    #добавляет аргумент "-df"
    parser.add_argument('-df', default=week_ago.strftime('%d.%m.%Y'),
                        type=str, help="date in format d.m.Y")
    #добавляет аргумент "-m" (
    parser.add_argument('--mode', '-m', default='n', type=str,
                        help="n - find new deals \n o - find old deals")
    #добавляет аргумент '-v'
    parser.add_argument('--verbose', '-v', type=int, default=0)
    return parser

#основная часть, где происходит вызов всех функций
if __name__ == '__main__':
    #вызов функции и запись в переменную возвращаемых данных из функции
    parser = create_parser()
    #аналогично
    args = parser.parse_args()
    logging_level = VERBOSITY_TO_LOGGING_LEVELS[args.verbose]
    logging.basicConfig(level=logging_level)
    #вызов библиотки, создающей excel
    wb = xlwt.Workbook()
    for word in KEY_WORDS:
        #Запись в переменную результатов функции search
        response = search(word, args.df, args.mode)
        #пауза
        time.sleep(DELAY)
        #запись нескольких переменных из функции, которая возвращает 2 результата
        deals_info, number_of_records = get_info(response)
        print(deals_info)
        logging.info("Количество записей {}".format(number_of_records))
        #если количество записей больеш 50, то цикл по беребору страниц и прарсингу информации с них
        if number_of_records is not None and int(number_of_records) > 50:
            pageAmount = number_of_records // 50 + 1
            logging.info("pageAmount is {}".format(pageAmount))
            for pageNumber in range(1, pageAmount):
                print(pageNumber)
                logging.info("Новая посиковая страница {}".format(pageNumber))
                response = search(word, args.df, args.mode, pageNumber)
                time.sleep(DELAY)
                #deals_info += get_info(response)[0]
                deals_info.append(get_info(response)[0])
                print(deals_info)
        if args.mode == 'o' and deals_info is not None:
            logging.info('Начато извлечение исполнителей........')
            deals_info = extract_distributor(deals_info)
        if deals_info is not None:
            logging.info(deals_info)
            create_report(wb, deals_info, word, args.mode)
    logging.info('Сохранено как ./Report {}_{}.xls'.format(date.today(), args.mode))
    #сохранение в файл спрасенных данных
    wb.save('./Report {}_{}.xls'.format(date.today(), args.mode))
