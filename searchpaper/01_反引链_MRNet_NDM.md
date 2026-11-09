# 反向引用链：谁在引用 MR-Net / NDM / DIF-Net / DIT

> 数据：OpenAlex `filter=cites:<work_id>`，时间限 2024-01-01 起。
> 引用数是 OpenAlex 口径，普遍低于 Google Scholar；这里只用于**召回**，不用于评价影响力。

---

## 1. 种子与引用规模

| 种子 | 年份 | 2024+ 引用 | 总引用（OpenAlex） | 在课题里的角色 |
|---|---|---|---|---|
| MR-Net: Multiresolution Deep Implicit Functions ([W3200254434](https://openalex.org/W3200254434)) | 2021 | 12 | 41 | 多分辨率隐式表示基线 |
| NDM: Neural Deformable Models for 3D Bi-Ventricular Heart... ([W4390872602](https://openalex.org/W4390872602)) | 2023 | 4 | 5 | **心脏版 NDM**，最直接的基线 |
| DIF-Net: Deformed Implicit Field ([W3175010717](https://openalex.org/W3175010717)) | 2021 | 69 | 148 | 隐式模板 + dense correspondence 的源头 |
| DIT: Deep Implicit Templates ([W3174726247](https://openalex.org/W3174726247)) | 2021 | 46 | 111 | 模板空间 + 变形 |
| Shape registration with learned deformations ([W3200745935](https://openalex.org/W3200745935)) | 2021 | 35 | 51 | 稀疏/不完整点云 + 学习变形（心脏邻近） |

---

## 2. 最重要的发现：引文图裂成两簇

把 2024–2026 的引用论文按「引用哪个种子」排开后，出现一个很清楚的裂缝：

**簇 A：心脏网格 / 4D 重建**
- 代表：Slice2Mesh、MorphiNet、CineMesh4D、Local2Mesh、Bi-PT、Anatomy-Aligned、Personalized 4D Whole-Heart、biv-me、TetHeart。
- 它们的引用对象主要是 `Shape registration with learned deformations`、Slice2Mesh 一类**网格模板变形**工作，几乎不引用 DIF-Net / DIT。
- 对应是「模板顶点编号」天然带来的，论文里通常一句话带过，不单独评价。

**簇 B：隐式模板 / 规范空间 / 对应**
- 代表：SDF4CHD、ImHeart、SHDF、VecHeart、Placenta implicit atlas、DIF-Net/DIT 的通用 3D 后续工作。
- 它们引用 DIF-Net / DIT / NDM，讨论 template field 与 deformation field 的联合优化、拓扑保持、双射。
- 但很少处理**真实心脏的稀疏 Cine MRI + 薄壁 + 4D**。

**你的课题正好在这条裂缝上。** 这既是机会（两边都没把对方的东西做全），也是风险（两边的 baseline 和评价口径不互通）。

> ⚠️ 2026 年的 LNCS/arXiv 论文在 OpenAlex 里参考文献索引可能不完整。表中「未见引用」只能说明**当前索引里没有**，投稿前必须在 PDF 参考文献里逐一核实。

---

## 3. 簇 A：引用种子的心脏 / 医学工作

| 论文 | 年/venue | 引用种子 | 方法一句话 | 对你的威胁 |
|---|---|---|---|---|
| **SDF4CHD** | 2024 MedIA | DIF-Net | SDF + CHD 类型/形状解耦；可学习类型模板 + 可逆变形 | 高：把「模板」扩展到**多拓扑**，直接反驳单模板假设 |
| **ImHeart** (Generating Anatomically Accurate Heart Structures via Neural Implicit Fields) | 2024 MICCAI | DIF-Net, DIT | 潜变量 + 可学习模板 + 统一变形场，建模多心腔关系 | 高：多部件模板，接近「完整心脏」 |
| **Type and Shape Disentangled Generative Modeling for CHD** | 2024 MICCAI | DIF-Net | 类型与形状解耦生成 | 中：CHD 拓扑变异 |
| **Personalized 4D Whole Heart Geometry Reconstruction from Cine MRI** | 2025 LNCS | NDM, shape registration | LAX+SAX cine → 4D 全心网格；无配对影像/网格 | **很高**：输入、输出、4D 都与你重合 |
| **VecHeart** | 2026 LNCS | DIF-Net, DIT | 混合 VecSet 表示，四腔整体重建与生成 | 很高：四腔 + 隐式 + 生成 |
| **SHDF** (Shared Hybrid Diffeomorphic Flow) | 2025 TMI | DIF-Net, DIT | 模板场与变形场共享优化；混合微分同胚流 | 高：直接讨论「模板准、变形场欠优化」的耦合 |
| **Volumetrically Consistent Implicit Atlas (Placenta)** | 2026 arXiv | DIF-Net, DIT | SDF + 神经微分同胚流 + 体正则，学共享规范模板 | 高（方法可迁移）：**体对应**而非表面对应 |
| **3D Spatiotemporal cardiac reconstruction (MACE)** | 2026 npj Digit. Med. | NDM | ReconSeg3D 把 SAX cine 重建为时相化 3D 双心室，接预后模型 | 中：下游临床评价范例 |
| **Improved 3D Whole Heart Geometry from Sparse CMR Slices** | 2025 LNCS | shape registration | SSA + LTN + STN 模块组合；图集标签保证拓扑合理 | 高：输入几乎一致；用单个病例做 atlas |
| **CineMesh4D** | 2026 LNCS | shape registration | 稀疏多视角 cine → 3D+t 全心网格；可微渲染 + 双上下文时序块 | 很高：4D 全心 + 稀疏 cine |
| **RVDeformer** | 2026 TMI | shape registration | 稀疏点云引导 RV 模板网格变形；点云-网格融合 | 中高：RV + 超声 + 模板 |
| **Slice2Mesh** | 2024 TMI | shape registration | 2D UNet + GCN 预测模板变形；稀疏轮廓部分监督；ARAP | 高：模板 + 稀疏监督的经典对照 |
| **SurfNet** | 2025 TMI | NDM | 耦合微分同胚变形重建皮层表面 | 低（跨器官）：微分同胚 + 表面 |
| **AortaDiff** | 2025 TVCG | NDM | 体引导条件扩散生成多分支主动脉表面 | 低（跨器官） |

---

## 4. 簇 A 的「新对手」：未在种子引文里出现

这些是 2024–2026 最直接抢位置的论文，但 OpenAlex 里**看不到它们引用 MR-Net/NDM**。必须读 PDF 核实。

| 论文 | 年/venue | 方法一句话 | 为什么危险 | 链接 |
|---|---|---|---|---|
| **MorphiNet** | 2026 TMI | 非配对 CT 学解剖先验 → 梯度场变形模板网格 → 图细分**保持 dense point correspondence** | 明确把「模板对应」当卖点，且用 CT 先验补 CMR 各向异性 | [doi](https://doi.org/10.1109/TMI.2026.3683925) |
| **Anatomy-Aligned Surface Field Learning** | 2026 arXiv | 心内/外膜展开到共享 UV 域，3D 重建变 2D 坐标场补全；显式跨受试者/跨时相对应 | 与你「隐式模板 + 对应」最正面竞争；UV 对应是原生设计 | [arXiv](https://arxiv.org/abs/2609.29825) |
| **Local2Mesh** | 2026 arXiv | 模板网格 + plane-aware Local Router + 图变形；无 3D 网格监督 | 稀疏 SAX、LV、无 3D GT，设定几乎一致 | [arXiv](https://arxiv.org/abs/2610.06052) |
| **Bi-PT** | 2026 arXiv | atlas–点云双向 cross-attention；NODE 局部仿射微分同胚；语义 Chamfer | 四腔 + 稀疏点云 + 对应语义约束 | [arXiv](https://arxiv.org/abs/2607.06923) |
| **Cardiac Mesh Flow** | 2026 arXiv | flow matching 一步生成多尺度 FFD 场，warp 模板；声称有解剖对应 | 模板 + 3D+t + 对应，生成路线 | [arXiv](https://arxiv.org/abs/2605.01884) |
| **Personalized 4D Whole-Heart Mesh via Multi-Scale Temporal** | 2026 arXiv | 端到端 image-to-mesh；Beer–Lambert 可微轮廓渲染；多尺度时序 | 4D 全心 + 稀疏 cine + 端到端 | [arXiv](https://arxiv.org/abs/2607.01952) |
| **Explicit Differentiable Slicing (DVS)** | 2026 MedIA | 显式可微体素化/切片，2D 切片直接监督 3D 网格；全局变形 | 解决 2D→3D 监督，工程上很强 | [doi](https://doi.org/10.1016/j.media.2026.103999) |
| **biv-me** | 2026 MedIA | 开源端到端双心室网格管线；5 数据集 1313 例外部验证 | 开源 + 大样本验证，容易成为审稿人要求的 baseline | [doi](https://doi.org/10.1016/j.media.2026.104252) |
| **TetHeart** | 2025 arXiv | 可变形四面体；全栈/稀疏切片统一 4D 网格；蒸馏 + 弱监督运动 | 术中稀疏场景 + 4D | [arXiv](https://arxiv.org/abs/2509.12090) |
| **AI-enabled cardiac shape reconstruction** | 2026 arXiv | 神经场从稀疏平面轮廓恢复 3D 几何 | 神经场 + 稀疏轮廓 | [arXiv](https://arxiv.org/abs/2603.27003) |
| **cMeta-INR** | 2025 PMB | 队列先验 + 元学习 INR，做可变形配准 | 隐式 + 模板 + 配准 | [doi](https://doi.org/10.1088/1361-6560/ae29e2) |
| **SCorP** | 2024 MICCAI | 直接从**未分割**医学图像预测表面密集对应；统计形状先验 | 绕过分割，直接学对应，威胁「点身份」叙事 | [arXiv](https://arxiv.org/abs/2404.17967) |
| **SPI-CorrNet** | 2024 MICCAI | 从稀疏未分割图像预测**概率** 3D 对应；aleatoric 不确定性 | 同时打「稀疏 + 对应 + 不确定性」 | [arXiv](https://arxiv.org/abs/2407.01931) |

> **SCorP / SPI-CorrNet 是最容易被忽略的两个对手。** 它们不在心脏圈，但「直接从图像预测密集对应 + 不确定性」这件事，正是你候选方向①③的核心动作。开题时必须解释：为什么心脏场景需要模板/隐式表示，而不是直接回归对应。

---

## 5. 簇 B：引用 DIF-Net / DIT 的通用 3D 工作

| 论文 | 年/venue | 引用种子 | 可借什么 | 链接 |
|---|---|---|---|---|
| **TutteNet** | 2024 CVPR | DIF-Net | 2D Tutte 嵌入组合出**单射** 3D 变形，可用于保证心脏变形不折叠 | [arXiv](https://arxiv.org/abs/2406.12121) |
| **Partial-to-Partial Shape Matching with Geometric Consistency** | 2024 CVPR | DIT | 部分-部分匹配的几何一致性约束；明确说「迁移到隐式表示是未来工作」 | [arXiv](https://arxiv.org/abs/2404.12209) |
| **RIST: SO(3)-Invariant Semantic Correspondence** | 2024 CVPR | DIT | 旋转不变的局部形状变换，学 dense correspondence | [arXiv](https://arxiv.org/abs/2404.11156) |
| **DAE-Net** | 2024 SIGGRAPH | DIF-Net, DIT | 可变形部件模板 + 自动编码器，做细粒度共分割 | [arXiv](https://arxiv.org/abs/2311.13125) |
| **SRIF** | 2024 SIGGRAPH Asia | DIF-Net, DIT | 用 2D 扩散模型做图像变形 + 流估计，得到语义对应；**不保证双射** | [arXiv](https://arxiv.org/abs/2409.11682) |
| **Spatial and Surface Correspondence Field** | 2024 TOG | DIF-Net, DIT | 空间 + 表面对应场；可变形 SDF 表示 | [arXiv](https://arxiv.org/abs/2405.03221) |
| **HNDF: Hybrid Neural Diffeomorphic Flow** | 2024 WACV | DIF-Net, DIT | triplane 特征 + 微分同胚流，模板变形生成 | [arXiv](https://arxiv.org/abs/2307.01957) |
| **CanFields** | 2025 ICCV | DIF-Net, MR-Net | 任意长度序列的微分同胚流插值；动态 consolidator | [arXiv](https://arxiv.org/abs/2406.18582) |
| **HNSR** | 2025 SIGGRAPH Asia | DIF-Net, DIT | 预训练 3D 生成模型的多分辨率语义特征 + 全局到局部匹配 | [arXiv](https://arxiv.org/abs/2509.17431) |
| **3D Congealing** | 2024 ECCV | DIF-Net | 无标注 3D 对齐，学规范空间 | — |

---

## 6. 这条链告诉你的三件事

1. **NDM 的心脏引文很少，但每一篇都很重**：Personalized 4D Whole Heart、3D Spatiotemporal MACE 都是 2025–2026 的直接对手。NDM 本身不是被大量改进，而是被「绕过」。
2. **DIF-Net/DIT 的方法论遗产主要在通用 3D 和跨器官图谱**，心脏圈用得不多。你如果能把这套「模板 + 变形 + 双射/拓扑保持」真正落到心脏稀疏观测上，位置是空的。
3. **最新的心脏对手不再从 MR-Net/NDM 出发**，而是从「可微渲染 + 2D 监督 + 4D 时序」出发。你的 related work 不能只写隐式模板谱系，必须把这条「image-to-mesh / 可微切片」谱系写进去，否则会被认为漏掉 SOTA。

---

## 7. 待核实清单（OpenAlex 引用索引不可靠）

- [ ] MorphiNet 是否引用 MR-Net / NDM / DIF-Net（读 PDF 参考文献）
- [ ] Anatomy-Aligned 是否引用 NDM / DIF-Net
- [ ] CineMesh4D 是否引用 NDM
- [ ] Local2Mesh / Bi-PT / Cardiac Mesh Flow 的 baseline 表里有没有 NDM / MR-Net
- [ ] SCorP / SPI-CorrNet 是否讨论过 cardiac 场景
