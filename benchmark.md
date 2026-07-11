步骤：

1. 最终数据大表（也就是各种方法在 4 个数据集、11 个指标上的得分）打印出来 
	1. 搞懂，各个指标都是什么含义？在当前这些环境能不能跑出来？
	2. 接着用shdf在一个数据集上的所有指标如何跑出来？
	3. 然后，所有的就很简单了，数据表就出来了，就可对比。
	   1.谁是全场总冠军？ 哪种方法在几乎所有几何指标（CD/EMD）上都压倒性获胜？
	   2.谁在点对应（Uncertainty/SRE）上最强？ 是不是形变场流派（NDF/SHDF）虽然几何精度不是最高，但点对应和配准误差低得惊人？
	   3.谁在极度稀疏的情况下摆烂了？ 当采样点数从 500K 降到 100K 时，哪个方法的 CD 飙升得最厉害？
	   4.谁生成的网格全是流形错误？ 哪些方法虽然 CD 好看，但自相交率（Self-Intersection）高达 15%？
2. 


需要写一个benchmark，_“数字心脏很重要 $\to$ 但临床影像太稀疏导致重建很难，且大家都忽视了建立点对应 $\to$ 现有的算法各有利弊且缺乏统一考场 $\to$ 所以，我们建了这个全指标、多源数据的权威考场（Benchmark）。”

现在有：四个处理后的数据集，
|数据集|来源|模态|帧数/Subject|Subject数|核心资产|用途|
|---|---|---|---|---|---|---|
|**4DM**|4D Myocardium|Cine MR + GT Mesh|25帧|25 (000~024)|GT水密mesh|测试 (重建+对应)|
|**ACDC**|ACDC Challenge 2017|Cine MR + GT Seg|30帧 (仅ED/ES有标签)|100+|GT多类分割|测试 (分割+重建)|
|**M&Ms-2**|M&Ms-2 Challenge|Cine MR (LA+SA)|25帧|2+|双视图MR|测试 (多厂商泛化)|
|**UKDH**|UK Digital Heart|HR/LR MR Seg|2帧 (ED+ES)|1014+|HR+LR分割对|SSM构建 / 测试|

需要：评价各个方法，模型，在统一的四个输入的数据集里的重建表现

考察两个任务：稀释MRI->3D mesh，稀释MRI->3D mesh + dense correspondence

卖点：大部分重建忽略dense correspondence，导致SSM、统计分析、  群体研究无法进行，本文同时评估几何质量geometry和对应关系correspondence

4DM：输入有MRI+GT:mesh
ACDC：输入有MRI+GT:segmentation（无mesh，需用Marching Cubes通过seg得到mesh）
M&Ms2：输入有MRI+GT:segmentation（无mesh，需用Marching Cubes通过seg得到mesh）
UK：输入只有HR seg（283 * 283 * 99，体素间距1.25 * 1.25 * 2）+LR seg （288 * 288 * 12，体素间距1.23 * 1.23 * 10）（无mesh，需用Marching Cubes通过seg得到mesh）HR Mesh = GT，LR Mesh = Sparse Input
统一输入：sparse MRI +Dense Mesh？？？不同数据集做不同的事情

统一坐标系：不同数据集，spacing不同、方向不同、尺寸不同、坐标不同。例如ACDC1.25×1.25×10mm，4DM1×1×1mm，不能直接比较。
Step1 Resampling：统一，1mm isotropic，或者128×128×128
Step2 Orientation：统一，RAS，或者LPS
Step3 Normalization：统一Heart Center=Origin，得到Canonical Space

选择baseline+选择指标评价+泛化（UK训练的模型，在ACDC数据集测试，反之亦然）









# 细节问题
1. Benchmark最终任务是什么？仅重建？还是重建+Dense Correspondence？就做3D的重建和配准，对于配准没有gt，用当前的一些方法比如SHDF来解决
2. Dense Correspondence是时间对应？还是病人间对应？



做不同病人的配准最大的问题是没有gt，如果用UK做SSM（心脏先验），就变成谁更像SSM而不是谁更像真实心脏，一定会被问GT谁定义的？




# 标题

配准是同一病人的不同帧的点对应，4D Dense Correspondence。

Benchmark for Cardiac Sparse-to-Dense Surface Reconstruction and Dense Correspondence

核心贡献根本不是Mesh，而是Sparse Clinical Data->Dense Cardiac Surface->Dense Correspondence


# 数据集

