#!/usr/bin/env python3
"""WorkShop-ARCH QAQC 迴圈檢核器 — 全綠才算過,任一 FAIL 即中止交付。
對照 QAQC.md A 系列規則 + 跨檔一致性(index.html ↔ 講師逐字稿.md ↔ prompt-templates.md ↔ criteria-verified.md)。"""
import re, os, sys, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
html  = open(f'{ROOT}/presentation/index.html', encoding='utf-8').read()
scr   = open(f'{ROOT}/講師逐字稿.md', encoding='utf-8').read()
tpl   = open(f'{ROOT}/prompt-templates.md', encoding='utf-8').read()

fails, warns = [], []
ok = lambda s: print(f"  ✅ {s}")
def fail(s): fails.append(s); print(f"  ❌ {s}")
def warn(s): warns.append(s); print(f"  ⚠️  {s}")

print("== 1. 結構:8 頁與編號 ==")
titles = re.findall(r'<section[^>]*data-title="([^"]+)"', html)
if len(titles) == 8: ok(f"8 頁:{titles}")
else: fail(f"頁數 {len(titles)} ≠ 8:{titles}")
kickers = re.findall(r'(\d\d) / 08', html)
# 第 8 頁為信紙式結語,原設計即無 kicker 編號 → 檢核 01–07 連續即可
if kickers == [f"{i:02d}" for i in range(1,8)]: ok("kicker 編號 01–07 連續(第 8 頁信紙式,依設計免編號)")
else: fail(f"kicker 編號異常:{kickers}")

print("== 2. 逐字稿:頁對應與時間軸 ==")
pages = re.findall(r'## 第 (\d) 頁・([^\(]+)\((\d):(\d\d)–(\d):(\d\d)\)', scr)
if len(pages) == 8: ok("逐字稿 8 頁段落齊")
else: fail(f"逐字稿頁段 {len(pages)} ≠ 8")
prev_end = 3  # 第1頁從0:00起,以分鐘累計檢查連續性
spans = [(int(h1)*60+int(m1), int(h2)*60+int(m2), n) for n,_,h1,m1,h2,m2 in pages]
cont = all(spans[i][1] == spans[i+1][0] for i in range(len(spans)-1))
if spans and spans[0][0]==0 and spans[-1][1]==60 and cont: ok("時間軸 0:00–1:00 連續無縫")
else: fail(f"時間軸不連續或未滿60分:{[(a,b) for a,b,_ in spans]}")

print("== 3. 用語紀律(委託人規則:台灣建築用語)==")
for w in ['對表','黃金路徑','案型']:
    for name,txt in [('index.html',html),('逐字稿',scr),('templates',tpl)]:
        c = txt.count(w)
        if c: fail(f"禁用詞「{w}」在 {name} 出現 {c} 次")
if not any(f.startswith('禁用詞') for f in fails): ok("禁用詞(對表/黃金路徑/案型)全檔歸零")
# 判準:html 僅允許「判準來源」;逐字稿同標準
for name,txt in [('index.html',html),('逐字稿',scr)]:
    hits = [m for m in re.findall(r'判準..?', txt) if not m.startswith('判準來源')]
    if hits: fail(f"「判準」殘留於 {name}(應為檢討標準):{hits}")
if not any('判準' in f for f in fails): ok("「判準」僅存於固定句「判準來源」")

print("== 3b. 白話紀律(委託人規則:白話+建築人視角,禁文言/技術腔)==")
literary = ['迭代','匯合','讓渡','混沌','兌現','收殺','暗線','裁決','賦能','範式','閉環']
scr_body = scr.split('**修訂紀錄**')[0]  # 修訂紀錄允許引用被禁的舊詞
lit_hits = [(w, scr_body.count(w)) for w in literary if w in scr_body]
if not lit_hits: ok("逐字稿無文言/技術腔詞彙")
else:
    for w,c in lit_hits: fail(f"文言/技術詞「{w}」在逐字稿出現 {c} 次(應改白話)")
