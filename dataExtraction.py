import select
import parsel

with open('p2.html', 'r') as f:
    html = f.read()
result = parsel.Selector(html)

table = result.xpath('//table[@class="td-void order-tb"]')
# print(table)

tbodys = table.xpath('.//tbody[not(contains(@id, "parent"))]') # 筛掉合并订单，该类订单无具体商品信息
# print(tbodys[-1])


# print(order_id)

# print(product_name)

for tbody in tbodys:
    
    # 获取订单编号
    tbody_class = tbody.xpath('@class').get('') 
    if "split-tbody" in tbody_class:    # 筛选合并订单后续的子订单
        order_id = tbody.xpath('.//tr[@class="tr-th"]/td/span/a/text()').get()
    else:
        order_id = tbody.xpath('.//tr[@class="tr-th"]/td/span[@class="number"]/a/text()').get()

    
    
    # 获取商品名称
    product_name = tbody.xpath('.//tr[@class="tr-bd"]/td/div/div/div/a/text()').get()
    print(f'{order_id}: {product_name}')