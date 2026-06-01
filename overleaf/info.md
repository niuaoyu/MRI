# 各个文件的路径

最终要写的benchmark的pdf在overleaf:/home/wp/nay/github/MRI/overleaf

四个数据集路径：/home/wp/nay/3d-reconstruction/data_process
处理心脏数据集到3DShape2VecSet的代码（有问题）:/home/wp/nay/123
3DShape2VecSet：/home/wp/nay/github/3DShape2VecSet/
3Dshape论文源文件在：/home/wp/nay/github/3DShape2VecSet/arXiv-2301.11445v9

# 多次跟老师沟通的信息
1.三维重建寻常，但如何加上点的对应关系 crosspendence不寻常
2.

# ========================================
# 项目整体总结（2026-06-01 整理）
# ========================================

## 最终目标

撰写一篇 **"Cardiac Substructure 3D Reconstruction with Dense Correspondence" 的 Benchmark 论文**。

论文的核心定位：针对心脏亚结构（双心室）3D重建与密集点对应（Dense Correspondence）问题，构建标准化基准 Benchmark，系统评估现有方法，填补该领域高质量基准数据集的空白。

## 为什么这个任务是重要的/有挑战性的

1. **问题本身的病态性**：从离散点云重建连续表面在数学上是病态的（有无穷多解）
2. **心脏的特殊复杂性**：解剖结构复杂、动态搏动运动、个体间差异大
3. **数据限制**：原始MRI体素层间分辨率低，从分割导出的点云稀疏且不完整
4. **点对应关系**：在重建的同时保持点对应（cross-correspondence）非常困难，即使人工也无法可靠标注
5. **缺乏基准**：现有研究在有限数据集和异构实验设置上评估，公平比较困难

## 论文核心架构

### 数据集（4个多源数据）

| 数据集 | 内容 | 类型 | 规模 |
|--------|------|------|------|
| **UK Digital Heart** | 双心室水密网格（ED/ES两阶段） | 静态 | 1331名健康成年人，HR 1.2×1.2×2mm |
| **M&Ms-2-4D** | 四维双心室表面网格（全周期） | 动态4D | 360名受试者，多疾病多中心 |
| **4DM** | 左心室网格 | 静态 | 25名健康受试者，作为外部先验 |
| **ACDC** | 轮廓点云（仅做评估） | 评估用 | 150名受试者，多病理 |

### 评估的方法

**Learning-free 方法**：DG (贪婪Delaunay)、BPA (球旋转)、PSR (泊松表面重建)、RIMLS

**Learning-based 方法**：
- 形状编码类：DeepSDF、AtlasNet
- 形变场类：IGR、DIF-Net、DIT
- 神经微分流类：NDF、HNDF、SHDF、3DShape2VecSet
- 其他：MR-Net、MeshDiffusion、NDM、CoFie、TetraDiffusion

### 实验设计

1. **数据效率研究**：不同采样策略（均匀/随机/FPS）× 不同点数量（500K/300K/100K）
2. **形状编码表示研究**：不同潜码类型（global/local/triplane）× 不同维度/分辨率
3. **模板学习/配准**：点对应关系质量评估

### 评估指标
- Chamfer Distance (CD)
- Earth Mover Distance (EMD)
- Dense correspondence 不确定性衡量：μ(pᵢ, pⱼ) = 1 − exp(−γ||(pᵢ+vᵢ)−(pⱼ+vⱼ)||²₂)

## 当前已有/在做的工作

### 数据处理流程（/home/wp/nay/3d-reconstruction/data_process/）
- UK Digital Heart：mask→mesh→切片点云→位姿配准→归一化→SDF采样
- M&Ms-2-4D：时序分解→nnU-Net自动分割中间帧→轮廓提取→SSM拟合→网格修复→SDF采样
- 4DM：直接使用OBJ文件→格式转换→SDF采样
- ACDC：低分辨率数据，仅用于评估（点云级）

### 4DM→3DShape2VecSet 转换代码（/home/wp/nay/123/）
- 将4DM的OBJ文件做SDF处理（box.py），再转成ShapeNetV2格式供3DShape2VecSet训练
- 现有转换脚本：run_conversion.py（简化版）和 convert_4dm_to_3dshape.py（完整版）
- **目前代码有问题**，需要调试

