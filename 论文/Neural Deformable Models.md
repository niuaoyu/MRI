# 继续

*导出时间: 2025/12/6 16:06:36*

---

### User

📎 **Ye_Neural_Deformable_Models_for_3D_Bi-Ventricular_Heart_Shape_Reconstruction_and_ICCV_2023_paper.pdf** (PDF)

需要复现这里的算法，需要怎么做？从零复现，pytorch，步骤指南

---

### ChatGPT

从零复现 Neural Deformable Models (NDM) 完整指南
我将为您提供一个系统的复现步骤指南。
📋 第一阶段：环境准备与数据处理
1.1 环境配置
bash复制代码# 创建虚拟环境
conda create -n ndm python=3.8
conda activate ndm

# 安装核心依赖
pip install torch torchvision torchaudio
pip install numpy scipy matplotlib
pip install trimesh open3d
pip install tqdm tensorboard

1.2 数据准备
该研究使用包含1,331个正常受试者的公开3D CMR数据集，每个受试者包含舒张末期(ED)和收缩末期(ES)阶段数据。
python复制代码# data_preprocessing.py
import numpy as np
import nibabel as nib
from scipy.spatial import distance_matrix

class CMRDataPreprocessor:
    def __init__(self, n_sax=10, n_lax=3, n_points=5600):
        self.n_sax = n_sax  # 短轴切片数
        self.n_lax = n_lax  # 长轴切片数
        self.n_points = n_points
    
    def extract_sparse_pointcloud(self, segmentation_mask):
        """从分割mask提取稀疏点云"""
        # 模拟2D CMR扫描提取点
        sparse_points = []
        
        # 提取SAX平面点
        for i in range(self.n_sax):
            slice_points = self._extract_contour_points(segmentation_mask, 'SAX', i)
            sparse_points.append(slice_points)
        
        # 提取LAX平面点
        for i in range(self.n_lax):
            slice_points = self._extract_contour_points(segmentation_mask, 'LAX', i)
            sparse_points.append(slice_points)
        
        sparse_points = np.concatenate(sparse_points, axis=0)
        
        # Farthest Point Sampling降采样
        sparse_points = self.farthest_point_sampling(sparse_points, self.n_points)
        
        return sparse_points
    
    def farthest_point_sampling(self, points, n_samples):
        """最远点采样"""
        n_points = points.shape[0]
        sampled_indices = [np.random.randint(n_points)]
        
        for _ in range(n_samples - 1):
            dists = distance_matrix(points, points[sampled_indices])
            min_dists = dists.min(axis=1)
            sampled_indices.append(min_dists.argmax())
        
        return points[sampled_indices]
    
    def normalize_pointcloud(self, points):
        """归一化点云"""
        # 中心化
        center = points.mean(axis=0)
        points = points - center
        
        # 线性归一化到[-0.85, 0.85]
        points = points / points.max() * 0.85
        
        return points, center

🧮 第二阶段：核心模型组件
2.1 可变形超二次曲面 (Deformable Superquadrics)
python复制代码# deformable_primitives.py
import torch
import torch.nn as nn

class DeformableSuperquadric(nn.Module):
    """可变形超二次曲面基元"""
    
    def __init__(self, n_u=50, n_v=50):
        super().__init__()
        self.n_u = n_u
        self.n_v = n_v
        
        # 创建材质坐标网格
        u = torch.linspace(-np.pi/2, np.pi/6, n_u)
        v = torch.linspace(-np.pi, np.pi, n_v)
        self.u, self.v = torch.meshgrid(u, v, indexing='ij')
        
    def forward(self, a0, a1, a2, a3):
        """
        参数:
            a0: 缩放参数 (batch, n_u)
            a1, a2, a3: 长宽比参数 (batch, n_u, n_v)
        """
        # 椭球方程
        x = a0.unsqueeze(-1) * a1 * torch.cos(self.u) * torch.cos(self.v)
        y = a0.unsqueeze(-1) * a2 * torch.cos(self.u) * torch.sin(self.v)
        z = a0.unsqueeze(-1) * a3 * torch.sin(self.u)
        
        points = torch.stack([x, y, z], dim=-1)
        return points
    
    def apply_axis_offset(self, points, e_xo, e_yo):
        """应用轴偏移变形"""
        points[..., 0] += e_xo.unsqueeze(-1)
        points[..., 1] += e_yo.unsqueeze(-1)
        return points


