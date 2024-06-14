import gradio as gr
import pandas as pd
import argparse
from src.dataExporter import JDDataExporter
from src.dataPortector import ConfigManager
from src.data_type.Form import Form
from config.log_config import configure_logging
configure_logging()

custom_css = """
<style>
    .warning textarea {
        color: red !important;  /* 警告文本颜色 */
    }
    .normal textarea {
        color: black !important;  /* 正常文本颜色 */
    }
</style>
"""

class WebUI():
    
    def __init__(self) -> None:
        self.configManager = ConfigManager()
        self.form = Form()

    def chage_configuration(
        self,
        username_input,
        date_range_input,
        header_input,
        exclude_coupon_orders, 
        exclude_privilege_orders, 
        filter_completed_orders,
        order_id_slider,
        consignee_name_slider,
        consignee_address_slider,
        consignee_phone_number_slider,
        courier_number_slider
        
        ):
        config = {
        "user_name": username_input,
        "date_range": date_range_input,
        "header": [field.strip() for field in header_input.split(",")],
        "filter_config": {
            "去除券(包)类订单": exclude_coupon_orders,
            "去除权益类订单": exclude_privilege_orders,
            "筛选已完成订单": filter_completed_orders,
            "自定义筛选": {
                "header_item": "",
                "keyword": []
            }
        },
        "masking_intensity": {
            "order_id": order_id_slider,
            "consignee_name": consignee_name_slider,
            "consignee_address": consignee_address_slider,
            "consignee_phone_number": consignee_phone_number_slider,
            "courier_number": courier_number_slider
        },
        "export_mode": "excel"
        }
        # username非空验证
        sign, username_input_updata = WebUI.validate_username(username_input)
        if not sign:
            return username_input_updata, gr.update(), gr.update()
        
        self.configManager.save_config(config)
        # dataExporter = JDDataExporter()
        # self.form = dataExporter.fetch_data()

        self.form = [{'order_id': 'UszhDl5ONZkg', 'shop_name': 'NIICAXRMJKa53OD1FFuD', 'product_id': 'ZkbX4579AAdnORuf', 'product_name': 'cTAw3vznpqBW0Cj9UVNJnDWL0mHi66JpRWmuVOyw3wXCRQmUhj5UZDQDbv28hM5f5SHIxmWkmWPE74C06ue64sdYNb1BG7OnnLyQPnJ24hGNPdxCWOCGvUU1eRJmY6pjUgkipvlVWcQCoMGUee5h7KBEKH2duUDEiMA9CfWqsEAsT99FfCdinWeFZBjv9b8zkh1Qk7TpZykmIhbJXCRRwSgW1v6iQ22UTXJ7OcLk1jTO1rTHMC4LyfV8Kzw3PHyxhIccUIaFwtXwFHEMgAxPvBlGIWf2i1Ki4h5iXUp5AAFBS9hDDD7ZZsbn3RjUdNLa3w9NdTTe922jDgHICCczZf6STbV2MK4fMigzzkUfqa69eiSfgP41qv11OEbWcmvpJtSZeEDJdnAuiO8OKJhANSRk41a5aHPbfcYu3WeJNnfLxSDJs0yZyvIJvk845byg2HPp1ipyWghMB261KVX74P1KfjXHwMORZmKsC9qyVWIyMs58w2eO', 'goods_number': 'XLd6Orytp7nbito7auvxxh6dBBNTInXLA0E8mwuxszub63NXc4', 'amount': '60176187.00', 'jingdou': 2822, 'order_time': '2021-07-16 13:27:44', 'order_status': 'delivered', 'courier_services_company': 'UPS', 'courier_number': 'I6RcoOlvLZ7R3hewSA', 'consignee_name': '3rHiPs', 'consignee_address': 'TJntnq5OMCnZVOXIX0LdV05JlB4pjvbJFxRngcTCPc4HqALTnI', 'consignee_phone_number': 'OSFXIl49LJ0', 'order_url': 'laEXr1LKokGZ4i0gFihk0PMJ1V8rfOk9F0Hue51YC31p5TIuPPcqIECDJgEMRj6JmYyqVVtCGZwohlAUUbTT2XwqweZXnHvF8hpiokKZqZSW3mzwRDYS0dlebhTft8qMcEr1so9uibax9GP9G8yDSJpCWxKaYwwwpMknmneLJMXlFqxHY9uSvZkIK1gXsht0ezjtDjecgKcIvWaRwIY1f0oMDVRKyTnGqdfl7wYxI6WaHmytfaimP3sADKJ3u8ZaEVuCnpwqT11vhOshUCoOGw6HG02a7ivk8v1F58u5bkzR'},
                    {'order_id': '8N85yp1gVlor', 'shop_name': '21rRG2fAfA00JSQ4Nz08', 'product_id': 'yXe0AFWu2SsHl8oo', 'product_name': 'Ijc6qViPOp49UFkgWuuFlA4jGPICxssTkiitDiX0ycaBv4rbJibD5pQmbC00TEZtQqXNyYaPBzZ91qjQUIP9IEo0dV8fDaut9obDSsvd4EK0MBcYXanpUMt0nQiUdr5g00nhoJ3lPZKpMqAwsPEmmqjgKHF5aKVZnYoP3C1t9c9mXTd3wZMUIlIJV3IW8d7VtVTpYxQsfRBhzPLMeHWXencXBx0wsFNX3iB8kFTURTvr0JN9bsvABAzolum65Iw2PmuHVF8fxEq8QRtEaz0e5ZqnNu8Qeh5I5MmNA3NqczuK0e63J71o54rYiUBCmR9ikWNxDh2KRyY2FBWp4p3weQJVftzbcFBv8XuEgyanBakfPS1N9uMfQkskjBAEa4XI5KZZtBRorrhUhgqZHILFdPXAOku56TWIHqIkkuhXs1Ff6S5szbist1gAdmqEoDDVO3WWUZDipKduwh3zXgfhm40NZxXWSeZBw0bxLlna9Uyi0dr9ZUxw', 'goods_number': 'Lr5K5cLjAeBIpYhe13hsOZcI8EWxH2D5ZDhIipbzNN0VSkyMbo', 'amount': '3416472.17', 'jingdou': 5348, 'order_time': '2022-08-04 13:51:15', 'order_status': 'delivered', 'courier_services_company': 'FedEx', 'courier_number': 'mpBxio8hKtiFju011k', 'consignee_name': 'CrN22o', 'consignee_address': 'BdxPHnZXwPA1uiaAnor0ULtZvTDLQpoM2MqL2tPulp7TMnwaeV', 'consignee_phone_number': 'WIHDQRJEooa', 'order_url': 'MjV1BdVKNoFO6cYsMVJLWfVTCaE7cVMeQqcs4deot5hWH1KPyanUVJgPUFynZovfYcHc6iI3ehr6q6KlN10F3Nx2ATPSVligewKf8PdWXXr53bIu4kcOoxs5SpXbKbBrzX3c3bszdfgdBktcda0iIdstR6dsOHsYTGLoygaEvgO9GbbPwfqZnEQC2iMi4HjH2z7z3VF6rGFRqyHkB4TE9YZSSUuuNZ6GDWgIdo9KQnqBQ3LKf5MDdKTLb2OA4uOVTL7OyU4KmvwrvNEEvb2i5T6IwZwiAMhhttncxTh4O2zM'}]
        form_preview = pd.DataFrame(self.form).drop(columns=["order_url"], inplace=True, errors='ignore')
        
        username_input_updata = gr.update(elem_classes="normal")
        data_preview_updata = form_preview
        storage_button_updata = gr.update(visible=True)
        return username_input_updata, data_preview_updata, storage_button_updata
    
    @staticmethod
    def validate_username(username):
        """ 检查Username是否填入 """
        if not username or username == "Name cannot be empty!":
            return False, gr.update(value="Name cannot be empty!", interactive=True, elem_classes="warning")
        return True, gr.update(value=username, interactive=True, elem_classes="normal")

    def build(self):
        with gr.Blocks(theme=gr.themes.Soft(), fill_height=True) as demo:
            gr.Markdown("# JD-Order-Data-Exporter")
            gr.Markdown(
                """
                <div style="display: inline-block;">
                    <a href="https://gitee.com/goodnameisfordoggy/jd-pers-order-exporter" style="text-decoration: none; color: white;">
                        <div style="display: inline-block; padding: 2px 5px; background-color: #4CAF50; border-radius: 5px;">
                            <b>[Gitee]</b> https://gitee.com/goodnameisfordoggy/jd-pers-order-exporter
                        </div>
                    </a>
                    <a href="https://github.com/Goodnameisfordoggy/JD-PersOrderExporter" style="text-decoration: none; color: white;">
                        <div style="display: inline-block; padding: 2px 5px; background-color: #007bff; border-radius: 5px;">
                            <b>[Github]</b> https://github.com/Goodnameisfordoggy/JD-PersOrderExporter
                        </div>
                    </a>
                </div>
                """)
            with gr.Tabs():
                with gr.Tab(label="Basic config"):
                    with gr.Column():
                        gr.HTML(custom_css)
                        username_input = gr.Textbox(label="(账号昵称)User name", lines=1, placeholder="Please input user name...", elem_classes = "normal")
                        date_range_input = gr.Textbox(label="(日期跨度)Date range", lines=1, placeholder="Please input date range...", value="近三个月订单")
                        header_input = gr.Textbox(
                            label="(需要的信息)Header", lines=1, 
                            placeholder="Please input output header...", 
                            value="order_id, shop_name, product_id, product_name, goods_number, amount, jingdou, order_time, order_status, courier_services_company, courier_number, consignee_name, consignee_address, consignee_phone_number"
                        )     
                with gr.Tab(label="Filter Config"):       
                    with gr.Column():
                        exclude_coupon_orders = gr.Checkbox(label="去除券(包)类订单 | Remove coupon (package) orders", value=False)
                        exclude_privilege_orders = gr.Checkbox(label="去除权益类订单 | Remove equity orders", value=False)
                        filter_completed_orders = gr.Checkbox(label="筛选已完成订单 | Filter completed orders", value=True)
                with gr.Tab(label="Masking Intensity"): 
                    gr.Markdown("数据输出时的脱敏(覆盖)强度 | Intensity of desensitization (coverage) at data output")
                    with gr.Row():
                        # 滑块组件
                        order_id_slider = gr.Slider(label="订单号\n(Order ID)", minimum=0, maximum=2, step=1, value=0, interactive=True)
                        consignee_name_slider = gr.Slider(label="收件人(Consignee Name)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                        consignee_address_slider = gr.Slider(label="收货地址(Consignee Address)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                        consignee_phone_number_slider = gr.Slider(label="联系方式(Consignee Phone Number)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                        courier_number_slider = gr.Slider(label="物流单号(Courier Number)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                with gr.Tab(label="Storage config"):
                    with gr.Column():
                        # 创建下拉列表组件
                        storage_mode = gr.Dropdown(
                            label="Select an mode",
                            choices=["excel", "mysql"],
                            value="excel",  # 设置默认值
                            interactive=False
                        )
                        with gr.Tabs():
                            with gr.Tab(label="excel"):
                                excel_file_path = gr.Textbox(label="Excel文件输出路径", lines=1, placeholder="Please input output path...")
                            with gr.Tab(label="mysql"):
                                host_input = gr.Textbox(label="Host", lines=1, placeholder="Please input host...", value="localhost", interactive= True)
                                user_input = gr.Textbox(label="User", lines=1, placeholder="Please input user...", value="root", interactive= True)
                                password_input = gr.Textbox(label="Password", lines=1, placeholder="Please input your password...", value="root", interactive= True)
                                database_input = gr.Textbox(label="Database", lines=1, placeholder="Please input your database...", value="", interactive= True)
            with gr.Column():
                export_button = gr.Button("Start exporting")
                data_preview = gr.DataFrame()
                
                with gr.Row():
                    storage_button = gr.Button("storage", visible=False)
                    storage_button.click()

                export_button.click(
                    self.chage_configuration, 
                    inputs=[username_input,
                        date_range_input,
                        header_input,
                        exclude_coupon_orders, 
                        exclude_privilege_orders, 
                        filter_completed_orders,
                        order_id_slider,
                        consignee_name_slider,
                        consignee_address_slider,
                        consignee_phone_number_slider,
                        courier_number_slider], 
                    outputs=[username_input, data_preview, storage_button]
                )
            parser = argparse.ArgumentParser(description='JD-PersOrderExporter demo Launch')
            parser.add_argument('--server_name', type=str, default='0.0.0.0', help='Server name')
            parser.add_argument('--server_port', type=int, default=8888, help='Server port')
            args = parser.parse_args()

            demo.launch(inbrowser=True, server_name=args.server_name, server_port=args.server_port, share=False)


if __name__ == "__main__":
    webui = WebUI()
    webui.build()