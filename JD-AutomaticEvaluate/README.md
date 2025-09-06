# JD-AutomaticEvaluate
version: JD-AutomaticEvaluate-3.2.4

## 简介
自动化评价工具，给予五星好评加图文。

## 🌟工具特点
- 本工具以订单对应的评价页面地址(orderVoucher_url)作为标识来组织评价任务，消除了部分商品没有商品编号的影响。
- 本工具支持单任务线性运行(符合一般真实用户操作逻辑): `订单列表`->`评价页面`->`商品详情页面copy文案，图片/ai生成文案`->`评价页面填写`


## 📢适用情况
- 本工具目前仅适用于处于待评价状态的订单

- 为确保商品评价内容的准确性，在一个单号有多个子商品评价任务时会逐个进行。若遇到商品详情页面`https://item.jd.com/XXXXXXXX.html`不存在的情况则跳过当前评价任务。

## 💥运行异常情况💥
- **强烈建议** ：发生异常退出之后把日志等级调到DEBUG后重新运行两次，有解决不了的问题拿着log文件来问。
- 若遇人机认证，可视为触发JD的临时风控，可以暂停工具运行几个小时后再试，目前暂未有证据表明该风控与黑号有直接关联；
- 若连续频繁出现人机认证，或多次手动验证后出现异常退出或账号Cookies失效，可视为触发了Cookies更新，请稍后几小时再尝试重新登陆；
- 若有JD大药房的商品订单请在运行工具前提前前往评价页面进行授权，经测试，目前一号一次一劳永逸；

# 🚀 快速开始 🚀🚀🚀
- python版本使用3.12, 建议版本3.8+
- 创建虚拟环境`python -m venv <venv_name>`
- 激活虚拟环境
  - Windows： `.\<venv_name>\Scripts\activate`
  - macOS/Linux: `source <venv_name>/bin/activate`
- 导入依赖：`pip install -r requirements.txt`

## 📟 命令行模式 ⌘
```
# 所有参数已设置好默认值，如需改动请往下阅读
# 使用默认参数运行
# 运行 py 文件
python JDpc-AutomaticEvaluate.py
# 运行 exe 文件
JD-AutomaticEvaluate.exe
```

### 🧩 参数总览

#### 📘 基础参数
| 参数名称 | 类型 | 默认值 | 功能描述 |
|--|--|--|--|
| `-h` `-help` | `action` | `None` | 显示帮助文档 |
| `-v` `-version` | `action` | `None` | 显示版本信息 |
| `-T` `--supported-table` | `action` | `None` | 显示已支持的ai模型信息 |
| `-L` `--log-level` | `str` | `INFO` | 调整日志记录的等级，终端输出与文件记录共用 |

#### 📏 内容校验
| 参数名称 | 类型 | 默认值 | 功能描述 |
|--|--|--|--|
| `MIN_EXISTING_PRODUCT_DESCRIPTIONS`<br>`-md` `--min-descriptions` | `int`   | `15` | 商品需至少有 **X 条真实文案**📝，工具才会读取已有文案 |
| `MIN_EXISTING_PRODUCT_IMAGES`<br>`-mi` `--min-images` | `int`   | `15` | 商品需至少有 **X 张真实图片**🖼️，工具才会读取已有图片 |
| `MIN_DESCRIPTION_CHAR_COUNT`<br>`-mc` `--min-charcount` | `int`   | `60` | ✍️评论文案最少字数限制（例：JD优质评价需 ≥60 字）   |

#### ⚙️ 灵活配置
| 参数名称 | 类型 | 默认值 | 功能描述 |
|--|--|--|--|
| `CLOSE_SELECT_CURRENT_PRODUCT`<br>`-cscp` `--close-select-current-product` | `action`  | `False` | 关闭❌仅查看当前商品：`True`=获取商详页面所有评论，`False`=仅获取当前商品的评论 |
| `CLOSE_AUTO_COMMIT`<br>`-cac` `--close-auto-commit` | `action`  | `False` | 关闭❌自动提交：`True`=填充评价内容后不提交，`False`=自动提交 |


#### 🛠️ 关键防护与异常处理
| 参数名称 | 类型 | 默认值 | 功能描述 |
|--|--|--|--|
| `DEAL_TURING_VERIFCATION`<br>`-dtv` `--deal-turing-verification` | `int`   | `0`   | ⚠️ 图灵测试处理：`0`=触发即退出，`1`=阻塞等待手动验证后继续运行  |
| `GUARANTEE_COMMIT`<br>`-gc` `--guarantee-commit` | `action`  | `False`   | ⛔ 保底评价：`True`=获取不到已有数据时用默认文案确保提交，`False`=不启用 |

