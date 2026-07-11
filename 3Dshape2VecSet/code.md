
**过去：**
cd /home/nay/github/3DShape2VecSet/

**zhaoxiuyang@172.16.227.8**
scp /home/nay/github/3DShape2VecSet/main_ae.py /home/nay/github/3DShape2VecSet/engine_ae.py zhaoxiuyang@172.16.227.8:/home/zhaoxiuyang/nay

**zhaoxiuyang@172.16.227.3**
scp /home/nay/github/3DShape2VecSet/main_ae.py /home/nay/github/3DShape2VecSet/engine_ae.py zhaoxiuyang@172.16.227.3:/home/zhaoxiuyang/nay

scp /home/nay/github/3DShape2VecSet/main_ae.py zhaoxiuyang@172.16.227.3:/home/zhaoxiuyang/nay

**rookie@202.194.67.162**
scp /home/nay/github/3DShape2VecSet/  rookie@202.194.67.162:/home/rookie/nay

**回来：**
scp /home/rookie/nay/output/ae/baseline_wd005_kl1e3/log.txt nay@202.194.67.156:/home/nay/github/3DShape2VecSet/output/test/baseline_wd005_kl1e3_4090/

scp /home/zhaoxiuyang/nay/output/ae/route2_2gpu_3090/log.txt nay@202.194.67.156:/home/nay/github/3DShape2VecSet/output/test



zhaoxiuyang@master8:~/nay$ ps -up 1968453 1968822
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
zhaoxiu+ 1968453  0.0  0.1 47816724 471420 pts/8 Sl+  7月07   0:46 python hold_gpu_mem.py
zhaoxiu+ 1968822  0.0  0.1 47816744 470576 pts/6 Sl   7月07   0:47 python hold_gpu_mem.py --gpu 1 --gb 23




# question

![[Pasted image 20260528172222.png]]
目的是 “空间归一化”，无论原本的心脏在三维空间里有多大、多畸形，经历这两行乘法后，它**被等比例、完美地锁死在了 $[-1, 1]^3$ 的标准正方体隐式神经场容器内部**。这为第一阶段 VAE 编码器（Encoder）提供了数值范围绝对整齐划一。
问题是，第一段encoder不需要point点的缩放？为什么缩放？其次，为什么根据surface最远的点缩放？肯定是空间点point更远。


