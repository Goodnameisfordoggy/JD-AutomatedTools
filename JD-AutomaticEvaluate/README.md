# JD-AutomaticEvaluate
version: JD-AutomaticEvaluate-2.1.3

#### 简介
自动化评价脚本，给予五星好评加图文。

注意：

- 本脚本目前仅适用于处于待评价状态的订单

- 脚本当前默认使用60字以上的已有评论文本，以及含有2张及以上的评论图片组。若当前商品已有评论中没有符合要求的文本则使用默认文本。没有符合要求的图片组，则不会自动添加评价图片，且跳过当前评价任务。

- 为确保商品评价内容的准确性，在一个单号有多个子商品评价任务时会逐个进行。若遇到商品详情页面(https://item.jd.com/XXXXXXXX.html)不存在的情况则跳过当前评价任务。

#### 特点
- 本脚本以订单对应的评价页面地址(orderVoucher_url)作为标识来组织评价任务，消除了部分商品没有商品编号(product_id)的影响。
- 本脚本支持单任务线性运行(符合一般真实用户操作逻辑): `订单列表`->`评价页面`->`商品详情页面copy文案，图片`->`评价页面填写`

#### 使用
- 如不需要请注释掉:
`btn_submit.click()`

# Update log
- JD-AutomaticEvaluate-2.1.3: 优化了登录逻辑；优化了任务构建逻辑，
- JD-AutomaticEvaluate-2.0.3: 支持单文件打包模式运行。
- JD-AutomaticEvaluate-2.0.2: 优化了项目结构；
- JD-AutomaticEvaluate-2.0.1: 日志优化、细微调整
- JD-AutomaticEvaluate-2.0.0: 自动化测试框架由 selenium 更换为 playwright
- JD-AutomaticEvaluate-1.0.1: update .gitignore
- JD-AutomaticEvaluate-1.0.1：对获取到的评论图片进行了简单的处理。
- JD-AutomaticEvaluate-1.0.0：Last edit time 2024-08-02