class BlendedBiVentricleShape(nn.Module):
    """融合的双心室形状模型"""
    
    def __init__(self):
        super().__init__()
        self.lv_endo = DeformableSuperquadric()  # w=0
        self.lv_epi = DeformableSuperquadric()   # w=1
        self.rv = DeformableSuperquadric()        # w=2
    
    def forward(self, params):
        """
        params包含:
            - c: 中心位置 (3,)
            - R: 旋转矩阵 (3, 3)
            - a0, a1, a2, a3: 形状参数
            - e_xo, e_yo: 轴偏移参数
        """
        lv_endo_points = self.lv_endo(params['a0_endo'], 
                                       params['a1_endo'],
                                       params['a2_endo'],
                                       params['a3_endo'])
        
        lv_epi_points = self.lv_epi(params['a0_epi'], 
                                     params['a1_epi'],
                                     params['a2_epi'],
                                     params['a3_epi'])
        
        rv_points = self.rv(params['a0_rv'], 
                            params['a1_rv'],
                            params['a2_rv'],
                            params['a3_rv'])
        
        # 应用轴偏移
        lv_endo_points = self.lv_endo.apply_axis_offset(
            lv_endo_points, params['e_xo_endo'], params['e_yo_endo'])
        
        lv_epi_points = self.lv_epi.apply_axis_offset(
            lv_epi_points, params['e_xo_epi'], params['e_yo_epi'])
        
        # 应用全局变换
        lv_endo_points = self._apply_global_transform(
            lv_endo_points, params['c'], params['R'])
        lv_epi_points = self._apply_global_transform(
            lv_epi_points, params['c'], params['R'])
        rv_points = self._apply_global_transform(
            rv_points, params['c'], params['R'])
        
        return {
            'lv_endo': lv_endo_points,
            'lv_epi': lv_epi_points,
            'rv': rv_points
        }
    
    def _apply_global_transform(self, points, c, R):
        """应用旋转和平移"""
        points = torch.matmul(points, R.T)
        points = points + c
        return points

2.2 神经微分同胚流 (Neural Diffeomorphic Flow)
python复制代码# diffeomorphic_flow.py
import torch
import torch.nn as nn
from torchdiffeq import odeint

class VelocityField(nn.Module):
    """速度场网络"""
    
    def __init__(self, hidden_dim=256, z_dim=256):
        super().__init__()
        
        self.net = nn.Sequential(
            nn.Linear(3 + z_dim + 1, hidden_dim),  # point + embedding + time
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 3)  # 输出3D速度
        )
    
    def forward(self, t, points_with_z):
        """
        t: 时间标量
        points_with_z: (batch, N, 3+z_dim) 点坐标和形状embedding
        """
        batch_size, n_points, _ = points_with_z.shape
        
        # 添加时间维度
        t_expanded = t * torch.ones(batch_size, n_points, 1, 
                                     device=points_with_z.device)
        input_feat = torch.cat([points_with_z, t_expanded], dim=-1)
        
        velocity = self.net(input_feat)
        return velocity


class DiffeomorphicFlow(nn.Module):
    """微分同胚流模块"""
    
    def __init__(self, hidden_dim=256, z_dim=256):
        super().__init__()
        self.velocity_field = VelocityField(hidden_dim, z_dim)
        self.z_dim = z_dim
    
    def forward(self, points, z, n_steps=10):
        """
        points: (batch, N, 3) 初始点
        z: (batch, z_dim) 形状embedding
        """
        batch_size, n_points, _ = points.shape
        
        # 扩展z到每个点
        z_expanded = z.unsqueeze(1).expand(-1, n_points, -1)
        
        # 组合点和embedding
        points_with_z = torch.cat([points, z_expanded], dim=-1)
        
        # ODE求解
        t = torch.linspace(0, 1, n_steps, device=points.device)
        
        def ode_func(t, state):
            points_current = state[..., :3]
            z_current = state[..., 3:]
            velocity = self.velocity_field(t, state)
            # z保持不变
            return torch.cat([velocity, torch.zeros_like(z_current)], dim=-1)
        
        trajectory = odeint(ode_func, points_with_z, t, method='dopri5')
        
        # 返回最终变形后的点
        deformed_points = trajectory[-1, ..., :3]
        
        return deformed_points

🏗️ 第三阶段：完整NDM架构
3.1 Point Transformer编码器
python复制代码# point_transformer.py
import torch
import torch.nn as nn

class PointTransformerLayer(nn.Module):
    """Point Transformer层"""
    
    def __init__(self, dim, k=16):
        super().__init__()
        self.k = k
        
        self.q_conv = nn.Linear(dim, dim)
        self.k_conv = nn.Linear(dim, dim)
        self.v_conv = nn.Linear(dim, dim)
        
        self.pos_mlp = nn.Sequential(
            nn.Linear(3, dim),
            nn.ReLU(),
            nn.Linear(dim, dim)
        )
        
        self.attn_mlp = nn.Sequential(
            nn.Linear(dim, dim),
            nn.ReLU(),
            nn.Linear(dim, dim)
        )
        
    def forward(self, points, features):
        """
        points: (batch, N, 3)
        features: (batch, N, dim)
        """
        Q = self.q_conv(features)
        K = self.k_conv(features)
        V = self.v_conv(features)
        
        # K-近邻
        dist = torch.cdist(points, points)
        _, indices = torch.topk(dist, self.k, dim=-1, largest=False)
        
        # 收集邻居特征
        batch_size, n_points, _ = features.shape
        batch_indices = torch.arange(batch_size).view(-1, 1, 1).expand(-1, n_points, self.k)
        
        K_neighbors = K[batch_indices, indices]
        V_neighbors = V[batch_indices, indices]
        points_neighbors = points[batch_indices, indices]
        
        # 位置编码
        pos_diff = points.unsqueeze(2) - points_neighbors
        pos_encoding = self.pos_mlp(pos_diff)
        
        # 注意力
        attn_features = Q.unsqueeze(2) - K_neighbors + pos_encoding
        attn_weights = self.attn_mlp(attn_features)
        attn_weights = torch.softmax(attn_weights, dim=2)
        
        # 聚合
        aggregated = (attn_weights * (V_neighbors + pos_encoding)).sum(dim=2)
        
        return features + aggregated