### 论文写作（overleaf）
- 已有一个IEEE格式的LaTeX模板/草稿
- 结构完整（Introduction → Related Works → Problem Statement → Methods → Benchmark → Experiments → Results → Conclusion）
- 但大部分内容还是占位符/草稿状态，需要填写完整

## 研究路线图
1. ✅ 数据集构建（已完成，见中期报告）
2. 🔄 (进行中) 基于微分同胚流匹配的双心室三维几何重建、形状配准与生成方法研究
3. 🔄 (待开展) 融合全过程拓扑保持与生物力学先验的双心室四维重建方法研究
4. 🔄 (持续) Benchmark论文撰写

## 关键特色
- 四维双心室表面网格数据集（M&Ms-2-4D）：已知第一个具有时序密集点对应关系的
- 在重建过程中保持dense correspondence是不寻常/有价值的研究点
- 多源异构标准化数据集体系，覆盖静态+动态、高分辨率+临床常规场景

# ========================================
# 评估现有方法的完整流程（2026-06-01 更新）
# ========================================

## 一、各数据集在 Benchmark 中的角色与用法

### 1.1 UK Digital Heart（静态双心室）
- **规模**：1331健康人，ED+ES，HR 1.2×1.2×2mm
- **数据形式**：
  - `mesh/{subject_id}/{phase}.ply` — 水密双心室网格（含顶点标签: 1=LV, 2=RV）
  - `points/{subject_id}/{phase}.ply` — 模拟临床切片的轮廓点云（5000点/样本，含SAX+LAX标签）
  - `norm/{subject_id}/{pose,unit_sphere}.npz` — 位姿变换矩阵 + 单位球归一化参数
  - `sdf/{subject_id}/{phase}.npy` — 500K查询点的SDF值，格式 [x,y,z, lv_sdf, rv_sdf] (N×5)
- **使用方式**：
  - **训练集/验证集**：取1000人，用 `points/` 下的轮廓点云作为输入，`mesh/` 下的网格作为GT
  - **测试集**：剩余331人
  - **评估内容**：静态形状重建质量、潜码表达能力、从稀疏(5000点)到密集的重建

### 1.2 M&Ms-2-4D（四维动态双心室）
- **规模**：360受试者，多疾病多中心，全心动周期
- **数据形式**：
  - `mesh/{subject_id}/{frame_index}.ply` — 每帧双心室水密网格
  - `points/{subject_id}/{frame_index}.ply` — 每帧轮廓点云
  - `sdf/{subject_id}/{frame_index}.npy` — SDF采样
  - 帧间顶点具有 **密集点对应关系**（通过SSM拟合+时序配准实现）
- **使用方式**：
  - **训练**：取300人，用稀疏点云重建表面
  - **测试**：剩余60人的完整序列
  - **评估内容**：4D时序重建一致性、帧间对应保持、运动模式恢复

### 1.3 4DM（左心室先验）
- **规模**：25健康人，左心室网格
- **使用方式**：
  - 因规模小，**不用于独立训练/测试**
  - 作为外部先验：跨数据集配准的参考模板，或数据扩充的辅助
  - 提供 `LVM_ED_mean.obj` 作为LV的统计形状模型参考

### 1.4 ACDC（仅评估）
- **规模**：150受试者，多病理，低分辨率（1.5-3.5mm）
- **数据形式**：
  - `points/{subject_id}/{phase}.ply` — 轮廓点云（短轴切片级，不是完整网格）
  - 无完整网格GT，因此 **无法做表面级精度评估**
- **使用方式**：
  - **仅做测试/泛化评估**
  - 输入：稀疏短轴轮廓点云
  - 输出评估：重建网格在已知切片位置是否与输入轮廓对齐？临床参数(容积/射血分数)是否准确？
- **评估内容**：方法对低分辨率、多病理数据的泛化能力、临床参数准确性

---

## 二、数据预处理统一流程（从原始数据到可评估格式）

所有方法需要统一的输入格式。步骤如下：

### 步骤 1：统一归一化
```
原始点云/网格
  ↓ SE(3) 位姿变换（对齐到SSM标准空间）
  ↓ 单位球归一化（中心→原点，最大半径→1）
  ↓ AABB归一化（包围盒→[-1,1]
```

