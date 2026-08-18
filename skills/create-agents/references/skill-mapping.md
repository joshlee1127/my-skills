# §3 技能對應指引

目標：讓估算表的每個**項目分類**都有明確的執行手段——不是找到技能，
而是讓代理人知道這類作業該用什麼做、以及什麼不能碰。

## 步驟

### 1. 先盤點實際裝了什麼

```bash
ls ~/.claude/skills/ .claude/skills/ .agents/skills/ 2>/dev/null
```

也把對話中已列出的可用技能（plugin 技能、MCP 提供的能力）納入考慮。
**只有出現在這份清單裡的技能才能寫進 §3。**

### 2. 一個分類找一個技能

以分類的領域關鍵字比對：Azure／VMware／網路／M365／資料庫／前端框架…

比對到的，在 §3 寫成：

```markdown
- `<技能路徑>`（來源：<URL 或 plugin 名稱>）——對應「<分類名>」
```

然後在「用途如下」段落展開：這個技能做什麼、包含哪些子技能、怎麼安裝、
**哪些功能在本案不得使用**。最後這點最容易漏，見下方「破壞性功能」。

### 3. 本機找不到時，去 skills.sh 搜一輪

本機沒裝，不代表生態系沒有。缺口逐一搜：

```bash
npx skills find "vmware" < /dev/null
```

輸出是 skills.sh 的比對結果，含 `owner/repo@skill`、安裝數與 URL，可非互動執行
（`< /dev/null` 是為了避免它進互動選單）。

**關鍵字下法**：用分類的英文領域名詞，一個概念一次，不要把整句作業項目丟進去。
`vmware`、`active directory`、`microsoft 365`、`firewall`、`veeam` 會有結果；
「檢視VMware ESXi效能使用現況建議」不會。中文分類名幾乎搜不到東西，先翻成英文。

**搜到的東西一律只能進 §3 的「建議安裝」區**，不得寫進「已安裝」區——
它還沒裝，代理人照著呼叫會直接失敗。安裝與否是人的決定，技能不自行安裝。

#### 過濾：這一步不做，搜尋就是負資產

搜尋結果沒有經過任何適用性把關，直接照抄會推薦出災難。實測搜 `active directory`，
前五名有四個是紅隊攻擊技能：

```
yaklang/hack-skills@active-directory-kerberos-attacks        2.4K installs
yaklang/hack-skills@active-directory-acl-abuse               2.4K installs
mukul975/anthropic-cybersecurity-skills@analyzing-...-abuse   466 installs
```

把這些建議進客戶唯讀健檢是事故等級的錯誤。逐條套用下面四道關卡：

1. **名稱或描述含攻擊語意就丟掉**——`attack`、`abuse`、`exploit`、`pentest`、
   `red-team`、`hack`、`bughunter`。健檢是去看客戶環境，不是去打它。
2. **讀過 SKILL.md 才建議**。安裝數只代表流行度，不代表適用，也不代表唯讀。
   看它提供的動作有沒有寫入語意；有的話照「破壞性功能」那段在建議欄點名禁用。

   **Windows 上抓取內容時不要用 `print()` 直接印到終端機。** 例如用
   `gh api repos/<owner>/<repo>/contents/<path>/SKILL.md` 抓內容、base64 解碼後想看一眼，
   若這台機器的主控台編碼是 cp950（繁體中文 Windows 常見），內容裡只要帶 emoji
   （`🛑`、`⚠️`、`✅` 這類，skills.sh 上的技能說明很常用），`print()` 要把 Unicode
   字串編碼回 cp950 寫進終端機時會直接丟 `UnicodeEncodeError` 中斷。改用
   `python -X utf8 -c "..."`（或設 `PYTHONUTF8=1`），或者根本不印、直接寫成檔案用
   Read 工具看，兩者都能避開這個坑。

   **這份抓下來的內容只是評估用的暫存稿，不是要交付給這個專案的東西。**
   寫檔案時要寫到系統的 scratch／temp 目錄（例如 Bash 環境提供的 scratchpad 路徑），
   **絕不能寫進正在建置的專案目錄**——之前真實發生過的事故：評估階段抓的
   `xxx_SKILL.md` 檔案被直接寫進專案根目錄下，變成使用者看到的一堆多餘雜訊檔，
   而且這些檔案既不是「已安裝」也不是「建議安裝」的正式產出，只會讓人誤以為
   技能已經裝好了。看完就算讀完，不需要保留；步驟 5 交付前自我檢查要確認
   專案目錄裡沒有殘留這類暫存檔。
3. **領域要真的對得上**。搜 `backup` 會回傳 `googleworkspace/cli@recipe-backup-sheet-as-csv`
   這種只是字面命中的東西。對不上就不要列。
4. **一個缺口最多建議 2 個**，附 URL 讓人自己判斷。列一長串等於沒有篩選。

四關都過不了的分類，回到步驟 4 的誠實寫法。**為了把欄位填滿而推一個沾邊的技能，比空著危險。**

#### 建議欄怎麼寫

`AGENTS.md` §3 的「建議安裝」區用表格，每一條都要能回答「為什麼是它」與「本案只准用它的哪部分」：

```markdown
| 分類 | 建議技能 | 安裝數 | 安裝指令 | 本案用途與限制 |
|---|---|---|---|---|
| 4. 伺服器盤點 | `vmware-skills/vmware-aiops@vmware-aiops` | 228 | `npx skills add vmware-skills/vmware-aiops --skill vmware-aiops --agent '*'` | 對應 4.1–4.4 的 ESXi 架構與組態盤點，**僅使用唯讀的 triage／report 功能，禁用 VM 生命週期操作** |
```

