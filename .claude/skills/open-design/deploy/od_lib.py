from playwright.sync_api import sync_playwright
TOKEN=open('.token').read().strip()
def dump(pg, n=60):
    for sel in ['textarea','button','[role=combobox]','[role=option]','[role=menuitem]','select','input','a']:
        for i,e in enumerate(pg.locator(sel).all()[:n]):
            try:
                if not e.is_visible(): continue
                t=(e.inner_text() or '')[:70].replace('\n',' | '); ph=e.get_attribute('placeholder') or ''; al=e.get_attribute('aria-label') or ''
                print(sel,i,repr(t), ('ph='+ph) if ph else '', ('aria='+al) if al else '')
            except Exception: pass
def start(p, storage=None):
    b=p.chromium.launch()
    kw=dict(http_credentials={'username':'open-design','password':TOKEN}, viewport={'width':1440,'height':900})
    if storage: kw['storage_state']=storage
    ctx=b.new_context(**kw); pg=ctx.new_page(); return b,ctx,pg
