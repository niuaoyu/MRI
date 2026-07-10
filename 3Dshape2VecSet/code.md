

scp /home/nay/github/3DShape2VecSet/ zhaoxiuyang@172.16.227.8:/home/zhaoxiuyang/nay









# question

![[Pasted image 20260528172222.png]]
目的是 “空间归一化”，无论原本的心脏在三维空间里有多大、多畸形，经历这两行乘法后，它**被等比例、完美地锁死在了 $[-1, 1]^3$ 的标准正方体隐式神经场容器内部**。这为第一阶段 VAE 编码器（Encoder）提供了数值范围绝对整齐划一。
问题是，第一段encoder不需要point点的缩放？为什么缩放？其次，为什么根据surface最远的点缩放？肯定是空间点point更远。


