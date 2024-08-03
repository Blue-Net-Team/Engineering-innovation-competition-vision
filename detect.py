import torch
import cv2
from model import CNN
from utils import LoadCap

def detect(x0:int, y0:int, x1:int, y1:int):
    cap_loader = LoadCap()

    # 加载模型
    cnn = CNN()
    cnn.load_state_dict(torch.load('model.pth'))
    cnn.eval()

    for img in cap_loader:
        if img is None:
            continue
        img = img[y0:y1, x0:x1]
        img = cv2.resize(img, (128, 128))
        img = torch.from_numpy(img).unsqueeze(0).float()

        with torch.no_grad():
            output = cnn(img)
            prediction = torch.argmax(output, dim=1)

            print(output)
            print(prediction)