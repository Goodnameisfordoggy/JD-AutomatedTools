# JD-AutomaticEvaluate
version: JD-AutomaticEvaluate-2.0.2

#### 简介
自动化评价脚本，给予五星好评加图文。

注意：

- 本脚本目前仅适用于处于待评价状态的订单

- 为确保商品评价内容的准确性，脚本每运行一次仅取每个父订单下的首个可评价商品进行评价，如有多个子订单请运行多次该脚本。

- 脚本当前默认使用60字以上的已有评论文本，以及含有2张及以上的评论图片组。若当前商品已有评论中没有符合要求的文本则使用默认文本。没有符合要求的图片组，则不会自动添加评价图片。

#### 特点
- 本脚本以订单编号(order_id)作为标识来组织评价任务，消除了部分商品没有商品编号(product_id)的影响。
- 本脚本每运行一次仅取每个订单下的首个可评价商品进行评价，确保商品评价内容的准确性，并确保了子商品订单在多次运行结束后均能完成评价，其下其他子订单（赠品，服务，券包等）暂按照商品进行评价。

#### 使用
- 如不需要自动点击提交按钮请注释掉
`btn_submit.click()`

# Update log
- JD-AutomaticEvaluate-2.0.2: 优化了项目结构；
- JD-AutomaticEvaluate-2.0.1: 日志优化、细微调整
- JD-AutomaticEvaluate-2.0.0: 自动化测试框架由 selenium 更换为 playwright
- JD-AutomaticEvaluate-1.0.1: update .gitignore
- JD-AutomaticEvaluate-1.0.1：对获取到的评论图片进行了简单的处理。
- JD-AutomaticEvaluate-1.0.0：Last edit time 2024-08-02