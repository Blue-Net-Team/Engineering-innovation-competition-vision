import cv2
import torch
import model
import utils
import torch.optim
from torch.utils.tensorboard import SummaryWriter


COLOR_DICT = {
    'R':0,
    'G':1,
    'B':2,
}


def train(epochs=100):
    # 检查是否有可用的GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # 创建数据集
    dataset = utils.DataSet2(ifrandom=True)
    # 创建数据加载器
    dataloader = utils.DataLoader(dataset, batch_size=1)
    # 创建模型
    cnn = model.CNN().to(device)
    # 创建优化器
    optimizer = torch.optim.SGD(cnn.parameters(), lr=0.001, momentum=0.5)
    # 创建损失函数
    loss_fn = torch.nn.CrossEntropyLoss()
    # 创建TensorBoard的写入器
    writer = SummaryWriter()

    nums = 0

    # 训练
    for epoch in range(epochs):
        loss_avg = 0
        for i, (img, label) in enumerate(dataloader):
            # 将数据移动到GPU上
            img = img.to(device)
            # 前向传播
            output = cnn(img)
            # 计算损失
            loss = loss_fn(output, torch.tensor([COLOR_DICT[label[0]]]).to(device))
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            # 打印损失
            print(f'epoch:{epoch}, i:{i}, loss:{loss.item()}')
            writer.add_scalar('Loss', loss.item(), nums)
            nums += 1
            loss_avg += loss.item()
        writer.add_scalar('Loss avg', loss_avg/len(dataloader), i + epoch * len(dataloader))
        print(f'epoch:{epoch}, loss_avg:{loss_avg/len(dataloader)}')

    # 保存模型
    torch.save(cnn.state_dict(), 'model.pth')
    # 关闭TensorBoard的写入器
    writer.close()

if __name__ == '__main__':
    train(100)