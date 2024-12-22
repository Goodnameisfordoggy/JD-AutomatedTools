# JD-AutomaticEvaluate
version: JD-AutomaticEvaluate-2.3.8

# 简介
自动化评价脚本，给予五星好评加图文。

注意：

- 本脚本目前仅适用于处于待评价状态的订单

- 为确保商品评价内容的准确性，在一个单号有多个子商品评价任务时会逐个进行。若遇到商品详情页面`https://item.jd.com/XXXXXXXX.html`不存在的情况则跳过当前评价任务。

# 特点
- 本脚本以订单对应的评价页面地址(orderVoucher_url)作为标识来组织评价任务，消除了部分商品没有商品编号(product_id)的影响。
- 本脚本支持单任务线性运行(符合一般真实用户操作逻辑): `订单列表`->`评价页面`->`商品详情页面copy文案，图片`->`评价页面填写`

# 快速开始
- python版本使用3.12, 建议版本3.8+
- 创建虚拟环境`python -m venv <venv_name>`
- 激活虚拟环境
  - Windows： `.\<venv_name>\Scripts\activate`
  - macOS/Linux: `source <venv_name>/bin/activate`
- 导入依赖：`pip install -r requirements.txt`

## 命令行模式

```
# 所有参数已设置好默认值，如需改动请查看参数列表
# 使用默认参数运行
python JD-AutomaticEvaluate.py
```

#### 示例

```
# 获取参数表
python JD-AutomaticEvaluate.py - h

# 修改限制条件 MIN_DESCRIPTIONS
python JD-AutomaticEvaluate.py -md 20

# 启用自动化设置（布尔值开关）
python JD-AutomaticEvaluate.py -scpc

# 启用AI模型(以xAI为例)
python JD-AutomaticEvaluate.py -g X -m grok-beta
```
以下为 JD-AutomaticEvaluate-2.2.6版本 参数列表示例：
```
options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -T, --supported-table
                        show supported AI groups and models

限制条件(默认值):
  -md MIN_DESCRIPTIONS, --min-descriptions MIN_DESCRIPTIONS
                        商品已有文案的最少数量(15) | 真实评论文案多余这个数脚本才会正常获取已有文案。
  -mi MIN_IMAGES, --min-images MIN_IMAGES
                        商品已有图片的最少数量(15) | 真实评论图片多余这个数脚本才会正常获取已有图片。
  -mc MIN_CHARCOUNT, --min-charcount MIN_CHARCOUNT
                        评论文案的最少字数(60) | 在已有评论中随机筛选文案的限制条件，JD:优质评价要求60字以上。

自动化设置:
  -scpc, --select-current-product-close
                        关闭仅查看当前商品 | 启用此设置，在获取已有评论文案与图片时将查看商品所有商品评论信息，关闭可能会导致评论准确性降低
  -acc, --auto-commit-close
                        关闭自动提交 | 启用此设置，在自动填充完评价页面后将不会自动点击提交按钮

AI设置:
  -g 与 -m 需同时设置;

  -g AI_GROUPS, --ai-group AI_GROUPS
                        AI模型的组别名称 | 使用AI模型生成评论文案
  -m AI_MODEL, --ai-model AI_MODEL
                        AI模型的名称 | 使用AI模型生成评论文案
```
## exe模式
- 打包命令(chromium-xxxx为浏览器版本号)，浏览器路径暂定使用playwright依赖自带的chrome浏览器。
```
pyinstaller --onefile --add-data="C:\Users\your_username\AppData\Local\ms-playwright\chromium-1134\chrome-win;chromium" JD-AutomaticEvaluate.py
```
## AI 模型api调用

```
# 先确保对应的 API key 已在环境变量中配置；查看变量名称:
python JD-AutomaticEvaluate.py -T
```
对于本项目，跨系统通用的持久配置环境变量(以xAI为例)
```
# 在项目根目录下
echo XAI_API_KEY=your_API_key >> .env
```
当然也可以使用常见的环境变量配置方法，在这里就不做赘述了QwQ
```
# 然后就可以运行了
python JD-AutomaticEvaluate.py -g X -m grok-vision-beta
```
|名称|官网|
|--|--|
|XAI|https://console.x.ai|
|SparkAI|https://xinghuo.xfyun.cn/spark|

注意：部分api访问需要特殊的网络qwq


# Update log
- JD-AutomaticEvaluate-2.3.8: 更新了 requirements.txt
- JD-AutomaticEvaluate-2.3.7: 模型补充，细微调整
- JD-AutomaticEvaluate-2.3.6: 支持使用 WebSocket 调用讯飞星火大模型（SparkAI）的api；
- JD-AutomaticEvaluate-2.2.6: 更新README；修复了一些问题；
- JD-AutomaticEvaluate-2.2.5: 支持了命令行运行；尝试接入AI模型
- JD-AutomaticEvaluate-2.1.5: 日志优化
- JD-AutomaticEvaluate-2.1.4: 内置了默认评价文案池；添加了获取已有评价文案、图片的最小现存数量限制；
- JD-AutomaticEvaluate-2.1.3: 优化了登录逻辑；优化了任务构建逻辑，
- JD-AutomaticEvaluate-2.0.3: 支持单文件打包模式运行。
- JD-AutomaticEvaluate-2.0.2: 优化了项目结构；
- JD-AutomaticEvaluate-2.0.1: 日志优化、细微调整
- JD-AutomaticEvaluate-2.0.0: 自动化测试框架由 selenium 更换为 playwright
- JD-AutomaticEvaluate-1.0.1: update .gitignore
- JD-AutomaticEvaluate-1.0.1：对获取到的评论图片进行了简单的处理。
- JD-AutomaticEvaluate-1.0.0：Last edit time 2024-08-02