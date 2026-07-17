# CLAUDE.md — WorkShop-ARCH

> 對這個 repo 動手前必讀。這裡是鐵則,不是建議——違反了就是壞掉的交付。

## What this repo is

「AI 說的對,還是聽起來對?」——給建築人的一小時判斷力工作坊。交付物是一份**單檔簡報**
(`presentation/index.html`)加一塊**現場協作白板**(`presentation/board/`),搭配一整套教學文件
(逐字稿、故事板、插圖規劃、prompt 範本)。所有文件對簡報的**唯一職責**是「跟今天的 deck 講同一件事」——
文件與 deck 一旦漂移,學員拿到的就是錯的教材。

## Deck structure

- `presentation/index.html`,8 頁,`<section class="slide" data-title="...">` 逐頁排列,kicker
  顯示 `01 / 08` ~ `07 / 08`(第 8 頁是信紙式結語,依設計免編號)。
- 單一自足檔案:HTML/CSS/JS 全部內嵌,無 build step。唯一外部依賴是白板頁引入的 Fabric.js CDN。
- 頁序與角色(改動前務必讀故事板.md 的完整版):01 開場 → 02 質問(語意/意義地基)→ 03 對照(生產線
  揭密)→ 04 動手一・檢討標準卡 → 05 動手二・A/B/C/D → 06 動手三・當一次總指揮 → 07 動手四・編排
  (Orchestration:複數 sub-agents 平行代跑 04/06 + 一個 LOOP CHECK AGENT 閉環驅動,人只留 05 決策)
  → 08 結語。

## Board + Firebase deploy caveat

`presentation/board/` 是 Fabric.js + Firebase Realtime Database(專案 `goodedunote`)的即時白板,
兩個房間對應兩頁:`room=slide2`(質問頁)、`room=slide7`(編排頁,次要分享用)。

**鐵則:repo 內的 `presentation/` 不是線上來源。** 要讓學員在工作坊現場連得到,必須把
`presentation/index.html` 與整個 `presentation/board/`(含填好的 `firebase-config.js`)另外複製到
`…/study/scripts/publish/goodedunote/public/workshop/`,再跑
`firebase deploy --only hosting --project goodedunote`。**改完這個 repo 沒有同步複製過去 deploy,
等於什麼都沒發生**——線上看到的還是舊版。細節見 `presentation/board/README.md`。

## Doc-alignment iron rules

簡報是唯一真相來源(ground truth),文件永遠跟著簡報走,不是反過來。**改動 `presentation/index.html`
的任何一頁(新增/刪除頁、改時間分配、改內容、改插圖),下面五份文件必須連帶檢查並更新,漏一份就是
沒做完**:

1. `講師逐字稿.md` —— 對應頁的段落內容、時間軸(`## 第 N 頁・NAME(H:MM–H:MM)`,必須 0:00–1:00
   連續無縫)、附錄講師自備清單。
2. `故事板.md` —— 對應頁在敘事裡的角色、鉤子、圖的位置。
3. `插圖規劃.md` + `image-prompts.md` —— 逐頁插圖規格與生圖 prompt(兩檔必須一致,且與
   `presentation/assets/arch/` 實際檔案、`index.html` 的 `<img>` 引用三方一致)。
4. `prompt-templates.md` —— 與 `index.html` 內注入的 `#tplCriteria` / `#tplAdvisor` /
   `#tplOrchestrate` 等區塊逐字一致(動態插槽除外)。
5. `criteria-verified.md` —— 任何新增/修改的法規數字,必須先完成三重溯源才能上簡報。

**改完一定要跑 `python3 qaqc_check.py`,全綠(🟢)才算做完;再用 Chrome 100% 縮放逐頁目視
(疊字/錯位/死留白/圖片沒載入),兩個角度缺一不可——這是 QAQC.md 的 V5 規則,腳本驗不了渲染層。**

## Don't-break rules

- **編碼**:全檔案 valid UTF-8,正體中文,禁止 mojibake(亂碼)。存檔/貼上前檢查編碼沒被破壞。
- **鍵盤導覽**:不得破壞 `←`/`→`/`PageUp`/`PageDown`/`1`-`9`/`0`/`Home`/`End` 的翻頁邏輯
  (`presentation/index.html` 底部 `<script>` 的 `go()` 與 `keydown` 監聽)。
- **`data-title`**:每個 `<section class="slide">` 必須保留 `data-title` 屬性,`qaqc_check.py`
  靠它算頁數與結構。
