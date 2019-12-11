# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup
# import json

import matplotlib.pyplot as plt
from functools import reduce
from datetime import date

flats = []
info = []

CHROMEDRIVER_PATH='/app/.chromedriver/bin/chromedriver'
GOOGLE_CHROME_BIN='/app/.apt/usr/bin/google-chrome'


def parse(street="Москва, улица Берзарина, 21"):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.binary_location = GOOGLE_CHROME_BIN
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    driver.switch_to.frame = 0

    street = street.replace(",", "%2C").replace(" ", "%20")

    url = f"https://realty.yandex.ru/otsenka-kvartiry-po-adresu-onlayn/{street}/kupit/kvartira/"

    driver.get(
        "https://passport.yandex.ru/auth?retpath=https%3A%2F%2Fpassport.yandex.ru%2Fprofile&noreturn=1")
    time.sleep(5)

    driver.find_element_by_id("passp-field-login").send_keys("SLSProg")
    time.sleep(2)
    driver.find_element_by_class_name("button2_type_submit").click()
    time.sleep(2)
    driver.find_element_by_id("passp-field-passwd").send_keys("1223334444")
    time.sleep(2)
    driver.find_element_by_class_name("button2_type_submit").click()
    time.sleep(5)
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    info.append(soup.find("h2", class_="BuildingInfo__header").text)
    for i in soup.findAll("div", class_="BuildingInfo__feature"):
        info.append(i.text.replace("\xa0", " "))

    def find(soup):
        for i in soup.find("div", class_="OffersArchiveSearchOffers__body").findAll("div", class_="OffersArchiveSearchOffers__row"):
            data = i.findAll("div", class_="OffersArchiveSearchOffers__cell")
            tip = data[1].find("span").text.replace(
                "\xa0", " ").replace("\u20bd", "RUB")
            last_price = data[3].find("div", class_="OffersArchiveSearchOffers__price").find(
                "span", class_="price").text.replace("\xa0", " ").replace("\u20bd", "RUB")
            last_price_per_metr = data[3].find("div", class_="OffersArchiveSearchOffers__extra-info").find(
                "span", class_="price").text.replace("\xa0", " ").replace("\u20bd", "RUB")
            date_of_publication = data[4].text.replace(
                "\xa0", " ").replace("\u20bd", "RUB")
            srok_of_exposition = data[4].find(
                "div", class_="OffersArchiveSearchOffers__extra-info").text.replace("\xa0", " ").replace("\u20bd", "RUB")

            state = data[5].text.replace("\xa0", " ")
            flats.append({
                "title": tip,
                "last_price": last_price,
                "last_price_per_metr": last_price_per_metr,
                "date_of_publication": date_of_publication,
                "srok_of_exposition": srok_of_exposition,
                "state": state})

    find(soup)
    count = 2
    running = True
    while running:

        driver.get(url + str(count) + "/")
        time.sleep(4)

        try:
            BeautifulSoup(driver.page_source, "html.parser").find(
                "div", class_='OffersArchiveSearchOffers__not-found').text
            driver.close()
            running = False
        except NoSuchElementException:
            time.sleep(1)
            find(BeautifulSoup(driver.page_source, "html.parser"))
            count += 1
        except AttributeError:
            time.sleep(1)
            find(BeautifulSoup(driver.page_source, "html.parser"))
            count += 1


def diff_dates(date1, date2):
    return abs(date2 - date1).days


def redact_price(price):
    price = reduce(lambda x, y: x + y, price.split()[:-1])
    price = int(price)
    if price <= 10000:
        return price * 1000
    return price


def redact_date(date0):
    date0 = date0.split('В')[0]
    date0 = list(map(int, date0.split('.')))
    date0.reverse()
    return date0


def redact_room(room):
    room = (room.split()[-1]).split('-')[0]
    return int(room)


#################################################
# street = ''
#################################################