class PointTransformerEncoder(nn.Module):
    """Point Transformer编码器"""
    
    def __init__(self, input_dim=3, hidden_dim=256, n_layers=4):
        super().__init__()
        
        self.embed = nn.Linear(input_dim, hidden_dim)
        
        self.layers = nn.ModuleList([
            PointTransformerLayer(hidden_dim)
            for _ in range(n_layers)
        ])
        
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        
    def forward(self, points):
        """
        points: (batch, N, 3)
        返回: (batch, hidden_dim)
        """
        features = self.embed(points)
        
        for layer in self.layers:
            features = layer(points, features)
        
        # 全局池化
        features = features.transpose(1, 2)  # (batch, dim, N)
        z = self.global_pool(features).squeeze(-1)  # (batch, dim)
        
        return z

3.2 完整NDM模型
python复制代码# ndm_model.py
import torch
import torch.nn as nn

class NDM(nn.Module):
    """Neural Deformable Model"""
    
    def __init__(self, hidden_dim=256):
        super().__init__()
        
        # 共享编码器
        self.encoder = PointTransformerEncoder(
            input_dim=3, 
            hidden_dim=hidden_dim
        )
        
        # 三个解码器分支（LV内膜、LV外膜、RV）
        self.decoder_lv_endo = PointTransformerEncoder(hidden_dim=hidden_dim)
        self.decoder_lv_epi = PointTransformerEncoder(hidden_dim=hidden_dim)
        self.decoder_rv = PointTransformerEncoder(hidden_dim=hidden_dim)
        
        # 全局变形参数预测器
        self.global_param_predictor = nn.ModuleDict({
            'lv_endo': self._build_global_predictor(hidden_dim),
            'lv_epi': self._build_global_predictor(hidden_dim),
            'rv': self._build_global_predictor(hidden_dim)
        })
        
        # 形状基元
        self.primitives = BlendedBiVentricleShape()
        
        # 局部变形（微分同胚流）
        self.local_deformation = nn.ModuleDict({
            'lv_endo': DiffeomorphicFlow(hidden_dim),
            'lv_epi': DiffeomorphicFlow(hidden_dim),
            'rv': DiffeomorphicFlow(hidden_dim)
        })
    
    def _build_global_predictor(self, hidden_dim):
        """构建全局参数预测器"""
        return nn.ModuleDict({
            'c': nn.Linear(hidden_dim, 3),  # 中心
            'R': nn.Linear(hidden_dim, 4),  # 四元数
            'a0': nn.Linear(hidden_dim, 50),  # 缩放
            'a1': nn.Linear(hidden_dim, 50*50),  # 长宽比
            'a2': nn.Linear(hidden_dim, 50*50),
            'a3': nn.Linear(hidden_dim, 50*50),
            'e_xo': nn.Linear(hidden_dim, 50),  # 轴偏移
            'e_yo': nn.Linear(hidden_dim, 50)
        })
    
    def forward(self, sparse_points, stage='both'):
        """
        sparse_points: (batch, N, 3) 稀疏输入点云
        stage: 'global', 'local', 或 'both'
        """
        # 编码
        z_shared = self.encoder(sparse_points)
        
        # 三个分支的特征
        z_lv_endo = self.decoder_lv_endo(sparse_points)
        z_lv_epi = self.decoder_lv_epi(sparse_points)
        z_rv = self.decoder_rv(sparse_points)
        
        results = {}
        
        for name, z in zip(['lv_endo', 'lv_epi', 'rv'], 
                           [z_lv_endo, z_lv_epi, z_rv]):
            
            # 预测全局参数
            global_params = self._predict_global_params(
                z, self.global_param_predictor[name]
            )
            
            # 生成全局变形后的形状
            primitive_points = self.primitives.forward_single(
                name, global_params
            )
            
            if stage == 'global':
                results[name] = primitive_points
            else:
                # 应用局部变形
                deformed_points = self.local_deformation[name](
                    primitive_points, z
                )
                results[name] = deformed_points
        
        return results
    
    def _predict_global_params(self, z, predictor):
        """预测全局变形参数"""
        params = {}
        
        params['c'] = predictor['c'](z)
        
        # 四元数归一化
        quat = predictor['R'](z)
        params['R'] = self._quaternion_to_rotation_matrix(quat)
        
        params['a0'] = torch.sigmoid(predictor['a0'](z))
        params['a1'] = torch.sigmoid(predictor['a1'](z)).view(-1, 50, 50)
        params['a2'] = torch.sigmoid(predictor['a2'](z)).view(-1, 50, 50)
        params['a3'] = torch.sigmoid(predictor['a3'](z)).view(-1, 50, 50)
        
        params['e_xo'] = torch.tanh(predictor['e_xo'](z)) * 0.5
        params['e_yo'] = torch.tanh(predictor['e_yo'](z)) * 0.5
        
        return params
    
    def _quaternion_to_rotation_matrix(self, quat):
        """四元数转旋转矩阵"""
        quat = quat / (torch.norm(quat, dim=-1, keepdim=True) + 1e-8)
        w, x, y, z = quat[..., 0], quat[..., 1], quat[..., 2], quat[..., 3]
        
        R = torch.stack([
            torch.stack([1-2*(y**2+z**2), 2*(x*y-w*z), 2*(x*z+w*y)], dim=-1),
            torch.stack([2*(x*y+w*z), 1-2*(x**2+z**2), 2*(y*z-w*x)], dim=-1),
            torch.stack([2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x**2+y**2)], dim=-1)
        ], dim=-2)
        
        return R

