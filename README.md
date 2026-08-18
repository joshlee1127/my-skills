# my-skills

給 Claude Code 用的 Agent Skills 倉庫。

目前收錄兩個技能：

- **[create-agents](skills/create-agents/)** — 把工時估算表轉成該專案專用的 `AGENTS.md` 與 `progress.md`。
- **[read-excel](skills/read-excel/)** — 快速、唯讀讀取任意 .xlsx／.xlsm 檔案內容，`create-agents` 讀取非工時估算表結構的 Excel 檔案時會用到，安裝 `create-agents` 時會一併安裝。

---

## create-agents

### 解決什麼問題

工時估算表是專案的**範圍合約**：客戶付的是表上那幾條作業項目的錢。把 AI 代理人放進這種專案時，最大的風險不是它做不好，而是它**熱心地做了表上沒有的事**——多裝一個工具、多掃一個網段、順手改一個設定。這些都沒報價。

這個技能把估算表翻譯成代理人的執行邊界：每一條規則都要能指回估算表的某一列，指不回去就不寫。

### 產出兩份檔案

**`AGENTS.md`** — 12 節的專案代理人指引，各節內容從估算表的欄位推導：

| 估算表欄位 | 產出到                                                                                          |
| ---------- | ----------------------------------------------------------------------------------------------- |
| 項目分類   | §1 作業項目、§3 技能對應、§5 架構分層、§11 檢查項目                                         |
| 作業項目   | §1 每條 bullet 的內容，保留原文用詞                                                            |
| 項次       | §4 提示檔的「涵蓋項次」、`progress.md` 的對照鍵                                              |
| 項目備註   | §6 技術堆疊（備註裡的`Azure Portal → Subscriptions`、`Get-MgSubscribedSku` 就是工具清單） |
| 驗收項目   | §4 驗收標準、§8 文件驗證、§11 交付前 checklist                                               |
| L1/L2 工時 | **不寫進去**——工時是報價資訊，不是執行邊界                                              |

技能也會依作業項目的動詞判定專案性質（**唯讀健檢** vs **變更型導入**），這決定 §10 安全性的基調——寫錯會讓代理人在客戶生產環境上做錯事。

**`progress.md`** — 由估算表整張展開的計畫表兼進度表。所有作業項目一開始就在裡面，狀態預設「未開始」，檔頭帶覆蓋率統計。

這是刻意的設計：邊做邊長的進度檔只回答得了「做過什麼」，回答不了「還剩多少沒做」，而後者才是專案中期會被問到的問題。

---

## read-excel

### 解決什麼問題

直接把 .xlsx（其實是 zip + XML）當文字讀，拿不到人看得懂的內容；用完整的試算表編輯工具處理「只是想看資料」的需求又太重、太慢，尤其是活頁簿很大、工作表很多，或合併儲存格讓資料看起來像缺漏的時候。

`read-excel` 是一支唯讀、只管把格線資料忠實搬出來的小工具：不猜欄位語意、不假設任何表格結構，也不修改檔案。`create-agents` 讀取工時估算表以外的 Excel（客戶確認表、資產清單⋯）時就是靠它。

```bash
# 先看活頁簿有幾個工作表、各自多大
python skills/read-excel/scripts/read_excel.py <file.xlsx> --list-sheets

# 傾印指定工作表（預設 Markdown、展開合併儲存格、最多 500 列）
python skills/read-excel/scripts/read_excel.py <file.xlsx> --sheet <name>

# 結構化輸出，供程式接續處理
python skills/read-excel/scripts/read_excel.py <file.xlsx> --format json --out out.json
```

細節與參數說明見 [skills/read-excel/SKILL.md](skills/read-excel/SKILL.md)。

---

## 安裝

### 方法 1：npx（推薦）

```bash
npx skills add https://github.com/joshlee1127/my-skills.git -s create-agents,read-excel
```

`-s create-agents,read-excel` 確保兩個技能一起裝進來——`create-agents` 讀取非估算表結構的 Excel 檔案時會呼叫 `read-excel`，少裝了會在執行到那一步時失敗。安裝到 `~/.claude/skills/`，之後要更新重跑同一行即可。

只想單獨試 `read-excel`（跟工時估算表無關的場合也能用）可以只裝它：

```bash
npx skills add https://github.com/joshlee1127/my-skills.git -s read-excel
```

### 方法 2：clone + 符號連結

想跟著改技能內容的話用這個，改完立即生效，不必重裝：

```bash
git clone https://github.com/joshlee1127/my-skills.git
```

**Windows**（需開發人員模式或系統管理員權限）：

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.claude\skills\create-agents" `
  -Target "<clone 路徑>\skills\create-agents"
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.claude\skills\read-excel" `
  -Target "<clone 路徑>\skills\read-excel"