### 步骤 2：生成标准输入格式
```
对于每种方法，从归一化后的数据生成其需要的输入：

A) 对于学习型方法（DeepSDF, 3DShape2VecSet, DIF-Net, NDF等）：
   ┌─────────────────────────────────────────────────────────────┐
   │ 输入: SDF 查询点 (N×3) + SDF 真值 (N×1 或 N×2)           │
   │ 例如: UKHeart的 sdf/*.npy → [x,y,z, lv_sdf, rv_sdf]      │
   │                                                             │
   │ 数据格式转换脚本在: /home/wp/nay/123/                       │
   │ 需要将 sdf/*.npy 转为 ShapeNetV2 格式:                      │
   │   ShapeNetV2_point/{cat_id}/4_pointcloud/                  │
   │     ├── model_xxxxxx.npz {vol_points, vol_label,           │
   │     │                      near_points, near_label}         │
   │     ├── model_xxxxxx.npy (scale值)                          │
   │     └── train.lst / val.lst / test.lst                      │
   │   ShapeNetV2_watertight/{cat_id}/4_pointcloud/              │
   │     └── model_xxxxxx.npz {points: surface_points}           │
   └─────────────────────────────────────────────────────────────┘

B) 对于非学习方法（DG, BPA, PSR, RIMLS）：
   ┌─────────────────────────────────────────────────────────────┐
   │ 输入: 轮廓点云 (points/*.ply) 或 采样点云                  │
   │ 直接在MeshLab/CGAL中处理即可                                │
   └─────────────────────────────────────────────────────────────┘

C) 对于形变场类方法（DIF-Net, NDF, SHDF等）：
   ┌─────────────────────────────────────────────────────────────┐
   │ 输入: 点云坐标 + 类别潜码 + 每实例潜码                     │
   │ 格式取决于各自的官方实现，需要适配                          │
   └─────────────────────────────────────────────────────────────┘
```

### 步骤 3：训练/推理流程
```
方法官方代码
  ↓ 适配数据接口
训练（学习型方法）/ 直接重建（非学习方法）
  ↓
输出：
  - 表面网格（PLY/OBJ，提取 iso-surface=0）
  - 密集点云（带对应关系）
  - 潜码/形变场（如有）
```

### 步骤 4：后处理（统一到评估空间）
```
重建网格
  ↓ 逆归一化（乘以scale + 减offset = 回到真实物理空间）
  ↓ 如果需要，采样成标准密度点云（10K点用于CD，8K用于EMD）
  ↓ 提取对应点（形变场方法可显式给出，非学习方法需ICP/最近邻匹配）
  ↓ 送入评估模块
```

---

## 三、评价指标体系

### 3.1 几何精度指标（重建表面与GT有多接近）

#### (1) Chamfer Distance (CD)
衡量两个点集之间的平均最近距离：

CD(S₁, S₂) = (1/|S₁|) ∑_{x∈S₁} min_{y∈S₂} ||x−y||₂ + (1/|S₂|) ∑_{y∈S₂} min_{x∈S₁} ||x−y||₂

- **用途**：整体形状相似度
- **实现**：scipy.spatial.KDTree / pytorch3d.ops.knn_points
- **采样点数**：从重建和GT网格表面各采样 **10K 点**
- **指标值**：越低越好，单位 mm（需逆归一化回物理空间）

#### (2) Earth Mover's Distance (EMD) / Wasserstein Distance
衡量两个分布之间的传输代价，比CD更严格（要求双射对应）：

EMD(S₁, S₂) = min_{φ: S₁→S₂, bijective} ∑_{x∈S₁} ||x − φ(x)||₂

- **用途**：更严格的形状差异度量（避免CD的"作弊"问题：CD允许一个点对应多个点）
- **采样点数**：从重建和GT各采样 **8K 点**
- **实现**：Sinkhorn算法或optimal transport库
- **指标值**：越低越好，单位 mm

#### (3) Normal Consistency (NC)
评估重建表面的法线方向准确度：

NC(S₁, S₂) = (1/|S₁|) ∑_{p∈S₁} |⟨n₁(p), n₂(π(p))⟩|

