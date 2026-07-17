# WorkShop-ARCH QAQC 規範

> 品質規則(A 系列)+ 多模型調度成本紀律(C 系列)。
> 參照 WorkShop 專案 W1-W5 的精神:每條規則要可檢驗,不是口號。

---

## A 系列・內容品質規則

| Lint | 規則 | 檢驗方式 |
|---|---|---|
| **A1 零自造法規數字** | index.html 與 prompt-templates.md 內,所有法規判準數值必須是「【講師填入】」佔位;任何模型不得填入真實建技/消防條文數值 | grep 判準區塊,出現具體數值即 FAIL |
| **A2 範本一致性** | index.html 內 `#tplCriteria` / `#tplAdvisor` 注入的文字,必須與 prompt-templates.md 的範本一/範本二逐字一致(caseSlot 動態行除外) | diff 比對 |
| **A3 board 關鍵檔不可動** | presentation/board/board.html 與 board.css 須與 WorkShop 原版 byte-level 相同(部署時才改 firebase-config);board.js 因今日(2026-07-17)UX 改版(空白鍵+拖曳平移/滾輪縮放/按0復位)刻意偏離,不列入本檢;database.rules.json 因新增房間 slide2/slide7(commit 14f80e4)刻意偏離,不比對 byte-level,改驗證 JSON 合法且房間白名單涵蓋 slide2/slide7 | diff(board.html/board.css)+ JSON 語意檢查(database.rules.json) |
| **A4 黃金路徑優先** | 主線動線必須只依賴「一個網頁聊天視窗」;IDE/CLI 內容必須標示「進階」且不得出現在主線步驟裡 | 人工審查 slide 1/4 |
| **A5 佔位不可上場** | 工作坊舉行前,所有【講師填入】必須由講師親自填妥並簽核;帶佔位符的版本禁止投影給學員 | 開場前 grep「講師填入」= 0 |

## C 系列・多模型調度成本紀律

> 源起:GPT-5.6 計價有 272K 斷崖——單次 request 超過 272K tokens,**整包**(非超出部分)進入 Long context 費率:input $5→$10 / cached $0.5→$1 / output $30→$45。Codex 給 GPT-5.6 的窗口是 372K,長 session 累積程式碼+log+對話,很容易不知不覺踩線,體感就是「額度用兩倍速度消失」。

| 規則 | 內容 | 理由 |
|---|---|---|
| **C1 一次性派遣** | Codex 一律 `codex exec` 無狀態單發,一個任務一個乾淨 session;禁止長 session 連續堆疊任務 | 每次派遣 context 從零起算,遠離 272K 線 |
| **C2 任務要小** | 派給 Codex 的單一任務範圍必須小到「讀入檔案+對話」總量遠低於 240K;大任務先由 Orchestrator 拆小再派 | 不讓單一任務自己長胖到踩線 |
| **C3 不餵整包** | 派遣 prompt 只給檔案路徑與精準範圍,讓 worker 自己讀「需要的部分」;禁止把整個專案或長 log 直接貼進 prompt | worker 讀檔也算 input tokens |
| **C4 compact 防線** | `~/.codex/config.toml` 設 `model_context_window = 272000` + `model_auto_compact_token_limit = 240000`(2026-07-12 已設,備份 .bak-20260712) | 240K 先摘要,不進高費率區 |
| **C5 compact 的代價要管理** | compact 會丟早期細節(架構決策原因、已失敗的嘗試、初始限制、跨檔關聯)。凡屬「不可遺失」的決策,一律寫進 session-log.md / QAQC.md 等**檔案**,不依賴對話記憶 | 檔案不會被 compact 掉 |
| **C6 貴模型做判斷、便宜模型做苦力** | 旗艦(Fable/Sol)只做審查、裁決、整合;機械搬移與草稿派 Haiku/Flash 等低價模型 | output $30-45/1M 的模型不該做 cp 檔案的事 |
| **C7 失敗歸因後再扣額度** | 派遣指令本身的錯(stdin、旗標、信任目錄)不計 worker 呼叫額度;只有「任務真正送達後的失敗」才計 | 見 session-log 調度決定 #5 |

## 與工作坊內容的接點

C 系列本身就是教材:學員問「為什麼不能把整個案子都丟給 AI 一直聊下去」時,答案就是 C1-C3——
**長對話不只讓 AI 變笨(細節被摘要掉),還讓它變貴(踩進 Long context 費率)。**
「一個任務、一個乾淨視窗、判準寫在檔案裡」對建築人是同一句話:圖說要進圖檔,不要只留在會議記憶裡。

---

變更紀錄:2026-07-12 建立(A1-A5 / C1-C7)。

## V 系列・版面技術規則(2026-07-13 新增,起因:委託人逐項點名的排版缺陷)

| 規則 | 內容 | 檢驗 |
|---|---|---|
| **V1 不准「切了又捲不到」** | 凡設 max-height 的文字容器必須配 overflow-y:auto | qaqc_check.py 靜態掃描 |
| **V2 可捲要看得出可捲** | 可捲區必須有可見滾軸樣式+「⇣ 內文可捲動」文字暗示(macOS 滾軸預設隱形) | 腳本掃描 |
| **V3 標題行高防疊字** | display 級標題 line-height ≥ 1.0(0.88 曾造成「譜,」孤行疊字事故) | 腳本掃描 |
| **V4 圖高下限** | 任何圖不得低於 8vh(看不到=沒有意義) | 腳本掃描 |
| **V5 渲染層目視(強制)** | 疊字/錯位/死留白/一屏入內/lazy 圖有載入——純靜態驗不了,**每次改版必跑 Chrome 100% 逐頁截圖目視**,與腳本兩個角度缺一不可 | Chrome 逐頁截圖 |
| **V10 同列同線** | 同一列(grid/flex row)的兄弟圖:上緣同線(容差4px)、盒高同值、圖說同基線;圖說不對稱=結構 bug,補齊而非刪除。**登記豁免**:第 3 頁 compare-grid 左小右大為故事板刻意設計(錯的世界縮小、reveal 放大),不受此檢 | dom_audit 量測+腳本掃描 |
| **V6 一頁一屏(已由驗收標準§一修訂:內容完整>一屏)** | 100%、1440×900 與 1280×800 整頁入屏;唯一許可內捲=prompt 區塊 | V5 目視+overflow-y:hidden 掃描 |
