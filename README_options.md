# 期權篩選工具包 — 使用說明

配合 [`options-trading-report.md`](./options-trading-report.md) 一齊用。三件嘢：

| 檔案 | 作用 |
|---|---|
| `options_screener.py` | 真·可跑嘅 Python screener（ATR + IV/HV + Greeks 評分排序） |
| `make_excel_template.py` | 生成 Excel/Google Sheets 模板（公式自動計分） |
| `options_screener_template.xlsx` | 上面生成出嚟嘅模板成品 |
| `demo_output.txt` | 離線 demo 嘅實際輸出（畀你預覽個樣） |

> ⚠️ 教育用途，非投資建議。期權高風險，落場前用模擬倉。

---

## 1. 安裝

```bash
pip install yfinance pandas numpy openpyxl
```

`options_screener.py` 本身只靠標準庫 + yfinance；Greeks 係自己用 Black-Scholes 計，唔使 scipy。

---

## 2. 跑 Python Screener

### (a) 離線 demo（無網都跑到，用合成數據）
```bash
python options_screener.py --demo --tickers AAPL NVDA KO SPY
```
會見到每隻標的嘅方向建議（BUY/SELL）同最高分嘅候選合約。輸出樣本喺 `demo_output.txt`。

### (b) 真實數據（你部機要有網）
```bash
python options_screener.py --tickers AAPL MSFT NVDA --side auto
```

常用參數：
```bash
--side auto|buy|sell     # auto = 用 IV/HV + HV-Rank 自動判斷
--min-dte 30 --max-dte 60
--min-oi 500 --min-vol 50 --max-spread 0.06
--top 5                  # 每隻標的顯示頭幾名
--rate 0.045            # 無風險利率(計 Greeks)
```

### (c) 用 Tradier（有真 Greeks/IV，需 API token）
```bash
python options_screener.py --tickers AAPL --tradier-token YOUR_TOKEN
# 實盤數據加 --tradier-live；唔加就用 sandbox
```
申請：<https://documentation.tradier.com/>

---

## 3. 評分邏輯（每項 25 分，滿分 100）

| 子項 | 點計 |
|---|---|
| 流動性 | OI 大、成交多、買賣價差窄 → 高分（硬性過濾：OI≥500、量≥50、價差≤6%） |
| Delta | 落喺目標區間（買 0.55–0.70 / 賣 0.15–0.30）→ 滿分 |
| 到價配合 | 主用市場引伸 1SD = `Spot×IV×√(DTE/365)`；買方 strike 喺 1SD 內好、賣方喺 1SD 外好。另顯示 ATR-based 移動做對照 |
| IV regime | 用 `IV/HV` ratio：買方想低（平）、賣方想高（貴） |

**方向判斷**：`IV/HV > 1.2` 或 HV-Rank 高 → **SELL**；`IV/HV < 1.0` 或 HV-Rank 低 → **BUY**。
到期前有 earnings + 買方 → 自動扣分（IV crush 風險）。

> 📌 **關於真 IVR**：yfinance 冇 IV 歷史，所以本工具用 **IV/HV ratio + HV-Rank** 做可計算嘅 regime proxy。想要正宗 IV Rank（IV 對自己一年高低），請喺 Excel 模板手動填一年 IV 高低，或接 ORATS / market-data 供應商。

---

## 4. Excel / Google Sheets 模板

生成：
```bash
python make_excel_template.py     # 出 options_screener_template.xlsx
```

三張表：
- **說明**：用法 + 評分規則
- **Watchlist**：填 現價 / ATR / 當前IV / 一年IV高低 / HV20 / earnings → 自動出 **IVR、IV/HV、方向建議、1SD 預期移動**
- **OptionScorer**：每行填一個候選合約 → 自動計 **expected move + 4 項子分 + 總分 + 過濾✓/✗**

🟡 黃色格 = 你自己填　🟢 綠色格 = 公式自動計（唔好改）。

公式全部用通用函數（IF/MIN/MAX/SQRT/LN/AND），可以**整份貼上 Google Sheets** 直接用。

---

## 5. 進場 / 退場（機械化規則速查）

| | 進場 | 止賺 | 止蝕 | 時間 |
|---|---|---|---|---|
| **買方**（long call/put） | IV/HV低、Δ0.55–0.70、DTE 45–90 | +50~100% | −40~50% | 21 DTE 重評 |
| **賣方**（short put/call、credit） | IV/HV高、Δ0.15–0.30、DTE 30–45 | 收 50% premium | 蝕 2× credit | 21 DTE 管理避 gamma |

詳細策略（spread / iron condor / calendar / skew / GEX 等進階）見 `options-trading-report.md`。

---

## 6. 建議流程

1. `--demo` 跑一次熟習輸出格式
2. 換真實 ticker 跑 live，揀總分高 + 過濾 ✓ 嘅候選
3. 用 Excel 模板做 watchlist 長期追蹤 IVR / IV-HV
4. 模擬倉驗證 1–2 個月，校準你嘅 Δ/DTE 偏好
5. 先細注（賬戶 1% 風險）實戰，嚴守機械化止賺止蝕
