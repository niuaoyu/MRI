# searchpaper：心脏 3D 重建 + 稠密对应 的文献检索包

> 目标：为硕士课题找出**还没被占的位置**。方法不是"多搜关键词"，而是四条互补的路线：反向引用链 → 组合限定词 → limitation 采摘 → 跨域借用。
> 产出时间：2026-10-27。所有结论基于 OpenAlex + arXiv 公开元数据与全文 HTML，**未使用 Google Scholar**（见 §4）。

---

## 1. 读的顺序

| 顺序 | 文件 | 解决什么问题 | 读完你应该能回答 |
|---|---|---|---|
| 1 | [00_检索方法与粗读法.md](00_检索方法与粗读法.md) | 方法本身：四条检索路线、证据分级、七栏粗读卡 | 我这套检索的可信度边界在哪 |
| 2 | [01_反引链_MRNet_NDM.md](01_反引链_MRNet_NDM.md) | 谁在引用 MR-Net / NDM / DIF-Net / DIT | 我的直接竞争对手是谁 |
| 3 | [02_组合限定词_2024_2026.md](02_组合限定词_2024_2026.md) | `cardiac + correspondence/template/implicit` 近两年捞到了什么 | 2026 年这个位置有多挤 |
| 4 | [03_候选问题表.md](03_候选问题表.md) | 从 limitation 段摘出的 11 个候选问题 + 判别实验 | 我该做哪一题 |
| 5 | [04_跨域借用_形状对应.md](04_跨域借用_形状对应.md) | 图形学/通用 3D 视觉里能搬的工具 | 我用什么工具做 |
| 6 | [05_粗读卡片.md](05_粗读卡片.md) | 14 篇必读的维度流转笔记 | 每篇的对应机制与失效点 |

---

## 2. 四条路线各自捞到了什么

| 路线 | 数据源 | 产出 | 关键发现 |
|---|---|---|---|
| 反向引用链 | OpenAlex `cites:` | 439 篇入池，50 篇精筛 | 引文图**分成两簇**：心脏网格/4D 一簇、隐式模板/对应一簇，**彼此几乎不互引**。2026 年最新的心脏竞品在 OpenAlex 里**不引用** MR-Net/NDM（需 PDF 核实） |
| 组合限定词 | OpenAlex `search=` + 日期过滤 | 15 组查询，10 篇 2026 心脏竞品 | `cardiac + template` 召回最差——同位置的论文更爱用 `atlas / canonical / UV domain / point identity` |
| limitation 采摘 | arXiv LaTeXML HTML | 52 篇抓取，11 个候选问题 | 最硬的三个空位：**薄壁 endo/epi 点身份**、**4D 环路闭合**、**拓扑变异下的对应定义** |
| 跨域借用 | arXiv `abs:` 检索 2024+ | 98 条，22 条保留，9 篇 limitation 全文 | 能搬：单射变形、无模板对应、点身份基准；不能搬：functional map、等距假设 |

---

## 3. 五条结论（如果只看五句话）

1. **"带对应的稀疏心脏重建"这个方法层已经挤满**：MorphiNet、Anatomy-Aligned、Personalized 4D、Local2Mesh、Bi-PT、Cardiac Mesh Flow、CineMesh4D、VecHeart、DVS、RVDeformer 在 2025–2026 两年内全部出现。**不要再造第五种"模板 + 变形 + 点身份"机制。**
2. **所有人都声称 dense correspondence，但没有一篇单独评价对应**。Dice/HD/Chamfer 对顶点置换不变——把顶点打乱，数字一个不变。这是整个领域的度量盲区，也是最稳的切入点（Q1/Q9）。
3. **最容易被漏掉的两个直接竞品**：SCorP（2024）与 SPI-CorrNet（2024），它们做的是"从无分割图像直接预测对应 + 不确定度"，不在心脏上，但方法是同一条路。
4. **图形学已经把"proximity ≠ point identity"写进 limitation**（Dense4D, 2026），并开始建点身份基准；心脏侧还没有对应的东西。跨域搬运的窗口在这里。
5. **最可能立项的是评价类工作**（Q1+Q5+Q9），因为它一周内能出第一张图，不依赖任何未公开代码；方法类里最可行的是薄壁单射（Q3+Q10）。

---

## 4. 必须声明的限制

