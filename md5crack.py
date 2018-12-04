#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2016 Sutrisno Efendi <kangfend@gmail.com>
# Crack md5 hash via http://hashkiller.co.uk

import argparse
import cfscrape
import os
import requests
import StringIO

from PIL import Image
from pyquery import PyQuery


HOST = 'https://www.hashkiller.co.uk'
SLICESIZE = 64
FILEOUT = "results.txt"

def crack(md5List, auto=True):
    scraper = cfscrape.create_scraper()
    response = scraper.get(HOST + '/md5-decrypter.aspx')

    # Save headers and cookies, to be used in next request
    session = requests.session()
    session.headers = response.headers
    session.cookies = response.cookies

    query = PyQuery(response.content)
    image_path = query("#content1_imgCaptcha").attr("src")
    image_content = scraper.get(HOST + image_path).content

    # Trying to decaptcha image
    captcha_image = Image.open(StringIO.StringIO(image_content))
    captcha_image.show()
    captcha = raw_input("[+] Input captcha: ")

    scraper = cfscrape.create_scraper(sess=scraper)
    response = scraper.post(HOST + '/md5-decrypter.aspx', data={
        'ctl00$ScriptMan1': 'ctl00$content1$updDecrypt|ctl00$content1$btnSubmit',
        'ctl00$content1$txtInput': md5List,
        'ctl00$content1$txtCaptcha': captcha,
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': query("#__VIEWSTATE").attr("value"),
        '__EVENTVALIDATION': query("#__EVENTVALIDATION").attr("value"),
        '__ASYNCPOST': 'true',
        'ctl00$content1$btnSubmit': 'Submit',
        query('#content1_pnlStatus input').attr('name'): query('#content1_pnlStatus input').attr('value')
    })
    response = PyQuery(response.content)
    status = response('#content1_lblStatus').text()
    result = response('#content1_lblResults .text-green, #content1_lblResults .text-red').text().replace('[Not found]', 'Not_found').split()
    return status, result

def chunks(listMD5, chunkSize):
    chunkSize = max(1, chunkSize)
    return (listMD5[i:i+chunkSize] for i in xrange(0, len(listMD5), chunkSize))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Crack md5hash over https://hashkiller.co.uk')
    parser.add_argument('file', nargs='+', help='file with md5 hash list')
    args = parser.parse_args()
    if args.file:
        inputFile = args.file[0]
        if os.name == "posix":
            os.system("clear")
        else:
            os.system("cls")
        print "[+] Looking for your hashes..."

        while True:
            try:
                with open(inputFile, 'r') as f:
                    listMD5 = f.readlines()
                # Max 64 hashes per request
                partials = chunks(listMD5, SLICESIZE)
                with open(FILEOUT, 'w') as outf:
                    for chunk in partials:
                        cracking = crack(''.join(chunk))
                        if cracking:
                            print cracking[1]
                            print cracking[0]
                            for result in cracking[1]:
                                if result != 'Not_found':
                                    outf.write( result + '\n')
                                else:
                                    outf.write('\n')
                            print "[+] Chunk Results: " + cracking[0]
                        else:
                            continue
                print: "Check file " + FILEOUT
                exit()
            except KeyboardInterrupt:
                print "\b\b[!] Thanks for using this tool."
                exit()
            except Exception as error:
                print "\b\b[-] %s" % error.message
                exit()
    else:
        parser.print_help()
