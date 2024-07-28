# 基于pytorch的颜色识别

本项目是针对工创比赛做的一次技术更新，希望构建一个神经网络代替传统的hsv颜色识别方法，以提高识别的准确率和鲁棒性。

## 基本思想

工创物料的识别过程中给于定位点，代码会不断预测这个定位点内的颜色(通过神经网络模型)

## 实现思路

只需要训练一个可以快速分辨**红绿蓝白**的模型即可。然后向模型输入定位点周围的图像，即可预测出定位点周围的颜色(四分类问题)
