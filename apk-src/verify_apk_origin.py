#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
模拟 APK 内 WebView 的 shouldInterceptRequest：
把 https://ziwei.local/** 全部映射到 assets 目录，验证自定义同源域下
主文档、相对 fetch 年份包、localStorage、五个 Tab、十三维断语都正常。
"""
import re
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ORIGIN = 'https://ziwei.local'
SHOT = ROOT.parent / 'preview-apk-origin.png'

PATTERN = re.compile(r'^https://ziwei\.local/.*$')


def mime_of(path):
    if path.endswith('.html'): return 'text/html; charset=utf-8'
    if path.endswith('.js'): return 'application/javascript; charset=utf-8'
    if path.endswith('.jsonl'): return 'application/json; charset=utf-8'
    if path.endswith('.zst'): return 'application/octet-stream'
    return 'application/octet-stream'


def main():
    results = []

    def check(name, ok, extra=''):
        results.append((name, bool(ok), extra))

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                              args=['--no-sandbox'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844},
                            device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text)
              if m.type == 'error' else None)

        served = []

        def on_route(route, request):
            path = urlparse(request.url).path or '/index.html'
            if path.endswith('/'):
                path += 'index.html'
            f = ASSETS / path.lstrip('/')
            if f.is_file():
                served.append((path, f.stat().st_size))
                route.fulfill(status=200, content_type=mime_of(path),
                              body=f.read_bytes(),
                              headers={'Access-Control-Allow-Origin': '*'})
            else:
                route.fulfill(status=404, body='404 Not Found')

        pg.route(PATTERN, on_route)
        pg.goto(ORIGIN + '/index.html', wait_until='load', timeout=90000)
        pg.wait_for_timeout(1000)

        base = pg.evaluate("""()=>({
          origin:location.origin, protocol:location.protocol,
          title:document.title,
          engine:typeof window.ZiweiEngine, zstd:typeof window.fzstd,
          corpus:typeof window.ZiweiCorpus, back:typeof window.__zwBack,
          cells:document.querySelectorAll('#board .cell').length,
          tabs:document.querySelectorAll('#fnav button').length,
          fnavPos:getComputedStyle(document.querySelector('#fnav')).position,
          hint:getComputedStyle(document.querySelector('.mobile-only')).display,
          scrollW:document.documentElement.scrollWidth, vw:innerWidth
        })""")
        check('自定义同源域加载', base['origin'] == ORIGIN and base['protocol'] == 'https:')
        check('主文档由 assets 提供', any(s[0] == '/index.html' for s in served))
        check('引擎/解码/语料挂载',
              base['engine'] == 'object' and base['zstd'] == 'object'
              and base['corpus'] == 'object')
        check('十二宫 + 五 Tab', base['cells'] == 12 and base['tabs'] == 5)
        check('底部导航固定', base['fnavPos'] == 'fixed')
        check('横滑提示已隐藏', base['hint'] == 'none')
        check('无横向溢出', base['scrollW'] <= base['vw'] + 1)

        # localStorage（AI Key / 上次 Tab 依赖）
        ls = pg.evaluate("""()=>{localStorage.setItem('__probe','ok');
          return localStorage.getItem('__probe');}""")
        check('localStorage 可用', ls == 'ok')

        # 相对路径 fetch 年份包 —— APK 内的核心离线链路
        f = pg.evaluate("""async ()=>{
          const r=await fetch('data/years/year-1955.jsonl.zst');
          const u=new Uint8Array(await r.arrayBuffer());
          return {status:r.status, len:u.length, magic:Array.from(u.slice(0,4))};
        }""")
        check('年份包同源 fetch', f['status'] == 200 and f['len'] > 1000000
              and f['magic'] == [40, 181, 47, 253])
        check('年份包由 assets 提供',
              any(s[0].startswith('/data/years/year-1955') for s in served))

        # 断语库页面点年份 → 走本地随包文件加载
        pg.locator('#fnav button[data-p="library"]').click()
        pg.wait_for_timeout(300)
        pg.locator('#yearGrid .y').filter(has_text='1955').first.click()
        pg.wait_for_timeout(2500)
        log = pg.locator('#libLog').inner_text()
        check('点击年份离线加载成功',
              ('已索引' in log or '解压完成' in log) and '全部来源失败' not in log,
              log[-140:].replace('\n', ' | '))

        # 十三维断语
        pg.locator('#fnav button[data-p="reading"]').click()
        pg.wait_for_timeout(600)
        body = pg.locator('#readBody').inner_text()
        check('十三维真实断语', len(body) > 500, f'{len(body)} 字')

        # 内嵌包解压正确性
        dec = pg.evaluate("""()=>{
          const bin=atob(window.ZiweiCorpus.packs['1990']);
          const u=new Uint8Array(bin.length);
          for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
          const raw=window.fzstd.decompress(u);
          let nl=0;for(let i=0;i<raw.length;i++)if(raw[i]===10)nl++;
          return nl;
        }""")
        check('内嵌包 8760 盘完整', dec == 8760)

        # 返回键钩子
        back = pg.evaluate('window.__zwBack()')
        check('返回键回到命盘', back is True
              and pg.locator('#page-chart').is_visible())
        pg.locator('#fnav button[data-p="chart"]').click()
        pg.wait_for_timeout(250)
        pg.screenshot(path=str(SHOT), full_page=False)

        check('无 JS 错误', len(errs) == 0, '; '.join(errs[:2]))
        b.close()

    print('=== 模拟 APK 同源拦截验证 ===')
    print('被拦截并提供 assets 的请求数:', len(served))
    for path, size in served[:6]:
        print(f'  {path}  {size} B')
    print()
    ok = 0
    for name, good, extra in results:
        print(f"  {'OK  ' if good else 'FAIL'}  {name}" + (f'   [{extra}]' if extra else ''))
        ok += good
    print(f'\n===== {ok}/{len(results)} 通过 =====')
    print('ORIGIN_BASE=' + str(base).replace("'", '"'))


if __name__ == '__main__':
    main()