def redact_input(street):
    # street, building = parse(street)
    parse(street)

    global flats
    building = info

    AveragePrice = 0
    CurrentPrice = [0, 0]
    AverageExposition = 0
    CountRooms = [0] * 7
    CountExpos = [0] * 7
    CountCost = [0] * 7
    YearCost = {}
    YearMinimum = 10000
    CurrentCountFlats = 0

    CountFlats = len(flats)

    # for i in flats:
    while len(flats) > 0:
        i = flats.pop()

        # rooms info

        room = redact_room(i['title'])
        CountRooms[room - 1] += 1
        CountCost[room - 1] += redact_price(i['last_price_per_metr'])
        CountExpos[room - 1] += int((i['srok_of_exposition']).split()[2])

        # time info
        thisY = redact_date(i['date_of_publication'])[0]
        YearMinimum = min(YearMinimum, thisY)
        PublicationDate = date(*redact_date(i['date_of_publication']))

        if diff_dates(date.today(), PublicationDate) <= 730:
            CurrentPrice[0] += redact_price(i['last_price_per_metr'])
            CurrentPrice[1] += 1

        AverageExposition += int((i['srok_of_exposition']).split()[2])

        AveragePrice += redact_price(i['last_price_per_metr'])

        if thisY in YearCost:
            YearCost[thisY][0] += redact_price(i['last_price_per_metr'])
            YearCost[thisY][1] += 1
        else:
            YearCost[thisY] = [redact_price(i['last_price_per_metr']), 1]

        if i['state'] == 'В продаже':
            CurrentCountFlats += 1

    for i in range(7):
        if CountRooms[i] != 0:
            CountExpos[i] //= CountRooms[i]
            CountCost[i] //= CountRooms[i]

    AverageExposition //= CountFlats
    AveragePrice //= CountFlats
    CurrentPriceFin = CurrentPrice[0] // CurrentPrice[1]

    for i in YearCost:
        AA, BB = YearCost[i][0], YearCost[i][1]
        YearCost[i] = AA // BB

    x_coords = sorted(YearCost.keys())
    y_coords = [YearCost[i] for i in x_coords]
    plt.plot(x_coords, y_coords)
    # plt.show()
    plt.savefig('graphic.png')

    # Формирование вывода

    Output = ''
    Output += street + '\n\n'
    for i in range(len(building) - 1):
        Output += building[i] + '. '
    if len(building) != 0:
        Output += building[-1] + '.\n'

    Output += f'Сейчас в продаже {CurrentCountFlats} квартир'
    if CurrentCountFlats % 10 in [1]:
        Output += 'а'
    elif CurrentCountFlats % 10 in [2, 3, 4]:
        Output += 'ы'

    letter1 = 'о'
    letter2 = ''
    if CountFlats % 10 in [1]:
        letter1 = 'а'
        letter2 = 'а'
    if CountFlats % 10 in [2, 3, 4]:
        letter1 = 'о'
        letter2 = 'ы'
    Output += f'.\nВсего с {YearMinimum} года в продаже был{letter1} {CountFlats} квартир{letter2}.\n'

    wordlist = ['дней', 'день', 'дня', 'дня', 'дня',
                'дней', 'дней', 'дней', 'дней', 'дней']
    Output += f'В среднем объявление в экспозиции {AverageExposition} {wordlist[AverageExposition%10]}.\n'

    Output += f'Продажа: средняя цена {AveragePrice//1000}.{AveragePrice%1000} р/кв.м\n'

    letter1 = 'й'
    if CountFlats % 10 == 1:
        letter1 = 'я'
    Output += f'Из {CountFlats} объявлени{letter1} о продаже:\n'
    for i in range(7):
        if CountRooms[i] != 0:
            Output += f'{i + 1}-комнатные - {CountRooms[i]} - В среднем в экспозиции {CountExpos[i]} {wordlist[CountExpos[i]%10]}. Ср. цена {CountCost[i]//1000}.{CountCost[i]%1000} р/кв.м\n'
    Output += f'\nАктуальная цена - {CurrentPriceFin//1000}.{CurrentPriceFin%1000} р/кв.м'

    return Output


print(redact_input("Москва, улица Берзарина, 21"))
