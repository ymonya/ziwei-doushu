# 紫微斗数 · 排盘与解读台

> 上游项目：[github.com/Renhuai123/ziwei-doushu](https://github.com/Renhuai123/ziwei-doushu)
> 本目录把上游**排盘引擎原样编译为浏览器脚本**，接入其公开的 **v4.0 十三维解读数据集**，并补齐 AI 流式解读、合盘图谱、断语库管理。

**三种交付形态**

| 形态 | 文件 | 用法 |
|---|---|---|
| 网页版（桌面 / 通用） | `index.html` | **双击即可离线使用**，无需安装、无需后端、无需联网 |
| **Android APK（手机竖屏）** | `ziwei-doushu-v1.0.apk` | 装到手机即用，界面**专为竖屏重排**（见第三节） |
| 竖屏版网页副本 | `mobile.html` | APK 内页面的独立副本，浏览器把窗口拉窄即可预览 |
| 构建工程 | `apk-src/` | 可复现打包，改 UI 后可重新签名出包 |

> 无需 API Key（仅 AI 解读需自备 Key）；排盘与断语解压全在本地完成，不上传任何排盘数据。

---

## 一、上游项目分析

### 1. 一句话定位

它不是一套完整的算命网站，而是**紫微斗数排盘引擎 + 知识库 + 超大规模解读数据集的开放快照**。作者的理念是「算法是公开的传统智慧，不应该被锁在围墙里」，把排盘算法开源，解读深度、产品体验、运营留在线上商业版 [ouranic.cn](https://ouranic.cn/)。

### 2. 技术栈与结构

| 项 | 内容 |
|---|---|
| 框架 | Next.js 16（App Router）+ TypeScript |
| 样式 / 动画 | Tailwind CSS + CSS Variables / Framer Motion |
| 排盘底层 | [iztro](https://github.com/SylarLong/iztro) + `lunar-javascript` |
| 排盘核心 | `lib/ziwei/`（约 20 个模块，`algorithm.ts` 641 行为主流程） |
| 古籍数据 | `lib/classics/`：骨髓赋、紫微斗数全集、紫微斗数全书 |
| 语料 | `docs/tianji-ziwei/`：倪海厦《天纪》紫微斗数原话 1848 条，带 B 站时间码 |
| Demo 界面 | `app/` + `components/`，最小可运行示例 |
| 回归测试 | `scripts/regression/` 21 条，CI 自动跑 |

### 3. 引擎能力（项目最有价值的部分）

| 能力 | 说明 |
|---|---|
| 真太阳时校正 | 出生地经度差 + 均时差；支持海外出生地 `utcOffsetMinutes` |
| 中国夏令时 | 判定 1986–1991 区间，**只判定、不自动扣除**，需用户确认后换算钟表读数 |
| 闰月四种口径 | 归前月 / 归下月 / 月中分界 / 归本月，可配置，不写死一派 |
| 晚子时换日 | 23:00–23:59 按次日排盘；填出生地时按**真太阳时**判断（2026-11-02 起） |
| 星曜亮度 | 庙旺得利平不陷 7 档 + 4 套流派表（默认《斗数全书》QS） |
| 四化 | 生年四化、大限 / 流年 / 流月 / 流日 / 流时四化、飞星自化 |
| 十二神煞 | 本命按生年支起、流年层按流年支起 |
| 格局判定 | `patterns.ts` 及 4 张《全书》格表，1100+ 行规则，含定贵 / 定富 / 定贫贱 / 定杂局 |
| 口径对齐 | 正月初一换年、天魁天钺、截空副截、旬空副旬、年支大耗等均按金标准盘校准 |

> ⚠️ 最容易踩的坑：`BirthInfo.hour` 是**时辰地支序号 0–11**（子=0 … 亥=11），不是 0–23 的钟点。v4.0 数据集字段名 `h` 同理，检索键为 `YYYY-MM-DD-时辰序号-性别`。

### 4. 开源边界（重要）

| ✅ 开源 | ❌ 不开源 |
|---|---|
| 排盘引擎 `lib/ziwei/` | 断语库规则源码（仓库里 `db-analysis.ts` 的 `STAR_DB = {}` 是占位） |
| 古籍公版原文、格局规则库、合盘知识 `heming-knowledge.ts` | AI 解读 prompt、`/api/interpret`、`/api/heming` 等后端 API |
| Demo 界面 | 用户系统、支付、服务端安全、部署配置 |
| 51.8 万样本数据集 v3.0、67.5 万盘 × 13 维解读数据集 v4.0 | 线上商业版前端（排盘页 1227 行 vs Demo 75 行） |

**结论**：Demo「画得出盘，给不出线上那套解读」。本应用补齐的能力中，AI 流式解读与合盘图谱是**依据开源规则自行实现**，不是上游线上功能，也不冒称线上断语库本体（断语库规则源码仍未开源）。

### 5. 数据集与许可

| 数据集 | 规模 | 覆盖 | 大小 |
|---|---|---|---|
| v4.0 解读数据集（2026-10-15，tag `v4.0-13d`） | 674,976 盘 × 13 维 = 8,774,688 段 | 1950–2026 | 解压 56.6 GB / 压缩 161 MB（按年份分片，约 2 MB/年） |
| v3.0 样本数据集 | 518,400 条 | 1924–1983 | 解压 33.1 GB |

- 代码 **MIT**；数据集 **CC BY 4.0**（商用自由，唯一要求保留来源标注）；古籍原文 **公有领域**；倪师《天纪》原话 **CC BY-NC-SA 4.0，禁止商用**。
- v4.0 的 13 个维度：`overview / personality / love / career / wealth / health / family / children / move / friends / home / spirit / parents`；每年一个 `year-YYYY.jsonl.zst`，每行一张盘，字段 `k,y,m,d,h,g,ms,t,c`，`c` 为 Markdown 全文。
- 已知问题：v3.0 有约 2,520 条样本日期不存在（2 月 30 日等）；v4.0 按旧默认亮度「现代修正 v2」生成，与现在默认《斗数全书》QS 口径的亮度字不完全一致；数据集按时辰序号直接排盘、未按出生地做真太阳时校正。
- 解压官方包需 `zstd -d --long=27`（128 MB 长窗口）。

### 6. 客观评价

- **优势**：排盘口径考究且可配置，回归测试与 CI 齐备，古籍与语料数据扎实，数据集规模罕见，许可宽松（代码和数据都可商用）。
- **限制**：它是「引擎快照」不是产品，Demo 界面很薄；断语和 AI 解读是商业壁垒；仓库随线上发版同步维护。
- **注意**：仓库会持续更新口径（如 2026-11-02 晚子时改按真太阳时、2026-10-20 默认亮度改 QS），二次开发最好锁定 commit / tag。

---

## 二、本次交付了什么

| 文件 | 说明 |
|---|---|
| `index.html` | **网页版主成品**：单文件（约 4.6 MB），内联引擎 + zstd 解码 + 1990 全年真实断语 + 12 张精选盘 |
| `ziwei-doushu-v1.0.apk` | **Android 安装包**（约 34.1 MB），手机竖屏专属布局，assets 内置全部离线数据 |
| `mobile.html` | APK 内竖屏页面的独立副本，浏览器窄窗口可直接预览竖屏效果 |
| `apk-src/` | 可移植构建工程（`MainActivity.java` / 资源 / 脚本；签名密钥需自备），见第三节第 6 点 |
| `preview-*.png` | 4 张竖屏效果截图（起盘表单、命盘、断语、APK 同源加载） |
| `ziwei-engine.js` | 独立排盘引擎，供二次开发直接 `<script>` 引入 |
| `zstd.js` | 浏览器端 zstd 解码库（**含长窗口帧修复补丁**） |
| `data/years/*.jsonl.zst` | 16 个官方年份包（约 2 MB/年），随 APK 内置 / 本地服务模式按需加载 |
| `README.md` | 本文档 |

**实现路线**：没有重写排盘算法。用 esbuild 把上游 `lib/ziwei/` 的 `algorithm.ts`、`patterns.ts`、四化、亮度流派、真太阳时、夏令时、城市、运限、名人示例、合盘知识库等模块**原样打包成 IIFE**，挂到 `window.ZiweiEngine`；UI 与解读层另写。因此**排盘结果与上游引擎完全一致**。APK 版与网页版共用同一份业务代码，只是注入了竖屏专属 CSS/JS。

### 功能清单

1. 生辰输入：公历 1900–2026、姓名、性别、出生地省市、时辰不详。
2. 真太阳时：实时显示经度差、均时差、换算后的真太阳时与时辰。
3. 夏令时：1986–1991 命中时提示，并提供「一键换算标准时间 −1h」按钮。
4. 晚子时自动换日；闰月四种口径、亮度四种流派可切换并即时重排。
5. 4×4 十二宫命盘：宫名、干支、主星 / 吉曜 / 煞曜 / 杂耀、亮度、生年四化、大限年龄段、命 / 身标记、博士十二神。
6. 点击宫位高亮三方四正，展开宫位详情与星曜释义。
7. 本命 / 大限 / 流年切换，四化以虚线徽标叠加显示。
8. 基础信息：节气四柱与农历四柱、五行局、命宫身宫、命主身主、阴阳、虚岁、当前大限、命宫摘要。
9. 格局判定：直接调用开源规则库，显示等级、说明、出处与成立条件。
10. 十三维基础解读 + 十二宫速览表 + 7 项引擎自检。
11. 明暗双主题、11 位名人示例盘、最近命盘、分享链接、导出盘面 JSON、打印 / 存 PDF。
12. 网页版移动端适配（命盘在自身容器内横向滑动，页面不横向溢出）；**APK 竖屏版改为十二宫按屏宽完整铺满**，见第三节。
13. **v4.0 真实十三维断语**：1990 全年包内嵌离线可查（8,760 盘），12 张精选盘瞬时命中，其余年份按需加载 / 导入；13 个维度自由切换，附整理版对照与来源署名。
14. **AI 流式解读**：OpenAI 兼容 `/chat/completions` SSE 逐字输出，支持 DeepSeek / 通义千问 / OpenAI / 智谱 GLM / Moonshot / 本地 Ollama / 自定义；命盘结构化注入 prompt、多轮追问、随时停止；API Key 仅存本机 `localStorage`，未配置时明确提示、不伪造输出。
15. **合盘图谱**：依据开源 `heming-knowledge.ts` 本地生成双人命盘、四化互飞 SVG、双宫联参、评分星级与方法论原文（含 14 主星夫妻宫断语）。
16. **断语库管理**：1950–2026 年份网格、内嵌包状态、本地导入 `.jsonl.zst` / `.jsonl`、在线 GitHub / 镜像下载、加载日志与进度。

> **两套解读要分清**：页面里的「整理版基础解读」是依据引擎星曜 / 宫位数据本地生成的**对照文本**；「v4.0 真实断语」是上游公开发布的数据集**原文**（CC BY 4.0，需署名）。应用内已分别标注，不冒充线上商业版解读。

---

## 三、Android APK（手机竖屏版）

### 1. 直接安装

把 `ziwei-doushu-v1.0.apk` 传到手机点击安装，或用 adb：

```bash
adb install -r ziwei-doushu-v1.0.apk
```

这是**自签名应用**（非应用商店渠道），首次安装需在系统设置里允许「安装未知来源应用」。装完打开即自带一张示例盘，**全程无需联网**。

### 2. 竖屏排版具体做了什么

网页版是桌面优先的宽屏布局，直接塞进 WebView 会出现横滑命盘、顶部导航挤压、双列内容过窄等问题。APK 版由 `apk-src/build_mobile.py` 在网页版基础上**注入竖屏专属 CSS / JS**（业务逻辑一行未改）：

| 改动 | 说明 |
|---|---|
| **底部 5 Tab** | 原顶部横向导航改为 App 式底部导航栏，图标「盘 / 断 / AI / 合 / 库」+ 短标签，选中态金色，适配安全区 |
| **命盘铺满** | 去掉桌面版 `min-width:660px` 横滑约束，4×4 十二宫按屏宽自适应铺满；宫名、主星、亮度、四化、干支字号与间距整体重排，中宫印章居中 |
| **双列转单列** | 起盘表单、十三维断语（检索条件 + 正文）、AI（设置 + 对话）、合盘（双人表单 + 双盘 + 飞化）、断语库（统计 + 年份网格）全部改为竖屏单列 |
| **十三维两列** | 13 个维度按钮改为 2 列网格，减少纵向滚动 |
| **表单紧凑化** | 日期 / 时间 / 性别下拉横排（3 列 / 2 列）；输入框 ≥16 px 防自动缩放；按钮与选项最小触控 40 px |
| **起盘自动定位** | 点「立即起盘」后平滑滚动到命盘，避免竖屏下只看到长表单 |
| **安全区 / 状态栏** | `viewport-fit=cover` + `env(safe-area-inset-*)`、`theme-color` 深色；Manifest 锁定 `portrait`；状态栏 / 导航栏配色跟随主题 |
| **返回键** | 在子页面按返回先回命盘页，在命盘页连按两次退出 |
| **缩放** | 允许双指放大查看命盘小字，不显示 `+ / −` 按钮 |
| **提示清理** | 隐藏桌面版「← 左右滑动查看完整命盘 →」（竖屏已铺满，无需横滑） |

### 3. 离线数据如何进 APK

APK 内是一个**单 Activity + 单 WebView** 的极简外壳（`apk-src/src/com/ziwei/app/MainActivity.java`），核心是同源资源拦截：

```
WebView 加载 https://ziwei.local/index.html
        ↓ shouldInterceptRequest（host == ziwei.local）
getAssets().open(path) → WebResourceResponse(200, mime, stream)
```

- 主文档与相对路径 `data/years/year-YYYY.jsonl.zst` 都走同一拦截，**同源 fetch 无需 CORS、无需放开 `file://` 跨文件权限**；`localStorage` 正常可用（AI Key、上次 Tab、最近命盘）。
- `assets/` 内置：竖屏 `index.html`（4.6 MB，含内嵌 1990 全年包 + 12 张精选盘）+ **16 个官方年份包**（32 MB）。点断语库里的年份即在浏览器内解压（约 1.2 s / 715 MB）并建索引，完全离线。
- 外部链接（GitHub、文档）交给系统浏览器，不在 WebView 内打开。
- 1950–2026 中未随包的年份仍可联网下载或本地导入，但**不下载也完全可用**。

### 4. 规格与签名

| 项 | 值 |
|---|---|
| 文件名 / 大小 | `ziwei-doushu-v1.0.apk` / 35,801,511 bytes（约 34.1 MB） |
| 应用名 / 包名 | 紫微斗数 / `com.ziwei.app` |
| 版本 | `1.0`（versionCode `1`） |
| 支持系统 | **Android 7.0+**（minSdk 24），targetSdk 35（Android 15） |
| 屏幕方向 | **portrait（锁定竖屏）** |
| 签名 | 自签名，**APK Signature Scheme v2 + v3** |
| 证书 SHA-256 | `3123d94da4383237743e5b4b865380c23565f379150fe44caa940f2e3e2d46f1` |
| 权限 | `INTERNET`、`ACCESS_NETWORK_STATE` |

v2/v3 签名覆盖 Android 7.0 及以上；`apksigner verify` 显示 v1 为 false 属正常（minSdk ≥ 24 不再需要 JAR 签名）。校验命令：

```bash
apksigner verify --verbose --print-certs ziwei-doushu-v1.0.apk
aapt2 dump badging ziwei-doushu-v1.0.apk
sha256sum ziwei-doushu-v1.0.apk
```

### 5. 权限与隐私

`INTERNET` **仅用于两处**：① AI 流式解读时，浏览器直连你自己填写的服务商端点；② 断语库在线下载未随包的年份。不填 API Key、不点在线下载时应用不发起任何外部请求。排盘计算、zstd 解压、十三维检索全部在设备本地完成，**不上传生辰或命盘数据到任何服务器**。页面内也保留了与网页版一致的明示说明。

### 6. 想改 UI 后重新打包

`apk-src/` 是完整可移植工程，**不依赖 Gradle / Android Studio**，只用 Android SDK 的 `aapt2` + `d8` + `zipalign` + `apksigner` 与 JDK：

```bash
cd apk-src
export ANDROID_SDK=/path/to/android-sdk   # 需含 build-tools/35.0.1 与 platforms/android-35
export KS_PASS='你的签名口令'             # 必填；首次构建用它生成 ziwei.jks
bash build.sh                             # 输出到上一级目录 ziwei-doushu-v1.0.apk
```

| 文件 | 作用 |
|---|---|
| `build.sh` | 全流程：资源编译 → Java 编译 → dex → 并入 assets → 对齐 → v2/v3 签名 |
| `build_mobile.py` | 由上一级 `index.html` 注入竖屏 CSS/JS，生成 `assets/index.html`（改竖屏样式改这里） |
| `make_icon.py` | 生成 5 档 PNG 启动图标 + Android 8+ 自适应矢量图标 |
| `src/.../MainActivity.java` | WebView 外壳与同源拦截逻辑 |
| `res/`、`AndroidManifest.xml` | 资源、竖屏锁定、权限、主题 |
| `verify_mobile.py` / `verify_apk_origin.py` | 手机竖屏 UI 回归 / 模拟 APK 同源拦截回归 |
| `ziwei.jks` | 自签名密钥，**不在仓库中**（避免任何人用你的证书投放恶意更新）：首次构建由 `KS_PASS` 自动生成；请自行备份，丢失或变更会导致无法覆盖安装 |

改完 `build_mobile.py` 里的 CSS 后重跑 `bash build.sh` 即可。注意：仓库不含签名密钥，你构建出的 APK 使用自生成证书，与仓库内预置的 APK **不是同一张证书**，无法覆盖安装仓库版，需先卸载再安装。这是有意设计——公开签名私钥等于允许任何人用你的证书发布同包名更新。

---

## 四、关键技术决策与修复

### 1. 单文件离线 + 按需年份包

网页版把所有 JS / CSS / 1990 全年压缩语料内联，`file://` 双击即可用；`data/years/` 的其余年份包在**本地服务模式**下按需拉取（`python3 -m http.server`）。`file://` 下浏览器禁止 fetch 本地文件，此时请用「本地导入」按钮选择 `.zst`，或起一个静态服务。**APK 版不存在此限制**——同源拦截让所有年份包都可直接 fetch（见第三节第 3 点）。

### 2. fzstd 长窗口帧缺陷修复（关键攻坚）

官方年份包用 `zstd --long=27`（128 MB 窗口）压缩，浏览器端解码库 `fzstd@0.1.1` 存在两个缺陷：

- **内容损坏（严重）**：解码超长 offset 时只读取 4 字节并做 32 位无符号右移，当 offset code 较大（官方包可达 26）且位偏移非 0 时**丢失高位**。官方 1990 包解压后应有 8,760 行，实际只剩 6,825 行、仅 2,414 行是合法 JSON，从约 105 MB 起内容错乱 —— 约 3,884 个长距离匹配指到了错误位置。此前仅校验「解压字节数」而漏检内容，是隐蔽的数据正确性隐患。
- **`Invalid string length`**：`rzfh` 中 `w == 1` 宽松比较在传入大型 `Uint8Array` 输出缓冲时会触发 `TypedArray.toString()`。

**修复**：改用 5 字节构造数值 + 除法右移 + 取模，避免 32 位截断；两处宽松比较改为严格比较。补丁脚本 `build/patch_fzstd.py` 同时覆盖 `lib/index.js`（require）与 `esm/index.mjs`（esbuild / import）两份独立源码 —— 只改其中一份，浏览器 bundle 仍会走未修复的那份。

> **为什么没有重压数据包**：把官方帧重压成浏览器兼容的普通窗口帧虽可绕过缺陷，但单年份体积会从 1.9 MB 膨胀到 8～30 MB（分块重压最优仍约 9 MB/年）。直接修复解码器可保持官方原包、离线单文件体积不变，且用户导入 / 在线下载的官方包同样正确 —— 属根因修复。APK 也因此能原样内置 16 个官方包而只占 32 MB。

**验证**：修复后解压结果与 Python `zstandard` 的**标准答案 sha256 完全一致**（`1c8d25a6…`），8,760 行全部合法；全部 16 个年份包平年 8,760 / 闰年 8,784 行全部合法。

### 3. AI 与合盘的实现边界

AI 解读是**自行实现的 OpenAI 兼容 SSE 客户端**（浏览器直连服务商），不是上游 `/api/interpret`；合盘图谱依据开源 `heming-knowledge.ts` 规则本地计算，不是上游 `/api/heming`。二者均不上传排盘数据到本应用之外的服务端（AI 请求会发送你勾选的命盘摘要到你自填的端点）。跨域失败、Key 无效、模型名错误均有可读提示。

### 4. 网页版与 APK 版共用业务代码

竖屏版不是另写一套应用：`build_mobile.py` 只在 `index.html` 的 `</style>` 前插入竖屏媒体查询、在 `</body>` 前插入一小段 UI 增强脚本（底部 Tab 图标、起盘滚动、返回键钩子）。排盘引擎、断语检索、AI、合盘、断语库代码原封不动，网页版的修复会自然继承。

---

## 五、怎么测试效果

**网页版**

1. **直接双击 `index.html`**（Chrome / Edge），打开就自带一张示例盘，先看盘对不对；或在本目录起静态服务：`python3 -m http.server 8000`。
2. 输入自己或家人的生辰，与主流排盘软件对照：命宫地支、五行局、十四主星落宫、生年四化、大限起岁。
3. 改出生地（如乌鲁木齐 ↔ 上海），观察真太阳时与最终时辰是否变化。
4. 输入 **23:30** 观察自动换日；输入 **1987 年 7 月** 观察夏令时提示；找闰月生日切换四种口径；切换亮度流派观察亮度字变化。
5. 点击任意一宫看三方四正高亮与该宫解读；切换大限 / 流年看四化叠加。
6. **十三维真实断语**：切顶部「十三维断语」，默认盘直接命中；把日期改成 1990 年任意日期 / 时辰 / 性别，点「加载」查真实断语（离线可用）；逐个点 13 个维度。
7. **断语库**：切「断语库」，点年份网格加载其它年份（本地服务模式 / 在线下载），或用「本地导入」选一个官方 `year-YYYY.jsonl.zst`；观察日志里的解压耗时与「已索引 N 张命盘」。
8. **AI 流式解读**：选服务商并填自己的 API Key 与模型名，点「生成解读」看逐字输出、追问、停止。用本地 Ollama 可完全离线（`OLLAMA_ORIGINS` 需允许跨域）。不填 Key 时页面会给出明确提示，不会编造内容。
9. **合盘图谱**：用名人快捷填入双方生辰，看双盘、四化互飞连线、评分与方法论原文。
10. 「导出盘面 JSON」可拿到完整结构化命盘 + 格局结果，便于写脚本批量比对。

**APK 竖屏版**

11. 装到手机后先看首屏：顶部标题栏 + **底部 5 个 Tab**；点「立即起盘」会自动滚到 **4×4 命盘完整铺满屏宽**（不用左右滑）。
12. 逐个切底部 Tab：十三维断语（2 列维度按钮）、AI 对话（设置在上、对话在下）、合盘（双人表单上下排列）、断语库（16 个年份网格）。
13. 断语库里点任一随包年份（如 1955），观察日志「解压完成 715 MB → 已索引 8,760 张命盘」——**这是完全离线的**。
14. 按系统返回键：在子页面会先回命盘页，再连按两次退出。

> 现在**可测**：十三维真实断语、AI 流式解读、合盘图谱、断语库检索与管理。
> 仍**不等同于**线上商业版：断语库规则源码、线上 AI prompt、后端 API、用户系统与商业版界面均未开源。

---

## 六、验证结果

| 验证项 | 结果 |
|---|---|
| 打包引擎 vs 上游 TypeScript 引擎 | 8 张不同盘（含闰日、晚子时、夏令时年份、男女命）**逐字段 JSON 完全一致** ✅ |
| 网页版端到端回归 | **62 / 62 通过** ✅（排盘 + 断语库 / AI 流式 / 合盘 / 数据管理全量回归） |
| 内嵌 1990 包（HTTP 与 `file://` 双模式） | 8,760 行、随机 3 盘均 13 维、约 3 万字/盘、浏览器内 1.6 s 解压、零控制台错误 ✅ |
| 全部 16 个年份包 | 平年 8,760 / 闰年 8,784 行，全部合法 JSON，sha256 与标准答案一致 ✅ |
| `file://` 离线打开 | 引擎 / 语料 / 解码库全部挂载，12 宫 + 5 个功能 Tab + 断语检索可用，零错误 ✅ |
| 网页版响应式 | 1600 / 768 / 390 px 三档均无整页横向溢出 ✅ |
| **竖屏 UI 回归**（360×780 / 390×844 / 412×915） | **63 / 63 通过** ✅：底部导航固定、命盘铺满不横滑、起盘自动滚动、日期下拉横排、5 个 Tab 无溢出、十三维断语、年份包同源、返回键、零 JS 错误 |
| **APK 同源拦截离线链路** | **15 / 15 通过** ✅：模拟 `https://ziwei.local/` 拦截，主文档与相对 fetch 均由 assets 提供；点 1955 年份包 → 浏览器内解压 715 MB / 1.24 s → 索引 8,760 盘；`localStorage`、断语、返回键均正常 |
| **APK 结构 / 签名** | zipalign 对齐通过；v2 + v3 签名有效；`screenOrientation=portrait`；17 个 assets 条目，16 个年份包 sha256 与源一致；可移植工程复现构建证书指纹一致 ✅ |
| 上游 `npm test` | 21 条中 20 条通过；`patterns-sihua-bonus.test.ts` 因当前 Node 22.13.1 缺少 `module.registerHooks`（需 Node ≥ 22.15 / 23.5）抛 TypeError。其余 20 条全部通过，**属测试工具链版本兼容问题，与排盘算法无关** |

> APK 未在真机 / 模拟器上运行（沙箱无 Android 设备），但页面层已用 Chromium 手机视口 + 模拟 `shouldInterceptRequest` 同源拦截做了等价验证，APK 层做了结构、签名、资源完整性校验。

---

## 七、二次开发

`ziwei-engine.js` 可直接复用：

```html
<script src="ziwei-engine.js"></script>
<script>
  const E = window.ZiweiEngine;
  E.setBrightnessSchool('QS');
  // hour = 时辰序号 0–11（子=0 … 亥=11），不是钟点
  const chart = E.generateChart({ year: 1990, month: 5, day: 15, hour: 6, gender: 'male' });
  console.log(chart.palaces, chart.wuxingJuName, E.detectPatterns(chart));
</script>
```

常用 API：`generateChart` / `getLunarInfo` / `setBrightnessSchool` / `detectPatterns` / `getMingGongSummary` / `formToBirthInfo` / `calcTrueSolarBranch` / `calculateTrueSolarTime` / `getSiHuaByStem` / `getLiuNianSiHua` / `getDaXianSiHua` / `PROVINCES` / `FAMOUS_PERSONS` / `STEMS` / `BRANCHES` / `STAR_DESCRIPTIONS`，以及合盘知识库 `STAR_IN_FUQI_GU` / `SIHUA_IN_FUQI_GU` / `HEMING_METHODOLOGY` / `MARRIAGE_STARS_BRIEF` / `HEMING_SCORE_CRITERIA`。

页面内其它全局对象：`window.fzstd`（`decompress(bytes[, out])` / `Decompress`）、`window.ZiweiCorpus`（`meta` / `packs`（年份 → zstd 包 base64）/ `samples`（精选盘））。若重新 `npm install` 还原了 `node_modules`，需重跑 `build/patch_fzstd.py` 再打包 `zstd.js`。竖屏版额外提供 `window.__zwBack()` 供 WebView 返回键调用。

Android 外壳的改动入口见第三节第 6 点。

---

## 八、来源与许可

各来源内容的授权分层与署名义务详见 [DATA-LICENSE.md](DATA-LICENSE.md)；代码适用根目录 [MIT LICENSE](LICENSE)。摘要如下：

- 排盘引擎来自 [Renhuai123/ziwei-doushu](https://github.com/Renhuai123/ziwei-doushu)（作者：王多鱼AI），代码 **MIT**；底层依赖 iztro、lunar-javascript。
- 十三维真实断语使用 [紫微斗数开源解读数据集 v4.0](https://github.com/Renhuai123/ziwei-doushu/releases/tag/v4.0-13d)（674,976 盘 × 13 维，作者 王多鱼AI，**CC BY 4.0**，已在本应用内保留来源署名）。其中引用的倪海厦《天纪》原话不在 CC BY 4.0 授权范围内（**CC BY-NC-SA 4.0，仅限非商业学习研究**）。
- 本应用的 UI、竖屏版式、「整理版基础解读」、AI 流式接入、合盘计算与 Android WebView 外壳为另行编写；未使用上游未开源代码。
- APK 为本地自签名测试包（签名密钥不随仓库分发，构建者用 `KS_PASS` 自行生成），不含任何第三方 SDK / 统计 / 广告组件。
- 命理内容属传统文化研究与娱乐参考，不构成任何人生决策建议。
