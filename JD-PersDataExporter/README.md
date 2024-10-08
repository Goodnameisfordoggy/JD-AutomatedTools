# JD-PersDataExporter
version: 2.1.4

## 简介
- 该项目是一个本地自动化工具，用于导出京东个人账户的订单信息。

## 注意事项
- 保持网络通畅，如遇到页面卡死，丢失，访问失败导致程序异常退出，请重启程序。

## 使用说明

#### webUI模式

<center>
<figure>
    <figcaption>
    填入账号昵称(必填，用于登录验证)，在两个下拉列表中选择日期跨度与需要的信息，点击按钮“开始导出”，会跳转浏览器到登录界面，正常登录即可。</figcaption>
    <img src="image/webUI_1.png" alt="webUI_1" width="600">
    <figcaption>webUI主界面</figcaption>
</figure>
</center>
<hr>
<center>
<figure>
    <figcaption>
    订单类型筛选设置，如需变动请在点击按钮“开始导出”前进行设置。</figcaption>
    <img src="image/webUI_2.png" alt="webUI_2" width="600">
    <figcaption>筛选器设置界面</figcaption>
</figure>
</center>
<hr>
<center>
<figure>
    <figcaption>
    脱敏(覆盖)强度选择(0：无，1：弱，2：强)，如需变动请在点击按钮“开始导出”前进行设置。</figcaption>
    <img src="image/webUI_3.png" alt="webUI_3" width="600">
    <figcaption>脱敏强度设置界面</figcaption>
</figure>
</center>
<hr>
<center>
<figure>
    <figcaption>
        <p>点击按钮“开始导出”且运行完成后，会在主界面加载出此界面。</p>
        <p>在此界面可以预览数据，并且可以通过(1.先更改Header中的选项数量或顺序；2.再点击按钮“更改所需数据”)来修改数据预览视图。</p>
        <p>保存数据：数据预览视图所见即所得。1.选择导出方式；2.填写对应的保存设置；3.点击按钮“储存”</p>
    </figcaption>
    <img src="image/webUI_6.png" alt="webUI_4" width="600">
    <figcaption>数据预览与储存界面</figcaption>
</figure>
</center>
<hr>
<center>
<figure>
    <figcaption>
    </figcaption>
    <img src="image/webUI_4.png" alt="webUI_5" width="600">
    <figcaption>Excel储存设置界面</figcaption>
</figure>
</center>
<hr>
<center>
<figure>
    <figcaption>
    </figcaption>
    <img src="image/webUI_5.png" alt="webUI_6" width="600">
    <figcaption>MySQL储存设置界面</figcaption>
</figure>
</center>
<hr>

#### 纯脚本模式
下载解压项目压缩包后按照以下说明进行
1. 使用前配置：
    - 打开config.json（配置文件）
    - 在`"user_name"`后的`""`内填充完整的账号名。该账号名仅用于登录成功验证。
    - 在`"date_range"`后的`[]`内写入要获取的订单的时间分组。必须写入完整的选项字段！若不设置则默认获取最近三个月订单信息。\
    示例：`["ALL"]`将获取账号内全部订单信息；`["2022年订单", "2023年订单", "2016年订单"]`将获取2023年，2022年，2016年这三年的全部订单信息。
  
        |时间分组可选项(与我的订单页面一致)|
        |---|
        |ALL (新增)
        |近三个月订单
        |今年内订单
        |2023年订单
        |2022年订单
        |2021年订单
        |2020年订单
        |2019年订单
        |2018年订单
        |2017年订单
        |2016年订单
        |2015年订单
        |2014年订单
        |2013年订单
        |2014年以前订单
- 在`"header"`后的`[]`中设置需要获取订单的信息类型。默认为全部获取。\
  示例：`["product_name", "order_id", "amount"]`生成的Excel文件第一列信息为商品名称，第二列信息为订单号，第三列信息为总金额(实付)。

    |可选项|信息类型|
    |---|---|
    order_id|订单号
    shop_name|店铺名称
    product_id|商品编号
    product_name|商品名称
    goods_number|商品数量
    amount|总金额(实付)
    jingdou|订单返京豆数量
    order_time|下单时间
    order_status|订单状态
    courier_services_company|物流公司/快递名称
    courier_number|快递单号
    consignee_name|收件人姓名
    consignee_address|收货地址
    consignee_phone_number|收件人联系方式(该信息源已脱敏)
