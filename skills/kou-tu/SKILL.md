---
name: kou-tu
description: 扣图。将人物、立牌或商品照片转为透明 PNG，使用 BiRefNet HR Matting 和 PyMatting 细化发梢、鬓角、指缝及边缘颜色。用户说“扣图”“抠图”“去发丝白边”“透明背景”时使用。
---

# 扣图

先读取用户原图并确定输出位置。使用本技能 scripts/cutout.py，本地 CPU 推理，首次由部署包根目录 setup.py 准备依赖与权重。

在项目根目录运行：
```sh
python setup.py
.venv/Scripts/python skills/kou-tu/scripts/cutout.py input.jpg output.png
```
Windows 用 .venv/Scripts/python.exe，macOS/Linux 用 .venv/bin/python。

原图为白底时可加 --white-background。局部精修可用 --trimap 指定与原图同尺寸的灰度 PNG，0 为确定背景、128 为过渡区域、255 为确定前景，特别保护白花瓣、指甲和皮肤高光。自定义模型运行目录用 --runtime 或 KOUTU_RUNTIME。

读取生成的深浅底对照，再按原尺寸检查发梢、鬓角、指缝、浅色衣服和耳饰。必要时编辑局部 trimap 重跑。输出新的 PNG，保留原文件。真实 RGBA、原图尺寸和背景透明度必须验证。发现白边、误抠、断发或裁切时先修复并复查，准确说明仍有的缺陷。