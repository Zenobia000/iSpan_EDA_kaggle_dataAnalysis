---
type: finding
id: FND-007
confidence: medium
source: ["[[EXP-007 模型比較]]"]
created: 2026-11-06
tags: [finding, model]
---
# LGBM 穩定勝過線性模型，但 RF 過擬合最重

## 證據
LGBM 0.291 vs LogReg 0.277（3/3 月份勝出）；RF 0.278 但 train/valid gap 0.31。
LogReg 只差 0.014 且幾乎不過擬合 → 需要可解釋性時是合理的替代。