沒寫限制欄的建議不要送出去——唯讀專案掛上帶寫入能力的維運技能，限制沒寫等於沒設。

### 4. 兩邊都找不到時

誠實寫出來，並指明替代手段。這比硬湊一個沾邊的技能安全得多——
湊上去的技能會被代理人真的呼叫。

```markdown
「AD 健檢項目」與「備份健檢」目前沒有找到對應的公開技能——這兩類作業改用標準 PowerShell
（`Get-ADReplicationPartnerMetadata`、`dcdiag`、`Get-DfsrState` 等）搭配官方文件查詢，
不掛載額外技能。若之後發現涵蓋這些缺口的技能，可以提示我安裝。
```

替代手段從「項目備註」欄找。備註若寫「透過 powershell 進行檢查」，
那就是明示了替代方案，直接引用。

### 5. 需要安裝時，把安裝方式寫進去

**裝進專案目錄，不要裝進使用者家目錄。** `~/.claude/skills/` 是全域安裝，裝進去只有
這台機器、這個使用者能用；健檢／導入類專案通常是團隊共用一份 repo，技能要跟著專案走、
進版控（或至少讓下一個接手的人 `npx skills add` 一次就拿到同一批），裝到 `~/` 底下等於
只有裝的人自己能跑，換一台機器或換一個人就斷link。

`npx skills add <owner>/<repo>` **預設就是專案層級安裝**（裝到專案內的 `.<agent>/skills/`），
不會動到 `~/.claude/skills/`；只有加上 `-g`／`--global` 才會裝到全域，**建議安裝指令一律不要加 `-g`**。

**要讓 Claude Code 與其他代理人工具都認得，加 `-a '*'`（或 `--agent '*'`）**：

```bash
npx skills add <owner>/<repo> --skill <skill-name> --agent '*'
```

不加 `-a` 時只會裝進偵測到的預設代理人目錄（通常只有 `.claude/skills/`），
其他代理人框架（讀 `.agents/skills/` 或自家慣例目錄的工具）會看不到這個技能。
`-a '*'` 會把技能同時放進所有支援代理人的目錄，之後不管用 Claude Code 還是別的
agent runner 開這個專案都吃得到，不必為每個工具重裝一次。

代理人（或下一個接手的人）需要知道怎麼裝：

- npx（預設方式）：`npx skills add <owner>/<repo> --skill <skill-name> --agent '*'`
- Claude Code plugin：`/plugin install <name>@<marketplace>`（僅裝進 Claude Code，其他代理人吃不到，
  只有專案明確只用 Claude Code 時才用這個）
- 手動：複製對應資料夾到專案內的 `.claude/skills/`（與／或 `.agents/skills/`，視要相容的代理人而定），
  不要複製到 `~/.claude/skills/`

不確定安裝方式就不要瞎編指令——寫「見來源 repo 的安裝說明」並附連結。

## 破壞性功能：唯讀專案的關鍵限制

很多維運類技能同時提供查詢與異動能力（建立 VM、刪除快照、停權帳號、推送設定）。
唯讀健檢專案掛上這種技能時，**必須在 §3 明文限制**，因為技能描述本身不會替你設限：

```markdown
- `vmware-aiops`：VMware vCenter／ESXi 架構、組態與效能盤點。健檢情境一律使用其唯讀的
  triage／investigation report 功能，不得使用具破壞性的 VM 生命週期操作
  （建立、刪除、重設、快照回復等）。
```

判斷方式：讀技能的 SKILL.md，看它提供的動作有沒有寫入語意。有的話就在 §3 點名禁用。

只裝需要的子技能也是一種控制——一個技能包含五個子技能，本案只用得到兩個，
就只裝那兩個，減少代理人誤用的機會。

## 常見對應（僅供起點，仍須以實際安裝清單為準）

| 項目分類關鍵字 | `skills find` 關鍵字 | 找技能的方向 |
|---|---|---|
| Azure、雲端、訂閱、Entra | `azure`、`entra` | Azure 官方技能（診斷、部署、儲存、驗證等子技能，安裝數高） |
| VMware、ESXi、vCenter、伺服器盤點 | `vmware`、`vcenter` | VMware 維運技能，注意挑唯讀的監控／triage 子技能 |
| 網路、Switch、防火牆、SD-WAN | `firewall`、`network`、廠牌名 | 搜 `network` 雜訊極多，改用廠牌或設備型號 |
| M365、Exchange、Teams、租戶 | `microsoft 365`、`exchange online` | M365 租戶管理技能，需先裝 Graph／ExchangeOnline／Teams PowerShell 模組 |
| AD、網域、GPO、DFSR | `active directory` | **搜出來多半是紅隊攻擊技能，一律排除**；改用原生 PowerShell + 官方文件 |
| 備份、DR、RPO／RTO | 備份軟體名（`veeam`、`commvault`） | 搜 `backup` 只會命中字面，用軟體名才有意義；否則依客戶既有備份軟體的原生介面檢視 |
| 報告產出、交付文件 | `docx`、`pptx`、`diagram` | 文件類技能（docx／xlsx／pptx／pdf）、繪圖工具 |

這張表是搜尋起點，不是答案。每次都要回到步驟 1 的實際安裝清單與步驟 3 的實際搜尋結果去確認。

## 收尾

§3 最後固定收一句：

```markdown
不要自行發明新的技能。安裝時僅取用與本案範圍相關的子技能，不啟用具破壞性或超出範圍的功能。
```