[ACDC Challenge](https://www.creatis.insa-lyon.fr/Challenge/acdc/index.html)、
ACDC数据集，150个案例，分五类，一类30个，是4D序列，但只有两个帧标签（舒张末期ED和收缩末期ES)，学长把两帧标签处理成点云数据了。


[M&Ms-2 Challenge](https://www.ub.edu/mnms-2/)
M&Ms2-4d，360个案例，一个心脏的长短轴分别25帧，分割的标签也对应（长轴跟短轴，每一时刻的帧都对齐了），也对应把所有的标签数据处理成点云数据了。


4DM
25个病人，只有左心室的25帧，有CMR+mesh+points数据。

https://data.mendeley.com/datasets/pw87p286yx/1
UK，1331个病例，每个人只有HR_ED.nii.gz，HR_ES.nii.gz，LR_ED.nii.gz，LR_ES.nii.gz，没有MRI，只有分割标签，没有数据，是双心室的，

UK = 提供大规模形状先验（UK不是为了重建，UK是为了学习心脏形状空间，1331做PCA得到均值形状，限制重建结果）
M&Ms2 = 提供训练深度模型的数据（会用UK的先验心脏模型做约束）
4DM = 高质量Mesh测试集
ACDC = 泛化测试集



# 方法

## 第一类：传统重建（根本没有训练，属于Surface Reconstruction）

输入：Point Cloud（4DM本来就用来测试的）
输出：Mesh （与gt mesh做对比计算损失）
例如：DG、BPA、PSR、RIMLS

## 第二类：Shape Prior

训练：UK(训练得到先验)+M&Ms2（训练用的数据集）->Train->Model
测试：4DM Point Cloud->Model->Mesh->Metric

输入：Sparse Point Cloud
输出：Complete Shape
例如：DeepSDF、IGR、DIF、MR-Net、NDF、HNDF、SHDF

## 第三类：Dense Correspondence

训练：UK(训练得到先验)  +  M&Ms2（训练用的数据集）  ->  Train  ->  Model
测试：4DM Point Cloud  ->  Model  ->  **Mesh+Correspondence**  ->  Metric

输入：Shape A、Shape B
输出：Vertex Correspondence
例如：DIF、CoFie、3DShape2VecSet

注意：DeepSDF根本不会输出Correspondence，而DIF天生输出Correspondence。

所以指标不是一种，而是两种，重建指标 和 对应指标



# 任务

不同方法在这四个数据集的表现


Input：Sparse Cardiac Point Cloud
Output：Dense Surface Mesh (optional Dense Correspondence)

所有方法统一遵守这个接口，即：
Point Cloud
    ↓
Reconstruction Method
    ↓
Dense Mesh
    ↓
Evaluation


Benchmark真正比较什么？

不是比较：谁训练得好
而是比较：面对同样输入，谁重建得最好

例如：
统一输入：Patient001 Sparse Point Cloud
PSR：→ Mesh_A
DeepSDF：→ Mesh_B
HNDF：→ Mesh_C
DIF：→ Mesh_D

然后和GT（mesh）比较：Chamfer、Hausdorff、ASSD

第二张表，比较  Dense Correspondence



# 问老师
1. 普通重建常见，那么为什么还要加上重建的任务？直接写配准不行吗？
2. 3D配准和重建，那配准的gt怎么来？


# 意义 introduction

数字心脏很重要 $\to$但临床影像太稀疏导致重建很难，且大家都忽视了建立点对应 $\to$现有的算法各有利弊且缺乏统一考场 $\to$所以，我们建了这个全指标、多源数据的权威考场（Benchmark）。

### 1. 临床与工程价值：数字孪生心脏的基础

在临床上，针对患者特异性的**心脏三维/四维几何重建**是术前评估、手术规划（如先心病、心肌肥厚手术）的基石，也是目前最前沿的“数字孪生心脏（Digital Heart）”的核心底层技术。

### 2. 核心概念的升华：从“能看”到“能算”

- **过去的重建（单纯几何重建）**：只要外形像个心脏、表面光滑就行。
    
- **现在的刚需（密集点对应，Dense Correspondence）**：导师反复强调，_“三维重建寻常，但如何加上点的对应关系不寻常”_。
    
    在实际临床分析中，我们不仅要看心脏的形状，更需要计算**心肌局部的运动轨迹、应变（Strain）以及将患者的心脏与健康人的标准心脏（Atlas）进行定量对比**。这就强力要求：重建出来的 3D/4D 模型上，**每一个顶点都必须拥有解剖学意义上的“身份证”**。无论心脏怎么跳动，或者换了哪个病人，第 $i$ 个顶点在解剖上必须永远代表同一个位置（例如左心室心尖顶端）。
    

## ❌ 二、 核心痛点：当前行业面临的问题所在（The Problems）

虽然这个任务至关重要，但目前的学术界和工业界正被以下四大相互交织的“泥潭”所困扰：

### 1. 临床数据的“先天残疾”（Data Limitation & Mathematical Ill-posedness）

医院里常规拍摄的心脏电影磁共振（Cine MRI）图像具有极高的层内分辨率，但**层与层之间的间距极大（层间距通常高达 5-10mm）**。

- **带来的痛点**：当把这些离散的二维切片边界提取出来后，我们在三维空间里拿到的输入是一堆**极度稀疏、断续且不完整的轮廓点云**。
    
- **数学上的病态性**：在几何学中，能穿过这几圈稀疏点云的连续封闭表面有**无穷多种可能性**。如何在没有任何人工干预的情况下，从如此残缺的输入中恢复出绝对符合医学解剖学规律的连续水密表面，是一个极其严峻的病态逆问题。
    

### 2. 现有方法“各执一词”，忽视了对应的价值（Methodological Trade-offs）

市面上面对这种稀疏输入，主要有三大流派的算法，但它们都有致命的局限性：

- **传统非学习流派（如泊松重建 PSR）**：它们是纯几何计算，在点云极度稀疏的层间区域经常发生塌陷、漏面，导致生成的网格**不水密（Non-watertight）**；更关键的是，它们对每个样本独立计算，**完全无法建立跨个体、跨时间的点对应关系**。
    
- **纯深度学习重建流派（如 DeepSDF 等隐式神经表示）**：虽然它们通过学习大数据先验，能重建出非常平滑美观的心脏外形，但它们同样将每个患者视为孤立实例，**在网络底层切断了顶点之间的解剖学映射**。
    
- **模板/形变场流派（如 DIF-Net, NDF 等）**：虽然这类方法试图通过“拉伸黄金模板”来建立对应关系，但在面对高度复杂的双心室亚结构（左心室壁、右心室腔、多心室交界面的高曲率区域）时，形变场极易发生剧烈扭曲，导致网格产生大量的**自相交面（Self-Intersection）物理错误**，或丢失乳头肌等关键几何细节。
    

### 3. 基准生态的“军阀割据”与空白（Absence of High-Quality Benchmark）

这是你写这篇 Benchmark 论文最直白、最正义的出发点：

- 尽管近年来涌现出许多 3D/4D 形状重建算法，但由于**缺乏一个统一、开源、标准化的心脏亚结构数据集体系**，大家都在各自私有的、或者格式混乱的数据上测试。
    
- 更严重的是，现有的通用三维重建基准（如 ShapeNet 基准）只测试 Chamfer Distance 等几何距离，**完全缺乏对“密集点对应质量（如配准误差、不确定性）”以及“下游临床诊断参数（如射血分数 EF、舒张容积 EDV 误差）”的综合量化评估**。
    

## 🚀 三、 总结：你的这篇 Benchmark 扮演了什么角色？

理清了上述背景和问题，你论文的**贡献（Contributions）**就顺理成章地诞生了。你正在写的这篇 Benchmark，扮演的是一个**打破行业僵局的“标准制定者”**：

1. **构建了统一的数据生态**：学长做的工作，本质上是把 UK Digital Heart（静态高分辨）、M&Ms-2（带时序对应 4D）、4DM、ACDC 等多源异构的临床原始数据，全部清洗、摆正、规范拓扑，构建了**全球首个兼顾三维重建与高精度稠密点对应的标准化心脏亚结构基准数据集**。
    
2. **制定了多维度的裁判规则**：本论文不偏科，不仅考核算法的“皮相”（几何表面精度 CD, EMD, HD95），还考核算法的“骨骼”（密集对应质量 Uncertainty, LD, SRE）、“血液物理流形”（自相交率、水密性）以及“临床灵魂”（体积误差、射血分数 EF 误差）。
    
3. **照亮了未来的研究路线**：通过对 15 种前沿算法在上述多源场景下的盲测大比拼，系统性地指出了不同流派（全局潜码 vs 局部三平面，隐式表示 vs 显式形变）在面对医学稀疏图像时的极限与代价，为下一代临床数字心脏重建算法指明了改进方向。
    

### 📝 动笔建议：

现在，请闭上眼睛把这个故事在脑子里过一遍：_“数字心脏很重要 $\to$ 但临床影像太稀疏导致重建很难，且大家都忽视了建立点对应 $\to$ 现有的算法各有利弊且缺乏统一考场 $\to$ 所以，我们建了这个全指标、多源数据的权威考场（Benchmark）。”_

有了这个清晰的讲故事逻辑，你可以直接打开 Overleaf 的 `I. INTRODUCTION` 章节。先别管具体的英文语法，试着把这个逻辑链条分成 3-4 个大段落，用你自己的话先把每一段的“核心大意（Bullet Points）”在草稿纸上列出来。这是跨出“思路恐慌”最扎实的一步！





# Cardiac Substructure 3D Reconstruction Benchmark（当前设计梳理）

> 更新时间：2026-07
>
> 当前目标：建立一个统一的 Cardiac Substructure 3D Reconstruction Benchmark，
> 系统评测传统几何重建、隐式表示、模板变形、生成式方法在**稀疏临床输入**下的三维重建能力，并统一评价 Dense Correspondence。


# 一、为什么要做这个 Benchmark？

## 背景

数字心脏（Digital Heart）越来越重要，是：

- 手术规划（Surgical Planning）
- 血流模拟（CFD）
- 生物力学分析（Biomechanics）
- 电生理模拟（Electrophysiology）
- 群体统计分析（Population Analysis）
- 数字孪生（Digital Twin）

的重要基础。

然而，目前临床MR存在天然限制：
baopo
- Slice间距大（Slice spacing）
- Z方向分辨率低
- 数据稀疏
- 很难直接恢复连续三维曲面

因此：

> Cardiac 3D Reconstruction 是一个典型的 Ill-posed Problem。

---

## 目前已有方法

目前已经出现很多方法：

### Learning-free

- DG
- BPA
- PSR
- RIMLS

特点：

- 输入点云
- 输出Mesh
- 不需要训练

---

### Shape Representation

例如：

- AtlasNet
- DeepSDF
- IGR
- SHDF

特点：

学习Shape Distribution。

---

### Template / Deformation

例如：

- DIF-Net
- DIT
- MR-Net
- MeshDiffusion
- NDF
- HNDF
- 3DShape2VecSet
- CoFie
- TetraDiffusion

特点：

学习：

Template

↓

Deformation Field

↓

Target Shape

其中部分模型天然具有 Dense Correspondence。

---

## 目前存在的问题

目前领域没有统一Benchmark：

不同论文：

- 数据集不同
- 输入不同
- Mesh定义不同
- Shape Prior不同
- Correspondence定义不同
- 指标不同

导致：

无法公平比较各种方法。

另外：

很多工作关注：

> Reconstruction

却忽略：

> Dense Correspondence

而Dense Correspondence对于：

- Registration
- Motion Analysis
- Statistical Shape Model
- Population Analysis

都是必须的。

---

# Benchmark目标

建立统一：

- Dataset
- Input
- Mesh Representation
- Evaluation
- Dense Correspondence Pipeline

公平比较不同类别方法。

---

# 二、Benchmark最终任务

目前暂定两个Task。

---

# Task1

## Sparse Cardiac Reconstruction

输入：

Sparse Clinical Observation

例如：

- SAX
- 2CH
- 3CH
- 4CH

输出：

Dense Mesh

评价：

- Chamfer Distance
- Hausdorff Distance
- ASSD
- Surface Normal Error（待定）

---

# Task2

## Dense Correspondence Evaluation

注意：

不是模型直接输出Correspondence。

统一流程：

Prediction Mesh

↓

Template Registration

↓

Dense Correspondence

↓

Evaluation

这样：

所有方法都能参加。

包括：

PSR

DeepSDF

DIF

HNDF

全部统一。

---

# 三、数据集设计

目前使用三个数据集。

---

## 1. UK Digital Heart

数量：

1331

数据：

- HR_ED
- HR_ES
- LR_ED
- LR_ES

只有Segmentation。

Mesh：

Marching Cubes生成。

作用：

- Shape Prior
- Shape Distribution
- Reconstruction训练
- Seen Shape测试

特点：

- 数据最多
- 高分辨率
- 正常人

---

## 2. M&Ms-2

数量：

258（处理后）

特点：

- SAX + LAX
- 多中心
- 多厂家
- 多疾病

目前：

SSM已经拟合。

具有：

Dense Correspondence。

作用：

- Reconstruction训练
- Dense Correspondence测试
- Multi-label测试

---

## 3. ACDC

数量：

150

特点：

- SAX
- ED ES人工标注

作用：

OOD（Out-of-distribution）

Generalization Test。

训练：

不用。

只测试。

---

# 数据集职责

UK

↓

Shape Distribution

↓

Training

↓

Seen Shape Test

----------------------

M&Ms2

↓

Dense Correspondence

↓

Registration Evaluation

----------------------

ACDC

↓

OOD Test

↓

Generalization

---

# 四、输入协议

统一模拟真实临床。

---

## A

Dense Input

输入：

Dense Point Cloud

主要评价：

Upper Bound。

---

## B

Clinical Sparse

模拟：

- SAX
- 2CH
- 3CH
- 4CH

真实临床采样。

---

## C

Ultra Sparse

进一步降低：

Slice数量：

例如：

- 2 slices
- 4 slices
- 6 slices

用于：

极端稀疏测试。

---

# 五、实验设计

## Experiment1

Seen Shape Reconstruction

训练：

UK Train

测试：

UK Test

比较：

Dense

Sparse

Ultra Sparse

---

## Experiment2

Unseen Shape Reconstruction

训练：

UK

测试：

M&Ms2

评价：

Shape Reconstruction。

---

## Experiment3

Generalization

训练：

UK

测试：

ACDC

评价：

Mesh与Contour契合程度。

---

# 六、Dense Correspondence

当前设计：

所有模型：

Prediction Mesh

↓

统一Template Registration

↓

Dense Correspondence

↓

Evaluation

而不是：

各模型输出自己的Correspondence。

原因：

很多模型：

例如：

PSR

DeepSDF

AtlasNet

没有Correspondence输出。

统一Registration以后：

所有方法公平。

---

# Correspondence评价

目前两个任务。

---

## Task1

Registration Shape Quality

评价：

Registration后：

Mesh误差。

例如：

- CD
- HD

---

## Task2

Label Transfer

Template：

LV

RV

Label

↓

Transfer

↓

Prediction Mesh

↓

Compare GT

评价：

- Dice
- IoU

主要用于：

Multi-label Reconstruction。

---

# 七、方法分类

---

## Category1

Learning-free

- DG
- BPA
- PSR
- RIMLS

特点：

Point

↓

Mesh

---

## Category2

Shape Representation

例如：

- AtlasNet
- DeepSDF
- IGR
- SHDF

特点：

学习Shape Distribution。

---

## Category3

Template / Flow

例如：

- DIF
- DIT
- MR-Net
- MeshDiffusion
- NDF
- HNDF
- 3DShape2VecSet
- CoFie
- TetraDiffusion

特点：

Template

↓

Deformation

↓

Shape

部分模型：

天然具有Correspondence。

---

# 八、Benchmark主要研究问题

Q1

各种Shape Representation：

谁重建最好？

---

Q2

随着输入越来越稀疏：

哪些模型最鲁棒？

Dense

↓

Sparse

↓

Ultra Sparse

---

Q3

Template

Deformation

Shape Prior

是否提升重建？

例如：

DeepSDF

vs

HNDF

vs

DIF

---

Q4

生成式方法：

Diffusion

是否改善稀疏输入？

---

Q5

Dense Correspondence：

Template Deformation

是否改善：

Registration

Label Transfer

---

# 九、当前仍未完全确定的问题

## Question1

多标签重建

还是：

整体双心室重建？

目前：

整体重建更简单。

但：

Multi-label更符合临床。

---

## Question2

ED和ES

是否分开训练？

目前：

建议：

分别实验：

- ED
- ES
- ED+ES

比较：

Motion Gap。

---

## Question3

Dense Correspondence

Ground Truth

目前来源：

Template Registration（Pseudo GT）

需要进一步确认：

是否完全采用SSM生成Correspondence。

---

## Question4

Efficiency

是否统计：

- Inference Time
- Training Time
- Params
- FLOPs

建议：

Benchmark应该统计。

---

## Question5

ACDC

没有GT Mesh。

评价：

使用：

Mesh

↓

Slice

↓

Contour

或

Dice。

最终指标需要确定。

---

# 十、当前最大的创新点

不是：

"收集几个数据集"

而是：

建立统一：

- Dataset Protocol
- Input Protocol
- Mesh Representation
- Registration Pipeline
- Dense Correspondence Evaluation
- Generalization Evaluation

实现：

传统方法

↓

隐式表示

↓

模板变形

↓

生成式方法

在同一平台上的公平比较。

---

# 十一、目前最大的风险

目前Benchmark最大的风险不是模型，而是：

Dense Correspondence GT。

需要最终明确：

Template Registration得到的Correspondence：

到底作为：

Pseudo Ground Truth

还是：

Evaluation Protocol。

这是后续和导师需要重点讨论的问题。