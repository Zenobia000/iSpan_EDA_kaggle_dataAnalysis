from common import AI_TIP, SETUP

NAME = "M2_hypothesis_eda"
CELLS = [
    ("md", """
# M2｜假設驅動 EDA：從資料找證據（3h）

原則：**先寫預期，再跑程式。** 沒有預期的圖表不畫。

本單元產出：3 張以上假設卡（至少 1 張被推翻或證據不足），以及 Lab1：相關 ≠ 因果。
""" + AI_TIP.format(skill="hypothesis-eda", agent="eda-agent")),
    ("code", SETUP),
    ("code", """
from olist_course.data.build_base import build_eda_table
from olist_course.data.load import load_tables

T = load_tables()
eda = build_eda_table(T)   # ⚠️ 含 T0 之後的欄位：只能理解機制，不能當特徵
eda["is_late"] = (eda["delivery_delay_days"] > 0).astype(int)
eda.shape
"""),
    ("md", """
## 0. 先看整體：差評率隨時間的變化
這張圖會在 M4 的「分布偏移」再出現一次。
"""),
    ("code", """
monthly = eda.set_index(config.T0_COL)[config.TARGET].resample("MS").agg(["mean", "size"])
monthly = monthly[monthly["size"] > 300]
ax = monthly["mean"].plot(marker="o", figsize=(10, 3), title="Low-review rate by purchase month")
for d in (config.TRAIN_END, config.VALID_END):
    ax.axvline(pd.Timestamp(d), ls="--", c="grey")
plt.show()
"""),
    ("md", """
## H1：實際遲到的訂單，差評率顯著較高

- 機制：顧客期待落空
- **預期**（先寫下來再跑）：___ 倍
"""),
    ("sol", """
h1 = eda.dropna(subset=["delivery_delay_days"]).groupby("is_late")[config.TARGET].agg(["size", "mean"])
h1["ratio_vs_on_time"] = h1["mean"] / h1.loc[0, "mean"]
h1
""", """
# TODO：依 is_late 分組，算訂單數與差評率，以及遲到/準時的倍數
"""),
    ("md", """
## Lab1：相關 ≠ 因果

H1 的關聯非常強。但「遲到」本身在 T0 不可得，而且可能有**混雜因素**同時影響遲到與差評。

**任務**：
1. 提出至少兩個競爭解釋（例如：偏遠地區、承諾天數很長、特定品類）
2. 在混雜因素的每一層內，再比較一次遲到 vs 準時
3. 判斷：「遲到 → 差評」在分層後是否仍然成立？混雜因素本身（T0 可得）能不能當特徵？
"""),
    ("sol", """
eda["est_days_bin"] = pd.qcut(
    (eda["order_estimated_delivery_date"] - eda[config.T0_COL]).dt.days, 4,
    labels=["short", "mid", "long", "very_long"],
)
strat = eda.dropna(subset=["delivery_delay_days"]).pivot_table(
    index="est_days_bin", columns="is_late", values=config.TARGET, aggfunc="mean", observed=True
)
strat.columns = ["on_time", "late"]
strat.assign(ratio=strat["late"] / strat["on_time"])
""", """
# TODO：以承諾送達天數（estimated - purchase）分 4 箱，每箱內比較 late vs on_time 的差評率
"""),
    ("sol", """
by_state = eda.dropna(subset=["delivery_delay_days"]).groupby("customer_state").agg(
    n=("order_id", "size"), late_rate=("is_late", "mean"), low_rate=(config.TARGET, "mean")
).query("n > 500")
ax = sns.scatterplot(data=by_state, x="late_rate", y="low_rate", size="n", legend=False)
for s, row in by_state.iterrows():
    ax.annotate(s, (row["late_rate"], row["low_rate"]), fontsize=8)
plt.title("State level: late rate vs low-review rate")
plt.show()
""", """
# TODO：以 customer_state 聚合，畫「遲到率 vs 差評率」散佈圖（生態謬誤警告：州層級 ≠ 訂單層級）
"""),
    ("ans", """
- 分層後，每一箱內遲到訂單的差評率仍然高出數倍 → 「遲到」與差評的關聯不是單純由承諾天數造成
- 但這仍然**不是因果證明**：可能還有未觀察的因素（賣家品質同時造成慢出貨與商品不符）
- 對建模的啟示：遲到在 T0 不可知；T0 可用的代理是「遲到風險」——承諾天數、距離、跨州、賣家過去的遲到紀錄
- 州層級的相關只能當線索，不能推論到單筆訂單（生態謬誤）
"""),
    ("md", """
## H2：多賣家訂單較容易差評
- 機制：分批到貨、其中一包遲到或缺件
- **預期**：___
"""),
    ("sol", """
eda.groupby(eda["n_sellers"].clip(upper=3))[config.TARGET].agg(["size", "mean"])
""", """
# TODO：依 n_sellers（>=3 合併）分組看差評率與樣本數
"""),
    ("md", """
## H3：運費占比越高越容易差評
- 機制：覺得「運費比商品還貴」不划算
- **預期**：___
"""),
    ("sol", """
ratio = eda["items_freight"] / (eda["items_price"] + eda["items_freight"])
eda.groupby(pd.qcut(ratio, 5), observed=True)[config.TARGET].agg(["size", "mean"])
""", """
# TODO：運費占比分 5 箱，看差評率是否單調
"""),
    ("md", "## 假設卡（依 hypothesis-eda skill 模板填寫三張）"),
    ("ans", """
#### H1：實際遲到 → 差評　**支持（但非因果）**
- 結果：遲到訂單差評率約為準時的數倍；在承諾天數分層內仍成立
- 競爭解釋：賣家品質同時造成慢出貨與商品問題
- T0 代理特徵：`est_delivery_days`、`customer_seller_km`、`same_state`、賣家過去遲到率（M3 練習）

#### H2：多賣家 → 差評　**支持，但樣本少**
- 多賣家訂單僅約 1%，差評率明顯較高；對整體模型貢獻有限

#### H3：運費占比 → 差評　**證據不足 / 弱**
- 分箱後差評率變化不大、非單調 → 預期增益小，M4 的 ablation 會檢驗
"""),
]