anchors = ['法規檢討表','圖審','技師','協調會']
miss = [a for a in anchors if a not in scr]
if not miss: ok("建築實務錨點齊備(法規檢討表/圖審/技師/協調會)")
else: fail(f"缺建築實務錨點:{miss}")
cues = len(re.findall(r'〔指', scr))
if cues >= 8: ok(f"逐字稿含帶圖講解指引 {cues} 處(≥8)")
else: fail(f"帶圖講解指引僅 {cues} 處(<8)——圖不該只掛在版面上")

print("== 4. A1:法規數字白名單 ==")
whitelist = {'1/5','20','1/8','12.5','75','80','2','500','45','30','100','50','41','101','188','300'}
fictional = {'9.5','3.0'}
html_nocmt = re.sub(r'/\*.*?\*/', '', html, flags=re.S)  # CSS 註解不算法規語境
ctx = re.findall(r'[^><\n]{0,50}(?:採光|排煙|樓地板|防煙|區劃|公分|公尺|平方公尺|§|條)[^><\n]{0,50}', html_nocmt+scr)
nums = {m for c in ctx for m in re.findall(r'\d+(?:\.\d+)?(?:/\d+)?', c)}
bad = {n for n in nums if n not in whitelist|fictional
       and not re.fullmatch(r'(19|20)\d\d', n) and n not in {'0','1','3','4','5','8','31','35','42','07','12','13','1.5','1.2','1.8'}}
if not bad: ok("法規語境數字全in白名單(1.5/1.2/1.8為示範窗尺寸)")
else: fail(f"白名單外數字:{sorted(bad)}")
for f_ in fictional:
    seg = html[max(0,html.find(f_)-120):html.find(f_)+120]
    if '虛構' in seg or '示範' in seg: ok(f"虛構值 {f_}% 帶標注")
    else: fail(f"虛構值 {f_}% 未帶標注")

print("== 5. A2:範本一致性(html注入 vs prompt-templates.md)==")
for key in ['PASS 或 FAIL','無法檢核','同意 / 不同意','【修正】','無法複核']:
    if key in tpl and key in html: ok(f"關鍵句同步:「{key}」")
    elif key in tpl: fail(f"範本句「{key}」未見於 index.html")
    else: warn(f"「{key}」不在 prompt-templates.md(可能已改寫,需人工確認)")

print("== 6. A3:board 目錄未被動過 ==")
r = subprocess.run(['diff','-r', f'{ROOT}/presentation/board',
    '/Users/shuotaochiang/Desktop/WorkShop/presentation/board'], capture_output=True, text=True)
if r.returncode == 0: ok("board/ 與 WorkShop 原版 byte-level 相同")
else: fail(f"board/ 有差異:\n{r.stdout[:300]}")

print("== 7. 概念貫穿:語意/意義、三塊、兩個動手 ==")
for concept in ['語意','意義','塊一','塊二','塊三']:
    inh, ins = concept in html, concept in scr
    if inh and ins: ok(f"「{concept}」雙檔皆有")
    else: fail(f"「{concept}」缺席:html={inh} 逐字稿={ins}")
for must,where in [('我採用了',html),('我採用了',scr),('無法檢核',html),('居室',html)]:
    if must not in where: fail(f"必備句「{must}」缺席")
ok("裁決句/誠實句檢查完成") if not any('必備句' in f for f in fails) else None

print("== 8. 需求追溯:兩觀念皆為全員動手 ==")
if '動手三' in html and ('全員' in html or '每個人' in html): ok("多模型調度=全員動手(非示範)")
# 觀念升級(2026-07-13):任務契約,不靠人設
if '你現在是' not in html and '你現在是' not in tpl: ok("零人設 prompt(任務契約:起點/終點/流程/修正)")
else: fail("殘留人設句「你現在是…」")
for kw in ['【任務】','【起點】','【終點】','【流程】','【修正】']:
    if html.count(kw) >= 2: pass
    else: fail(f"任務契約要素「{kw}」未在兩張卡齊備")
