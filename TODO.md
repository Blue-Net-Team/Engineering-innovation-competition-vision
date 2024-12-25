# 需求和代办整理

- TODO:完成多边形的参数调试函数
- TODO:快速调试功能---将AdjustConfig和main重构，添加调试开关和编码器，使用远程图传+编码器的快速调参
- TODO:完成`TraditionalColorDetector`的`get_color_position`函数
- TODO:通过传统颜色阈值的方案重构`detect_material_positions`函数,**保持传参和返回值不变**，先用for循环得到各个颜色的mask，将mask放入`detect_material_positions`函数中，得到单一颜色的位置，再将所有颜色的位置合并成结果字典
