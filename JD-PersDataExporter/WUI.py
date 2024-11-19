
import os
import platform
import argparse
import gradio as gr
import pandas as pd

from theme import PremiumBox, GorgeousBlack
from src.Exporter import JDOrderDataExporter
from src.dataPortector import OrderExportConfig


class WebUI():
    def __init__(self) -> None:
        pass

    def construct(self):
        with gr.Blocks(title="JD-OrderDataExporter", theme=PremiumBox(), fill_height=True) as demo:
            gr.Markdown("# JD-Order-Data-Exporter")
            with gr.Row():
                gr.Markdown(
                    """
                    <div style="display: flex; align-items: center;">
                        <a href="https://github.com/Goodnameisfordoggy/JD-PersOrderExporter" style="margin-right: 10px;">
                            <img src="https://img.shields.io/badge/🚀-Github-gree" alt="Github Badge">
                        </a>
                        <a href="https://gitee.com/goodnameisfordoggy/jd-pers-order-exporter">
                            <img src="https://img.shields.io/badge/🚀-Gitee-red" alt="Gitee Badge">
                        </a>
                    </div>
                    """
                )
            with gr.Tabs():
                with gr.Tab(label="基础配置(Basic config)"):
                    with gr.Column():
                        self.data_retrieval_mode_input = gr.Dropdown(
                            label="数据获取模式",
                            info="Data Retrieval Mode (精简模式仅含：订单编号，父订单编号，订单店铺名称，商品编号，商品名称，商品数量，实付金额，订单返豆，下单时间，订单状态，收货人姓名，收货地址，联系方式)",
                            choices= ["精简", "详细"], 
                            value="详细",
                            interactive=True,
                        )
                        self.date_range_input = gr.Dropdown(
                            label="日期跨度",
                            info="Date Range",
                            choices= ["近三个月订单", "今年内订单", "2023年订单", "2022年订单", "2021年订单", "2020年订单", "2019年订单", "2018年订单", "2017年订单", "2016年订单", "2015年订单", "2014年订单", "2014年以前订单"], 
                            value="近三个月订单",
                            interactive=True,
                        )
                        self.status_search_input = gr.Dropdown(
                            label="订单状态",
                            info="Order Status",
                            choices= ["全部状态", "等待付款", "等待收货", "已完成", "已取消"], 
                            value="已完成",
                            interactive=True,
                        )
                        self.high_search_input = gr.Dropdown(
                            label="高级筛选",
                            info="High Search",
                            choices= ["全部类型", "实物商品"],
                            value="全部类型",
                            interactive=True,
                        )
                        self.btn_export = gr.Button("Start exporting(开始导出)", variant="primary")
                with gr.Tab(label="数据导出配置(Storage config)"):
                    with gr.Tab(label="Data(数据)"):
                        with gr.Column():
                            self.header_input = gr.Dropdown(
                                    label="表头",
                                    info="Headers",
                                    choices= ["订单编号", "父订单编号", "店铺名称", "商品编号", "商品名称", "商品数量", "实付金额", "订单返豆", "下单时间", "订单状态", "收货人姓名", "收货地址", "收货人电话"], 
                                    value=["订单编号", "父订单编号", "店铺名称", "商品编号", "商品名称", "商品数量", "实付金额", "订单返豆", "下单时间", "订单状态", "收货人姓名", "收货地址", "收货人电话"],
                                    interactive=True,
                                    multiselect=True
                            )
                            gr.Markdown("数据输出时的脱敏(覆盖)强度 | Intensity of desensitization (coverage) at data output")
                            with gr.Row():
                                # 滑块组件
                                self.order_id_slider = gr.Number(label="订单号", info="Order ID", minimum=0, maximum=2, step=1, value=0, interactive=True)
                                self.consignee_name_slider = gr.Number(label="收件人姓名", info="Consignee Name", minimum=0, maximum=2, step=1, value=2, interactive=True)
                                self.consignee_address_slider = gr.Number(label="收货地址", info="Consignee Address", minimum=0, maximum=2, step=1, value=2, interactive=True)
                                self.consignee_phone_number_slider = gr.Number(label="联系方式", info="Consignee Phone Number", minimum=0, maximum=2, step=1, value=2, interactive=True)
                    with gr.Tab(label="导出到Excel"):
                        with gr.Row():
                            self.excel_file_path_input = gr.File(label="选择已有的Excel文件", file_types=[".xlsx"])
                            with gr.Column():
                                self.excel_file_path_output = gr.Textbox(label="文件名", info="File Name")
                                self.btn_download_excel = gr.DownloadButton(label="下载文件")
                        with gr.Accordion("列宽调节(Col width adjust)", open=False):
                            with gr.Row():
                                self.col_order_id_width =  gr.Slider(label="订单编号", info="Order Id", minimum=5, maximum=120, step=1, value=14, interactive=True)
                                self.col_parent_order_id_width =  gr.Slider(label="父订单编号", info="Parent Order Id", minimum=5, maximum=120, step=1, value=14, interactive=True)
                                self.col_order_shop_name_width =  gr.Slider(label="店铺名称", info="Order Shop Name", minimum=5, maximum=120, step=1, value=20, interactive=True)
                                self.col_actual_payment_amount_width =  gr.Slider(label="实付金额", info="Actual Payment Amount", minimum=5, maximum=120, step=1, value=13, interactive=True)
                            with gr.Row():
                                self.col_product_id_width =  gr.Slider(label="商品编号",  info="Product Id",minimum=5, maximum=120, step=1, value=20, interactive=True)
                                self.col_product_name_width =  gr.Slider(label="商品名称", info="Product Name", minimum=5, maximum=120, step=1, value=39, interactive=True)
                                self.col_goods_number_width =  gr.Slider(label="商品数量", info="Goods Number", minimum=5, maximum=120, step=1, value=8, interactive=True)
                                self.col_product_total_price_width =  gr.Slider(label="商品总价", info="Product Total Price", minimum=5, maximum=120, step=1, value=13, interactive=True)
                            with gr.Row():
                                self.col_order_time_width =  gr.Slider(label="下单时间", info="Order Time", minimum=5, maximum=120, step=1, value=25, interactive=True)
                                self.col_order_status_width =  gr.Slider(label="订单状态", info="Order Status", minimum=5, maximum=120, step=1, value=10, interactive=True)
                                self.col_jingdou_increment_width =  gr.Slider(label="订单返豆", info="Jingdou Increment", minimum=5, maximum=120, step=1, value=8, interactive=True)
                                self.col_jingdou_decrement_width =  gr.Slider(label="订单用豆", info="Jingdou Decrement", minimum=5, maximum=120, step=1, value=8, interactive=True)
                            with gr.Row():
                                self.col_consignee_name_width =  gr.Slider(label="收货人姓名", info="Consignee Name", minimum=5, maximum=120, step=1, value=10, interactive=True)
                                self.col_consignee_address_width =  gr.Slider(label="收货地址", info="Consignee Address", minimum=5, maximum=120, step=1, value=40, interactive=True)
                                self.col_consignee_phone_number_width =  gr.Slider(label="联系方式", info="Consignee Phone Number", minimum=5, maximum=120, step=1, value=12, interactive=True)
                                self.col_courier_services_company_width =  gr.Slider(label="物流公司", info="Courier Services Company", minimum=5, maximum=120, step=1, value=10, interactive=True)
                                self.col_courier_number_width =  gr.Slider(label="快递单号", info="Courier Number", minimum=5, maximum=120, step=1, value=18, interactive=True)

                        
                        # change_header_button = gr.Button("Change header(更改所需数据)", visible=False)
                        self.btn_storage_to_excel = gr.Button("storage(储存)", variant="primary")
            with gr.Column():
                self.frame_data_preview = gr.DataFrame(visible=False)
                                
                            
        return demo

    def connect(self):
        self.btn_export.click(
            self.export, 
            inputs=[
                self.data_retrieval_mode_input,
                    
            ],
            outputs=[
                self.frame_data_preview,
            ]
        )
        self.excel_file_path_inputself.excel_file_path_input.change(self.process_file, inputs=self.excel_file_path_input, outputs=self.excel_file_path_output)

    def update_data_preview(self, header_input):
        """ 
        改变数据预览视图: 
        
        Return: [data_preview_update]
        """
        df = pd.DataFrame(self.form)
        form_preview = df[header_input]

        return gr.update(value=form_preview)
    
    def process_file(self, file):
        # file 是一个包含文件信息的对象
        if file:
            return f"{file.name.split('\\')[-1]}"  # 提取文件名
        else:
            return "未选择文件"
    
    def get_user_input(self, **inputs):
        config = OrderExportConfig()
        config.data_retrieval_mode = inputs.get("data_retrieval_mode")
        
        return config
    
    def export(self, **inputs):
        """
        Returns:
            list:
            - update_data_preview (func)
        """
        config = self.get_user_input(**inputs)
        print(config.data_retrieval_mode)

        return [self.update_data_preview]
        
if __name__ == "__main__":
    webui = WebUI()
    demo = webui.construct()

    parser = argparse.ArgumentParser(description='JD-PersOrderExporter demo Launch')
    parser.add_argument('--server_name', type=str, default='0.0.0.0', help='Server name')
    parser.add_argument('--server_port', type=int, default=8888, help='Server port')
    args = parser.parse_args()

    demo.launch(server_name=args.server_name, server_port=args.server_port, share=False)