🎯 第四阶段：训练流程
4.1 损失函数
python复制代码# losses.py
import torch
import torch.nn as nn

def chamfer_distance(pred, gt):
    """Chamfer距离"""
    # pred -> gt
    dist_pred_to_gt = torch.cdist(pred, gt)
    min_dist_pred_to_gt = dist_pred_to_gt.min(dim=-1)[0]
    
    # gt -> pred
    min_dist_gt_to_pred = dist_pred_to_gt.min(dim=-2)[0]
    
    cd = min_dist_pred_to_gt.mean() + min_dist_gt_to_pred.mean()
    return cd


class NDMLoss(nn.Module):
    """NDM损失函数"""
    
    def __init__(self, lambda_d=0.1, lambda_s=0.05):
        super().__init__()
        self.lambda_d = lambda_d
        self.lambda_s = lambda_s
    
    def forward(self, pred_points, gt_points, global_points=None):
        """
        pred_points: 预测的点云
        gt_points: 真实点云
        global_points: 全局变形后的点（用于计算局部变形）
        """
        # 几何相似性损失
        L_geo = chamfer_distance(pred_points, gt_points)
        
        # 局部变形正则化
        if global_points is not None:
            local_deformation = pred_points - global_points
            L_d = (local_deformation ** 2).mean()
            
            # 平滑性正则化（近似梯度）
            diff_u = local_deformation[:, 1:, :, :] - local_deformation[:, :-1, :, :]
            diff_v = local_deformation[:, :, 1:, :] - local_deformation[:, :, :-1, :]
            L_s = (diff_u ** 2).mean() + (diff_v ** 2).mean()
        else:
            L_d = 0
            L_s = 0
        
        total_loss = L_geo + self.lambda_d * L_d + self.lambda_s * L_s
        
        return {
            'total': total_loss,
            'geo': L_geo,
            'deformation': L_d,
            'smoothness': L_s
        }

4.2 边际空间学习训练
python复制代码# train.py
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm

