# 扣图 · 本地部署包

用 BiRefNet HR Matting 与 PyMatting 从人物、亚克力立牌、商品原图提取透明 PNG。初始蒙版由模型生成，再细化半透明过渡和前景颜色。对发丝、指缝、白花瓣等复杂边缘，支持人工 trimap 精修。

## 环境

Python 3.13（64 位，完整安装含 venv 和 pip），Windows、macOS 或 Linux。当前依赖版本在 Windows 64 位验证。其他系统需实际验证对应依赖的安装与运行。默认 CPU；高分辨率模型需要较多内存，处理时间取决于电脑。

## 安装

解压部署包，在项目目录打开终端：

```sh
python setup.py
```

模型约 1.1 GB，默认从 BiRefNet 官方 GitHub 发布下载，下载完成后校验 SHA-256。首次断线后重新运行可续传。需要公开镜像时显式运行：

```sh
python setup.py --mirror
```

已有相同模型，可通过 --model-file "/absolute/path/BiRefNet_HR-matting.onnx" 复制并验证。模型位于 runtime/，依赖位于 .venv/，缓存留在项目内。

## 使用

Windows：

```powershell
.\.venv\Scripts\python.exe skills/kou-tu/scripts/cutout.py "input.jpg" "outputs/result.png" --white-background
```

macOS / Linux：

```sh
.venv/bin/python skills/kou-tu/scripts/cutout.py input.jpg outputs/result.png --white-background
```

仅在原图为白底时加 --white-background。可用绝对路径。输出包括原尺寸 RGBA PNG 与深浅底检查图，文件重名会停止。已有透明图输入时以白色合成后重新估算蒙版。

## 精修发丝和指缝

先查看深浅底对照并按原尺寸放大。对难以区分的白花、皮肤高光、指甲和发丝，制作与原图方向校正后同尺寸的灰度 PNG 蒙版。确定背景用0，过渡区域用128，确定前景用255。用新输出名运行：

```sh
.venv/Scripts/python skills/kou-tu/scripts/cutout.py input.jpg outputs/refined.png --trimap trimap.png
```

软件负责初始轮廓与软边估计。精细发丝和透明饰品需要逐图检查与局部 trimap，成图效果取决于原图分辨率和边缘信息。

## Codex 技能

将 skills/kou-tu 复制到自己的 Codex 全局技能目录，或在本仓库根目录执行：

```sh
npx skills add . --skill kou-tu -g -a codex
```

调用时说“用扣图技能处理这张图”。通过 KOUTU_RUNTIME 指向部署目录的 runtime 文件夹，或给脚本传 --runtime 指定目录；系统 Python 需使用本项目的 .venv 解释器。

## 上传 GitHub

本压缩包包含源码、技能和模型清单。解压后可直接建仓库上传，.gitignore 已排除 .venv、runtime、输出图片和压缩包。上传前按你的发布范围核对文件。

## 来源与授权

BiRefNet 项目和权重来自 ZhengPeng7/BiRefNet，MIT。PyMatting 来自 pymatting/pymatting，MIT。依赖各自的许可证随依赖安装；使用和再分发时保留相关署名。上游链接见 THIRD_PARTY.md。

## 验证记录

本包基于本机已实跑的 BiRefNet HR 2048×2048 + PyMatting 流程整理。模型文件以 model.json 里的 SHA-256 校验。新版脚本已在本机复用既有隔离依赖和校验后的模型端到端运行，并输出原尺寸 RGBA PNG，深浅底目视通过。首次安装器已检查命令入口和语法；完整新环境安装及另一台电脑运行仍待验证。本包不包含用户照片或密钥。