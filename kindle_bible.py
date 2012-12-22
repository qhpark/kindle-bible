#!/bin/env python
# -*- coding: UTF-8 -*-
#
# Bible Scraper
#
# Downloads and locally caches bible contents and generate opf, ncx, html pages
# for mobipocket to generate prc files for Kindle.
# - support nav points for easy navigation.
#
# Q-Ha Park
# 01/08/2010

# vim:set encoding=utf-8

# history
# v0.2 - public domain
# v0.1 - first version (do not distribute)

formatting_version = 'v0.20'

import os
import re
import sys
import time
from urllib import urlopen
from math import sqrt


# options
enable_quicklinks = False
enable_navpoints  = True
#double_build = True
double_build = False
double_use_table = False
#debug = True
debug = False

# bible version
# set double_build to FALSE, if you need one book only.
version = ['RHV', 'NIV']

class Encode:
    def __init__(self, stdout, enc):
        self.stdout = stdout
        self.encoding = enc
    def write(self, s):
        self.stdout.write(s.encode(self.encoding))

sys.stdout = Encode(sys.stdout, 'utf-8')
# useful variables
default_encoding = 'euc-kr'
out_encoding = 'cp949'
# bible list
bible_list = \
    {        \
       'SAE' :                                         \
            {                                          \
                'name' : u'새번역성경',                \
                'lang' : u'kor',                       \
                'enc'  : u'euc-kr',                    \
            },                                         \
       'GAE' :                                         \
            {                                          \
                'name' : u'개역개정',                  \
                'lang' : u'kor',                       \
                'enc'  : u'euc-kr',                    \
            },                                         \
       'AGAPE' :                                       \
            {                                          \
                'name' : u'쉬운성경',                  \
                'lang' : u'kor',                       \
                'enc'  : u'euc-kr',                    \
            },                                         \
#      'DURRANO' :                                     \
#           {                                          \
#               'name' : u'우리말성경',                \
#               'lang' : u'kor',                       \
#               'enc'  : u'euc-kr',                    \
#           },                                         \
       'HDB' :                                         \
            {                                          \
                'name' : u'현대인',                    \
                'lang' : u'kor',                       \
                'enc'  : u'euc-kr',                    \
            },                                         \
       'RHV' :                                         \
            {                                          \
                'name' : u'개역한글',                  \
                'lang' : u'kor',                       \
                'enc'  : u'euc-kr',                    \
            },                                         \
       'NIV' :                                         \
            {                                          \
                'name' : u'New International Version', \
                'lang' : u'eng',                       \
                'enc'  : u'utf-8',                     \
            },                                         \
       'KJV' :                                         \
            {                                          \
                'name' : u'King James Version',        \
                'lang' : u'eng',                       \
                'enc'  : u'utf-8',                     \
            }                                          \
    }

bible_translate = \
{\
    'kor' : [u'성서', u'구약', u'신약'],\
    'eng' : [u'Holy Bible', u'The Old Testament', u'The New Testament'],\
}


def version_str():
    debug_str = ''
    if debug:
        debug_str = '_debug'
    if (double_build):
        return _u(version[0] + '_' + version[1]) + debug_str
    else:
        return _u(version[0]) + debug_str

# whole book - to flush to a file later
opf_file       = ''
cover_html     = ''
toc_html       = ''
toc_ncx        = ''
body_html      = ''
body_html_list = []

# book : # chapter list
bible_info = []

# number of chapters
old_test_num = 39
new_test_num = 27
total_num_books = old_test_num + new_test_num
if debug:
    total_num_books = 4
# title
# group 1 - Book - Chapter Number "Chapter'
# group 2 - Book - Chapter Number 
# group 3 - Book 
# group 4 - Chapter Number 
re_title = re.compile(r'http://www.holybible.or.kr/images/arrow.gif .*?> <b>(((.*?) ([0-9]+))(.*)) \[.*\]</b>')
# valid chapter
re_check = re.compile(r'<ol')
# verse
re_verse = re.compile(r'<li><font .*?>(.*?)</font>')
# link
re_link = re.compile(r'<a href=.*?>(.+?)</a>')

def check_valid(data):
    if re_check.search(data):
        return True
    else:
        return False

def get_verse(verse):
    # get whatever is in <li>
    # v = re_verse.match(verse).group(1)
    return re_link.sub(r'\1', verse).strip() 
     