其中 π(p) 是 p 在 GT 表面上的最近邻点，n₁, n₂ 是对应的法线

- **用途**：表面细节和朝向质量
- **范围**：0~1，越高越好

#### (4) Volume IoU (Intersection over Union)
重建网格与GT网格体素化后的交并比：

IoU = |V_recon ∩ V_gt| / |V_recon ∪ V_gt|

- **用途**：体空间上的重叠率，直观衡量整体形状一致程度
- **体素化分辨率**：256³
- **范围**：0~1，越高越好

#### (5) Self-Intersection Ratio
网格中自相交面的比例：
- **用途**：检查重建网格的拓扑质量
- **越低越好**（理想：0%）

### 3.2 密集对应质量指标

密集对应（Dense Correspondence）是这个 Benchmark 的 **核心重点**。

#### (1) Correspondence Uncertainty
对于两个实例 Oᵢ, Oⱼ，给定对应的形变场 vᵢ, vⱼ：

μ(pᵢ, pⱼ) = 1 − exp(−γ ||(pᵢ + vᵢ(pᵢ)) − (pⱼ + vⱼ(pⱼ))||²₂)

- **含义**：两个实例经过形变对齐到模板空间后，对应点之间的距离
- **γ**：缩放因子，控制敏感度
- **值域**：0~1，**0 = 完美对应**，→1 = 对应不准确
- **使用方式**：
  - 类级可视化：模板空间中的平均对应热图
  - 点级统计：所有对应点对的 uncertainty 均值和方差

#### (2) Landmark Distance (如果存在解剖标志点)
对于可识别的解剖标志（如心尖、二尖瓣环等），手动标注后测量：

LD = (1/L) ∑_{l=1}^{L} ||p̂_l − p_l||₂

- **用途**：最直接的对应质量验证
- **值越低越好**，单位 mm

#### (3) Shape Registration Error
利用重建+对应进行形状配准的误差：

RE = CD(T_{i→j}(Oᵢ), Oⱼ)

其中 T_{i→j} 是利用对应关系从形状 i 到 j 的形变配准

- **用途**：间接验证对应质量的实用指标（对应越好，配准越准）

### 3.3 潜码空间质量指标（仅学习型方法）

#### (1) Latent Space Interpolation Smoothness
在潜码空间中线性插值：z(α) = (1−α)z₁ + αz₂，重建形状序列并检查是否平滑过渡

- **评估方式**：相邻插值帧的CD + 视觉检查
- **期望**：形状应平滑变形，无突跳

#### (2) Latent Space Compactness
潜码空间的聚类质量，对于同类形状，latent codes 应该紧凑

- **指标**：类内距离 / 类间距离
- **或**：潜码的PCA解释方差比

#### (3) Generalization Ability
测试集上的重建误差 vs 训练集上的重建误差的比值：

G = CD_test / CD_train

- **越接近1越好**（说明没有过拟合）
- **远大于1** → 过拟合

### 3.4 临床参数准确性

对于心功能分析，从重建网格计算临床参数并与GT比较：

- **EDV**（舒张末期容积）：ED帧的LV/RV腔容积
- **ESV**（收缩末期容积）：ES帧的LV/RV腔容积
- **EF**（射血分数）：EF = (EDV-ESV)/EDV × 100%
- **SV**（每搏输出量）：SV = EDV - ESV
- **LVM**（左心室心肌质量）

评估方式：
- Pearson/Spearman 相关系数
- Bland-Altman 分析（一致性界限）
- 绝对误差百分比

---

## 四、多角度实验设计

### 实验 1：数据效率研究
**目的**：评估各方法在输入数据质量和数量变化时的鲁棒性

| 变量 | 条件设置 |
|------|---------|
| **输入点数量** | 50, 100, 500, 1000, 5000 点（由轮廓点云FPS采样得到） |
| **采样策略** | 均匀采样、随机采样、最远点采样(FPS) |
| **噪声鲁棒性** | 对输入点云加入高斯噪声 σ = {0.01, 0.05, 0.1} |
| **稀疏性** | 缺失部分切片，模拟临床采集不完整的情况 |

**用哪个数据集**：UK Digital Heart 为主 + ACDC（验证泛化）

