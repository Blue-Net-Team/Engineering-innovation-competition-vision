#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-07-28 23:32:20 +0800
* LastEditTime: 2024-09-04 17:43:18 +0800
* FilePath: \ColorDetector-base-on-pytorch\train.py
* details: 
* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
import datetime
import cv2
import torch
import detector.model
import utils
import torch.optim
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


COLOR_DICT = {
    'R':0,
    'G':1,
    'B':2,
    'W':3
}

COLOR_DICT_reverse = {
    0:'R',
    1:'G',
    2:'B',
    3:'W'
}


def train(epochs=100):
    # 检查是否有可用的GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # 创建数据集
    dataset = utils.DataSet2(ifrandom=False)
    test_dataset = utils.DataSet2('./datas/test')
    # 创建数据加载器
    train_dataloader = utils.DataLoader(dataset, batch_size=64, shuffle=True)
    test_dataloader = utils.DataLoader(test_dataset, batch_size=64, shuffle=True)
    # 创建模型
    cnn = model.CNN().to(device)
    # 加载预训练模型
    # cnn.load_state_dict(torch.load('pre_train.pth'))
    # 创建优化器
    optimizer = torch.optim.SGD(cnn.parameters(), lr=0.001, momentum=0.5, weight_decay=1e-5)
    # 创建损失函数
    loss_fn = torch.nn.CrossEntropyLoss()
    # 创建TensorBoard的写入器
    writer = SummaryWriter()

    nums = 0

    # 日期
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d-%H-%M-%S')
    # 训练
    for epoch in range(epochs):
        Accuracy = 0
        loss_avg = 0
        # 使用tqdm显示训练进度条
        for i, (img, label) in enumerate(tqdm(train_dataloader, desc=f"Epoch {epoch+1}/{epochs} - Training")):
            cnn.train()
            # 将数据移动到GPU上
            img = img.to(device)
            label = label.to(device)  # 确保标签也在GPU上
            # 前向传播
            output = cnn(img)
            # 计算损失
            loss = loss_fn(output, label)
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            # 打印损失
            writer.add_scalar('Loss', loss.item(), nums)
            nums += 1
            loss_avg += loss.item()
        writer.add_scalar('Loss total', loss_avg, i + epoch * len(train_dataloader))
        print(f'epoch:{epoch}, loss_total:{loss_avg}')

        _accuracy = 0

        # 使用tqdm显示测试进度条
        for i, (img, label) in enumerate(tqdm(test_dataloader, desc=f"Epoch {epoch+1}/{epochs} - Testing")):
            cnn.eval()
            # 将数据移动到GPU上
            img = img.to(device)
            label = label.to(device)  # 确保标签也在GPU上
            # 前向传播
            output = cnn(img)
            prediction = torch.argmax(output, dim=1)
            # 计算准确率
            _accuracy += (prediction == label).sum().item()
        _accuracy = _accuracy / len(test_dataloader.dataset)
        writer.add_scalar('Accuracy', _accuracy, epoch)
        print(f'epoch:{epoch}, Accuracy:{_accuracy}')
        if _accuracy > Accuracy:
            Accuracy = _accuracy
            torch.save(cnn.state_dict(), f'best_model{now}.pth')


    # 保存模型
    torch.save(cnn.state_dict(), f'final_model{now}.pth')
    # 关闭TensorBoard的写入器
    writer.close()

if __name__ == '__main__':
    train(1000)