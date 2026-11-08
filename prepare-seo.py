from pathlib import Path
from html.parser import HTMLParser
import html, json, re

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
ORIGIN = 'https://chatselect.webcraftio.com'
TITLE = 'Select WhatsApp Messages on Windows | ChatSelect'
DESCRIPTION = 'Select hundreds of WhatsApp messages on Windows with ChatSelect. Choose a message count, follow the setup guide, and pause anytime. Free Windows beta.'
page = (DIST/'index.html').read_text(encoding='utf-8')
page = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', page, flags=re.S)
page = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{DESCRIPTION}">', page)
page = page.replace('A little help for long conversations', 'WhatsApp message selector for Windows')
page = page.replace('Select hundreds of WhatsApp messages on Windows. Choose how many, set up your chat, and let ChatSelect take care of the ticking.', 'ChatSelect is a free Windows utility that selects WhatsApp messages for you. Choose a count, follow the setup guide, and review your selection.')
new_faq = '<details><summary>How can I select hundreds of WhatsApp messages on Windows?<span aria-hidden="true">+</span></summary><p>Open ChatSelect, choose a message count, and click Start setup. In WhatsApp, open your chat in Select messages mode. Mark an empty checkbox with F6, mark the bottom boundary with F7, then press F8 to start. Review the selected messages when it finishes.</p></details>\n    '
if 'How can I select hundreds of WhatsApp messages on Windows?' not in page:
    page = page.replace('<div class="faq-list">', '<div class="faq-list">\n    '+new_faq)

class FAQReader(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_detail=False; self.field=None; self.q=[]; self.a=[]; self.items=[]; self.skip=False
    def handle_starttag(self, tag, attrs):
        if tag=='details': self.in_detail=True; self.q=[]; self.a=[]
        if self.in_detail and tag=='summary': self.field='q'
        if self.in_detail and tag=='p': self.field='a'
        if self.in_detail and tag=='span' and dict(attrs).get('aria-hidden')=='true': self.skip=True
    def handle_endtag(self, tag):
        if tag=='span': self.skip=False
        if tag in ('p','summary'): self.field=None
        if tag=='details' and self.in_detail:
            self.items.append({'@type':'Question','name':' '.join(''.join(self.q).split()),'acceptedAnswer':{'@type':'Answer','text':' '.join(''.join(self.a).split())}})
            self.in_detail=False
    def handle_data(self, data):
        if self.in_detail and not self.skip:
            if self.field=='q': self.q.append(data)
            if self.field=='a': self.a.append(data)
faq=FAQReader(); faq.feed(page)
graph={'@context':'https://schema.org','@graph':[
 {'@type':'WebSite','@id':ORIGIN+'/#website','url':ORIGIN+'/','name':'ChatSelect','inLanguage':'en'},
 {'@type':'WebPage','@id':ORIGIN+'/#webpage','url':ORIGIN+'/','name':TITLE,'description':DESCRIPTION,'inLanguage':'en','isPartOf':{'@id':ORIGIN+'/#website'},'about':{'@id':ORIGIN+'/#app'},'hasPart':{'@id':ORIGIN+'/#faq'}},
 {'@type':'SoftwareApplication','@id':ORIGIN+'/#app','name':'ChatSelect','url':ORIGIN+'/','description':'A free Windows beta utility for selecting WhatsApp messages. Users choose a message count, set up their chat and review the resulting selection.','operatingSystem':'Windows','applicationCategory':'UtilitiesApplication','softwareVersion':'1.0 beta','isAccessibleForFree':True,'downloadUrl':ORIGIN+'/downloads/ChatSelect-Windows-v1.0-beta.zip','screenshot':ORIGIN+'/assets/app-setup.jpg','offers':{'@type':'Offer','price':0,'priceCurrency':'USD','url':ORIGIN+'/#download'}},
 {'@type':'FAQPage','@id':ORIGIN+'/#faq','url':ORIGIN+'/#questions','mainEntity':faq.items}
]}
tags=f'''<!-- SEO and sharing metadata -->
  <link rel="canonical" href="{ORIGIN}/">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="ChatSelect">
  <meta property="og:locale" content="en_US">
  <meta property="og:title" content="{TITLE}">
  <meta property="og:description" content="{DESCRIPTION}">
  <meta property="og:url" content="{ORIGIN}/">
  <meta property="og:image" content="{ORIGIN}/assets/social-preview.png">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="ChatSelect for Windows. Select WhatsApp messages and skip the manual clicks.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE}">
  <meta name="twitter:description" content="{DESCRIPTION}">
  <meta name="twitter:image" content="{ORIGIN}/assets/social-preview.png">
  <meta name="twitter:image:alt" content="ChatSelect for Windows. Select WhatsApp messages and skip the manual clicks.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <script type="application/ld+json">{json.dumps(graph,ensure_ascii=False,separators=(',',':'))}</script>
  <!-- /SEO and sharing metadata -->'''
page = re.sub(r'<!-- SEO and sharing metadata -->.*?<!-- /SEO and sharing metadata -->', '', page, flags=re.S)
page = page.replace('</head>',tags+'\n</head>')
(DIST/'index.html').write_text(page,encoding='utf-8')
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+ORIGIN+'/sitemap.xml\n',encoding='utf-8')
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+ORIGIN+'/</loc></url></urlset>\n',encoding='utf-8')
assert 40 <= len(TITLE) <= 60
assert 140 <= len(DESCRIPTION) <= 160
assert page.count('<h1>') == 1
assert len(faq.items) == 8
assert all(q['name'] and q['acceptedAnswer']['text'] for q in faq.items)
assert 'aggregateRating' not in graph['@graph'][2]
print(json.dumps({'title':TITLE,'title_characters':len(TITLE),'description_characters':len(DESCRIPTION),'visible_faq_answers':len(faq.items),'schema_types':[x['@type'] for x in graph['@graph']]},indent=2))
