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
# 后续对话记录
# ========================================