def get_bible(ver, book, chapter):
    frl = './%s/BK%02d_CH%03d.html' % (ver,book,chapter)
    url = 'http://www.holybible.or.kr/B_%s/cgi/bibleftxt.php?VR=%s&VL=%d&CN=%d' \
            % (ver,ver,book,chapter)
    # check if we have cached web files to local drive.
    if (os.path.isfile(frl) == False):
        text = urlopen(url).read()
        if (os.path.exists(ver) == False):
            os.mkdir(ver)
        f = open(frl, 'wb')
        f.write(text)
        f.close()
        return text
    # already cached
    f = open(frl, 'rb');
    text = f.read()
    f.close
    return text


def print_kr (str):
    #print unicode(str,'euc-kr').encode('utf-8')
    print unicode(str,'euc-kr')
def _k(str):
    return unicode(str,'cp949')
def _u(str):
    return unicode(str)
def _enc(str, ver):
    return unicode(str, bible_list[ver]['enc'])

         #     u'<meta http-equiv="Content-Type"' + \
         #     u'content="text/html" charset="%s">\n' % out_encoding +\
         #     u'</head>\n' + \
               #u'<head>\n' + 
doc_type = u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n' +\
           u'   "http://www.w3.org/TR/html4/loose.dtd">\n'
def html_start(start, handle = ''):
    if (start):
        return doc_type + \
               u'<html>\n' + \
               u'<head>\n' + \
               u'<meta http-equiv="Content-Type" content="text/html;charset=%s" >'\
               % "euc-kr" + \
               u'<title>Bible (%s)</title>' % handle + \
               u'<style type="text/css">\n' + \
               u'a { text-decoration:none }\n' +\
               u'</style>\n' +\
               u'</head>\n' + \
               u'<body>\n'

               # euc-kr above should be '% out_encoding + \ '
    else:
        return u'</body>\n</html>\n'
#def html_label(book_idx, chap_idx):
#    return u'<a name="_Q_%d_%d_0"></a>' % (book_idx, chap_idx )
def html_label(book_idx, chap_idx = 0, verse_idx = 0):
    return u'<a name="_Q_%d_%d_%d"></a>\n' % (book_idx, chap_idx, verse_idx)

def html_link(tag, book_idx, chap_idx = 0, verse_idx = 0, file = ''):
    return u'<a href="%s#_Q_%d_%d_%d">%s</a>' % (file, book_idx, chap_idx, verse_idx, tag)

def html_table(data, border=0, width = '', align ='', valign='' ):
    return u'<table border=%d width=%s align=%s, valign=%s >%s</table>' % (border, width, align, valign, data)

def html_add_tr(element):
    return u'<tr>%s</tr>' % element

def html_add_td(element):
    return u'<td>%s</td>' % element

def html_add_td_width(element, width, align='', valign=''):
    return u'<td width=%d%% align=%s valign=%s>%s</td>' % (width, align, valign, element)

def html_text(text, size):
    #return u'<font size="%d">%s</font>' % (size, text)  
    return u'<font size="%d">%s</font>' % (size, text)  
    #return text 

def html_head(level, tag):
    #return u'<h%d>%s</h%d>\n' % (level, tag, level)  
    #return u'<div>%s</div>\n' % tag  
    return u'<b>%s</b><br>\n' % tag  

def html_newline():
    return u'<br>' 

def html_verse(num, verse):
    return html_text(u' %u '%num,1) + html_text(verse,3) 
    #return u'<li>%s</li>' % verse

def mbp_pagebreak():
    return u'<mbp:pagebreak />\n' 

def html_a_name(name):
    return u'<a name="%s"/>\n' % name

#def generate_body_begin():
#   # start html
#   body_html = html_start(True)