- `"filter_config"`的子项中可以选择筛选订单的类型，最后会影响输出结果。
  示例：若`"去除券(包)类订单"`设置为`true`,那么输出的订单中将不包含券(包)类订单。\
  此外，还设置了通过关键词自定义筛选，其中`"header_item"`的值只能为已有的header_item的名称；`"keyword"`填入要筛选的一个或多个关键词。\
  示例：若`"header_item"`值为`"product_name"`，`"keyword"`值为`["小米", "泡腾片"]`那么最后只会保留商品名称中存在“小米”或“泡腾片”的订单。
- `"masking_intensity"`子项的值代表该项信息的脱敏强度。值为int类型。
  
  |可选项|强度|
  |:---:|:---:|
  0|无
  1|弱
  2|强

  如需多次导出到同一文件，请保证每次(至少order_id)的脱敏强度一致。
  
- `"export_mode"`的值用于设置数据导出方式。

  |可选项|
  |---|
  |excel
  |mysql

  选择`mysql`请在`mysql_user.ini`文件配置相关信息。

2. 启动工具并使用
- 双击运行exe文件，等待浏览器跳转到登录界面。
- 登录你的京东账号，建议使用扫码登录(方便快捷)，其他方式也行。
- 部分账号有概率会出现二次安全验证。如：图形验证，滑块验证，手机号验证码再次登录验证，身份证前几位和后几位验证等。(再次声明，所有信息均在本地使用和处理，请放心通过安全验证)
- 等待程序执行，期间不要关闭浏览器窗口(可以最小化)；程序结束会自动关闭终端窗口，此时在exe文件所在目录可以找到包含订单信息的Excel文件。

## 环境与依赖
- python版本: 3.12.0
- Chrome, 与Chrome对应版本的chromedriver
- 部分包为较新版本,但不代表低版本不可用.
  
    |包名|版本|
    |:---:|:---:|
    parsel|1.9.1
    selenium|4.21.0
    openpyxl|3.1.2
    pandas|2.2.2
    mysql-connector-python|8.4.0
    gradio|4.36.1
  
# Update log
- 2.1.4: 优化了Excel储存方式中对列数据类型与单元格格式的设置
- 2.1.3: 优化了DatabaseManager，使数据库的连接与使用更优雅。
- 2.1.2: 优化了物流公司和物流单号的获取方法。
- 2.1.1: 为webUI添加了跟随系统明暗模式的主题。
- 2.0.1：优化了部分脚本逻辑，使浏览器的生存周期更合理。
- 2.0.0: 为脚本添加了webUI入口，具有简单的样式设计，使其更美观，易使用。
- 1.8.7: 优化了从订单详情获取数据的部分方法(添加脱敏(覆盖)，正则优化)。
- 1.8.6：新增了部分数据信息的获取，导出。
- 1.7.6：为所有模块添加了简单的日志记录，使用全局配置管理。
- 1.6.6: 补齐了所有模块对应的test文件。
- 1.6.5: 添加了英文的README文件。
- 1.6.4: 将两种数据导出方式(Excel, MySQL), 对同一文件的覆盖改为追加。 
- 1.6.3: 新增了对部分敏感信息脱敏(覆盖)强度的选择。
- 1.5.3: 简单重构，添加了test目录来测试部分必要的模块；添加了requirements.txt。
- 1.4.3: 定义了一个表（数据类型），方便数据传递和方法的集成。
- 1.3.3: 新增数据导出方式，导出到MySQL服务器。
- 1.2.3: 将部分类属性私有化；修复了自定义筛选订单类型功能，在部分情况下的异常。
- 1.2.2：将项目按照面向对象规则重组，并使用包结构管理源码。
- 1.1.2: 优化了数据筛选方法。减少了数据迭代次数，提升了性能。
- 1.1.1：新增了订单类型筛选功能。
- 1.0.1: 优化了商品名称，商品数量获取方法。考虑了一个订单号下有多个同店铺商品未进行订单拆分的情况。