**预期发现**：
- 学习方法在数据充足时占优，非学习方法在稀疏/极端条件下可能更鲁棒
- 形变场方法（DIF-Net, NDF等）可能在极稀疏输入下能有更好的平滑先验
- DeepSDF等全局潜码方法可能比局部方法需要更多点来达到相同精度

### 实验 2：形状编码表达能力研究
**目的**：系统评估不同潜码/表示方式的表达能力

| 潜码类型 | 配置 | 类别 |
|---------|------|------|
| **Global latent** | 维度 d = {16, 64, 128, 256} | DeepSDF类 |
| **Local grid (3D)** | 网格分辨率 {4³, 8³, 16³}，per-cell=16 | NDF/HNDF类 |
| **Triplane** | 分辨率 {32², 64², 128²}，通道 {16, 32, 64} | 3DShape2VecSet/HNDF类 |
| **VecSet** | d=512, m=512, L=8 | 3DShape2VecSet的Transformer特征集 |

**评估维度**：
1. 重建精度（CD/EMD）vs 潜码维度 → 找出性能饱和点
2. 插值平滑度（潜码线性插值的重建质量）
3. 随机采样生成质量（3D形状生成任务）
4. 潜码空间的分离性（不同心室形态是否在潜空间中聚类）

**用哪个数据集**：UK Digital Heart（大样本，适合统计分析）

### 实验 3：密集对应 / 配准质量研究
**目的**：评估不同方法重建的同时保持点对应的能力

| 方法类别 | 对应策略 |
|---------|---------|
| 形变场方法（DIF-Net, NDF, SHDF, HNDF） | 通过模板空间+形变场显式建立对应 |
| 模板网格方法（AtlasNet等） | 通过固定模板的参数化建立对应 |
| 非学习方法 | 重建后无法建立对应（需额外配准步骤） |
| DeepSDF类 | 无显式对应机制 |

**评估**：
1. 模板空间一致性：将不同形状映射到模板空间，检查对应点的几何合理性
2. 跨受试者配准：用对应关系将A的形状映射到B，计算配准误差
3. 4D时序对应（M&Ms-2-4D）：连续帧之间同一顶点的轨迹是否平滑
4. 类级对应热图可视化

**用哪个数据集**：M&Ms-2-4D（4D对应）为主 + UK Digital Heart（跨受试者配准）

### 实验 4：4D时序重建研究
**目的**：评估方法在动态序列上的表现

- 输入：M&Ms-2-4D 每帧的轮廓点云
- 要求：所有帧共享相同的拓扑（顶点数、连接关系一致）
- 评估：
  1. 每帧单独重建的精度（实验1指标）
  2. 帧间一致性：相邻帧顶点位移的平滑性
  3. 运动模式：EF等心功能参数计算准确性
  4. 时序对应保持：同样顶点在不同帧中是否代表同一解剖点

**用哪个数据集**：M&Ms-2-4D

### 实验 5：泛化能力与跨数据集迁移
**目的**：评估方法在未见过的数据分布上的表现

| 训练 | 测试 | 测试目标 |
|------|------|---------|
| UK Digital Heart | ACDC | 高→低分辨率，健康→病理泛化 |
| UK Digital Heart | M&Ms-2-4D | 静态→动态泛化 |
| 所有训练集 | ACDC | 最大数据量下的最佳泛化 |

**关键问题**：
- 学习型方法在分布偏移时的退化程度
- 非学习方法对数据分布不敏感（优点）
- 哪种潜码表示对域偏移最鲁棒？

### 实验 6：消融研究
对每种方法的关键组件进行消融：
- 有无点对应约束
- 潜码维度的影响
- 训练数据规模的影响
- 损失函数中各项的贡献

---

## 五、完整的实施步骤（从代码到结果）

### Phase 1：数据准备
```bash
# 1. 确认所有数据集已预处理完成
ls /home/wp/nay/3d-reconstruction/data_process/{uk_digital_heart,mnms2_4d,4dm,acdc}/sdf/

# 2. 整理数据统计
#    - 每个数据集的有效样本数
#    - 网格质量检查（水密性/面数）
#    - 分割为 train/val/test
```

