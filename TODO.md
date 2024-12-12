# 需求和代办整理

- TODO:完成多边形的参数调试函数
- TODO:快速调试功能---将AdjustConfig和main重构，添加调试开关和编码器，使用远程图传+编码器的快速调参
- TODO:在Solution定义一个函数，传入一个字典{"R":(x1,y1),"G":(x2,y2),"B":(x3,y3)}判断三个点的位置，返回一号位颜色

    ```python
    def get_position1(self, dict)->str:
        ...
    ```

    要创建一号位的区域参数，使用detect_material_positions函数得到1号位的区域，参数由x1,x2,y1,y2组成，即x左上角点(x1,y1)和右下角点(x2,y2)。一号位区域是这两个点围成的矩形区域。
- TODO:运动检测还要判断顺时针和逆时针，还需要进一步沟通
