import wikipediaapi
import argparse, re, logging
from ebooklib import epub

USER_AGENT = 'WikiDL/0.1 (github.com/LonMcGregor/WikiDL)'

log = logging.getLogger('wiki_dl')
logging.basicConfig()

ap = argparse.ArgumentParser(
    prog='WikiDL',
    description='Wiki downloader and ebook formatter',
    )
ap.add_argument('page', help='The URL or english title of the page to download')
ap.add_argument('output', help='Location to write output file')
ap.add_argument('-i', '--images', default=False, action='store_true', help='Download and embed images')
ap.add_argument('-r', '--references', default=False, action='store_true', help='Download externally referenced webpages (if they exist as HTML)')
ap.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose logging')
args = ap.parse_args()

def wikidl():
    theurl = re.match(r'^https?://(\w\w+)(?:.m)?.wikipedia.org/wiki/([^#]+)(#.+)?', args.page)
    fullurl = theurl[0]
    lang = theurl[1]
    title = theurl[2]
    section = theurl[3]
    log.debug([lang, title, section])

    #if url not give, just a title, use that as the search
    if fullurl==None and lang==None:
        lang='en'
        title=args.page

    log.info('Downloading %s' % title)

    wapi = wikipediaapi.Wikipedia(
        user_agent=USER_AGENT,
        language=lang,
        extract_format=wikipediaapi.ExtractFormat.HTML
        )
    page = wapi.page(title)
    if not page.exists():
        logging.critical('This page does not exist, cannot download')
        return

    html = page.text

    book = epub.EpubBook()
    book.set_identifier('wikipedia:%s'%page.pageid)
    book.set_title(title)
    book.set_language(lang)

    book.add_author('Wikipedia')

    # create chapter
    c1 = epub.EpubHtml(title=title, file_name='chap_01.xhtml', lang=lang)
    c1.content = (html)
    book.add_item(c1)

    # TODO create image from the local image
    if args.images:
        image_content = open('wikipedia.png', 'rb').read()
        img = epub.EpubImage(
            uid='image_1',
            file_name='static/wikipedia.png',
            media_type='image/png',
            content=image_content,
        )
        book.add_item(img)

    # define Table Of Contents
    book.toc = (
        epub.Link('chap_01.xhtml', title, 'page'),
    )
    book.spine = ['nav', c1]

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = ''
    nav_css = epub.EpubItem(
        uid='style_nav',
        file_name='style/nav.css',
        media_type='text/css',
        content=style,
    )
    book.add_item(nav_css)

    # write to the file
    epub.write_epub(args.output, book, {})

if __name__ == '__main__':
    log.setLevel(logging.INFO)
    if args.verbose:
        log.setLevel(logging.DEBUG)
    wikidl()
