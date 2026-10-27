from od_lib import *
import time
import os
BRIEF=os.environ["BRIEF"]
os.makedirs("out",exist_ok=True)
with sync_playwright() as p:
    b,ctx,pg=start(p,'out/state.json' if os.path.exists('out/state.json') else None)
    pg.goto('http://127.0.0.1:7456/', wait_until='networkidle', timeout=60000); pg.wait_for_timeout(2500)
    ed=pg.locator('[contenteditable="true"], textarea').first
    if 'onboarding' in pg.url:
        pg.get_by_role('button', name='Local Agent').click(); pg.wait_for_timeout(3000)
        pg.get_by_role('button', name='Continue').click(); pg.wait_for_timeout(3000)
    ed=pg.get_by_test_id("home-hero-input"); ed.click(); pg.wait_for_timeout(500); pg.keyboard.insert_text(BRIEF); pg.wait_for_timeout(800)
    pg.screenshot(path='out/run_0_brief.png')
    pg.get_by_role('button', name='Run').click(); pg.wait_for_timeout(5000)
    print('URL', pg.url); pg.screenshot(path='out/run_1_started.png')
    t0=time.time(); last=''
    while time.time()-t0 < 900:
        pg.wait_for_timeout(20000)
        txt=pg.locator('body').inner_text()
        tail=txt[-600:].replace('\n',' | ')
        if tail!=last: print(f'[{int(time.time()-t0)}s]', tail[-300:]); last=tail
        pg.screenshot(path='out/run_progress.png')
        stop=pg.get_by_role('button', name='Stop')
        running = stop.count() and stop.first.is_visible()
        if not running and time.time()-t0>60: break
    import subprocess
    TOKEN=open('.token').read().strip(); pid=pg.url.split('/projects/')[1].split('/')[0]
    subprocess.run(['sh','-c',f'curl -s -H "Authorization: Bearer {TOKEN}" http://127.0.0.1:7456/api/projects/{pid}/files | python3 -c "import sys,json;[print(f[\'name\']) for f in json.load(sys.stdin)[\'files\']]" | while read f; do curl -s -H "Authorization: Bearer {TOKEN}" "http://127.0.0.1:7456/api/projects/{pid}/files/$f" -o "out/$f"; echo saved out/$f; done'])
    print('DONE at', int(time.time()-t0), 's; URL', pg.url)
    pg.screenshot(path='out/run_2_final.png', full_page=False)
    ctx.storage_state(path='out/state.json'); b.close()