#def generate_body_end():
#   # wrap-up 
#   body_html += html_start(False)
opf_template = \
u'''<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="uid">
    <metadata>
        <dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core" xmlns:oebpackage="http://openebook.org/namespaces/oeb-package/1.0/">
            <dc:Title>%(title)s</dc:Title>
            <dc:Language>ko</dc:Language>
            <dc:Identifier id="uid">%(uid)s</dc:Identifier>
        </dc-metadata>
        <x-metadata>
            <output encoding="utf-8"></output>
        </x-metadata>
    </metadata>
    <manifest>
        <item id="ncx" href="toc_%(version)s.ncx" media-type="text/xml"/>
        <item id="item1" media-type="text/x-oeb1-document" href="cover_%(version)s.html"></item>
        <item id="item2" media-type="text/x-oeb1-document" href="toc_%(version)s.html"></item>
        <item id="item3" media-type="text/x-oeb1-document" href="body_%(version)s.html"></item>
    </manifest>
    <spine toc="ncx">
        <itemref idref="item1"/>
        <itemref idref="item2"/>
        <itemref idref="item3"/>
    </spine>
    <tours></tours>
    <guide>
        <reference type="start" title="Startup Page" href="cover_%(version)s.html"></reference>
        <reference type="coverpage" title="Cover Page" href="cover_%(version)s.html"></reference>
        <reference type="toc" title="Table of Contents" href="toc_%(version)s.html"></reference>
    </guide>
</package>
'''
def gen_uid():
    return u'09%08X' % int(time.time())

def generate_opf():
    global opf_file
    opf_args = {}
    opf_args['version'] = version_str() 
    opf_args['uid'] = gen_uid()
    if (double_build):
        opf_args['title'] = u'BIBLE - %s' % (bible_list[version[0]]['name'] + '-' +\
                                             bible_list[version[1]]['name'])
    else:
        opf_args['title'] = u'BIBLE - %s' % bible_list[version[0]]['name'] 
    if debug:
        opf_args['title'] += u'_debug_%s' % gen_uid()
    opf_file = opf_template % opf_args

ncx_template = \
u'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
  </head>
  <docTitle>
    <text>BIBLE TOC</text>
  </docTitle>
  <navMap>
      %s
  </navMap>
</ncx>
'''
navpoint_template = \
u'''
    <navPoint id="%(id)s" playOrder="%(order)s">
      <navLabel>
        <text>%(id)s</text>
      </navLabel>
      <content src="%(link)s"/>
    </navPoint>
