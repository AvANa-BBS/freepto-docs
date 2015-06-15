#!/usr/bin/env python3

import os
import sys
import shutil
from urllib.request import urlopen, urlretrieve
from urllib.parse import urljoin, urlsplit
from datetime import datetime

from bs4 import BeautifulSoup
from bs4.element import Comment


def remove_js(content):
    '''remove js inclusion'''
    # Bit of cleanup
    scripts = content.find_all('script')
    for s in scripts:
        s.replace_with(Comment("script rimosso"))


def download_url(pageurl, target, div_id):
    imgdir = target + "_files"

    def get_external(el, tag):
        if not os.path.exists(imgdir):
            os.mkdir(imgdir)
        resource_url = urljoin(pageurl, el[tag])
        base = urlsplit(resource_url).path.split('/')[-1]
        target = os.path.join(imgdir, base)
        if not os.path.exists(target):
            urlretrieve(resource_url, filename=target)
        el[tag] = os.path.join(os.path.basename(imgdir), base)

    p = BeautifulSoup(urlopen(pageurl))
    content = p.find_all('div', id="%s" % div_id).pop()
    if content is None:
        raise Exception("cant' find #wiki_html; not a we.riseup.net page?")
    head = p.find('head')
    remove_js(p)


    # Images
    for image in content.find_all("img"):
        get_external(image, "src")
    for css in p.find_all("link"):
        get_external(css, "href")
    shutil.copy("%s/screen.css" %os.getcwd(), imgdir)

    # Finally, write to disk!
    content = '''<html>%(head)s<body>
    <div class="content_box"><div class="wiki">%(body)s</div></div>
    <div class="creation-notes">
    This is a copy of <a href="%(url)s">%(url)s</a>, taken on %(date)s
    </div>
    </body></html>''' % {'head': head, 'body': content, 'url': pageurl,
                         'date': datetime.now().strftime('%d %B %Y')}

    with open(target, 'w', encoding='utf-8') as buf:
        buf.write(content)

if __name__ == '__main__':
    download_url(sys.argv[1], sys.argv[2], sys.argv[3])
