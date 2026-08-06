  
datasets|num|cmr|gt mesh|phase|input|features
1. uk-digital-heat | 1331 | sax高分辨率 | marching cubes | es, ed | 模拟2ch 3ch 4ch sax采样|分辨率高
2. M&Ms-2 | 258 | sax+lax低分辨率 | ssm拟合 | 25(35)帧只用有人工标注的es, ed |  模拟2ch 3ch 4ch sax采样| 与ssm有密集点对应关系，数据来自多中心多疾病的受试者
3. ACDC | 150 | sax低分辨率 | 不需要 | 30帧, 只用有人工标注的es, ed | 原始低分辨率sax采样|被广泛使用

方法分类:
1. 直接隐式重建：DeepSDF 、 IGR  、 MR-Net
2. **隐式模板变形**：DIF 、DIF-Net、DIT、NDF（微分同胚）、HNDF（triplane+微分同胚）
3. 显式模板变形：AtlasNet
4. 混合表示重建：CoFie（直接/混合局部隐式）、MeshDiffusion / TetraDiffusion / 3DShape2VecSet（混合表示 / 生成式）

评估任务
1.重建
  i. 见过的形状重建 a.使用训练用的密集数据推理 b. 从稀疏轮廓点云推理(真实场景) c.在b的基础上-2,4,6个输入轮廓(更严格的真实场景，人为降低片间分辨率)
  ii. 没见过的形状重建 同上子任务
  iii. 泛化性重建，在a数据集训练，在b数据集评估, 评估内容是重建形状对轮廓的契合程度
i,ii任务使用 uk-digital-heat， iii任务使用 ACDC
2.点对应(配准)
  i. 使用固定模板点拟合所有形状，评估形状质量和点对应关系, 依然评估1中的a,b,c子任务
  ii. 标签转移，对比ssm标签和配置后形状上的标签(用于区分左右心室结构，解决多标签重建的问题)
 上面两个任务都使用M&Ms-2数据集

实验重点:
1. 各种表示方式之间的优劣
2. 编码方式对模型表现的影响(尤其是稀疏点云输入的场景下)
3. 变形场如何影响点对应表现
4. 生成式方法对稀疏输入的改善情况

数据更新内容:
1. 改变uk-digital-heat的mesh表示方式，针对共享心室壁这一结构，使用共享点+左右心室face的结构(mr-net使用的这个结构)
2. 分别使用ed/es的ssm拟合M&Ms-2的ed/es，ssm的主成分对同阶段的拟合方法更好

问题：
1.是多标签重建(需要改造全部方法)，还是坚持双心室作为一个整体重建(对于模板变形方法，依然可以分离左右心室)
2.ed和es需要分开实验吗，因为二者差别很大
3.推理时间/模型参数/训练开销需要纳入统计吗



要做的3D重建和配准（点对应）benchmark：分三个阶段，先梳理当前列举的这些模型的重建方法结果如何，再梳理模版变形这些方法做点对应的效果如何（肯定是不行的），最后自己提出好的点对应的方法。目前还在第一阶段。

这里的点对应是指：学的变形场，通过模型训练一个变形场，变形场指导变形模板，得到预测的心脏，然后与ground truth做对比，但这没有点对应的关系（目前没有方法做点对应）

重建的输入输出数据不管是点云还是mesh还是sdf都是类似，要根据方法来变



重建的评价指标是有的
配准的方法还没有，配准的评价指标暂时不考虑

三维重建寻常，但如何加上点的对应关系不寻常，重建出来的 3D模型上，**每一个顶点都必须拥有解剖学意义上的“身份证”**。无论心脏怎么跳动，或者换了哪个病人，第 $i$ 个顶点在解剖上必须永远代表同一个位置（例如左心室心尖顶端）




当前目标：建立一个统一的 Cardiac Substructure 3D Reconstruction Benchmark，系统评测传统几何重建、隐式表示、模板变形、生成式方法在**稀疏临床输入**下的三维重建能力，并统一评价 Dense Correspondence。


