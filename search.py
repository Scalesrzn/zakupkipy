def search(word, dateFrom, pageNumber=1):
    url = create_url(word, dateFrom, pageNumber)
    logging.info('Отправка URL \n {}'.format(url))
    response = get_page(url)
    logging.info("Ожидание {} секунд.....\n".format(DELAY))
    return response

#задаем параметры метаданных
def get_page(search_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url=search_url, headers=headers)
    response.encoding = 'UTF-8' #кодировка с поддержкой кириллицы
    return response
