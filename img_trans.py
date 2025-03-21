from ImgTrans import SendImgUDP
from ImgTrans.ImgTrans import NeedReConnect
from utils import Cap

if __name__ == "__main__":
    stream = SendImgUDP("wlan0", 4444)
    cap = Cap()
    while True:
        if stream.connecting():
            break
    while True:
        try:
            img = cap.read()[1]
            stream.send(img)
        except NeedReConnect:
            while True:
                if stream.connecting():
                    break