class MarginalSpaceLearningTrainer:
    """边际空间学习训练器"""
    
    def __init__(self, model, train_loader, val_loader, device='cuda'):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        
        self.criterion = NDMLoss()
        self.optimizer = optim.Adam(model.parameters(), lr=5e-4)
        
    def train_stage1_global(self, n_epochs=50):
        """阶段1: 训练全局变形参数"""
        print("Stage 1: Training global deformations...")
        
        # 冻结局部变形模块
        for param in self.model.local_deformation.parameters():
            param.requires_grad = False
        
        for epoch in range(n_epochs):
            self.model.train()
            epoch_loss = 0
            
            for batch in tqdm(self.train_loader):
                sparse_points = batch['sparse'].to(self.device)
                gt_points = batch['dense'].to(self.device)
                
                # 只使用全局变形
                pred = self.model(sparse_points, stage='global')
                
                # 计算损失（每个部分单独）
                loss_dict = {}
                for name in ['lv_endo', 'lv_epi', 'rv']:
                    losses = self.criterion(
                        pred[name], 
                        gt_points[name]
                    )
                    loss_dict[name] = losses['total']
                
                total_loss = sum(loss_dict.values())
                
                self.optimizer.zero_grad()
                total_loss.backward()
                self.optimizer.step()
                
                epoch_loss += total_loss.item()
            
            print(f"Epoch {epoch+1}/{n_epochs}, Loss: {epoch_loss/len(self.train_loader):.4f}")
            
            if (epoch + 1) % 10 == 0:
                self.validate(stage='global')
    
    def train_stage2_local(self, n_epochs=50):
        """阶段2: 训练局部变形"""
        print("Stage 2: Training local deformations...")
        
        # 解冻局部变形模块
        for param in self.model.local_deformation.parameters():
            param.requires_grad = True
        
        # 可以选择冻结或微调全局参数
        # for param in self.model.global_param_predictor.parameters():
        #     param.requires_grad = False
        
        for epoch in range(n_epochs):
            self.model.train()
            epoch_loss = 0
            
            for batch in tqdm(self.train_loader):
                sparse_points = batch['sparse'].to(self.device)
                gt_points = batch['dense'].to(self.device)
                
                # 获取全局和局部变形结果
                with torch.no_grad():
                    global_pred = self.model(sparse_points, stage='global')
                
                final_pred = self.model(sparse_points, stage='both')
                
                # 计算损失
                loss_dict = {}
                for name in ['lv_endo', 'lv_epi', 'rv']:
                    losses = self.criterion(
                        final_pred[name], 
                        gt_points[name],
                        global_pred[name]  # 用于计算局部变形正则化
                    )
                    loss_dict[name] = losses['total']
                
                total_loss = sum(loss_dict.values())
                
                self.optimizer.zero_grad()
                total_loss.backward()
                self.optimizer.step()
                
                epoch_loss += total_loss.item()
            
            print(f"Epoch {epoch+1}/{n_epochs}, Loss: {epoch_loss/len(self.train_loader):.4f}")
            
            if (epoch + 1) % 10 == 0:
                self.validate(stage='both')
                self.save_checkpoint(f'checkpoint_stage2_epoch{epoch+1}.pth')
    
    def validate(self, stage='both'):
        """验证"""
        self.model.eval()
        val_loss = 0
        
        with torch.no_grad():
            for batch in self.val_loader:
                sparse_points = batch['sparse'].to(self.device)
                gt_points = batch['dense'].to(self.device)
                
                pred = self.model(sparse_points, stage=stage)
                
                for name in ['lv_endo', 'lv_epi', 'rv']:
                    losses = self.criterion(pred[name], gt_points[name])
                    val_loss += losses['total'].item()
        
        print(f"Validation Loss: {val_loss/len(self.val_loader):.4f}")
    
    def save_checkpoint(self, filename):
        """保存检查点"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filename)

4.3 主训练脚本
python复制代码# main.py
import torch
from torch.utils.data import Dataset, DataLoader

class BiVentricleDataset(Dataset):
    """双心室数据集"""
    
    def __init__(self, data_dir, split='train'):
        self.data_dir = data_dir
        self.split = split
        # 加载数据列表
        self.data_list = self._load_data_list()
    
    def __len__(self):
        return len(self.data_list)
    
    def __getitem__(self, idx):
        # 加载稀疏点云和密集真值
        data = self._load_data(self.data_list[idx])
        return {
            'sparse': torch.FloatTensor(data['sparse']),
            'dense': {
                'lv_endo': torch.FloatTensor(data['lv_endo']),
                'lv_epi': torch.FloatTensor(data['lv_epi']),
                'rv': torch.FloatTensor(data['rv'])
            }
        }
    
    def _load_data_list(self):
        # 实现数据列表加载
        pass
    
    def _load_data(self, data_path):
        # 实现单个数据加载
        pass


def main():
    # 超参数
    batch_size = 2
    n_epochs_global = 50
    n_epochs_local = 50
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # 数据加载
    train_dataset = BiVentricleDataset('data/', split='train')
    val_dataset = BiVentricleDataset('data/', split='val')
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, 
                             shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, 
                           shuffle=False, num_workers=4)
    
    # 模型
    model = NDM(hidden_dim=256)
    
    # 训练器
    trainer = MarginalSpaceLearningTrainer(
        model, train_loader, val_loader, device
    )
    
    # 两阶段训练
    trainer.train_stage1_global(n_epochs_global)
    trainer.train_stage2_local(n_epochs_local)
    
    print("Training completed!")


if __name__ == '__main__':
    main()

📊 第五阶段：评估与可视

---

### User

继续

---

### ChatGPT

化
python复制代码# evaluation.py
import torch
import numpy as np
from scipy.spatial.distance import directed_hausdorff
import trimesh

class BiVentricleEvaluator:
    """双心室评估器"""
    
    def __init__(self, model, device='cuda'):
        self.model = model.to(device)
        self.device = device
        self.model.eval()
    
    def evaluate(self, test_loader):
        """完整评估流程"""
        metrics = {
            'lv_endo': {'chamfer': [], 'hausdorff': [], 'dice': []},
            'lv_epi': {'chamfer': [], 'hausdorff': [], 'dice': []},
            'rv': {'chamfer': [], 'hausdorff': [], 'dice': []}
        }
        
        with torch.no_grad():
            for batch in test_loader:
                sparse_points = batch['sparse'].to(self.device)
                gt_points = batch['dense']
                
                # 预测
                pred = self.model(sparse_points, stage='both')
                
                # 计算指标
                for name in ['lv_endo', 'lv_epi', 'rv']:
                    pred_np = pred[name].cpu().numpy()
                    gt_np = gt_points[name].numpy()
                    
                    # Chamfer距离
                    cd = self.compute_chamfer_distance(pred_np, gt_np)
                    metrics[name]['chamfer'].append(cd)
                    
                    # Hausdorff距离
                    hd = self.compute_hausdorff_distance(pred_np, gt_np)
                    metrics[name]['hausdorff'].append(hd)
                    
                    # Dice系数（需要体素化）
                    dice = self.compute_dice_coefficient(pred_np, gt_np)
                    metrics[name]['dice'].append(dice)
        
        # 汇总统计
        results = {}
        for name in ['lv_endo', 'lv_epi', 'rv']:
            results[name] = {
                'chamfer_mean': np.mean(metrics[name]['chamfer']),
                'chamfer_std': np.std(metrics[name]['chamfer']),
                'hausdorff_mean': np.mean(metrics[name]['hausdorff']),
                'hausdorff_std': np.std(metrics[name]['hausdorff']),
                'dice_mean': np.mean(metrics[name]['dice']),
                'dice_std': np.std(metrics[name]['dice'])
            }
        
        return results
    
    def compute_chamfer_distance(self, pred, gt):
        """计算Chamfer距离（毫米）"""
        dist1 = np.min(np.sum((pred[:, None, :] - gt[None, :, :]) ** 2, axis=2), axis=1)
        dist2 = np.min(np.sum((gt[:, None, :] - pred[None, :, :]) ** 2, axis=2), axis=1)
        return (np.mean(np.sqrt(dist1)) + np.mean(np.sqrt(dist2))) / 2
    
    def compute_hausdorff_distance(self, pred, gt):
        """计算Hausdorff距离（毫米）"""
        hd1 = directed_hausdorff(pred, gt)[0]
        hd2 = directed_hausdorff(gt, pred)[0]
        return max(hd1, hd2)
    
    def compute_dice_coefficient(self, pred, gt, voxel_size=1.0):
        """计算Dice系数"""
        # 体素化
        pred_voxels = self.voxelize_points(pred, voxel_size)
        gt_voxels = self.voxelize_points(gt, voxel_size)
        
        # Dice计算
        intersection = np.logical_and(pred_voxels, gt_voxels).sum()
        dice = 2 * intersection / (pred_voxels.sum() + gt_voxels.sum())
        
        return dice
    
    def voxelize_points(self, points, voxel_size=1.0):
        """点云体素化"""
        min_bound = points.min(axis=0) - voxel_size
        max_bound = points.max(axis=0) + voxel_size
        
        grid_size = ((max_bound - min_bound) / voxel_size).astype(int) + 1
        voxels = np.zeros(grid_size, dtype=bool)
        
        indices = ((points - min_bound) / voxel_size).astype(int)
        voxels[indices[:, 0], indices[:, 1], indices[:, 2]] = True
        
        return voxels
    
    def compute_clinical_metrics(self, pred_points):
        """计算临床指标（体积、射血分数等）"""
        # 转换为mesh
        lv_endo_mesh = self.points_to_mesh(pred_points['lv_endo'])
        lv_epi_mesh = self.points_to_mesh(pred_points['lv_epi'])
        rv_mesh = self.points_to_mesh(pred_points['rv'])
        
        # 计算体积
        lv_cavity_volume = lv_endo_mesh.volume
        lv_myocardium_volume = lv_epi_mesh.volume - lv_endo_mesh.volume
        rv_volume = rv_mesh.volume
        
        # 计算质量（假设心肌密度1.05 g/mL）
        lv_mass = lv_myocardium_volume * 1.05
        
        return {
            'lv_cavity_volume': lv_cavity_volume,
            'lv_mass': lv_mass,
            'rv_volume': rv_volume
        }
    
    def points_to_mesh(self, points):
        """点云转mesh（使用Poisson重建）"""
        # 估计法向量
        pcd = trimesh.PointCloud(points)
        
        # 使用alpha shape或ball pivoting创建mesh
        mesh = trimesh.convex.convex_hull(points)
        
        return mesh


# visualization.py
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class BiVentricleVisualizer:
    """双心室可视化工具"""
    
    @staticmethod
    def visualize_reconstruction(sparse_input, pred_output, gt_output=None):
        """可视化重建结果"""
        fig = plt.figure(figsize=(15, 5))
        
        # 输入稀疏点云
        ax1 = fig.add_subplot(131, projection='3d')
        ax1.scatter(sparse_input[:, 0], sparse_input[:, 1], sparse_input[:, 2], 
                   c='blue', s=1, alpha=0.5)
        ax1.set_title('Input Sparse Points')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        
        # 预测结果
        ax2 = fig.add_subplot(132, projection='3d')
        colors = {'lv_endo': 'red', 'lv_epi': 'green', 'rv': 'blue'}
        for name, points in pred_output.items():
            ax2.scatter(points[:, 0], points[:, 1], points[:, 2],
                       c=colors[name], s=1, alpha=0.3, label=name)
        ax2.set_title('Predicted Dense Shape')
        ax2.legend()
        
        # 真值对比
        if gt_output is not None:
            ax3 = fig.add_subplot(133, projection='3d')
            for name, points in gt_output.items():
                ax3.scatter(points[:, 0], points[:, 1], points[:, 2],
                           c=colors[name], s=1, alpha=0.3, label=name)
            ax3.set_title('Ground Truth')
            ax3.legend()
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def visualize_deformation_field(global_shape, local_shape):
        """可视化变形场"""
        fig = plt.figure(figsize=(10, 5))
        
        # 全局形状
        ax1 = fig.add_subplot(121, projection='3d')
        ax1.scatter(global_shape[:, 0], global_shape[:, 1], global_shape[:, 2],
                   c='blue', s=1, alpha=0.5)
        ax1.set_title('Global Deformation')
        
        # 局部变形后
        ax2 = fig.add_subplot(122, projection='3d')
        ax2.scatter(local_shape[:, 0], local_shape[:, 1], local_shape[:, 2],
                   c='red', s=1, alpha=0.5)
        
        # 绘制变形向量（采样部分点）
        sample_indices = np.random.choice(len(global_shape), 100, replace=False)
        for idx in sample_indices:
            ax2.plot([global_shape[idx, 0], local_shape[idx, 0]],
                    [global_shape[idx, 1], local_shape[idx, 1]],
                    [global_shape[idx, 2], local_shape[idx, 2]],
                    'g-', alpha=0.3, linewidth=0.5)
        
        ax2.set_title('Local Deformation')
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_training_curves(loss_history):
        """绘制训练曲线"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # 总损失
        axes[0, 0].plot(loss_history['total'])
        axes[0, 0].set_title('Total Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].grid(True)
        
        # 几何损失
        axes[0, 1].plot(loss_history['geo'])
        axes[0, 1].set_title('Geometry Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].grid(True)
        
        # 变形正则化
        axes[1, 0].plot(loss_history['deformation'])
        axes[1, 0].set_title('Deformation Regularization')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].grid(True)
        
        # 平滑正则化
        axes[1, 1].plot(loss_history['smoothness'])
        axes[1, 1].set_title('Smoothness Regularization')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Loss')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.show()


# 完整评估脚本
def run_evaluation():
    """运行完整评估"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # 加载模型
    model = NDM(hidden_dim=256)
    checkpoint = torch.load('checkpoint_stage2_epoch50.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    
    # 加载测试数据
    test_dataset = BiVentricleDataset('data/', split='test')
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)
    
    # 评估器
    evaluator = BiVentricleEvaluator(model, device)
    
    # 运行评估
    print("Running evaluation...")
    results = evaluator.evaluate(test_loader)
    
    # 打印结果
    print("\n=== Evaluation Results ===")
    for name in ['lv_endo', 'lv_epi', 'rv']:
        print(f"\n{name.upper()}:")
        print(f"  Chamfer Distance: {results[name]['chamfer_mean']:.3f} ± {results[name]['chamfer_std']:.3f} mm")
        print(f"  Hausdorff Distance: {results[name]['hausdorff_mean']:.3f} ± {results[name]['hausdorff_std']:.3f} mm")
        print(f"  Dice Coefficient: {results[name]['dice_mean']:.3f} ± {results[name]['dice_std']:.3f}")
    
    # 可视化示例
    visualizer = BiVentricleVisualizer()
    
    with torch.no_grad():
        sample = next(iter(test_loader))
        sparse = sample['sparse'].to(device)
        pred = model(sparse, stage='both')
        
        # 转换为numpy
        sparse_np = sparse[0].cpu().numpy()
        pred_np = {k: v[0].cpu().numpy() for k, v in pred.items()}
        gt_np = {k: v[0].numpy() for k, v in sample['dense'].items()}
        
        visualizer.visualize_reconstruction(sparse_np, pred_np, gt_np)


if __name__ == '__main__':
    run_evaluation()

🔧 第六阶段：实用工具与优化
python复制代码# utils.py
import torch
import numpy as np
import random

def set_seed(seed=42):
    """设置随机种子"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def count_parameters(model):
    """统计模型参数量"""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"Total parameters: {total:,}")
    print(f"Trainable parameters: {trainable:,}")
    
    return total, trainable


