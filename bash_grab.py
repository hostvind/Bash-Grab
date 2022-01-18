import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time

t_start = datetime.now()

if not os.path.exists('Strips'):
    os.makedirs('Strips')

url_prefix = 'https://bash.im'
url_suffix = '/strips'

g_counter = 0
g_last = ''
g_debug = ' '
g_name = 'blank'

f_errors = open('errors.log', 'a+')
f_date = open('date_list.txt', 'w')
f_date.write('')

f_errors = open('errors.log', 'w')
f_errors.write('')


def le_IMG(subject):
    global g_debug, g_counter, g_name
    print('===========================================\r\n')
    imgurl = subject.find("img").get('data-src')
    ext = '.' + imgurl.split('.')[1]
    print('URL = ' + imgurl)

    hrefs = subject.find("div", class_='quote__author').find_all("a")
    strip = str(hrefs[0].text)
    strip = int(strip)
    print('Strip #: ' + '{:04d}'.format(strip))
    date = str(hrefs[0].get('href')).split("/")[2]
    print('Date is: ' + date)
    if (len(hrefs) == 3):
        author = str(hrefs[1].text)
        print('Author: ' + author)
        quote = str(hrefs[2].text.split('#')[1])
        print('Quote#: ' + quote)
        g_name = '{:04d}'.format(strip) + '_' + author + '_' + quote + ext
    elif (len(hrefs) == 2):
        selection = subject.find('div', class_='quote__author')

        author_block = selection.text.lstrip()
        trim_head = author_block.find('Нари')
        trim_end = author_block.find('по мотив')
        if (trim_end == -1):
            trim_end = len(author_block)
        author_block = author_block.lstrip()[trim_head:trim_end].split(' ')
        author_block.pop(0)
        author = ' '.join(author_block).lstrip()
        if author[len(author)-1] == ' ':
            author = author[:-1]
        print('Author: ' + author)

        if (selection.text.lstrip().find("#") != -1):
            quote = str(hrefs[1].text.split('#')[1])
            print('Quote#: ' + quote)
            g_name = '{:04d}'.format(strip) + '_' + author + '_' + quote + ext
        else:
            g_name = '{:04d}'.format(strip) + '_' + author + ext

    image = requests.get(url_prefix+'/'+imgurl)
    f_strip = open('Strips/' + g_name, 'wb')
    f_strip.write(image.content)
    f_strip.close()

    f_date.write('{:04d}'.format(strip) + '\t' + date + '\r\n')
    print(g_name + ' Done\r\n')
    g_counter += 1


keep_on = True
while (keep_on is True):
    # keep_on = False
    myReq = requests.get(url_prefix+url_suffix)
    soup = BeautifulSoup(myReq.text, 'html.parser')

    images = soup.find_all('article', class_='quote strip')

    f_page = open('page.txt', 'w')
    for x in images:
        f_page.write(str(x)+'\r\n')
    f_page.close()

    navs = soup.find_all(class_='pager__item')
    next_button = navs[2]

    if (str(next_button).find('href') >= 0):
        url_suffix = next_button.get('href')
    else:
        print('this is the very end')
        keep_on = False

    for x in images:
        try:
            le_IMG(x)
        except Exception as e:
            print("Unsuccessful attempt on count "+str(g_counter))
            print("Exception message: " + str(e))
            print(g_debug)
            f_errors.write(str(g_counter) + ' failed after '
                           + str(g_last) + '\r\n')
            break
        finally:
            g_debug = ''

f_errors.close()
f_date.close()

t_end = datetime.now()
print("Start Time =", t_start.strftime("%H:%M:%S"))
print("End Time =", t_end.strftime("%H:%M:%S"))
t_run = t_end-t_start
print("Run Time =", t_run)
