# 需求和代办整理

- TODO:快速调试功能---将AdjustConfig和main重构，添加调试开关和编码器，使用远程图传+编码器的快速调参
- TODO:圆环第二版：通过红蓝圆环的中点（接近绿色圆环圆心）和识别到的绿色圆环的圆心得到平均绿色圆环圆心，同时得到红蓝圆环的连线的角度
```python
# 将原来的annulus_detect_top改为annulus_detect_top2
def annulus_detect_top(self,img:cv2.typing.MatLike) -> str:
    """
    圆环与直线识别
    ----
    Args:
        img(cv2.typing.MatLike): 图像
    Returns:
        str: 识别结果

    识别结果的格式为:"GHXXXYYYLHAA",其中:
    * G是固定字母，代表绿色圆环
    * H是正负标记位
    * XXX是绿色圆环圆心的x坐标
    * YYY是绿色圆环圆心的y坐标
    * L是固定字母，代表红蓝圆环的连线
    * H是正负标记位
    * AA是红蓝圆环的连线角度

    "G01251056L013"代表绿色圆环位置在(-125,+056)，红蓝圆环的连线角度为13度
    """
```