class EarlyStopping:
    """早停机制"""
    
    def __init__(self, patience=10, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
    
    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0


class LearningRateScheduler:
    """学习率调度器"""
    
    def __init__(self, optimizer, warmup_epochs=5, total_epochs=100):
        self.optimizer = optimizer
        self.warmup_epochs = warmup_epochs
        self.total_epochs = total_epochs
        self.base_lr = optimizer.param_groups[0]['lr']
    
    def step(self, epoch):
        if epoch < self.warmup_epochs:
            # Warmup
            lr = self.base_lr * (epoch + 1) / self.warmup_epochs
        else:
            # Cosine annealing
            progress = (epoch - self.warmup_epochs) / (self.total_epochs - self.warmup_epochs)
            lr = self.base_lr * 0.5 * (1 + np.cos(np.pi * progress))
        
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
        
        return lr


# inference.py
class BiVentricleInference:
    """推理接口"""
    
    def __init__(self, model_path, device='cuda'):
        self.device = device
        self.model = NDM(hidden_dim=256).to(device)
        
        checkpoint = torch.load(model_path, map_location=device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
    
    def predict(self, sparse_points):
        """
        输入: 稀疏点云 (N, 3) numpy array
        输出: 密集重建结果字典
        """
        # 预处理
        sparse_tensor = torch.FloatTensor(sparse_points).unsqueeze(0).to(self.device)
        
        # 推理
        with torch.no_grad():
            pred = self.model(sparse_tensor, stage='both')
        
        # 转换为numpy
        result = {
            'lv_endo': pred['lv_endo'][0].cpu().numpy(),
            'lv_epi': pred['lv_epi'][0].cpu().numpy(),
            'rv': pred['rv'][0].cpu().numpy()
        }
        
        return result
    
    def predict_with_metrics(self, sparse_points):
        """预测并返回临床指标"""
        pred = self.predict(sparse_points)
        
        evaluator = BiVentricleEvaluator(self.model, self.device)
        metrics = evaluator.compute_clinical_metrics(pred)
        
        return pred, metrics
    
    def export_to_mesh(self, sparse_points, output_path):
        """导出为mesh文件"""
        pred = self.predict(sparse_points)
        
        # 为每个结构创建mesh
        for name, points in pred.items():
            mesh = trimesh.convex.convex_hull(points)
            mesh.export(f"{output_path}/{name}.obj")
        
        print(f"Meshes exported to {output_path}/")

📝 使用示例
python复制代码# example_usage.py

def example_training():
    """训练示例"""
    set_seed(42)
    
    # 配置
    config = {
        'batch_size': 4,
        'hidden_dim': 256,
        'n_epochs_global': 50,
        'n_epochs_local': 50,
        'lr': 5e-4,
        'device': 'cuda'
    }
    
    # 数据
    train_dataset = BiVentricleDataset('data/', split='train')
    val_dataset = BiVentricleDataset('data/', split='val')
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=4
    )
    
    # 模型
    model = NDM(hidden_dim=config['hidden_dim'])
    count_parameters(model)
    
    # 训练
    trainer = MarginalSpaceLearningTrainer(
        model, train_loader, val_loader, config['device']
    )
    
    trainer.train_stage1_global(config['n_epochs_global'])
    trainer.train_stage2_local(config['n_epochs_local'])


def example_inference():
    """推理示例"""
    # 加载模型
    inference = BiVentricleInference('checkpoint_stage2_epoch50.pth')
    
    # 加载稀疏点云
    sparse_points = np.load('sample_sparse_points.npy')
    
    # 预测
    pred, metrics = inference.predict_with_metrics(sparse_points)
    
    print("Clinical Metrics:")
    print(f"LV Cavity Volume: {metrics['lv_cavity_volume']:.2f} mL")
    print(f"LV Mass: {metrics['lv_mass']:.2f} g")
    print(f"RV Volume: {metrics['rv_volume']:.2f} mL")
    
    # 可视化
    visualizer = BiVentricleVisualizer()
    visualizer.visualize_reconstruction(sparse_points, pred)
    
    # 导出mesh
    inference.export_to_mesh(sparse_points, 'output_meshes/')


if __name__ == '__main__':
    # 训练
    example_training()
    
    # 推理
    example_inference()

📚 完整项目结构
kotlin复制代码ndm_reproduction/
├── data/
│   ├── train/
│   ├── val/
│   └── test/
├── models/
│   ├── __init__.py
│   ├── ndm_model.py
│   ├── deformable_primitives.py
│   ├── diffeomorphic_flow.py
│   └── point_transformer.py
├── utils/
│   ├── __init__.py
│   ├── data_preprocessing.py
│   ├── losses.py
│   ├── visualization.py
│   └── metrics.py
├── train.py
├── evaluation.py
├── inference.py
├── example_usage.py
├── requirements.txt
└── README.md

🎯 关键复现要点总结


数据准备：从CMR分割mask提取稀疏点云（SAX+LAX切片）


两阶段训练：先训练全局变形，再训练局部变形


核心组件：


Point Transformer编码器


可变形超二次曲面基元


神经微分同胚流




损失函数：几何相似性 + 变形正则化 + 平滑正则化


评估指标：Chamfer距离、Hausdorff距离、Dice系数、临床指标


完整复现后，您应该能够实现论文中报告的性能指标。祝您复现顺利！🚀