#### 🤖 AI 智能生成
| 参数名称 | 类型 | 默认值 | 功能描述 |
|--|--|--|--|
| `CURRENT_AI_GROUP`<br>`-g` `--ai-group` | `str` | `None`   | 🤖 模型组别（如 `Spark`）|
| `CURRENT_AI_MODEL`<br>`-m` `--ai-model` | `str` | `None`   | 🤖 模型名称（如 `Lite`）|

### 参数使用示例
```
# 获取参数表
JD-AutomaticEvaluate -h

# 修改限制条件 MIN_DESCRIPTIONS
JD-AutomaticEvaluate -md 20

# 启用自动化设置（布尔值开关）
JD-AutomaticEvaluate -scpc

# 启用AI模型(以xAI为例)
JD-AutomaticEvaluate -g X -m grok-beta
```

### ⚠️ 注意事项
请仔细阅读上述参数功能后再使用
```
# 不要同时使用功能互斥的参数
❌JD-AutomaticEvaluate --close-auto-commit --guarantee-commit
```

## 📦 exe模式
- 打包命令(chromium-xxxx为浏览器版本号)，浏览器路径暂定使用playwright依赖自带的chrome浏览器。
```
# 基础打包命令
pyinstaller --onefile --add-data="C:\Users\your_username\AppData\Local\ms-playwright\chromium-1169\chrome-win;chromium" JDpc-AutomaticEvaluate.py
```
打包完成就可以运行了Qwq

## AI 模型 api 调用
先确保对应的 API key 已在环境变量中配置；使用`-T`查看对应变量名称:

对于本项目，跨系统通用的持久化配置环境变量的方法(以xAI为例)
```
# 在项目根目录下
echo XAI_API_KEY=your_API_key >> .env
```
当然也可以使用常见的环境变量配置方法，在这里就不做赘述了QwQ
```
# 然后就可以运行了
JD-AutomaticEvaluate -g X -m grok-vision-beta
```
|名称|官网|
|--|--|
|XAI（2025暂无免费额度）|https://console.x.ai|
|SparkAI|https://xinghuo.xfyun.cn/spark|

注意：部分api访问需要特殊的网络qAq


# Update log
- JD-AutomaticEvaluate-3.2.4: ios端新增外卖订单自动评价
- JD-AutomaticEvaluate-3.1.4: pc异常修复
- JD-AutomaticEvaluate-3.1.3: ios端优化
- JD-AutomaticEvaluate-3.1.2: ios端逻辑优化
- JD-AutomaticEvaluate-3.1.1: ios端自动化操作逻辑优化
- JD-AutomaticEvaluate-3.1.0: ios端自动化操作逻辑优化
- JD-AutomaticEvaluate-3.0.0: JD APP ios端适配
- JD-AutomaticEvaluate-2.9.20: 命令参数解析优化
- JD-AutomaticEvaluate-2.9.19: 调整了项目结构
- JD-AutomaticEvaluate-2.9.18: 优化了页面加载
- JD-AutomaticEvaluate-2.9.17: 修复异常；
- JD-AutomaticEvaluate-2.9.16: 修复异常；
- JD-AutomaticEvaluate-2.9.15: 修复异常；
- JD-AutomaticEvaluate-2.9.14: 新增了保底提交
- JD-AutomaticEvaluate-2.8.14: 优化了图灵测试的处理
- JD-AutomaticEvaluate-2.7.14: 优化了主循环与env文件的初始化
- JD-AutomaticEvaluate-2.7.13: 修复与微调
- JD-AutomaticEvaluate-2.7.12: 新增 Cookies 判定失效后的处理
- JD-AutomaticEvaluate-2.6.12: 恢复功能
- JD-AutomaticEvaluate-2.6.11: 网页元素变动适配性更新，恢复了自动评价功能；
- JD-AutomaticEvaluate-2.5.11: 日志新增图灵测试提醒
- JD-AutomaticEvaluate-2.5.10: 不同版本页面适配性更新；
- JD-AutomaticEvaluate-2.4.10: 日志优化；
- JD-AutomaticEvaluate-2.4.9: 新版本适配更新；
- JD-AutomaticEvaluate-2.3.9: 简单维护，作为稳定版打包；
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