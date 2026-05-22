# 背景
1. 扩散模型在 2D 图像生成取得突破（Stable Diffusion，DALL·E，Imagen），但在3D 形状生成领域适配困难，不是diffusion的原因，是3D数据比2D复杂；
2. 3D 数据表示（voxel体素、PC点云、mesh网格、neural field神经场）中，神经场是连续、高保真、可表达复杂拓扑、不依赖固定网络，最适合 generative diffusion 的 3D 表示。但现有神经场表示（全局隐向量、规则 / 不规则隐式网格）存在细节不足、冗余高、不适配 Transformer 的问题；
3. 现有 3D 生成模型多基于 GAN、自回归，基于神经场的 latent diffusion 研究尚浅。

# 研究目的
设计适配扩散模型的 3D 神经场表示，实现高质量、多条件的 3D 形状生成与重建。找到一种“既能表达复杂3D结构，又适合Transformer和Diffusion”的latent representation。构建一个能够将任意三维形状（表面模型或点云）编码为适合生成扩散模型处理的统一表示，并基于此实现从无条件生成到多种条件生成的完整应用体系。

核心思想：**不再显式存储空间坐标，只保留latent set，让网络自己学习空间关系**

核心问题
1. 如何设计紧凑且高保真的 3D 神经场隐式表示？
2. 如何让表示天然适配 Transformer，提升生成与编码能力？
3. 如何在隐空间实现无条件 / 多条件（类别、文本、单视图、点云）3D 扩散生成？

# 创新点
1. 提出Latent Set表示：将 3D 形状编码为固定长度隐向量集合，**抛弃显式空间坐标**，用交叉注意力实现特征空间插值，替代传统空间插值；（之前的3DILG等方法中，latent向量被放置在三维空间中的特定位置x ​处，通过核回归（Kernel Regression）基于距离进行插值）
2. 集合式隐空间扩散框架：两阶段训练（VAE 编码压缩 + 隐集合扩散），适配 Transformer 架构；
3. 多条件统一生成范式：用交叉注意力注入类别、文本、图像、点云条件，支持多任务生成。


# 方法
模块：「VAE + Transformer + Neural Field + Diffusion」 

pipeline：形状自编码shape autoencoder + Latent Diffusion
1. 形状自编码包括三个核心组件：形状编码器（Shape Encoding）、KL正则化块（KL Regularization Block）和形状解码器（Shape Decoding）
	1. 编码过程可表示为：Encpoints(X)=CrossAttn(PosEmb(X0),PosEmb(X))，其中X0=FPS(X)是通过最远点采样（FPS）获得的下采样点集
	2. KL正则化块使用两个线性投影层FCμ和FCσ
2. 


​
 



# 解释
1. 首次用“Transformer latent set + attention interpolation”替代传统几何网格与空间插值，使 neural field 真正成为适合 diffusion generative modeling 的统一3D表示。
2. 把任意3D形状（比如椅子、汽车）用一组数字向量（latent set）来表示，然后通过注意力机制在查询点位置进行插值，最终预测该点是否在物体内部。扩散模型不是直接生成点云，也不是直接生成体素网格，而是先学一个更适合扩散模型处理的三维形状表示
3. 