### Phase 2：安装所有方法的官方实现
| 方法 | 代码来源 | 适配要点 |
|------|---------|---------|
| DeepSDF | https://github.com/facebookresearch/DeepSDF | SDF数据，auto-decoder框架 |
| DIF-Net | https://github.com/yiren-deng/DIF-Net | 需点云+形变场联合学习 |
| NDF | https://github.com/ShuaiSUN3D/NDF | 微分同胚流，需SDF+形变场 |
| HNDF | 作者开源 | Triplane混合表示 |
| SHDF | 作者开源 | 共享混合流 |
| 3DShape2VecSet | /home/wp/nay/github/3DShape2VecSet/ | VecSet表示+Transformer |
| AtlasNet | 作者开源 | 模板面片组 |
| MR-Net | 作者开源 | 医学图像专用 |
| IGR | 作者开源 | 隐式几何正则化 |
| DG/BPA/PSR/RIMLS | CGAL/MeshLab | 直接调用即可 |

### Phase 3：统一训练/推理脚本
为每种方法编写 wrapper，接口统一为：
```python
def train(method_name, train_data_path, config):
    """训练方法"""
    
def evaluate(method_name, test_data_path, checkpoint):
    """推理并输出重建网格"""
    # 返回: reconstructed_mesh (顶点+面), correspondence_map (可选)
    
def compute_metrics(recon_mesh, gt_mesh, recon_points, gt_points):
    """统一评估"""
    # 返回: {cd, emd, nc, iou, ...}
```

### Phase 4：运行实验
```bash
# 对所有方法循环执行
for method in deepsdf difnet ndf hndf shdf 3dshape2vecset ...:
    # 实验1: 数据效率
    python run_experiment.py --method $method --experiment data_efficiency
    # 实验2: 潜码表示
    python run_experiment.py --method $method --experiment latent_capacity
    # 实验3: 对应质量
    python run_experiment.py --method $method --experiment correspondence
    # ...
```

### Phase 5：结果整理
- 生成指标汇总表（methods × experiments × metrics）
- 可视化：CD曲线图、对应热图、重建对比图
- 统计分析：配对t检验/Wilcoxon检验（方法间显著差异）

---

## 六、预期得出的结论

### 主要发现假设

1. **形变场方法在保持密集对应方面具有本质优势**
   - DIF-Net/NDF/SHDF/HNDF通过模板+形变机制可以显式建立对应
   - 在配准质量指标上显著优于DeepSDF等纯重建方法

2. **局部表示（三平面/网格）在几何细节上优于全局潜码**
   - VecSet (3DShape2VecSet) 和三平面 (HNDF) 在高曲率区域（如乳头肌）精度更高
   - 全局潜码更适合平滑结构，但局部细节能力有限

3. **数据效率存在显著差异**
   - 非学习方法在极稀疏输入（<500点）下仍可工作
   - 学习方法在数据稀疏时退化严重，但输入充足时大幅超越非学习方法
   - Triplane/VecSet表示在中等稀疏度下比全局潜码更鲁棒

4. **跨数据集泛化仍然是一个主要挑战**
   - 在UK Digital Heart（高分辨率健康人）上训练的方法，迁移到ACDC（低分辨率多病理）时精度显著下降
   - 非学习方法不受此影响（单实例重建）

5. **4D时序重建的独特挑战**
   - 独立帧重建无法保证时序一致性
   - 需要显式的时序约束或4D模型来获得生理合理的运动

6. **当前方法的共同局限性**
   - 极稀疏输入下的退化
   - 低分辨率/病理数据的泛化困难
   - 自相交等拓扑缺陷仍然存在（特别是学习方法）

### 论文结论的核心贡献

1. **基准数据集**：首个系统化的心脏3D重建benchmark，覆盖多源、多尺度、多病理
2. **系统评估**：对15+种方法在同一框架下的公平比较
3. **发现与洞见**：为后续研究者在方法选择和设计上提供指导
4. **开放挑战**：指出当前方法的不足和未来方向

### 展望 / 未来工作
- 融合生物力学先验的心脏四维重建
- 基于扩散模型的心脏形状生成
- 弱监督/自适应的域泛化方法
- 端到端的临床参数预测

# ========================================
# 后续对话记录
# ========================================
