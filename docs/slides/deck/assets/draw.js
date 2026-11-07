/* 手繪幾何繪圖工具（rough.js）。用法：const D = Draw('r'); D.sq(...)
   語意：sq 方＝訓練/結構，ci 圓＝驗證/重點，tri 三角＝保留集/警示。座標皆為 1920×1080 畫布像素。 */
window.Draw = function (svgId) {
  const svg = document.getElementById(svgId), rc = rough.svg(svg);
  const C = { ink:'#1b1b1b', ind:'#2b4c7e', ver:'#e0442b', mus:'#e8b53a', grey:'#a8a296', paper:'#f3efe6' };
  const add = n => (svg.appendChild(n), n);
  const base = o => Object.assign({ stroke:C.ink, strokeWidth:2.2, roughness:1.3 }, o || {});
  const fillOf = (color, style) => color ? { fill: C[color] || color, fillStyle: style || 'hachure', hachureGap: 7, fillWeight: 2 } : {};
  const D = {
    C, rc,
    sq: (x, y, s, color, o) => add(rc.rectangle(x, y, s, s, base(Object.assign(fillOf(color), o)))),
    rect: (x, y, w, h, color, o) => add(rc.rectangle(x, y, w, h, base(Object.assign(fillOf(color), o)))),
    ci: (cx, cy, d, color, o) => add(rc.circle(cx, cy, d, base(Object.assign(fillOf(color, 'solid'), o)))),
    tri: (cx, cy, s, color, o) => add(rc.polygon([[cx, cy - s * 0.58], [cx + s / 2, cy + s * 0.42], [cx - s / 2, cy + s * 0.42]], base(Object.assign(fillOf(color, 'solid'), o)))),
    dia: (cx, cy, s, color, o) => add(rc.polygon([[cx, cy - s / 2], [cx + s / 2, cy], [cx, cy + s / 2], [cx - s / 2, cy]], base(Object.assign(fillOf(color, 'solid'), o)))),
    line: (x1, y1, x2, y2, o) => add(rc.line(x1, y1, x2, y2, base(o))),
    dash: (x1, y1, x2, y2, o) => add(rc.line(x1, y1, x2, y2, base(Object.assign({ strokeLineDash: [10, 10] }, o)))),
    curve: (pts, o) => add(rc.curve(pts, base(o))),
    poly: (pts, color, o) => add(rc.polygon(pts, base(Object.assign(fillOf(color, 'solid'), o)))),
    arrow: (x1, y1, x2, y2, o) => {
      const a = Math.atan2(y2 - y1, x2 - x1), L = 22;
      D.line(x1, y1, x2, y2, o);
      D.line(x2, y2, x2 - L * Math.cos(a - 0.45), y2 - L * Math.sin(a - 0.45), o);
      D.line(x2, y2, x2 - L * Math.cos(a + 0.45), y2 - L * Math.sin(a + 0.45), o);
    },
    cross: (cx, cy, s, o) => { const c = Object.assign({ stroke: C.ver, strokeWidth: 4 }, o); D.line(cx - s, cy - s, cx + s, cy + s, c); D.line(cx + s, cy - s, cx - s, cy + s, c); },
    /* 直條圖：values 0–max；回傳每根柱子的 {x,y,w,h} 方便放標籤 */
    bars: (x, y, w, h, values, colors, max, o) => {
      const n = values.length, gap = w / n, bw = gap * 0.6, M = max || Math.max(...values), out = [];
      D.line(x, y + h, x + w, y + h);
      values.forEach((v, i) => { const bh = h * v / M, bx = x + i * gap + (gap - bw) / 2;
        D.rect(bx, y + h - bh, bw, bh, colors[i % colors.length], o); out.push({ x: bx, y: y + h - bh, w: bw, h: bh }); });
      return out;
    },
  };
  return D;
};
