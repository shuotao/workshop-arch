# WorkShop-ARCH · 建築人的一小時工作坊(LOOP 自查 × 總指揮/顧問拍板)

「AI 說的對,還是聽起來對?」——給建築人的一小時判斷力工作坊:教兩件事,自己查(自主檢核循環 LOOP)、找人定案(總指揮/顧問拍板),最後一頁再往上加一層編排(agent orchestration)。

## The workshop

- 60 分鐘,8 頁投影片,兩條主軸貫穿:
  - **主軸一(LOOP)**:標準不動、改了再測、測到過關——第 4 頁後半讓學員親手做一次。
  - **主軸二(多個 AI)**:AI 只能給意見,定案的是人——第 6 頁每個人都要自己做一次。
  - 第 7 頁把兩條主軸疊起來:同一件事能不能派一群 agent 平行代跑,人只留最後的決策格。

8 頁結構(對應 `presentation/index.html` 的 `data-title`):

| # | 頁 | 內容 |
|---|---|---|
| 01 | 開場 | 卸下工具焦慮(+ 設計視覺風格參考 Refero Design credit) |
| 02 | 質問 | 語意(光譜)vs 意義(絕對正確)——全場地基;白板 room=slide2 |
| 03 | 對照 | 一句話問到底 vs 拆塊分工的生產線 |
| 04 | 動手一・檢討標準卡 | 複製 prompt、貼案子數字、看它敢不敢說 FAIL;含 HJPLUS 台灣建築師知識庫連結 |
| 05 | 動手二・A/B/C/D | FAIL 之後的四條路 |
| 06 | 動手三・當一次總指揮 | 開第二個 AI 複核第一個,「你來定案」 |
| 07 | 動手四・編排(Orchestration) | 複數 sub-agents 平行代跑 04/06、一個 LOOP CHECK AGENT 閉環驅動、①自然語言/②明確指令 指令包;白板 room=slide7(次要,分享用) |
| 08 | 結語 | 蓋章收束;延伸連結 BIM_MCP 知識庫 |

## The deck

單檔簡報:`presentation/index.html`。純 HTML/CSS/JS,無 build step、無外部框架依賴(Fabric.js 只在白板頁引入)。投影片切換、進度條、複製按鈕、動態組裝(第 4 頁檢討項目選單)全部內嵌在同一個檔案裡。

## The board

現場即時協作白板(`presentation/board/`):

- Fabric.js v6(CDN)畫布 + Firebase Realtime Database(專案 `goodedunote`)即時同步。
- 兩個房間對應兩頁:`board.html?room=slide2`(質問頁,匿名貼「以為要絕對其實是光譜」的事)、`board.html?room=slide7`(編排頁,分享改好的「明確指令區」)。
- 手勢:滾輪縮放、空白鍵+拖曳平移、按 `0` 復位。
- ⚠️ **雙路徑部署 caveat**:repo 內的 `presentation/` **不是**線上來源——要上線必須把 `presentation/index.html` 與整個 `presentation/board/`(含填好的 `firebase-config.js`)另外複製到 goodedunote 的 Firebase Hosting 目錄再 `firebase deploy`。細節見 `presentation/board/README.md`。

## Run locally

```bash
cd presentation
python3 -m http.server 8000
# 開 http://localhost:8000/index.html
```

白板功能需要先完成 `presentation/board/firebase-config.js` 設定(見 `presentation/board/README.md`)。

## Deploy

- **GitHub Pages**:此 repo 可直接接 Pages(若已設定),但 Pages 上看到的**只有簡報本體**,白板的即時同步仍依賴 Firebase 專案。
- **Firebase(goodedunote)**:目前工作坊現場實際使用的線上版本走 Firebase Hosting,來源目錄**不是**這個 repo 的 `presentation/`,而是另外複製維護的 `…/study/scripts/publish/goodedunote/public/workshop/`。**改動這個 repo 的簡報或白板後,記得同步複製過去再 deploy**,否則會造成 repo 與線上內容漂移。完整步驟見 `presentation/board/README.md` 的「部署(注意:雙路徑)」一節。

## Doc map

| 檔案 | 內容 |
|---|---|
| `presentation/index.html` | 簡報本體(唯一交付物) |
| `presentation/board/` | 協作白板(殼 + 樣式 + 邏輯 + Firebase 設定) |
| `講師逐字稿.md` | 逐字稿,含時間軸、舞台指示、講師自備清單 |
| `故事板.md` | 敘事配置規格:每頁角色、鉤子、圖的敘事位置 |
| `插圖規劃.md` | 全部插圖的唯一規格來源(美術方向、逐頁配置) |
| `image-prompts.md` | 每張插圖的生圖 prompt(依插圖規劃.md 展開) |
| `prompt-templates.md` | 三個可複製範本(檢討標準卡/複核任務卡/編排 pseudocode)的比對基準 |
| `criteria-verified.md` | 法規數字三重溯源紀錄 |
| `驗收標準.md` | 版面/視覺驗收鐵則 |
| `QAQC.md` | 品質規則(A/C/V 系列),`qaqc_check.py` 的規則說明 |
| `qaqc_check.py` | 自動化跨檔一致性檢核器 |
| `CLAUDE.md` | 對這個 repo 動手前必讀的鐵則(結構、部署 caveat、文件對齊規則) |

延伸:domain 智慧來自 [REVIT_MCP_study](https://shuotao.github.io/REVIT_MCP_study/docs/BIM_MCP/index.html) 貢獻者社群 → **BIM_MCP 知識庫**。

## Verify

```bash
python3 qaqc_check.py   # 必須全綠才算完成
```

再加一道靜態檢核抓不到的:每次改版都要用 Chrome 100% 縮放、1440×900 與 1280×800 兩種視窗逐頁目視,確認無疊字/錯位/死留白/圖片沒載入——`qaqc_check.py` 的輸出裡也會提醒這一步(V5 規則)。
