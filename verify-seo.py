from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import ast, json, re, struct, xml.etree.ElementTree as ET

root=Path(__file__).resolve().parent/'dist'
source=(root/'index.html').read_text(encoding='utf-8')
class Reader(HTMLParser):
    def __init__(self): super().__init__(); self.tags=[]
    def handle_starttag(self,tag,attrs): self.tags.append((tag,dict(attrs)))
r=Reader();r.feed(source)
def meta(key):
    values=[a.get('content','') for t,a in r.tags if t=='meta' and (a.get('name')==key or a.get('property')==key)]
    assert len(values)==1,(key,'missing or duplicate')
    return values[0]
titles=re.findall(r'<title>(.*?)</title>',source,re.S)
assert len(titles)==1 and 40<=len(titles[0])<=60
assert 140<=len(meta('description'))<=160
assert sum(t=='h1' for t,a in r.tags)==1
canonical=[a['href'] for t,a in r.tags if t=='link' and a.get('rel')=='canonical']
assert len(canonical)==1 and canonical[0].startswith('https://') and canonical[0].endswith('/')
generator=ast.parse((root.parent/'prepare-seo.py').read_text(encoding='utf-8'))
origin=next(ast.literal_eval(n.value) for n in generator.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ORIGIN' for t in n.targets))
assert canonical[0]==origin+'/', 'Canonical differs from the configured public domain'
assert meta('og:title')==titles[0] and meta('twitter:title')==titles[0]
assert meta('og:url')==canonical[0]
assert meta('og:description')==meta('description')==meta('twitter:description')
assert meta('twitter:card')=='summary_large_image'
for field in ('og:image','twitter:image'):
    url=meta(field); assert url.startswith(canonical[0]); assert (root/urlparse(url).path.lstrip('/')).is_file()
assert meta('og:image:alt') and meta('twitter:image:alt')
png=(root/'assets/social-preview.png').read_bytes()
assert png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(1200,630)
schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S).group(1))
def check_owned_urls(value):
    if isinstance(value,dict):
        for key,child in value.items():
            if key in ('@id','url','downloadUrl','screenshot') and isinstance(child,str):
                assert child.startswith(origin+'/'), ('Incorrect structured-data domain',child)
            check_owned_urls(child)
    elif isinstance(value,list):
        for child in value: check_owned_urls(child)
check_owned_urls(schema)
types={n['@type']:n for n in schema['@graph']}
assert {'WebSite','WebPage','SoftwareApplication','FAQPage'}<=types.keys()
app=types['SoftwareApplication']; assert app['offers']['price']==0 and app['operatingSystem']=='Windows'
assert 'aggregateRating' not in app and 'review' not in app
assert (root/urlparse(app['downloadUrl']).path.lstrip('/')).is_file()
assert len(types['FAQPage']['mainEntity'])==sum(t=='details' for t,a in r.tags)
for t,a in r.tags:
    if t=='img':
        assert 'alt' in a and int(a['width'])>0 and int(a['height'])>0
        assert (root/a['src']).is_file()
    if t=='a' and 'download' in a:
        assert (root/a['href']).is_file()
locations=[n.text for n in ET.parse(root/'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert locations==canonical
robots=(root/'robots.txt').read_text(); assert 'Sitemap: '+canonical[0]+'sitemap.xml' in robots
print(json.dumps({'result':'passed','title_characters':len(titles[0]),'description_characters':len(meta('description')),'headings':1,'FAQ_answers':len(types['FAQPage']['mainEntity']),'social_image':'1200x630','sitemap':'valid XML','canonical':canonical[0]},indent=2))