- **kicker / counter**:頁面上的 `NN / 08` 編號與底部 `<span id="cur">` 計數器必須跟頁數同步——
  加頁或刪頁,兩處都要改,`qaqc_check.py` §1 會抓不一致。
- **頁數改動**:任何增刪頁,同步更新 `qaqc_check.py` 裡「8 頁」的斷言(目前有多處寫死 8/16/…)。
- **視覺鐵則**(詳見驗收標準.md / QAQC.md V 系列):禁止用 `vh` 定文字容器高度(只能固定 px 或內容
  自然高);禁止彩色 accent(唯一允許的強調是墨色的粗細與明暗反轉,插圖層的磚紅是既有例外,不得
  再擴大);容器圓角 ≤8px,100px 藥丸形狀僅限 `.btnbox` 這類主要 CTA。

## 法規數字紀律

任何出現在 `presentation/index.html` 或 `prompt-templates.md` 裡、被學員當真的法規判準數值
(採光比、排煙距離、條號等),**必須先在 `criteria-verified.md` 完成三重溯源**(法源條號 → 全國
法規資料庫現行條文逐字核對 → 記錄核對日期),才准寫進簡報。教學用的虛構示範值(例如頁面上標明
「教學虛構值」的 9.5%、3.0)不受此限,但**必須在同一句話裡明確標註「虛構」或「示範」**,不得跟
真實法規數字混在一起不加註記——`qaqc_check.py` §4(A1)會逐一核對。

## Model-tier / CLI facts block(照抄,不要憑印象改寫)

這是第 7 頁「動手四・編排」教的內容,也是講師逐字稿第 7 頁段落的依據。**任何地方要提到 CLI 調度,
一律照下面這張表講,不要憑印象亂改**——不同 CLI 的旗標不是同一套,講錯或寫錯,學員回去自己套用
會直接失敗:

| CLI | headless 執行 | 模型旗標 | 可用模型 |
|---|---|---|---|
| `codex` | `codex exec` | `-m` | `sol`(最強)/ `terra`(均衡)/ `luna`(最省) |
| `claude` | `claude -p` | `--model` | `opus` / `sonnet` / `haiku` |
| `agy` | `agy -p` | `--model` | Gemini 模型(旗標是長的 `--model`,不是 `-m`) |

- **主 agent(你在互動視窗裡直接對話的那個)不掛任何模型/headless 旗標。** 只有 sub-agent(背景
  代跑)才需要 `exec`/`-p` 加模型旗標。
- **生圖**:`codex call skill/imagegen` → 接的是 gpt-image;`agy call skill/nano-banana` → 另一
  個生圖管道。兩者是 `call skill/X` 語法,不是模型旗標。
- **自動核准(免每步確認)**:`codex` 加 `--sandbox workspace-write`;`claude`/`agy` 等其他 CLI
  加 `--dangerously-skip-permissions`。這兩個也不能混——`codex` 沒有 `--dangerously-skip-permissions`
  這個選項,`claude` 也沒有 `--sandbox`。
- **⚠️ 常見幻覺陷阱**:不要把 `-m` 跟 `--model` 在不同 CLI 之間搞混(`codex -m sol` 對,
  `claude -m sonnet` 錯,必須是 `claude --model sonnet`);不要讓 sub-agent 自己「猜」一個聽起來
  合理但不存在的旗標——指令包(`presentation/index.html` 第 7 頁的①②兩區)存在的目的就是把這件事
  寫死,不留語意空間給機器猜。

## Verify / Definition of Done

1. `python3 qaqc_check.py` 全綠(🟢),沒有 FAIL(⚠️ 警告需人工確認,不阻擋交付但不能無視)。
2. Chrome 100% 縮放,逐頁目視(桌面尺寸,建議 1440×900 與 1280×800 兩種視窗都看一次):無疊字、
   無錯位、無死留白、圖片確實載入(非 `onerror` 隱藏狀態)。
3. 若動了白板(`presentation/board/`)或簡報,且要讓學員在現場連得到:同步複製到 goodedunote 的
   Firebase Hosting 目錄並 `firebase deploy`(見上方「Board + Firebase deploy caveat」),**且
   repo 與線上內容要一致,不得只更新一邊**。
4. 提交前確認上面「Doc-alignment iron rules」列的五份文件都已檢查過,不是只改了 `index.html`。

延伸:domain 智慧來自 [REVIT_MCP_study](https://shuotao.github.io/REVIT_MCP_study/docs/BIM_MCP/index.html)
貢獻者社群 → BIM_MCP 知識庫。
