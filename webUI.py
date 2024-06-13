import gradio as gr

def chage_configuration(
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
    print(config)
    return config

# 验证函数：检查输入是否为空
def validate_username(username):
    if not username:
        return "User name is required."
    return None

def main():
    
    with gr.Blocks() as demo:
        gr.Markdown("# JD-Order-Data-Exporter")
        gr.Markdown(
            """
            <div style="display: inline-block;">
                <a href="https://gitee.com/goodnameisfordoggy/jd-pers-order-exporter" style="text-decoration: none; color: white;">
                    <div style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; border-radius: 5px;">
                        <b>[Gitee]</b> https://gitee.com/goodnameisfordoggy/jd-pers-order-exporter
                    </div>
                </a>
                <a href="https://github.com/Goodnameisfordoggy/JD-PersOrderExporter" style="text-decoration: none; color: white;">
                    <div style="display: inline-block; margin-left: 10px; padding: 10px 20px; background-color: #007bff; border-radius: 5px;">
                        <b>[Github]</b> https://github.com/Goodnameisfordoggy/JD-PersOrderExporter
                    </div>
                </a>
            </div>
            """)
        with gr.Tabs():
            with gr.Tab(label="基础配置"):
                with gr.Column():
                    username_input = gr.Textbox(label="User name", lines=1, placeholder="Please input user name...")
                    date_range_input = gr.Textbox(label="Date range", lines=1, placeholder="Please input date range...", value="近三个月订单")
                    header_input = gr.Textbox(
                        label="Header", lines=1, 
                        placeholder="Please input output header...", 
                        value="order_id,shop_name,product_id,product_name,goods_number,amount,jingdou,order_time,order_status,courier_services_company,courier_number,consignee_name,consignee_address,consignee_phone_number,order_url"
                    )     
            with gr.Tab(label="Filter Config"):       
                with gr.Column():
                    exclude_coupon_orders = gr.Checkbox(label="去除券(包)类订单", value=False)
                    exclude_privilege_orders = gr.Checkbox(label="去除权益类订单", value=False)
                    filter_completed_orders = gr.Checkbox(label="筛选已完成订单", value=True)
            with gr.Tab(label="Masking Intensity"): 
                with gr.Row():
                    # 滑块组件
                    order_id_slider = gr.Slider(label="订单号(Order ID)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                    consignee_name_slider = gr.Slider(label="收件人(Consignee Name)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                    consignee_address_slider = gr.Slider(label="收货地址(Consignee Address)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                    consignee_phone_number_slider = gr.Slider(label="联系方式(Consignee Phone Number)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                    courier_number_slider = gr.Slider(label="物流单号(Courier Number)", minimum=0, maximum=2, step=1, value=2, interactive=True)
        with gr.Column():
            export_button = gr.Button("Start exporting")
            config_output = gr.JSON()
            export_button.click(
                chage_configuration, 
                inputs=[username_input,
                    date_range_input,
                    header_input,
                    exclude_coupon_orders, 
                    exclude_privilege_orders, 
                    filter_completed_orders], 
                outputs=config_output
            )
            



        demo.launch(inbrowser=True)


if __name__ == "__main__":
    main()