目前已经出现很多方法：

传统方法（表面重建Surface Reconstruction）：DG、BPA、PSR、RIMLS
特点： 输入点云、输出Mesh、不需要训练

形状表示Shape Representation：AtlasNet、DeepSDF、IGR、SHDF、DIF、MR-Net、NDF、HNDF
特点：学习Shape Distribution

模版变形Template / Deformation（点对应Dense Correspondence）：DIF-Net、DIT、MR-Net、MeshDiffusion、NDF、HNDF、3DShape2VecSet、CoFie、TetraDiffusion
特点：模型model学习变形场deformation field，变形场deformation field指导模板template变形成目标形状target shape
其中部分模型天然具有 Dense Correspondence。

DeepSDF根本不会输出Correspondence，而DIF天生输出Correspondence





AtlasNet（[1802.05384](https://arxiv.org/pdf/1802.05384)）
DeepSDF([openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf))
IGR（[Implicit Geometric Regularization for Learning Shapes](https://arxiv.org/pdf/2002.10099)）、
SHDF、
DIF-Net（[Deformed Implicit Field: Modeling 3D Shapes With Learned Dense Correspondence](https://openaccess.thecvf.com/content/CVPR2021/papers/Deng_Deformed_Implicit_Field_Modeling_3D_Shapes_With_Learned_Dense_Correspondence_CVPR_2021_paper.pdf)），
DIT([2011.14565](https://arxiv.org/pdf/2011.14565))、MR-Net、
MeshDiffusion（[MeshDiffusion__Score_based_Generative_3D_Mesh_Modeling.pdf](https://meshdiffusion.github.io/static/paper/MeshDiffusion__Score_based_Generative_3D_Mesh_Modeling.pdf)）、
NDF、
HNDF([Hybrid Neural Diffeomorphic Flow for Shape Representation and Generation via Triplane](https://openaccess.thecvf.com/content/WACV2024/papers/Han_Hybrid_Neural_Diffeomorphic_Flow_for_Shape_Representation_and_Generation_via_WACV_2024_paper.pdf))、3DShape2VecSet([arxiv.org/pdf/2301.11445](https://arxiv.org/pdf/2301.11445))、
CoFie（[7886b89aced4d37dd25a6f32854bf3f9-Paper-Conference.pdf](https://papers.neurips.cc/paper_files/paper/2024/file/7886b89aced4d37dd25a6f32854bf3f9-Paper-Conference.pdf)）、
TetraDiffusion（[ecva.net/papers/eccv_2024/papers_ECCV/papers/07010.pdf](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07010.pdf)）


ED和ES一起训练

重建指标 和 Dense Correspondence Evaluation对应指标的统一流程是什么？
Q1：各种Shape Representation，谁重建最好？
Q2：随着输入越来越稀疏（Dense、Sparse、Ultra Sparse），哪些模型最鲁棒？
Q3：Template Deformation（Shape Prior）是否提升重建？例如：DeepSDF vs HNDF vs DIF
1.谁是全场总冠军？ 哪种方法在几乎所有几何指标（CD/EMD）上都压倒性获胜？
2.谁在点对应（Uncertainty/SRE）上最强？ 是不是形变场流派（NDF/SHDF）虽然几何精度不是最高，但点对应和配准误差低得惊人？
3.谁在极度稀疏的情况下摆烂了？ 当采样点数从 500K 降到 100K 时，哪个方法的 CD 飙升得最厉害？
4.谁生成的网格全是流形错误？ 哪些方法虽然 CD 好看，但自相交率（Self-Intersection）高达 15%？



现在有：四个处理后的数据集

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



# 数据集

所有的数据集都具有点对应关系

[ACDC Challenge](https://www.creatis.insa-lyon.fr/Challenge/acdc/index.html)、
ACDC数据集，150个案例，分五类，一类30个，是4D序列，但只有两个帧标签（舒张末期ED和收缩末期ES，ED ES人工标注)，只有短轴sax


[M&Ms-2 Challenge](https://www.ub.edu/mnms-2/)
M&Ms2-4d，360个案例，多中心、多厂家、多疾病，处理后还剩258个，心脏的长短轴（SAX + LAX）分别25帧，分割的标签也对应（长轴跟短轴，每一时刻的帧都对齐了），也对应把所有的标签数据处理成点云数据了。

4DM
25个病人，只有左心室的25帧，有CMR+mesh+points数据。

https://data.mendeley.com/datasets/pw87p286yx/1
UK，1331个病例，每个人只有HR_ED.nii.gz，HR_ES.nii.gz，LR_ED.nii.gz，LR_ES.nii.gz，没有MRI，只有分割标签Segmentation，没有数据，是双心室的，数据最多，高分辨，正常人

UK = 提供大规模形状先验（UK不是为了重建，UK是为了学习心脏形状空间，1331做PCA得到均值形状，限制重建结果）
M&Ms2 = 提供训练深度模型的数据（会用UK的先验心脏模型做约束）
4DM = 高质量Mesh测试集
ACDC = 泛化测试集

当前最大的创新点不是收集几个数据集，而是建立统一：
- Dataset Protocol
- Input Protocol
- Mesh Representation
- Registration Pipeline
- Dense Correspondence Evaluation
实现：传统方法，显示、隐式表示，模板变形，在同一平台上的公平比较

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
    

### 3. 基准生态的空白（Absence of High-Quality Benchmark）

这是你写这篇 Benchmark 论文最直白、最正义的出发点：

- 尽管近年来涌现出许多 3D/4D 形状重建算法，但由于**缺乏一个统一、开源、标准化的心脏亚结构数据集体系**，大家都在各自私有的、或者格式混乱的数据上测试。
    
- 更严重的是，现有的通用三维重建基准（如 ShapeNet 基准）只测试 Chamfer Distance 等几何距离，**完全缺乏对“密集点对应质量（如配准误差、不确定性）”以及“下游临床诊断参数（如射血分数 EF、舒张容积 EDV 误差）”的综合量化评估**。
    

## 🚀 三、 总结：你的这篇 Benchmark 扮演了什么角色？

正在写的这篇 Benchmark，扮演的是一个**打破行业僵局的“标准制定者”**：

1. **构建了统一的数据生态**：学长做的工作，本质上是把 UK Digital Heart（静态高分辨）、M&Ms-2（带时序对应 4D）、4DM、ACDC 等多源异构的临床原始数据，全部清洗、摆正、规范拓扑，构建了**全球首个兼顾三维重建与高精度稠密点对应的标准化心脏亚结构基准数据集**
    
2. **制定了多维度的裁判规则**：本论文不偏科，不仅考核算法的“皮相”（几何表面精度 CD, EMD, HD95），还考核算法的“骨骼”（密集对应质量 Uncertainty, LD, SRE）、“血液物理流形”（自相交率、水密性）以及“临床灵魂”（体积误差、射血分数 EF 误差）
    
3. **照亮了未来的研究路线**：通过对 15 种前沿算法在上述多源场景下的盲测大比拼，系统性地指出了不同流派（全局潜码 vs 局部三平面，隐式表示 vs 显式形变）在面对医学稀疏图像时的极限与代价，为下一代临床数字心脏重建算法指明了改进方向
    

### 📝 动笔建议：

现在，请闭上眼睛把这个故事在脑子里过一遍：_“数字心脏很重要 $\to$ 但临床影像太稀疏导致重建很难，且大家都忽视了建立点对应 $\to$ 现有的算法各有利弊且缺乏统一考场 $\to$ 所以，我们建了这个全指标、多源数据的权威考场（Benchmark）。”_

















