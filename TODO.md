# 需求和代办整理

- TODO:完成多边形的参数调试函数
- TODO:快速调试功能---将AdjustConfig和main重构，添加调试开关和编码器，使用远程图传+编码器的快速调参
- TODO:重构get_position1函数为get_position，传入一个字典{"R":(x1,y1),"G":(x2,y2),"B":(x3,y3)}以及位号，返回对应位号的颜色

    ```python
    def get_position1(self, res_dict: dict[str, tuple[int, int]], area_id:int=1)->str:
        ...
    ```

    要创建除了1号位参数外的其他位参数，需要在config中添加对应的参数
- TODO:将config.json的位号参数修改为类似于以下的形式

    ```json
    {
        "area1_points":[
            [0,0],      //左上角
            [0,0]       //右下角
        ],
        "area2_points":[
            [0,0],      //左上角
            [0,0]       //右下角
        ],
        "area3_points":[
            [0,0],      //左上角
            [0,0]       //右下角
        ]
    }
    ```

- TODO:运动检测还要判断顺时针和逆时针，还需要进一步沟通
