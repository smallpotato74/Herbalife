# 期權篩選工具包 — 使用說明

配合 [`options-trading-report.md`](./options-trading-report.md) 一齊用。三件嘢：

| 檔案 | 作用 |
|---|---|
| `options_screener.py` | 真·可跑嘅 Python screener（ATR + IV/HV + Greeks 評分排序） |
| `make_excel_template.py` | 生成 Excel/Google Sheets 模板（公式自動計分） |
| `options_screener_template.xlsx` | 上面生成出嚟嘅模板成品 |
| `options.html` | 📱 每日㩒入去睇嘅 dashboard 網站（卡片+spread+趨勢線+總覽表） |
| `options_data.json` / `.js` | dashboard 讀嘅數據（screener 生成） |
| `options_history.json` / `.js` | 每日 IV/HV/分數歷史（畫趨勢線） |
| `.github/workflows/options-daily.yml` | 每日自動跑 screener + 更新網站 |
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

## 5. 📱 Dashboard 網站（每日㩒入去睇）

`options.html` 係一個靜態網頁,讀 `options_data.json` 顯示：每隻標的嘅 BUY/SELL badge、
最高分候選合約、Greeks、評分條、同進出場提示。手機都睇得舒服,仲可以篩 BUY/SELL。

**dashboard 功能**：
- 每隻標的卡片：BUY/SELL badge、最高分候選合約（Greeks + 評分條）
- **Spread 組合**（defined-risk）：自動砌 Bull/Bear vertical + Iron Condor,顯示
  max賺 / max蝕 / R:R / 回本價 / 闊度,賣方唔使裸沽
- **IV/HV 趨勢線**（sparkline,紅虛線=1.0 買賣分界）
- **總覽表**：所有標的候選一個表,點欄位標題即排序
- 篩 BUY/SELL、卡片/表格切換

### 數據點嚟
```bash
# --json 寫 options_data.json/.js;--history 累積每日趨勢
python options_screener.py --tickers AAPL MSFT NVDA SPY \
    --json options_data.json --history options_history.json

# 第一次想趨勢線即刻有嘢睇,可補 demo 歷史(只限 --demo):
python options_screener.py --demo --tickers AAPL NVDA KO SPY \
    --json options_data.json --history options_history.json --demo-history 60
```

### 三種開法
1. **本地直接開**（最簡單）：雙擊 `options.html`。fetch 失敗會自動 fallback 用
   `options_data.js`（全域變數版,免 CORS）。
2. **本地 server**：`python -m http.server` → 開 `http://localhost:8000/options.html`。
3. **GitHub Pages（推薦,有網址,手機都㩒到）**：
   - Repo → **Settings → Pages** → Source 揀你個 branch（或 `main`）→ 根目錄 `/`
   - 網址會係 `https://<user>.github.io/<repo>/options.html`
   - 加入手機主畫面,每日㩒一下就睇到最新

### 每日自動更新（唔使你手動）
`.github/workflows/options-daily.yml` 已經設定好：
- 每個美股交易日 **21:30 UTC**（美東收市後）自動跑 screener（真實數據）
- 重新生成 `options_data.json/.js` 並 commit 返入 repo
- GitHub Pages 自動 serve 最新版 → 你個網站自己更新

> 想即刻試:去 repo 嘅 **Actions → 每日更新期權 Dashboard → Run workflow**（可改 tickers）。
> ⚠️ 要喺 repo **Settings → Actions → General** 開「Read and write permissions」,Action 先 push 到。
> 如果 GitHub runner 嗰陣 yfinance 被限流,workflow 會保留舊數據唔會整爛個網。

---

## 6. 進場 / 退場（機械化規則速查）

| | 進場 | 止賺 | 止蝕 | 時間 |
|---|---|---|---|---|
| **買方**（long call/put） | IV/HV低、Δ0.55–0.70、DTE 45–90 | +50~100% | −40~50% | 21 DTE 重評 |
| **賣方**（short put/call、credit） | IV/HV高、Δ0.15–0.30、DTE 30–45 | 收 50% premium | 蝕 2× credit | 21 DTE 管理避 gamma |

詳細策略（spread / iron condor / calendar / skew / GEX 等進階）見 `options-trading-report.md`。

---

## 7. 建議流程

1. `--demo` 跑一次熟習輸出格式
2. 換真實 ticker 跑 live，揀總分高 + 過濾 ✓ 嘅候選
3. 用 Excel 模板做 watchlist 長期追蹤 IVR / IV-HV
4. 模擬倉驗證 1–2 個月，校準你嘅 Δ/DTE 偏好
5. 先細注（賬戶 1% 風險）實戰，嚴守機械化止賺止蝕
