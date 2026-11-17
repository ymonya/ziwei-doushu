#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""手机竖屏版 APK 页面端到端验证（同源静态服务，模拟 APK 内 https://ziwei.local/ 行为）"""
import functools
import http.server
import socketserver
import threading
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent / 'assets'
SHOT = Path(__file__).resolve().parent.parent
PORT = 8766


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    handler = functools.partial(Quiet, directory=str(ROOT))
    srv = Server(('127.0.0.1', PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    viewports = [(360, 780), (390, 844), (412, 915)]
    total = passed = 0
    report = []

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                              args=['--no-sandbox'])
        for w, h in viewports:
            pg = b.new_page(viewport={'width': w, 'height': h},
                            device_scale_factor=2, is_mobile=True, has_touch=True)
            errs = []
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
            pg.on('console', lambda m: errs.append('console: ' + m.text)
                  if m.type == 'error' else None)
            pg.goto(f'http://127.0.0.1:{PORT}/index.html',
                    wait_until='load', timeout=90000)
            pg.wait_for_timeout(900)
            # 保证在命盘页测量
            pg.locator('#fnav button[data-p="chart"]').click()
            pg.wait_for_timeout(350)

            base = pg.evaluate("""()=>{
              const de=document.documentElement;
              const f=document.querySelector('#fnav').getBoundingClientRect();
              const bd=document.querySelector('#board').getBoundingClientRect();
              const bw=document.querySelector('.board-wrap').getBoundingClientRect();
              const cs=getComputedStyle(document.querySelector('#fnav'));
              return {vw:innerWidth, vh:innerHeight,
                scrollW:de.scrollWidth, bodyW:document.body.scrollWidth,
                fnavPos:cs.position, fnavBottom:Math.round(f.bottom), fnavH:Math.round(f.height),
                boardW:Math.round(bd.width), wrapW:Math.round(bw.width),
                cells:document.querySelectorAll('#board .cell').length,
                center:!!document.querySelector('#board .center'),
                tabs:document.querySelectorAll('#fnav button').length,
                engine:typeof window.ZiweiEngine, zstd:typeof window.fzstd,
                corpus:typeof window.ZiweiCorpus, back:typeof window.__zwBack,
                icos:[...document.querySelectorAll('#fnav button')].map(x=>x.dataset.ico),
                apk:document.documentElement.getAttribute('data-apk')};
            }""")

            c = {
                '无整页横向溢出': base['scrollW'] <= base['vw'] + 1 and base['bodyW'] <= base['vw'] + 1,
                '底部导航固定': base['fnavPos'] == 'fixed' and abs(base['fnavBottom'] - base['vh']) <= 2,
                '命盘铺满不横滑': 0 < base['boardW'] <= base['wrapW'] + 1,
                '十二宫完整': base['cells'] == 12 and base['center'],
                '五个 Tab': base['tabs'] == 5,
                '引擎/解码/语料': base['engine'] == 'object' and base['zstd'] == 'object'
                                  and base['corpus'] == 'object',
                '短标签图标': all(base['icos']) and base['apk'] == '1',
                '返回键钩子': base['back'] == 'function',
            }

            # 起盘后应自动滚到命盘（竖屏表单较长）
            pg.locator('#goBtn').click()
            pg.wait_for_timeout(1000)
            bp = pg.evaluate("""()=>{const r=document.querySelector('#board').getBoundingClientRect();
              const r3=getComputedStyle(document.querySelector('.r3')).gridTemplateColumns;
              return {top:Math.round(r.top), r3:r3};}""")
            c['起盘后滚到命盘'] = -20 <= bp['top'] <= 300
            c['日期下拉横排三列'] = len(bp['r3'].split()) == 3
            if w == 390:
                pg.screenshot(path=str(SHOT / 'preview-board.png'), full_page=False)
            pg.evaluate('window.scrollTo(0,0)')
            pg.wait_for_timeout(200)

            # 逐 Tab 切换 + 溢出检查
            for key in ['reading', 'ai', 'heming', 'library', 'chart']:
                pg.locator(f'#fnav button[data-p="{key}"]').click()
                pg.wait_for_timeout(250)
                vis = pg.locator(f'#page-{key}').is_visible()
                sw = pg.evaluate('document.documentElement.scrollWidth')
                c[f'Tab {key} 可用且无溢出'] = bool(vis) and sw <= base['vw'] + 1

            # 十三维真实断语
            pg.locator('#fnav button[data-p="reading"]').click()
            pg.wait_for_timeout(500)
            body = pg.locator('#readBody').inner_text()
            c['十三维断语正文'] = len(body) > 500
            if w == 390:
                pg.screenshot(path=str(SHOT / 'preview-reading.png'), full_page=False)

            # 同源年份包（APK 内走 shouldInterceptRequest）
            fetch = pg.evaluate("""async ()=>{
              const r=await fetch('data/years/year-1955.jsonl.zst');
              const u=new Uint8Array(await r.arrayBuffer());
              return {status:r.status, len:u.length, magic:Array.from(u.slice(0,4))};
            }""")
            c['年份包同源可读'] = (fetch['status'] == 200 and fetch['len'] > 1000000
                                  and fetch['magic'] == [40, 181, 47, 253])

            # 内嵌 1990 包解压正确性（fzstd 补丁）
            dec = pg.evaluate("""()=>{
              const bin=atob(window.ZiweiCorpus.packs['1990']);
              const u=new Uint8Array(bin.length);
              for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
              const raw=window.fzstd.decompress(u);
              let nl=0;for(let i=0;i<raw.length;i++)if(raw[i]===10)nl++;
              return {nl, bytes:raw.length};
            }""")
            c['内嵌包 8760 盘'] = dec['nl'] == 8760

            # 返回键钩子
            pg.locator('#fnav button[data-p="library"]').click()
            pg.wait_for_timeout(200)
            back = pg.evaluate('window.__zwBack()')
            c['返回键回命盘'] = (back is True
                                and pg.locator('#page-chart').is_visible())
            pg.locator('#fnav button[data-p="chart"]').click()
            pg.wait_for_timeout(200)
            c['命盘页再按返回不拦截'] = (pg.evaluate('window.__zwBack()') is False)

            if w == 390:
                pg.screenshot(path=str(SHOT / 'preview-chart.png'), full_page=False)

            c['无 JS 错误'] = len(errs) == 0
            for k, v in c.items():
                total += 1
                passed += bool(v)
            report.append({'vp': f'{w}x{h}', 'base': base, 'checks': c, 'errs': errs})
            pg.close()
        b.close()
    srv.shutdown()

    for r in report:
        print(f"\n===== {r['vp']} =====")
        b = r['base']
        print(f"  scrollW={b['scrollW']} vw={b['vw']} | fnav={b['fnavPos']} "
              f"bottom={b['fnavBottom']}/{b['vh']} h={b['fnavH']} | "
              f"board={b['boardW']}/{b['wrapW']} cells={b['cells']}")
        for k, v in r['checks'].items():
            print(f"  {'OK  ' if v else 'FAIL'}  {k}")
        if r['errs']:
            print('  错误:', r['errs'][:4])
    print(f"\n===== 合计 {passed}/{total} 通过 =====")
    print(json.dumps({'passed': passed, 'total': total}, ensure_ascii=False))


if __name__ == '__main__':
    main()