if not any('任務契約要素' in f for f in fails): ok("兩張卡任務契約五要素齊備")
else: fail("第6頁疑似仍為示範模式")
if re.search(r'塊一不要動|規則.{0,6}不.{0,4}動', scr) and re.search(r'再查一次|再檢核|再測', scr): ok("LOOP 來回段存在(塊一不動、塊二改了再測)")
else: fail("LOOP 來回段缺失")

print("== 10. 視覺整合(故事板處方 §零)==")
css_checks = [
    ('--color-paper:#f3f1ed', 'Parchment 畫布(驗收標準§二)'),
    ('--color-ink:#181011', 'Ink Black 主墨'),
    ('--color-dark:#302023', 'Aubergine 深色反轉節'),
    ('--color-bone:#d8d4d4', 'Bone 髮絲線'),
    ('--page-max:1200px', '版心 1200px'),
    ('mix-blend-mode:multiply', '淺頁圖融接(multiply)'),
    ('prefers-reduced-motion', '動效尊重 reduced-motion'),
]
for token, name in css_checks:
    if token.replace(' ','') in html.replace(' ',''): ok(name)
    else: fail(f"缺 {name}({token})")
cool = [g for g in ['#fafafa','#eeeeee'] if re.search(rf'{g}(?![0-9a-fA-F])', html)]
# 零例外裁定(2026-07-13):禁彩色 accent、單一字族
if '#B5472A' not in html and '#b5472a' not in html: ok("磚紅已全數拔除(零彩色 accent)")
else: fail("殘留磚紅 #B5472A")
if not re.search(r'font-family:[^;]*(?:serif|Fraunces|Georgia)', html.replace('sans-serif','SANS').replace('ui-sans-serif','SANS')): ok("單一 grotesque 字族(襯線已清除)")
else: fail("殘留襯線字族")
if 'grayscale' not in html: ok("圖像層保留原生紅色強調(2026-07-13 委託人裁定);UI 層仍零彩色")
else: fail("插圖不應再套 grayscale(委託人已恢復圖像紅色)")
if not cool: ok("冷灰色票已清除")
else: fail(f"殘留冷灰:{cool}")
if 'can-scroll' in html and re.search(r'\.slide\{[^}]*overflow-y:auto', html): ok("內容完整優先:slide 內捲+can-scroll 捲動指示(驗收標準§一)")
else: fail("slide 捲動策略未落實(需 overflow-y:auto + can-scroll 指示)")
if '每一頁是一個節拍' in html: ok("互動提示語就位")
else: fail("互動提示語缺席")

print("== 9. 插圖三方一致(插圖規劃.md ↔ assets/arch ↔ html 引用)==")
plan = open(f'{ROOT}/插圖規劃.md', encoding='utf-8').read()
plan_ids = set(re.findall(r'\bp\d-[a-d]\b', plan))
disk_ids = {f[:-4] for f in os.listdir(f'{ROOT}/presentation/assets/arch') if f.endswith('.png')}
html_ids = set(re.findall(r'assets/arch/(p\d-[a-d])\.png', html))
if plan_ids == disk_ids == html_ids and len(plan_ids) == 16:
    ok(f"16 張三方一致(規劃/實檔/引用)")
else:
    fail(f"插圖不一致:規劃{len(plan_ids)} 實檔{len(disk_ids)} 引用{len(html_ids)};"
         f"缺檔{sorted(plan_ids-disk_ids)} 缺引用{sorted(plan_ids-html_ids)} 多引用{sorted(html_ids-plan_ids)}")