```

**macOS / Linux**：

```bash
ln -s "$(pwd)/skills/create-agents" ~/.claude/skills/create-agents
ln -s "$(pwd)/skills/read-excel" ~/.claude/skills/read-excel
```

### 方法 3：直接複製

不想處理符號連結權限就複製資料夾：

```bash
cp -r skills/create-agents skills/read-excel ~/.claude/skills/
```

### 需求

- **Claude Code**（技能本體）
- **Python 3.8+** 與 **openpyxl**（解析 xlsx 用）：

```bash
pip install openpyxl
```

安裝完可以驗一下技能有沒有被認出來——在 Claude Code 執行 `/create-agents`，或直接跑下面的腳本。

---

## 使用

### 在 Claude Code 裡

把估算表放進專案，然後說：

```
依照 context/工時估算表.xlsx 產生 AGENTS.md
```

技能會解析估算表 → 判定專案性質 → 盤點已安裝的技能做對應 → 對缺口跑 `npx skills find` 搜 skills.sh 並過濾 → 寫出 `AGENTS.md` → 展開 `progress.md`。過程中需要補的資訊（客戶名稱、交付路徑約定等）會一次問完。

搜到的技能只會進 §3 的「建議安裝」區並附安裝指令與使用限制，**不會自行安裝，也不會被當成可用技能**。搜尋結果會先過濾掉攻擊性技能——實測搜 `active directory`，前五名有四個是紅隊攻擊技能，把那種東西掛進客戶唯讀健檢是事故等級的錯誤。

### 直接跑腳本

不想走完整流程，只想看估算表被解析成什麼：

```bash
# 人看的大綱
python skills/create-agents/scripts/read_estimate.py <估算表.xlsx> --format md

# 結構化 JSON，供程式接續處理
python skills/create-agents/scripts/read_estimate.py <估算表.xlsx> --out out.json

# 展開成計畫表 / 進度表
python skills/create-agents/scripts/init_progress.py <估算表.xlsx> --out progress.md
```

> **Windows 提醒**：腳本一律以 UTF-8 位元組輸出。用管線接給另一支程式時對方可能以 cp950 解碼而讀成亂碼，需要接續處理請用 `--out` 直接寫檔。

`init_progress.py` **重跑是安全的**：以作業項目為鍵保留既有狀態，只補新增項目；估算表改版後被刪掉的項目會移到檔尾「估算表已無此項」等人工確認，不會靜靜消失。所以估算表變更時直接重跑，不要手工同步。

---

## 估算表格式要求

只要有這幾個欄位就能解析，順序不拘、多餘欄位無妨：

| 欄位               | 必要           | 說明                                                        |
| ------------------ | -------------- | ----------------------------------------------------------- |
| 項目分類           | 建議           | 沒有的話全部歸到「(未分類)」                                |
| 項次               | 建議           | 覆蓋率對帳的依據                                            |
| **作業項目** | **必要** | 沒有這欄無法解析                                            |
| 項目備註           | 建議           | §6 技術堆疊的主要來源                                      |
| 驗收項目           | 建議           | §4／§8／§11 的來源                                       |
| L1/L2 工時         | 選用           | 欄名含`L1`、`L2`、`工時`、`人時`、`人天` 皆可辨識 |

解析器已處理手工維護的估算表常見的幾種狀況：

- 標題列不在第 1 列（往下掃 15 列找）
- 「項目分類」用合併儲存格，只寫在區塊第一列
- 每個區塊尾端的「小計／合計／總計」列（歸為分類工時，不當作業項目）
- **資料打錯欄**——真實案例是標題「驗收項目」在 K 欄、內容打在 L 欄。這些內容會被收進 `extra` 並示警，而不是靜靜丟掉，因為那通常正是驗收標準

csv 或格式古怪到解不動的表，技能會改用人工整理，但仍會保住「分類／項目／備註／驗收」四類資訊。

---

## 目錄結構

```
my-skills/
├── skills/create-agents/
│   ├── SKILL.md                      # 主流程（8 步）+ 欄位→節次對照 + 交付前檢查
│   ├── scripts/
│   │   ├── read_estimate.py          # 估算表 → JSON / 大綱（工時估算表專用，懂欄位語意）
│   │   └── init_progress.py          # 估算表 → progress.md（可安全重跑）
│   ├── references/
│   │   ├── agents-md-sections.md     # 12 節逐節撰寫指引，含好／壞對照
│   │   └── skill-mapping.md          # §3 技能對應原則
│   └── assets/
│       └── AGENTS.template.md        # 12 節骨架範本
├── skills/read-excel/
│   ├── SKILL.md                      # 唯讀讀取任意 .xlsx／.xlsm，不假設表格結構
│   └── scripts/
│       └── read_excel.py             # 列工作表 / 傾印內容（md／json）/ 展開合併儲存格
├── output/                           # 範例估算表
└── context/                          # 專案來源資料（不進版控）
```

`output/AWS健檢工時估算(範例假資料).xlsx` 是一份可以直接拿來試跑的假資料估算表。
