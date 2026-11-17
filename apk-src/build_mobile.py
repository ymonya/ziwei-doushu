#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
由桌面版单文件 index.html 生成 APK 专用的「手机竖屏版」 index.html。
只做注入，不改动排盘引擎 / 断语 / AI / 合盘 任何业务逻辑。
"""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
WEB_DIR = Path(os.environ.get('ZIWEI_WEB_DIR', str(ROOT.parent)))
SRC = WEB_DIR / 'index.html'
DST = ROOT / 'assets' / 'index.html'

VP_OLD = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
VP_NEW = ('<meta name="viewport" content="width=device-width, initial-scale=1.0, '
          'viewport-fit=cover">\n'
          '<meta name="theme-color" content="#0b0d12">\n'
          '<meta name="mobile-web-app-capable" content="yes">')

MOBILE_CSS = r'''
/* ==================== 手机竖屏 · APK 专属布局 ==================== */
@media (max-width:600px){
  html,body{max-width:100%;overflow-x:hidden}
  body{padding-bottom:calc(68px + env(safe-area-inset-bottom));font-size:13px;line-height:1.6}
  /* ---- 顶栏：压缩为一行，保留主题/关于 ---- */
  header{position:sticky;top:0;padding-top:env(safe-area-inset-top)}
  .hd{padding:8px 12px;gap:9px}
  .logo{width:32px;height:32px;font-size:16px;border-radius:4px}
  .tt h1{font-size:14px;letter-spacing:.12em;white-space:nowrap}
  .tt p{font-size:8px;letter-spacing:.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px}
  .hd-tag{display:none}
  .mobile-only{display:none!important} /* 竖屏命盘已完整铺满，无需「左右滑动」提示 */
  #themeBtn,#aboutBtn{padding:6px 8px;font-size:11px;flex:none;white-space:nowrap}
  /* ---- 底部 Tab Bar（手机 App 习惯） ---- */
  .fnav{position:fixed!important;left:0;right:0;bottom:0;top:auto!important;z-index:80;
        border-top:1px solid var(--line);border-bottom:none;
        background:var(--bg2);
        background:color-mix(in srgb,var(--bg2) 96%,transparent);
        backdrop-filter:blur(16px);padding-bottom:env(safe-area-inset-bottom)}
  .fnav-in{display:grid;grid-template-columns:repeat(5,1fr);gap:0;padding:0 2px;overflow:visible;max-width:none}
  .fnav button{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;
        width:100%;padding:6px 1px 5px;font-size:0;letter-spacing:0;
        border-bottom:none;border-top:2px solid transparent;line-height:1.1;min-height:54px}
  .fnav button .nb{display:none}
  .fnav button::before{content:attr(data-ico);font-family:var(--serif);font-size:14px;
        width:25px;height:25px;display:grid;place-items:center;color:var(--muted);
        border:1px solid var(--line);border-radius:7px;transition:.18s}
  .fnav button::after{content:attr(data-lbl);font-family:var(--sans);font-size:10px;
        color:var(--muted);letter-spacing:.02em;white-space:nowrap}
  .fnav button.on{color:var(--gold);border-top-color:var(--gold);border-bottom-color:transparent}
  .fnav button.on::before{color:var(--gold);border-color:var(--gold2);
        background:color-mix(in srgb,var(--gold) 12%,transparent)}
  .fnav button.on::after{color:var(--gold);font-weight:600}
  /* ---- 单列流式布局 ---- */
  .wrap{display:block!important;padding:12px 10px 22px!important;max-width:100%!important}
  .left{position:static!important}
  .grid2,.grid3,.read-layout,.ai-layout,.hp-forms,.hp-grid{grid-template-columns:1fr!important}
  .read-side,.ai-side{position:static!important}
  .card{border-radius:9px}
  .card-h{padding:10px 12px}
  .card-h h2{font-size:13px}
  .card-h .sub{font-size:9px}
  .card-b{padding:12px;max-width:100%;overflow-x:auto}
  footer{padding:16px 12px 24px;font-size:10px}
  .toast{bottom:calc(78px + env(safe-area-inset-bottom));max-width:88vw;text-align:center;font-size:11.5px}
  /* ---- 触控尺寸 ---- */
  input[type=text],select,.field input,.field select,.field textarea,.chat-foot input[type=text]{
        font-size:16px;min-height:40px;padding:9px 10px}
  .btn{min-height:40px;padding:10px 14px}
  .btn.sm{min-height:34px;padding:7px 11px;font-size:11px}
  /* 日期 / 时间下拉横排，缩短表单高度 */
  .r2,.r3{display:grid;gap:6px}
  .r3{grid-template-columns:repeat(3,minmax(0,1fr))}
  .r2{grid-template-columns:repeat(2,minmax(0,1fr))}
  .r2 select,.r3 select,.r2 input,.r3 input{font-size:13px;padding:8px 22px 8px 7px;min-height:40px}
  .seg button{min-height:38px;font-size:13px}
  .chip{min-height:32px;display:inline-flex;align-items:center}
  .topic-tabs button{min-height:32px}
  .row{margin-bottom:11px}
  /* ---- 命盘 4x4 完整铺满竖屏（不横滑） ---- */
  .board-wrap{width:100%;max-width:100%;margin:0}
  .board{min-width:0!important;width:100%;gap:1px;
         grid-template-rows:repeat(4,minmax(88px,auto))}
  .cell{min-height:88px;padding:4px 5px;overflow:hidden}
  .c-top{margin-bottom:3px;padding-right:22px;gap:2px}
  .c-name{font-size:9px;letter-spacing:0}
  .c-dx{top:4px;right:5px;font-size:7.5px}
  .tag{font-size:7px;padding:1px 2px}
  .stars{gap:1px 3px;margin-bottom:2px}
  .stars.major{min-height:18px;margin-bottom:3px;gap:1px 4px}
  .stars.major .star{font-size:11px}
  .stars.lucky .star,.stars.sha .star{font-size:8.5px}
  .stars.minor .star{font-size:8px}
  .bri{font-size:7px}
  .sh{font-size:7px;padding:1px}
  .c-bot{padding-top:3px;gap:2px}
  .c-gz{font-size:8.5px;letter-spacing:0}
  .c-shen{font-size:7.5px}
  .center{padding:8px;gap:3px}
  .center::before{inset:5px}
  .center .seal{width:30px;height:30px;font-size:9px;margin-bottom:2px}
  .center h3{font-size:11.5px;letter-spacing:.1em}
  .center .ln{font-size:8.5px;line-height:1.5}
  .center .kv{font-size:8px;gap:2px 6px;margin-top:2px}
  .chart-head h2{font-size:15px}
  .chart-head .born{font-size:10px}
  .timenav{gap:8px}
  .timenav .seg{width:100%}
  .legend{font-size:9px;gap:5px 10px}
  /* ---- 十三维断语 ---- */
  .read-layout{gap:12px}
  .dim-list{grid-template-columns:repeat(2,1fr);gap:4px}
  .dim-list button{padding:8px 9px;font-size:11.5px;min-height:38px}
  .dim-list button .cnt{display:none}
  .md{font-size:14px;line-height:1.9}
  .md h2,.md h3,.md .h{font-size:14px;margin:16px 0 7px}
  .md table{font-size:11px}
  .read-top{gap:6px}
  .topic-body{font-size:12.5px;line-height:1.9}
  .tbl,.fly-tbl{font-size:10.5px}
  .tbl th,.tbl td,.fly-tbl th,.fly-tbl td{padding:6px 5px}
  .pd-h .n{font-size:17px}
  .pd-text{font-size:12px}
  .pat .lv{width:34px;height:34px;font-size:11px}
  .badge{font-size:9px}
  /* ---- AI 对话 ---- */
  .ai-layout{gap:12px}
  .chat-head{padding:10px 12px}
  .chat-body{min-height:240px;max-height:none;padding:12px;height:auto}
  .chat-foot{padding:10px 12px;gap:6px}
  .chat-foot input[type=text]{flex:1 1 100%;min-width:0}
  .chat-foot .btn{flex:1 1 auto}
  .ai-status{padding:0 12px 8px}
  .preset-grid{grid-template-columns:1fr 1fr}
  .preset-grid button{min-height:34px}
  .ai-blank{padding:36px 18px}
  .msg{font-size:12.5px}
  /* ---- 合盘 ---- */
  .hp-person{padding:11px}
  .hp-mini .mc{min-height:48px;padding:4px 3px;font-size:8.5px}
  .hp-mini .mc .pn{font-size:8.5px}
  .hp-mini .mc .ms{font-size:9.5px}
  .hp-mini .ctr{font-size:10px}
  .hp-svg{max-width:100%}
  .score{flex-wrap:wrap;gap:8px}
  .score .stars{font-size:16px}
  .score .lv{font-size:16px}
  /* ---- 断语库 ---- */
  .lib-stat{grid-template-columns:repeat(2,1fr);gap:8px}
  .lib-stat .s{padding:10px}
  .lib-stat .s .n{font-size:18px}
  .year-grid{grid-template-columns:repeat(auto-fill,minmax(66px,1fr));gap:6px}
  .year-grid .y{padding:8px 3px;font-size:10.5px;min-height:38px;
        display:flex;align-items:center;justify-content:center}
  .lib-log{max-height:150px;font-size:9.5px}
  .drop{padding:16px 10px;font-size:11px}
  .notice{font-size:10.5px}
  .hint{font-size:10px}
}
/* 极窄屏兜底 */
@media (max-width:360px){
  .fnav button::before{width:22px;height:22px;font-size:12px}
  .fnav button::after{font-size:9px}
  .board{grid-template-rows:repeat(4,minmax(82px,auto))}
  .cell{min-height:82px;padding:3px 4px}
  .stars.major .star{font-size:10px}
  .tt p{display:none}
  .year-grid{grid-template-columns:repeat(4,1fr)}
}
/* 竖屏高屏：命盘格可稍微舒展 */
@media (max-width:600px) and (min-height:760px){
  .board{grid-template-rows:repeat(4,minmax(96px,auto))}
  .cell{min-height:96px}
}
'''

MOBILE_JS = r'''
<script>
/* ===== APK 手机竖屏增强（仅 UI，不触碰业务逻辑） ===== */
(function(){
  var L={chart:['盘','排盘'],reading:['断','断语'],ai:['AI','AI 解读'],
         heming:['合','合盘'],library:['库','语库']};
  var btns=document.querySelectorAll('#fnav button');
  btns.forEach(function(b){
    var x=L[b.dataset.p]||['·',''];
    b.dataset.ico=x[0]; b.dataset.lbl=x[1];
    b.addEventListener('click',function(){ try{window.scrollTo(0,0);}catch(e){} });
  });
  /* 返回键：先回命盘页，再按两次退出（由 MainActivity 调用） */
  window.__zwBack=function(){
    var on=document.querySelector('#fnav button.on');
    var b=document.querySelector('#fnav button[data-p="chart"]');
    if(on && on.dataset.p!=='chart' && b){ b.click(); return true; }
    return false;
  };
  /* 竖屏表单较长：起盘后自动滚到命盘，避免用户以为只有输入框 */
  var go=document.getElementById('goBtn');
  if(go) go.addEventListener('click',function(){
    setTimeout(function(){
      try{
        var bw=document.querySelector('.board-wrap');
        if(!bw) return;
        var card=bw.closest('.card')||bw;
        var y=card.getBoundingClientRect().top+window.pageYOffset-58;
        window.scrollTo({top:y>0?y:0,behavior:'smooth'});
      }catch(e){}
    },280);
  });
  /* 标记运行环境，便于页面内做 APK 特化提示 */
  document.documentElement.setAttribute('data-apk','1');
})();
</script>
'''


def main():
    html = SRC.read_text(encoding='utf-8')
    assert VP_OLD in html, 'viewport meta 未找到'
    html = html.replace(VP_OLD, VP_NEW, 1)

    assert '</style>' in html, '</style> 未找到'
    html = html.replace('</style>', MOBILE_CSS + '\n</style>', 1)

    assert '</body>' in html, '</body> 未找到'
    html = html.replace('</body>', MOBILE_JS + '\n</body>', 1)

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(html, encoding='utf-8')
    print(f'生成竖屏版: {DST}  {DST.stat().st_size} bytes')


if __name__ == '__main__':
    main()
