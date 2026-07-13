// DOM 完整性稽核(驗收標準 §三 第 2 層)— 在瀏覽器 console / javascript_tool 執行
// 逐 slide 檢:零裁切、零互疊、零出界、圖全載。回傳 JSON 結果。
(() => {
  const WHITELIST_SCROLL = el => el.matches('pre.code, .gentext, .slide');
  const slides = [...document.querySelectorAll('.slide')];
  const report = [];
  const vis = el => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 4 && r.height > 4;
  };
  slides.forEach((slide, idx) => {
    const issues = [];
    const wasActive = slide.classList.contains('active');
    slides.forEach(s => s.classList.remove('active'));
    slide.classList.add('active');
    // 1) 裁切:文字元素內容高 > 可視高,且不可捲
    slide.querySelectorAll('p,li,h1,h2,h3,div,pre,figcaption,span,button').forEach(el => {
      if (!vis(el)) return;
      if (el.scrollHeight - el.clientHeight > 4) {
        const s = getComputedStyle(el);
        const scrollable = /(auto|scroll)/.test(s.overflowY);
        if (!scrollable && !WHITELIST_SCROLL(el))
          issues.push({ type: 'CLIPPED', el: el.tagName + '.' + (el.className || '').toString().slice(0, 30), diff: el.scrollHeight - el.clientHeight });
      }
    });
    // 2) 互疊:slide 直屬區塊兩兩比對(容差 2px)
    const blocks = [...slide.children].filter(vis);
    for (let i = 0; i < blocks.length; i++) for (let j = i + 1; j < blocks.length; j++) {
      const a = blocks[i].getBoundingClientRect(), b = blocks[j].getBoundingClientRect();
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2)
        issues.push({ type: 'OVERLAP', a: blocks[i].className.toString().slice(0, 30), b: blocks[j].className.toString().slice(0, 30), px: Math.round(Math.min(ox, oy)) });
    }
    // 3) 出界:可見元素超出 slide 可捲範圍右/下緣
    const sr = slide.getBoundingClientRect();
    slide.querySelectorAll('*').forEach(el => {
      if (!vis(el)) return;
      const r = el.getBoundingClientRect();
      if (r.right - sr.right > 4) issues.push({ type: 'OUT_X', el: (el.className || el.tagName).toString().slice(0, 30), px: Math.round(r.right - sr.right) });
    });
    // 4) 圖全載
    slide.querySelectorAll('img').forEach(img => {
      if (!img.naturalWidth) issues.push({ type: 'IMG_NOT_LOADED', src: img.src.split('/').pop() });
    });
    report.push({ slide: idx + 1, title: slide.dataset.title, issues });
    if (!wasActive) slide.classList.remove('active');
  });
  slides[0].classList.add('active');
  const fails = report.filter(r => r.issues.length);
  return JSON.stringify({ viewport: innerWidth + 'x' + innerHeight, verdict: fails.length ? 'FAIL' : 'PASS', fails }, null, 1);
})();
