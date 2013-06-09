# -*- coding: utf-8 -*-
from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag
from django.utils.datetime_safe import datetime


class CorriereParser(BaseParser):
    SUFFIX = ''
    subdomains = ['www',
                  'corrieredibologna',
                  'corrierefiorentino',
                  'corrieredelveneto',
                  'corrieredelmezzogiorno',
                  'brescia',
                  'bergamo',
                  'roma',
                  '27esimaora',
                  'nuvola',
                  'buonenotizie',
                  'seigradi',
                  'invisibili',
                  'solferino28']

    domains = [sd + '.corriere.it' for sd in subdomains]

    disallowed_files = ['pdf','jpg']

    feeder_base = 'http://www.corriere.it/'
    feeder_pat = '^http://([A-z\.]*)(' + \
                 '|'.join(subdomains) + ').corriere.it/'

    def _parse(self, html):
        # clearly i'm not very good with regexes
        if self.url.lower()[-3:] in self.disallowed_files:
            self.real_article = False
            return

        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        elt = soup.find(name='h1', attrs={'itemprop':'headline name'})
        if elt is None:
            self.real_article = False
            return
        for br in elt.findAll('br'):
            br.replaceWith('\n')
        self.title = elt.getText()
        elt.extract()
        bl = soup.find(name='h2')
        if bl is not None:
            self.byline = bl.getText()
            bl.extract()
        dt = soup.find(name='strong', attrs={'itemprop':'datePublished'})
        if dt is not None:
            self.date = dt.getText()
        else:
            self.date = datetime.now().isoformat()

        div = soup.find(name='div',attrs={'itemprop':'articleBody'})
        if div is None:
            self.real_article = False
            return

        acceptable_body = []
        for x in div.childGenerator():
            if isinstance(x, Tag) and x.name == 'p' and x.get('class') not in ['footnotes','reader']:
                for t in ['div','object','h1','h2']: # unacceptable tags
                    objs = x.findAll(name=t)
                    if objs:
                        for o in objs: o.extract()
                if x.getText() != '':
                    acceptable_body.append(x.getText())
        self.body = '\n\n'.join(acceptable_body)

        author = soup.find(name='span',attrs={'itemprop':'author'})
        if author is not None:
            self.author = author.getText()

# BROKEN: i sottodomini hanno quintali di merda sotto <subdom>.corriere.it/<città>/(aziende|traffico|...)
#   subdomain e città coincidono solo per roma/milano/brescia/bergamo, i subdom tematici sono alla cazzo...
#   Il problema è che senza questo, i sottodomini non vengono scrapati se non per i pezzi esplicitamente linkati dalla home
# create a class for each subdomain, so we parse everything
# import re
# for subDomain in CorriereParser.subdomains:
#     if subDomain not in ('www',):
#         newName = subDomain.title()
#         if re.match('\d(.*)',subDomain):
#             newName = "X" + newName
#         city = subDomain
#
#         exec("""
# class %sCorriereParser(CorriereParser):
#     feeder_base = 'http://%s.corriere.it'
#     domains = ['%s.corriere.it']
#     feeder_pat = 'http://%s.corriere.it/%s/(notizie|politica|cronache)
#         """ % (newName,subDomain,subDomain))