| 限制 | 影响 | 处理 |
|---|---|---|
| **没用 Google Scholar** | 无法做真正的 "cited by"，OpenAlex 的引用覆盖滞后 3–9 个月，2026 年新预印本基本没被收录 | 用 OpenAlex `cites:` 替代；arXiv 补最新；关键论文的引用关系需在 PDF 里人工核 |
| **Wolf 级别的引用数缺失** | 无法判断"谁是这个圈子的核心" | 用作者/机构频率替代（见 01 §3） |
| **部分 Springer/Elsevier 论文无摘要** | VecHeart、CineMesh4D、SHDF、RVDeformer、biv-me 只有 B/C 级证据 | 已列在 03 §4，需拿 PDF |
| **arXiv 摘要检索对 `bijective/homeomorphism/point identity` 命中 0** | 跨域检索可能漏掉关键工作 | 这些词主要在正文；需 S2 全文检索补充 |
| **所有 limitation 原句来自 arXiv 版本** | 正式版可能措辞不同 | 写进开题前对 PDF 复核页码 |

---

## 5. 目录结构

```
searchpaper/
├─ 00_检索方法与粗读法.md        ← 方法与证据分级
├─ 01_反引链_MRNet_NDM.md        ← 引文链
├─ 02_组合限定词_2024_2026.md    ← 关键词矩阵
├─ 03_候选问题表.md              ← 11 个候选问题 + 判别实验
├─ 04_跨域借用_形状对应.md        ← 可搬的工具与不可搬的假设
├─ 05_粗读卡片.md                ← 14 篇维度流转笔记
├─ _raw/                        ← 原始检索结果（JSON / TXT）
│  ├─ seeds.json                 ← 5 个种子论文的 OpenAlex ID
│  ├─ resolved.json              ← 种子解析结果
│  ├─ citations_2024plus.json    ← 引用种子的 2024+ 论文
│  ├─ topic_search.json          ← 15 组关键词检索原始结果
│  ├─ pool.json                  ← 439 篇去重池
│  ├─ details.json               ← 50 篇精筛详情
│  ├─ idmap.json                 ← DOI → arXiv ID 映射
│  ├─ arxiv.json                 ← 52 篇的摘要 + limitation 段
│  ├─ arxiv_cross.json           ← 9 篇跨域论文的 limitation 段
│  ├─ crossdomain.json           ← OpenAlex 跨域检索（噪声大，留档）
│  ├─ crossdomain_arxiv.json     ← arXiv 跨域检索（98 条）
│  ├─ limits.txt                 ← 心脏侧 limitation 汇总（可读）
│  └─ cross_limits.txt           ← 跨域 limitation 汇总（可读）
└─ _scripts/                     ← 全部可复现脚本
   ├─ resolve.py                 ← 种子标题 → OpenAlex ID
   ├─ citations.py               ← 拉取引用种子的论文
   ├─ search_topics.py           ← 15 组关键词查询
   ├─ shortlist.py               ← 去重 + 打分 → pool.json
   ├─ details.py                 ← 精筛 50 篇详情
   ├─ idmap.py                   ← S2 批量 DOI → arXiv
   ├─ html_limits.py             ← arXiv HTML limitation 抽取（核心工具）
   ├─ dump_limits.py             ← 生成 limits.txt
   ├─ crossdomain.py             ← OpenAlex 跨域检索（对照用）
   ├─ rank_crossdomain.py        ← 跨域结果排序
   ├─ crossdomain_arxiv.py       ← arXiv 跨域检索
   └─ cross_limits.py            ← 跨域 limitation 抽取
```

---

## 6. 复现

```bash
cd C:/nay/github/MRI/searchpaper
export PYTHONIOENCODING=utf-8

python _scripts/resolve.py          # 种子 → OpenAlex ID
python _scripts/citations.py        # 引文链
python _scripts/search_topics.py    # 关键词矩阵
python _scripts/shortlist.py        # 去重打分
python _scripts/details.py          # 精筛
python _scripts/idmap.py            # DOI → arXiv
python _scripts/html_limits.py      # limitation 抽取
python _scripts/dump_limits.py      # 人类可读汇总
```

注意：
- arXiv API 限速 1 req/3s，脚本里已加 sleep；
- OpenAlex 需要 `User-Agent`，否则 403；
- Windows 下必须设 `PYTHONIOENCODING=utf-8`，否则 GBK 解码报错。

---

## 7. 下一步（按优先级）

1. **Q1 演示**：对任一方法输出做顶点置换，确认 Dice/HD/Chamfer 不变（半天）。
2. **标 landmark**：M&Ms-2 取 20 例，标 6–8 个点，算测地误差（2–3 天）。
3. **跑 biv-me**：20 例，算环路漂移（Q5）与穿透率（Q3）。
4. **补 PDF**：SHDF、VecHeart、CineMesh4D、RVDeformer、biv-me（把 B/C 升到 A）。
5. **S2 全文检索**：`point identity` / `homeomorphism` / `bijective`，补跨域漏检。
6. **对开题报告**：把 03 的主表压成 3 页，作为"研究问题"章节；把 05 的"四种对应机制"压成 1 页，作为 related work 骨架。
