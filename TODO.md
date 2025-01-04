# 需求和代办整理

- TODO:快速调试功能---将AdjustConfig和main重构，添加调试开关和编码器，使用远程图传+编码器的快速调参
- TODO:光线频闪会导致颜色二值化的图像也出现频闪问题（尤其是蓝色），需要解决
- TODO:在树莓派上测试各个功能（尤其是圆环识别）的识别速度，不再用帧率作为指标，而是识别时间
- TODO:完成远程图传到调参功能
- TODO:解决绿色圆环难以识别的问题（可能是与物料的色相不同导致）
- TODO:参考旧版本的圆环识别，但是要实现一个函数，只识别圆环(没有识别颜色的功能)，返回圆环的坐标 @Anan-yy
```python
def annulus_top(self,img:cv2.typing.MatLike) -> tuple[int,int]:
    ...
    return x,y
```