imgs = re.findall(r'<img[^>]*assets/arch[^>]*>', html)
noalt = [i[:60] for i in imgs if not re.search(r'alt="[^"]{4,}"', i)]
if not noalt: ok("每張 img 皆有白話 alt 描述")
else: fail(f"img 缺 alt:{noalt}")
dup = [i for i in html_ids if html.count(f'assets/arch/{i}.png') != 1]
if not dup: ok("每張圖恰好引用一次")
else: fail(f"重複/異常引用:{dup}")

print("== 11. V 系列:版面技術規則(靜態可查部分)==")
# V1 凡設 max-height 的文字容器(非 img),同一規則須有 overflow-y:auto 或該 selector 已於他處定義捲動
mh_rules = re.findall(r'([^{}]+)\{([^{}]*max-height[^{}]*)\}', html)
bad_clip = []
for sel, body in mh_rules:
    if any(k in sel for k in ('img','figure','.ill','p1-bg')): continue  # 圖層容器非文字框
    if 'overflow-y:auto' in body.replace(' ',''): continue
    base = sel.strip().split()[-1].split('{')[0]
    if re.search(rf'{re.escape(base)}[^{{]*\{{[^}}]*overflow-y:\s*auto', html): continue
    bad_clip.append(sel.strip())
if not bad_clip: ok("V1 所有 max-height 文字框皆可捲(無「被切但捲不到」)")
else: fail(f"V1 文字框設高卻無捲動:{bad_clip}")
# V2 可捲區必須「看得出可捲」:滾軸樣式 + 文字暗示
if '::-webkit-scrollbar' in html and '內文可捲動' in html: ok("V2 捲動可見性:滾軸樣式+「⇣ 內文可捲動」暗示")
else: fail("V2 可捲區缺可見暗示(macOS 滾軸預設隱形)")
# V3 大標行高防疊字
lh = re.findall(r'h[12]\.display\{[^}]*line-height:([\d.]+|var\([^)]+\))', html)
bad_lh = [x for x in lh if not x.startswith('var') and float(x) < 1.0]
if not bad_lh: ok(f"V3 display 標題行高安全(≥1.0):{lh}")
else: fail(f"V3 標題行高過緊會疊字:{bad_lh}")
# V8 禁 vh 尺寸(驗收標準§一鐵則 1):高度只能來自內容或固定 px
vh_rules = re.findall(r'(?:max-height|min-height|height):\s*[\d.]+vh', html)
if not vh_rules: ok("V8 全檔零 vh 尺寸(寬螢幕互疊事故根絕)")
else: fail(f"V8 殘留 vh 尺寸:{vh_rules}")
# V9 圓角紀律:容器 ≤8px,藥丸 100px 僅限 CTA
radii = set(re.findall(r'border-radius:\s*(\d+)px', html))
bad_r = [r for r in radii if int(r) > 8 and r != '100']
if not bad_r: ok(f"V9 圓角紀律(≤8px,pill 100px 例外):{sorted(radii)}")
else: fail(f"V9 圓角違規:{bad_r}")
# V10 同列兄弟圖:route-card 需有統一盒高與圖說座位(渲染層由 dom_audit 驗)
if re.search(r'\.route-card figure\.ill img\{height:\d+px', html) and 'figcaption' not in html: ok("V10 路線卡統一盒高;全檔零圖說(2026-07-13 委託人裁定:圖說干擾)")
else: fail("V10 未落實(盒高)或殘留 figcaption")
kl = html.count('class="keyline"')
if kl >= 4: ok(f"V7 金句座位(keyline)就位 {kl} 處(敘事審查修正)")
else: fail(f"V7 金句座位僅 {kl} 處(<4)——金句不得埋在頁底小字")
print("  ℹ️  渲染層檢核(疊字/錯位/死留白/一屏入內)無法純靜態驗——依 QAQC.md V5:每次改版必須跑一次 Chrome 100% 逐頁截圖目視,兩個角度缺一不可")

print()
print(f"===== QAQC 結果:{'🟢 全綠 PASS' if not fails else f'🔴 {len(fails)} FAIL'},{len(warns)} 警告 =====")
sys.exit(1 if fails else 0)