'''
#navpoint_template = '%(link)s %(order)d'
def get_link_str(book_idx, chap_idx = 0, verse_idx = 0, file = ''):
    return u'%s#_Q_%d_%d_%d' % (file, book_idx, chap_idx, verse_idx)

def generate_navpoints(body_file):
    global toc_ncx
    args = {}
    navpoints = ''
    order = 0
    for bidx in range(1, len(bible_info) + 1):
        order += 1
        args['id'   ] = u'nv%d' % order
        args['order'] = order
        args['link' ] = get_link_str(bidx, 0, 0, body_file)
       #print navpoint_template
       #print args
       #print navpoint_template % args 
        navpoints += navpoint_template % args 
        # bible_list[bidx - 1][1] - # of chpaters 
        for cidx in range(1, bible_info[bidx - 1][1] + 1):
            order += 1
            args['id'   ] = u'nv%d' % order
            args['order'] = order
            args['link' ] = get_link_str(bidx, cidx, 0, body_file)
            navpoints += navpoint_template % args 
    toc_ncx = ncx_template % navpoints  

def generate_cover():
    global cover_html
    cover_html += html_start(True, 'COVER')
    if debug:
        cover_html += u'<b>' + html_text(u'!DO NOT RELEASE(%s:%s)!' % \
                (version_str(), gen_uid()) , 4) + u'</b>'
    cover_html += html_newline() * 10
    cover_html += u'<div align=center>'
    if (double_build):
        cover_html += html_text(u'<b>' + \
                bible_translate[bible_list[version[0]]['lang']][0] + u'|' + \
                bible_translate[bible_list[version[1]]['lang']][0] + \
                u'</b>', 7)
        cover_html += html_newline() * 3
        cover_html += u'<b>' + html_text(u'[' + \
                bible_list[version[0]]['name'] + u'|' + \
                bible_list[version[1]]['name'] + \
                u']', 5) + u'</b>'
    else:
        cover_html += html_text(u'<b>' + bible_translate[bible_list[version[0]]['lang']][0] + u'</b>', 7)
        cover_html += html_newline() * 3
        cover_html += u'<b>' + html_text(u'[' + bible_list[version[0]]['name'] + u']', 5) + u'</b>'
    cover_html += html_newline() * 4
    cover_html += u'<b>' + html_text('** Version : %s Built @ %s **' \
                            % (formatting_version, time.asctime()), 1) + u'</b>'
    cover_html += html_newline()
    cover_html += u'<b>' + html_text('by masterq' , 1) + u'</b>'
    cover_html += u'</div>'
    cover_html += html_start(False)

def generate_toc(bodyname):
    global toc_html
    toc_html += html_start(True, 'TOC')
    if (double_build):
        toc_html += html_text(\
                bible_translate[bible_list[version[0]]['lang']][1]+ '|' +\
                bible_translate[bible_list[version[1]]['lang']][1] , 5) + u'\n'
    else:
        toc_html += html_text(bible_translate[bible_list[version[0]]['lang']][1], 5) + u'\n'
    toc_html += html_newline() + u'\n'
    for bi in range(0,len(bible_info)):
        b_name, b_num_chaps = bible_info[bi]
        if (bi == old_test_num):
            if (double_build):
                toc_html += html_text(bible_translate[bible_list[version[0]]['lang']][2] + u'|' + \
                                      bible_translate[bible_list[version[1]]['lang']][2], 5) 
            else:
                toc_html += html_text(bible_translate[bible_list[version[0]]['lang']][2], 5) 
            toc_html += html_newline() + u'\n'
        toc_html += html_link(html_text(b_name,4), bi + 1, file=bodyname) + html_newline() + u'\n'
    toc_html += html_start(False)
        
def generate_book(book_name, book_idx, chap_list):
    bb = ''
    if (enable_quicklinks):
        if (book_idx > 1):
            bb += html_link(html_text('&lt;&lt;',4), book_idx - 1) 
        if (book_idx < total_num_books):
            bb += html_link(html_text('&gt;&gt;',4), book_idx + 1) 
    # chapter 0 is used for book title
    s  = mbp_pagebreak() 
    s += html_label(book_idx)
    s += html_head(1, html_text(book_name + bb, 7))
    #s += html_text(_k(book_name), 15)
    #s += html_newline()
    
    c_top = ''
    q =''
    for ci in range(1,len(chap_list[0]) + 1):
        # get chapter info 
        if (bible_list[version[0]]['lang'] == u'kor'):
            ch_name = _k(re_title.search(chap_list[0][ci - 1]).group(1))
        else:
            ch_name = _k(re_title.search(chap_list[0][ci - 1]).group(2))
        if (double_build):
            if (bible_list[version[1]]['lang'] == u'kor'):
                ch_name += _k('|' + re_title.search(chap_list[1][ci - 1]).group(1))
            else:
                ch_name += _k('|' + re_title.search(chap_list[1][ci - 1]).group(2))

        # c_top += html_link(html_text((u'%3d' % ci).replace(' ','&nbsp;') ,2), book_idx, ci) 
        # generate links to chapters first 
        c_top += html_add_td(html_link(html_text(u'%d' % ci ,2), book_idx, ci))
        if (((ci % 10) == 0) and ci != len(chap_list[0])):
            c_top += u'</tr>\n<tr>' 
        #s += ' '
        # verse
        verse_list = [[],[]]
        verse_list[0] = re_verse.findall(chap_list[0][ci - 1])
        if (double_build):
            verse_list[1] = re_verse.findall(chap_list[1][ci - 1])
        v = u'\n' 
        # unfortunately, I couldn't find any prc/mobi converter that
        # doesn't fuck up hyperlinks.. forget the <li> tag.
        #v += u'<ol>\n'
        if (not double_build):
            for vi in range(1, len(verse_list[0]) + 1):
                v += html_newline()
                v += html_label(book_idx, ci, vi)
                v += html_verse(vi, get_verse(_k(verse_list[0][vi - 1]))) 
                v += u'\n'
        elif (not double_use_table):
            for vi in range(1, max(len(verse_list[0]), len(verse_list[1])) + 1):
                v += html_newline()
                v += html_label(book_idx, ci, vi)
                if (vi <= len(verse_list[0])):
                    v += html_verse(vi, get_verse(_k(verse_list[0][vi - 1])))
                    v += html_newline()
                if (vi <= len(verse_list[1])):
                    v += html_verse(vi, get_verse(_k(verse_list[1][vi - 1])))
                v += u'\n'
        else:
            v += html_newline()
            for vi in range(1, max(len(verse_list[0]), len(verse_list[1])) + 1):
                v += html_label(book_idx, ci, vi)
                row  = u'<tr>'
                if (vi <= len(verse_list[0])):
                    row += html_add_td_width(html_verse(vi, get_verse(_k(verse_list[0][vi - 1]))), 50, 'left', 'top')
                else:
                    row += html_add_td_width('&nbsp;', 50, 'left', 'top')
                if (vi <= len(verse_list[1])):
                    row += html_add_td_width(html_verse(vi, get_verse(_k(verse_list[1][vi - 1]))), 50, 'left', 'top')
                else:
                    row += html_add_td_width('&nbsp;', 50, 'left', 'top')
                row += u'</tr>'
                v += html_table(row, width = '100%')
                # kindle table madness....
                # row = html_table(row, width = '50%')
                # row2 = u'<tr>' 
                # row2 += html_add_td_width(row, 50, 'left', 'top')
                # row2 += html_add_td_width('&nbsp', 50, 'left', 'top')
                # row2 += u'</tr>' 
                # v += html_table(row2, width = '100%')
                v += u'\n'
            #v = html_table(v, width='100%')
             
        # chapter 
        q += u'<div>'
        q += html_label(book_idx, ci)
        h = html_text(ch_name, 5)
        if (enable_quicklinks):
            if (ci > 1):
                #h += html_link(html_text('[%d]' % ci - 1,3), book_idx, ci - 1) 
                h += html_link(html_text('&lt;&lt;',3), book_idx, ci -1) 
            if (ci < len(chap_list[0])):
                #h += html_link(html_text('[%d]' % (ci + 1),3), book_idx, ci + 1) 
                h += html_link(html_text('&gt;&gt;',3), book_idx, ci + 1) 
        # insert header information
        q += html_newline() 
        q += html_head(2, h)
        for vlbl in range(11, len(verse_list[0]), 10):
            q += html_link(html_text('%d '%vlbl,1), book_idx, ci, vlbl) 
        # q += h

        # concatenate verse
        q += v
        q += u'<div>'
    s += html_table(html_add_tr(c_top))
    s += q 
    s += html_newline()
    s += html_newline()
    s = mbp_pagebreak() + u'<div>' + s + u'</div>'
    # end html
    body_html_list.append(s)

def write_html(file, data, enc):
    f = open(file, 'w');
    f.write(data.encode(enc))
    f.close()


def main():
    book_name = 'NO BOOK'
    print '--- Building %s ---' % bible_list[version[0]]['name']
    #for book_idx in range(1,5): 
    for book_idx in range(1, total_num_books + 1): 
        chap_list = [[],[]]
        for chapter in range(1,500): 
            text = get_bible(version[0], book_idx, chapter) 
            print _k("Loading... %s" % re_title.search(text).group(1))

            # check if it's a valid chapter
            if (check_valid(text) == True):
                chap_list[0].append(text) 
                if (double_build):
                    text2 = get_bible(version[1], book_idx, chapter) 
                    print _k("Loading [2nd bible] ... %s" % re_title.search(text2).group(1))
                    assert check_valid(text2) 
                    chap_list[1].append(text2) 

                # if it's a new book_idx, add it to the list.
                if (chapter == 1):
                    # new book_idx - generate header for that.
                    if (not double_build):
                        book_name = _k(re_title.search(text).group(3)) 
                    else:
                        book_name = _k(re_title.search(text).group(3) + '|' + \
                                       re_title.search(text2).group(3)) 
            else:
                num_chapters = chapter - 1
                print u'Loading... [%s] "%s" Done!  [%d chapters]' \
                        % (bible_list[version[0]]['name'], book_name, num_chapters) 
                # save book_idx name and # chapters for toc later  
                bible_info.append([book_name, num_chapters])

                # generate book (header, index, chapters..) 
                generate_book(book_name, book_idx, chap_list)
                break
    #generate BODY html 
    body_html = html_start(True, 'BODY')
    for book in body_html_list:
        body_html += book
    body_html += html_start(False)
    write_html('body_%s.html' % version_str(), body_html, out_encoding); 

    # generate toc (need to pass the name of the body file)
    generate_toc('body_%s.html' % version_str())
    write_html('toc_%s.html' % version_str(), toc_html, out_encoding); 

    # generate cover
    generate_cover()
    write_html('cover_%s.html' % version_str(), cover_html, out_encoding); 

    # generate opf and toc.ncx if navpoints are enabled.
    if (enable_navpoints):
        generate_navpoints('body_%s.html' % version_str())
        write_html('toc_%s.ncx' % version_str(), toc_ncx, 'utf-8')
        generate_opf()
        write_html('%s.opf' % version_str(), opf_file, 'utf-8')


    for n,ch in bible_info:
        print '%s : %d' % (n,ch)
#def main():
#   build_single()
    #build_double()
if __name__ == "__main__":
    main()
