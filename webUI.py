import mysql.connector
import gradio as gr
import pandas as pd
import argparse
from src.dataExporter import JDDataExporter
from src.dataPortector import ConfigManager
from src.databaseManager import DatabaseManager
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

    def export(self,
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
        """ 
        按钮绑定操作: 
        
        Return: [ 
            basic_config_warring_update,
            username_input_update,
            data_preview_update,
            storage_button_update,
            storage_mode_update]
        """
        self.chage_configuration(username_input, date_range_input, header_input, exclude_coupon_orders, exclude_privilege_orders, filter_completed_orders, order_id_slider, consignee_name_slider, consignee_address_slider, consignee_phone_number_slider, courier_number_slider)
        # username非空验证
        sign, username_input_update = WebUI.validate_Username(username_input)
        if sign is False:
            return [gr.update(visible=True), username_input_update, gr.update(), gr.update(), gr.update()]
        # dataExporter = JDDataExporter()
        # self.form = dataExporter.fetch_data()

        self.form += [{'order_id': 'UszhDl5ONZkg', 'shop_name': 'NIICAXRMJKa53OD1FFuD', 'product_id': 'ZkbX4579AAdnORuf', 'product_name': 'cTAw3vznpqBW0Cj9UVNJnDWL0mHi66JpRWmuVOyw3wXCRQmUhj5UZDQDbv28hM5f5SHIxmWkmWPE74C06ue64sdYNb1BG7OnnLyQPnJ24hGNPdxCWOCGvUU1eRJmY6pjUgkipvlVWcQCoMGUee5h7KBEKH2duUDEiMA9CfWqsEAsT99FfCdinWeFZBjv9b8zkh1Qk7TpZykmIhbJXCRRwSgW1v6iQ22UTXJ7OcLk1jTO1rTHMC4LyfV8Kzw3PHyxhIccUIaFwtXwFHEMgAxPvBlGIWf2i1Ki4h5iXUp5AAFBS9hDDD7ZZsbn3RjUdNLa3w9NdTTe922jDgHICCczZf6STbV2MK4fMigzzkUfqa69eiSfgP41qv11OEbWcmvpJtSZeEDJdnAuiO8OKJhANSRk41a5aHPbfcYu3WeJNnfLxSDJs0yZyvIJvk845byg2HPp1ipyWghMB261KVX74P1KfjXHwMORZmKsC9qyVWIyMs58w2eO', 'goods_number': 'XLd6Orytp7nbito7auvxxh6dBBNTInXLA0E8mwuxszub63NXc4', 'amount': '60176187.00', 'jingdou': 2822, 'order_time': '2021-07-16 13:27:44', 'order_status': 'delivered', 'courier_services_company': 'UPS', 'courier_number': 'I6RcoOlvLZ7R3hewSA', 'consignee_name': '3rHiPs', 'consignee_address': 'TJntnq5OMCnZVOXIX0LdV05JlB4pjvbJFxRngcTCPc4HqALTnI', 'consignee_phone_number': 'OSFXIl49LJ0', 'order_url': 'laEXr1LKokGZ4i0gFihk0PMJ1V8rfOk9F0Hue51YC31p5TIuPPcqIECDJgEMRj6JmYyqVVtCGZwohlAUUbTT2XwqweZXnHvF8hpiokKZqZSW3mzwRDYS0dlebhTft8qMcEr1so9uibax9GP9G8yDSJpCWxKaYwwwpMknmneLJMXlFqxHY9uSvZkIK1gXsht0ezjtDjecgKcIvWaRwIY1f0oMDVRKyTnGqdfl7wYxI6WaHmytfaimP3sADKJ3u8ZaEVuCnpwqT11vhOshUCoOGw6HG02a7ivk8v1F58u5bkzR'},
{'order_id': '8N85yp1gVlor', 'shop_name': '21rRG2fAfA00JSQ4Nz08', 'product_id': 'yXe0AFWu2SsHl8oo', 'product_name': 'Ijc6qViPOp49UFkgWuuFlA4jGPICxssTkiitDiX0ycaBv4rbJibD5pQmbC00TEZtQqXNyYaPBzZ91qjQUIP9IEo0dV8fDaut9obDSsvd4EK0MBcYXanpUMt0nQiUdr5g00nhoJ3lPZKpMqAwsPEmmqjgKHF5aKVZnYoP3C1t9c9mXTd3wZMUIlIJV3IW8d7VtVTpYxQsfRBhzPLMeHWXencXBx0wsFNX3iB8kFTURTvr0JN9bsvABAzolum65Iw2PmuHVF8fxEq8QRtEaz0e5ZqnNu8Qeh5I5MmNA3NqczuK0e63J71o54rYiUBCmR9ikWNxDh2KRyY2FBWp4p3weQJVftzbcFBv8XuEgyanBakfPS1N9uMfQkskjBAEa4XI5KZZtBRorrhUhgqZHILFdPXAOku56TWIHqIkkuhXs1Ff6S5szbist1gAdmqEoDDVO3WWUZDipKduwh3zXgfhm40NZxXWSeZBw0bxLlna9Uyi0dr9ZUxw', 'goods_number': 'Lr5K5cLjAeBIpYhe13hsOZcI8EWxH2D5ZDhIipbzNN0VSkyMbo', 'amount': '3416472.17', 'jingdou': 5348, 'order_time': '2022-08-04 13:51:15', 'order_status': 'delivered', 'courier_services_company': 'FedEx', 'courier_number': 'mpBxio8hKtiFju011k', 'consignee_name': 'CrN22o', 'consignee_address': 'BdxPHnZXwPA1uiaAnor0ULtZvTDLQpoM2MqL2tPulp7TMnwaeV', 'consignee_phone_number': 'WIHDQRJEooa', 'order_url': 'MjV1BdVKNoFO6cYsMVJLWfVTCaE7cVMeQqcs4deot5hWH1KPyanUVJgPUFynZovfYcHc6iI3ehr6q6KlN10F3Nx2ATPSVligewKf8PdWXXr53bIu4kcOoxs5SpXbKbBrzX3c3bszdfgdBktcda0iIdstR6dsOHsYTGLoygaEvgO9GbbPwfqZnEQC2iMi4HjH2z7z3VF6rGFRqyHkB4TE9YZSSUuuNZ6GDWgIdo9KQnqBQ3LKf5MDdKTLb2OA4uOVTL7OyU4KmvwrvNEEvb2i5T6IwZwiAMhhttncxTh4O2zM'},
{'order_id': 'qX6lA12cQTvn', 'shop_name': 'OOW062cbGxqoGEeO7X45', 'product_id': 'SuzdxovMqvMAKfWb', 'product_name': 'cQhRH0RR79ZKNpLiLcDgaCGk0AFYSRPC4pYpOuuId8mB3GDSUavQJ8AnbnZzH2p5DipslqOuVJCJAuYYi7fF7tj0v6aaSEFBLdEj0jCOS3dQSv1u7bQXHiyZiUtruTaqnykmN0wxaotQCIO8jvMtJVrpNhu5tZe26PMOsqkjgh6QySwFK09A3vzkgd6oyaOcBDOFu77A2kce5PL2MjpKC0xwy6e32Hh5zRlSABsoKj8aGGvWQOzJMh5PhEnUafHiGGlrvPCXAASQRm9X6yT99pRyZy76rXEkpNB98FySkgxHS72kIk8uDbzfLuiqHj5hF1ikf34sIxlgOnw4c19k8sj2CmGXwiLYp4FpRZdTZFhZxSpirY5ptxaRNJrsdk6tCgESziD4RGhtiSt4QmATcoifuL3vdM2YRr2qsGrlFMRFeqHgi6x4e2AjQPQboGPB0jhAf0UKs5FV9G3jZHJQHMd0iodRMyuCVaz2uEIGgZbak8c6ZIk3', 'goods_number': 'TS32pKdIuBT7co92Jerky3CTRwy1rX3oPLIIPOjdYUT460I73d', 'amount': '65178740.07', 'jingdou': 5907, 'order_time': '2020-04-03 21:50:03', 'order_status': 'delivered', 'courier_services_company': 'DHL', 'courier_number': 'eNKYKwMpzxAtfjW3Aw', 'consignee_name': '3yDLAJ', 'consignee_address': 'K4MooDdVkWjukoMxUxpiBx09jzxUcn9UOpnVVSDJHgaLZlCZiz', 'consignee_phone_number': 'neXm1VuAdTk', 'order_url': 'yTDassHtzqsOE8kpJbRQpaXdCNCENqTAY5jDQwFkHMAFVpR1u6QhigkokcyhPJx1QPCBwcOQxOVaLvCs90H53xHlEeAoINq2GRnP60mx6FQJniPy3gSggh4ztAs9Cv79hYxLjUQCstNcf6Y6yRdT4mZwNULjj9IQEJBADEwQmcbWpO0G7JqLBrMsoevxgQJPnUVNafsYUIo6K6V59bgMxv1nXsYztQkMQaImTtddnXNDx0nMkWC8E3nNSzVW6gdrpXQdn1ZOSXrwLXFZhmGI8Ovqn7DLORledxjRa8naTZY2'},
{'order_id': 'W8JlbKWEKHd5', 'shop_name': 'jj8SfW6U2aSFtvVRkr5W', 'product_id': 'w8CNTIO7nJo0rcCr', 'product_name': 'dkHHuYwxAkvyZBKZZTlvyAKBBxEPjlv8lIJagzmn01YnjipHvvuj8mc33t6qVDXbjHc4eLxqiESfimOdz1z492fHNm8PQhlnijWba3TeO1VOZ7ZypwtioIJcZAsH4wvWQQwMU6L4YHkaoRkBzPkYfAqecxQoQhmSivLG3tzIHse2EJnkTGsvaKfTdk0sBsG4TiRCQnqqkwOgm8ujc4r2Y6FO2Af37WzWErYSgztlv98bDRTdd7M9O9WeRzkE2J93EhjZiQBrpN2pYt5BvuSGjfh09uxJfAQz424QSm213OTrmUa3YrAm5r8VGJGac68AhZ8p9zKadOZ9b4kK3cu36TOvC5sRHtYR0BQoVfah3skq39xQ2YeyGRM2Kt3UTO3Zb8BCV0A1ApdNlcbaR4OmZVuGK3SeZ18w8CMPslCxUC9eijdWo478lHQexvzRBB45WTLYlFPNVCO7quWa5wpYjKyg9ZPiRHitXZMu0TyYnkwzch7tRExJ', 'goods_number': 'v7qhdlQVkgPuw9WzHvkQ1iAeSvhyw0BC20QsJ0Gb9hpemAQ1eJ', 'amount': '6784995.48', 'jingdou': 6386, 'order_time': '2020-08-27 09:14:24', 'order_status': 'pending', 'courier_services_company': 'UPS', 'courier_number': 'JeNwkE4yrvfMKT0HKV', 'consignee_name': 'DNyvdG', 'consignee_address': 'wlc3PnTCXMnogrRcSZ1gIt2pBjkDKHNiLRbMm72ax7v2hE2Fdn', 'consignee_phone_number': 's6GQOdyNHga', 'order_url': 'Ya0ITf28VwFzmkmKE6LfUHTNnkcjWILTvpTYMOzGZ4jSDfg1pn31awPSCQd2FzbsrBYaYK2xOPEKYGTDbMp7VlNejZmGsM9zwoi5zya8I32aG047sidjHXNs266MpaEUH8phn5rD5Ee1kkczL0K8lRuTtFvq1ylmwofsP2SukipRD5mMhZzAtuTgKMktdZPczpmqAnGl1mBlu1WEE848h2VO8g5BQ1EqOI8uC2xxt4gT06UvUpzabgpPQhtAUPWn6HzRhkfFA8StKDL1y0rhe6rT5oE1mTkQsyeQrDQuSlPH'},
{'order_id': 'FHlMZyxwiCib', 'shop_name': 'SZ5ybXHbM4CFNYlnfwUL', 'product_id': 'yRSnyQJwYP6hmKJV', 'product_name': '6xSNaQkbw7XMMub2cPrldex4GTFhU2FY6A4eeD1v4tJ07M0oDDuwtxTKv5cwcABNGdYgUQjmwSCzUBtTGNi4MwVlMVSA4raCXuS27iLiscUlz7azfMOvLySyRIqB0a49YcjXU8sjbKyRJkQRXaHX3SMm2Uys4nRJDNaJw4YNLhSrostowok1BpiouoO24RAPa36BoRF6jgkisf6P1ZDfDpjnfVpsNmnnXWAiJm6Z2sFOP86t4DzncMDUAEbUhFEN1wwY5UNoki3RrlKIOqMmOvvDXU3D0CXNI3XMprH3rsVHD0iF4vH8CBMD7KKVsR8S4OVwOaytJPRdSJlmK9OLIc0DRTJM52V9b2QIAlLA2DbovUWj5Ki5sS4zvKDl97SZpYO7x15TZDUKyLTeEC1clWSmdz5ME27ebXw3vi9DpSEQtA28LOYKbAi1CUVrIL0yiVL5RXKEuwSZGzP3jLbd3ZC1ZWFOV95X3Yybhpa0i5NSxk7iUjGd', 'goods_number': 'IK1uIaJz0VOUyFMcdWGS2sdc8vW0xGd2maLwA4KUlMY84gA7dP', 'amount': '93902542.49', 'jingdou': 3228, 'order_time': '2020-09-25 02:53:18', 'order_status': 'cancelled', 'courier_services_company': 'DHL', 'courier_number': 'cS9qhiFQc7weSTIA9V', 'consignee_name': 'HZ3GWf', 'consignee_address': 'xY0mkO5NFGiYgs8iaOza4AWn9RRCcZKQzlUBMyB0wz5RHD3jGI', 'consignee_phone_number': 'LEHHq7Gefuw', 'order_url': 'auDSy3VDzrkBpmpnQjzQfoaJVBXL2YuYdNy3vXnRixDV0njDaWpOdHOQj6hk1G7YtdmfazT5OjNQpOH2GoEKep72sMQf58iR32x3HtRR59NXLbwCTf0HbcVi9LBk03bZ4RMjjeraAehe9x6dGr4dHUZOswpn4eFbhR0xaZ6QLaiWQKqRu6sf9mXofMOuXY4HWQhgxP2JiIwzeg7fewulQPThhsXG9t1XYGgCSOfFyfVo5CCqpo3sgPjUOgenKGopPIKMg1vlgyksGv85BDY1kDCxyv9kikyhJkFhfwI6wu8d'},
{'order_id': 'tRxBzC23m18o', 'shop_name': 'W7pWhFH94Hbm9Xfmkfd0', 'product_id': 'cSPlh5hihXlKSNqR', 'product_name': '9nWVMQIvHfSmsxieNEAYBCCnyRXHi27yPBBzIthfkygelO6Ts9wjlFVj7Ze3Ib6yfBOuSs4gpE1H6XtAQ85X5nH6e2uVxWB5K4s0OeGGpjd2ny8cBFFZhJ3B7dSdQxGIFzQ2UbVTRlMoTU8cMseL0IuXOstc7Hz7muUk2JylARSMuoVzXZEm5llfznn7r0fP3MHlG1xShvVHbojGUPslitgjmiB9hnyfrvpP62qHbEHmt2CYlkGeq8mbhkolIDUh3CV43QmfOFH9IJ1JvaZ3lrw3ZUouI7CDWXRfjI6QMWaU8InaQZFh13qlq2mCIvkSPSrfKiXCbXBwx8Ta7NuBseT86pTcL2ZO4OcXZ8aqpxKDvM9X4RtI0KLRXwZjnoVz3fxy2MmR8Vu3TRpy8h0KwFOVOMOd13YPDZls3dArI5bjHXfdefdFeZ6xHwckQtNiy31O2Tc0AfkDvQY1kmMRyqbykZEpjTiZdOsOqf1RRHPcl7wXbb1p', 'goods_number': 'hsWECqGq6HcHW4GMwVQdZVCjCzJEHNqIPpl6D6cuqVpLOBZIbi', 'amount': '11424129.01', 'jingdou': 6936, 'order_time': '2022-09-15 02:57:59', 'order_status': 'shipped', 'courier_services_company': 'FedEx', 'courier_number': 'p2G7E0bPGCdVN9AfCZ', 'consignee_name': 'mZ9QHr', 'consignee_address': 'ScZTTRzynFjUw0HIA1w8QoaXuWonm3dqEUKAuOnKoOzedVidzE', 'consignee_phone_number': 'u1fWvah4UOs', 'order_url': 'MjasUSVAPc0pPpnLXikNc11xVJ38nYbCYM7E8HSXA9BdAIVdXAcxI5UO1GxQNgRROWJmcB8y6AvfmGmHGJyYevYvlf4DB2Da0KE6H4haHc5eybB3EOLav9wc3Qej2UoSA1BzlJeqTaqW7ilvd5aH2yeXHKB5vNfSwZaoPkitl554VypPIOE4sy1ygebGK7fLHoeeKsxUQa9kQYEz2sWsFKh4JwikpyytsS6jMka3ba2wFQtJHS3JhpZBKjsviflx2tczFx6yT3bRb8UvBl1znp17331D4qYPd5hQY0xG6EPr'},
{'order_id': 'ClZa2Nt9pSpF', 'shop_name': 'ri6BHokTiZSjLkZpF24u', 'product_id': 'Lwf4q9fZ326Gvtky', 'product_name': '96E1D6slp2StutTXGTDWxtWaGalndJsEYvS6qnhv98YYGKnEQecYn6vDoQKILW8zkPY5c5UPLEtxXgy7X3UGqEnuEnUtWiqUSYIjr8JGMj7UrwxO5auWxNoJXVGYDCPOZr544t67VAdgn4XAQ7jhTdlIWMHdKMjWVWiuJ2NrheSiw2NzYEegGYpfiIlsoQL05hAVTKETFQAjQ6rdDXYaRhxtAMJ2HzvufEWyhLovo7Xc1luBNEXeJCIYV4iHkFbtMrZHDXTpdaQxC4VwWV4DSC7mW5ZKDtHQG1Ve5VX90fghVVLPvVCH6p46JFrlgeJwFRvQZqiXCF7cLiyx7KLRV3OO0UEtNHfg52MSxDbp8L44fDPK5ZZ3S1JIfcwxuqgZ0uqv1wdZY41YH7LO9qPJcT87UN4Eu5Z4dAT9veCvdKlpo4saNHwI2bFf3FGs9MIyW8AXu4z1ABH3jZtApezEDLMSpxE7aSzvjj3FkYcQRY4CnvHWxBOq', 'goods_number': 'yYQ8INgbymSjIeyqRPNl1T3DPnm18i38o90rluhhiRZ9Z1XgNs', 'amount': '52427982.86', 'jingdou': 4037, 'order_time': '2020-08-27 17:39:46', 'order_status': 'delivered', 'courier_services_company': 'USPS', 'courier_number': '8eusi5dT4LGw0DmEIq', 'consignee_name': 'BqMSUb', 'consignee_address': '1Tiqk385HhGuBzlSdT4bkmZcYZXWBNgt0dN02XmCDUJecyyuYp', 'consignee_phone_number': '0GPqjo9hIfC', 'order_url': 'ME5jab1UnoN72X9GkVsvMnPh03a91AtA473zPOl861tn5ddq8ZnUHLuprt9T8ptg4JUV5BGHsrd9MchU1szturltsguabdV1NChj8iAR2Wxzv5QECXFk42NKoKgqygHTqGEl77ZL75TRYBMUtompd3w2XMBL9x8W7EGPUUfigMd43vV7UkxBuxUPjrMUcbbjFjhGLwZxdedHfkuVOkEXqrgFKQotTK02tmdv8FFWSREK2KlFO8h8ol1rMOKQtt37rMzD88TDO3N3xjdow1P9AzWDACkGhipBqoM1CvC43dLV'},
{'order_id': 'wJiAYx303I9y', 'shop_name': 'bsLfDW46r0md29tlIJ6z', 'product_id': 'UHFPYgxgnQ3i5sJh', 'product_name': 'BksGPNJuvmbFPCeBgjKCmJikjlhqgWpb5je0kLG81BRR63wy2ZDo3Iv17llbq56V5jKEEyb3jHK2L0tXvURyLd0Wjp9blCS8M4YBdV8uqwXhuo2Dpf5ZJEDa1AAfX0KgZQa9LoSP1A6fe0Rq2ReykumvvNG5c1NoFrtkbUgyRU2p3iCNQoAwAMeTrHIaAgOtluTLKlj5vtiJ3dYqAB4v8wh6tohWXJbweQY9SYNpMKkYNGFEvqnMkEaSQOrgRJRuvpAyOBK0w0qZ7UoWy2lyeDiZRjVnV33G1ZSL4SgzVl6LygIKCCos4FANy05jk6PpPl8gRkUshJrencE1GbG9qP2lgvencbu457jR33ZQtBBNpkjpF3KRYf6o27YGiua01OCNoVju2hxUObmOexiHXef8HF6EZd9wvjGSv4bDEpWkYPoygFWf00V22ao5sk6LCoputerbJEI9jdlYWU7P6JKMcGSgLmGmcP5ZRlIpdSciIWR3t6RZ', 'goods_number': 'z6P4napsva0YJIcBOu39q4agU5b9UUHDVmuV0GQrWaelvaxC5J', 'amount': '15220549.07', 'jingdou': 6592, 'order_time': '2023-07-29 10:03:38', 'order_status': 'pending', 'courier_services_company': 'DHL', 'courier_number': 'kQB7O6mwgjel84QSmX', 'consignee_name': 'x9gAy7', 'consignee_address': 'e59rwsbfv6dhRtdNXnM0IbNQy7T7OPLuRsKhuykjDUTVqZJ4q1', 'consignee_phone_number': 'dZ3BeyBKGKV', 'order_url': '91v9kNw5izDcyIZE8f0tIMF1VB40hJ8ISaMWjnyC439bdWPy3fhHJvudWgPfomTHq1y998o2ZY559UGih7gaAN2cahpKOf4Mt3MOvcPpOhM1URN0pZBVg4O0nkfPSwZXlGTo8NPsSXW75usXGAayeq4nrs06ABqhbejlF0xkH8SCxeJapQx3EPAqtoZlXaP3BgMWckFgdWwS2M4CaMImu3wzDoOQTX64pil3l53YIDrh7JncIKzleXCeS2lDiBsS1G2gWYXcpdGfRNFz31Rb3Tb679Qk561C3nf1oHimNJin'},
{'order_id': 'kkHQz3jVNYqB', 'shop_name': 'b6BDv65V9oTuTfBHiH1g', 'product_id': '9D3vET2Zt742APB0', 'product_name': 'zV9M7SAUdpPb0l9Ps7HkvU5WffUg6ERq5bgePxm8w6P7nv9bJ4NIppgu68Lp89SWFQDuC9t3Nq0jBSj3cctKitS5UPytnnjTIRu9IMoNC9FMs8CAK1YE7cbk7SPmufBBlkPK4S4YZUQ22pJGBTcwPiQuxAOFZgKtoLhv6QhEcP0mR85bdLWL3qF1rsh4bXU0KahHxmMxTYDzUPfkcHlWILCPQGIdVRsV0uvLpqjOcHuXAUXy6IJnBmnMYp9zbQmJ0KstvazkjQ87MaIXcjXpyUK9QfUXVMOzDZ2KNothuhdqNsgsiRYgoTnVeMubwOVvDI5XcPzUzAm3eXAGEdTx8YHfEBHV54NpwTbSUeoflZuaAu3R2516QInnbh0Nk49jcv8jKh4cqpuxA156A2Wpi8m7M2lVDPUrzCk9ibbWBREMz6UYr0Mwx0LeU3ueJBMXNkejgbabY055TOnzGyyPee94SAT5O8yRpjmsSH0YBDxTMKXhLD5S', 'goods_number': '0rGd0PqqqUSZJ2bqdoHkhUydopXneSsYrprhBP0my389tqavJL', 'amount': '70873124.81', 'jingdou': 3169, 'order_time': '2023-11-01 01:23:20', 'order_status': 'cancelled', 'courier_services_company': 'USPS', 'courier_number': 'qoInoZU6X6cYe9V0u9', 'consignee_name': 'i4YqBi', 'consignee_address': 'rcxi7wwFuNIQzEwQ4J41vAoDzCn8sJ1yemhluCRpF9tFyAicMN', 'consignee_phone_number': 'jeSz0Ee7XEF', 'order_url': 'OIbEJDyGN6KPtAYT5kCHed5sdExrn8Zy4H3t0s1h7dcDJQTyTEITNVxLpWj9Bc74lOHieBdAgsUTFReUTvADHEB70C7copW3DrVmtcLikHHXR62JnhWVyY7CCJ7dNx6tFcLW4VsnrCHb84dEru8LKXiMPdpdfFzIo6yzL3ADTLJuEkshimDqKOytSiHThtVU4e2CYTRXwvdt3vl7VMlXnDApyXf2euKaO7PKgCCXLkc6YoYf5oGyv14FCAgbfkQNb9XjaMVAUFVJDqFgu3XcZtnIOYRCAUsBhJQ1tC6AmScb'},
{'order_id': 'Dko9sCHbJfZP', 'shop_name': 'zDGeHWEA77vTYztdqZCn', 'product_id': 'snNb8aJQOKwjSbw1', 'product_name': 'ISc7MEfTLgWvW1W0i5pZfJr4Up9CS3nKdgZHADHR2CwgRp44wYJu2sGsvoOyKCqZLC1oL6M2BvUqRTRN2GdesF8m61sN5vGSrZp5vou6QkxvM1D6YdURMKYilvF1olTBcmr7OKy8BDxNqOwTftiFI5H3P9XfgCUXoN5bsWFwvaIXiKwbY0qhtp9jsRbaqqHT8UWigjFcQZvDnHOLcEIKeytHGXaL6BIDRSBs2OM5zNolpweQC2lUcVsrLZgFo3FwFrd0lUmvZDLmLh10f6EJyih0ATquGw55KEgz8z6UuUJ3xaitmNOFbZDWwLN76qXb5FoJQYlUrY5EIGN7b0cCH0DTgjm7S1tlIlLXf4EK2tHDWgYbzitecChGAoYdeOrjIJds8E4XsP6IjwjCRT47W1gXfSW6brFMYhmUvzQjHZ0ImcYN2qDntspPbUZgApuWcbGPL9RQVtoSJB2kCuQ2VARZlg114Y4lUyjneaENH0J3qNRUKVxE', 'goods_number': 'vCPEFVAu9b9LzUXPg7lti2hM81t4YmOUeqB361tgUFpZclKLb7', 'amount': '63136256.40', 'jingdou': 1341, 'order_time': '2021-01-27 23:26:37', 'order_status': 'shipped', 'courier_services_company': 'FedEx', 'courier_number': '2fLzzoQmZf2eY8nosY', 'consignee_name': 'jHdhlU', 'consignee_address': 'kPJ90vIvREYQ6Vk59i2TsS8jhaIjms2inF0JWS8dETVakEpp5A', 'consignee_phone_number': 'BRAZ4GQHzDU', 'order_url': 'cIP6skOMER5AsnmHEGSzCV4c1EAhgliuhCDNcdWBPVelBHlL1svHnIejzZD2G3SzpVRayrdAY5H1z7L8XFW2UBjv6aVQG1Dl8vKOG6716s6KaktuM3rlGT3HNVJPhlEwzCAn1ufvRYJYKSutmgj8UtJcRXAmdnQW7j5uB9pGwvnAwNnyUPqQZoFVUuu4ZRY6tDUD3cK1cCkhRBJ4bLZZnVQgJDuzN3IjM24KErUEcWPD22BVFska0P8iczCYukZmkiRhjKaGaMgUpFJ737BjGiRNVezR0BRkBRVtbIDEn11H'}]
        form_preview = pd.DataFrame(self.form).drop(columns=["order_url"], inplace=False, errors='ignore')
        return [gr.update(visible=False), username_input_update, gr.update(value=form_preview, visible=True), 
            gr.update(visible=True),  gr.update(visible=True)]
    
    def storage(self,
            storage_mode, 
            header_input, 
            excel_file_path,
            host_input,
            user_input,
            password_input,
            database_input,
            table_name_input
        ):
        """ 
        按钮绑定操作: 
        
        Return: [
            storage_config_warring_update,
            database_input_update,
            table_name_input_update
        ]
        """
        if storage_mode == 'excel':
            self.form.save_to_excel([field.strip() for field in header_input.split(",")], excel_file_path)
        elif storage_mode == 'mysql':
            sign, database_input_update = WebUI.validate_Database(database_input)
            if sign is False:
                return [gr.update(visible=True), database_input_update, gr.update()]
            mysql_user_info = {
                "host": host_input,
                "user": user_input,
                "password" :password_input,
                "database": database_input,
            }
            try:
                self.form.save_to_mysql([field.strip() for field in header_input.split(",")], table_name_input, **mysql_user_info)
            except AttributeError:
                return [gr.update(visible=True), gr.update(value="Database not exist ! | 数据库不存在 !", interactive=True, elem_classes="warning"), gr.update()]
            except mysql.connector.errors.ProgrammingError:
                return [gr.update(visible=True), gr.update(elem_classes="normal"), gr.update(value="The table name is invalid ! | 表名不合法 !", elem_classes="warning")]  
        return [gr.update(visible=False), gr.update(elem_classes="normal"), gr.update(elem_classes="normal")]
    
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
        self.configManager.save_config(config)
    
    @staticmethod
    def validate_Username(username):
        """ 检查 Username 是否填入 """
        warning = "Username cannot be empty ! 该项不能为空 !"
        if not username or username == warning:
            return [False, gr.update(value=warning, interactive=True, elem_classes="warning")]
        return [True, gr.update(value=username, interactive=True, elem_classes="normal")]
    
    @staticmethod
    def validate_Database(database):
        """ 检查 Database 是否填入 """
        warning = "Database cannot be empty ! | 该项不能为空 !"
        if not database or database == warning:
            return [False, gr.update(value=warning, interactive=True, elem_classes="warning")]
        return [True, gr.update(value=database, interactive=True, elem_classes="normal")]
    
    # @staticmethod
    # def validate_Table_Name(database):
    #     """ 检查 Table Name 是否合法 """
    #     pass
    
    def build(self):
        with gr.Blocks(theme=gr.themes.Soft(), fill_height=True) as demo:
            gr.Markdown("# JD-Order-Data-Exporter")
            gr.Markdown(
                """
                <div style="display: inline-block;">
                    <a href="https://gitee.com/goodnameisfordoggy/jd-pers-order-exporter" style="text-decoration: none; color: white;">
                        <div style="display: inline-block; padding: 2px 5px; background-color: #4CAF50; border-radius: 5px;">
                            <b>[Gitee]</b> 🚀
                        </div>
                    </a>
                    <a href="https://github.com/Goodnameisfordoggy/JD-PersOrderExporter" style="text-decoration: none; color: white;">
                        <div style="display: inline-block; padding: 2px 5px; background-color: #007bff; border-radius: 5px;">
                            <b>[Github]</b> 🚀
                        </div>
                    </a>
                </div>
                """)
            with gr.Tabs():
                with gr.Tab(label="Basic config(基础配置)"):
                    with gr.Column():
                        gr.HTML(custom_css)
                        username_input = gr.Textbox(label="User name(账号昵称)", lines=1, placeholder="Please input user name...", elem_classes = "normal")
                        date_range_input = gr.Textbox(label="Date range(日期跨度)", lines=1, placeholder="Please input date range...", value="近三个月订单")
                        header_input = gr.Textbox(
                            label="Header(需要的信息)", lines=1, 
                            placeholder="Please input output header...", 
                            value="order_id, shop_name, product_id, product_name, goods_number, amount, jingdou, order_time, order_status, courier_services_company, courier_number, consignee_name, consignee_address, consignee_phone_number"
                        )     
                with gr.Tab(label="Filter Config(筛选器配置)"):       
                    with gr.Column():
                        exclude_coupon_orders = gr.Checkbox(label="Remove coupon (package) orders | 去除券(包)类订单", value=False)
                        exclude_privilege_orders = gr.Checkbox(label="Remove equity orders | 去除权益类订单", value=False)
                        filter_completed_orders = gr.Checkbox(label="Filter completed orders | 筛选已完成订单", value=True)
                with gr.Tab(label="Masking Intensity(覆盖强度)"): 
                    gr.Markdown("Intensity of desensitization (coverage) at data output | 数据输出时的脱敏(覆盖)强度")
                    with gr.Row():
                        # 滑块组件
                        order_id_slider = gr.Slider(label="Order ID(订单号)", minimum=0, maximum=2, step=1, value=0, interactive=True)
                        consignee_name_slider = gr.Slider(label="Consignee Name(收件人)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                        consignee_address_slider = gr.Slider(label="Consignee Address(收货地址)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                        consignee_phone_number_slider = gr.Slider(label="Consignee Phone Number(联系方式)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                        courier_number_slider = gr.Slider(label="Courier Number(物流单号)", minimum=0, maximum=2, step=1, value=2, interactive=True)
                with gr.Tab(label="Storage config(储存配置)"):
                    with gr.Column():
                        with gr.Tabs():
                            with gr.Tab(label="excel"):
                                excel_file_path = gr.Textbox(label="Excel file output path(Excel文件输出路径)", lines=1, placeholder="please input output path or we will use defult one...")
                            with gr.Tab(label="mysql"):
                                host_input = gr.Textbox(label="Host", lines=1, placeholder="Please input host...", value="localhost", interactive= True)
                                user_input = gr.Textbox(label="User", lines=1, placeholder="Please input user...", value="root", interactive= True)
                                password_input = gr.Textbox(label="Password", lines=1, placeholder="Please input your password...", value="root", interactive= True)
                                database_input = gr.Textbox(label="Database", lines=1, placeholder="Please input your database...", value="", interactive= True)
                                table_name_input = gr.Textbox(label="Table Name", lines=1, placeholder="Please input your table name or we will use defult one...", value="", interactive= True)
            with gr.Column():
                export_button = gr.Button("Start exporting(开始导出)")
                basic_config_warring = gr.Markdown('<span style="color: red; font-size: larger;"> There are some problems with the Basic config! | 基础配置有一些问题! </span>', visible=False)
                data_preview = gr.DataFrame(visible=False)
                with gr.Column():
                    with gr.Row():
                        storage_button = gr.Button("storage(储存)", visible=False)
                        # 创建下拉列表组件
                        storage_mode = gr.Dropdown(
                            label="Select an mode(选择一种储存方式)",
                            choices=["excel", "mysql"],
                            value="excel",  # 设置默认值
                            visible=False,
                            interactive=True
                        )
                    with gr.Row():
                        storage_config_warring = gr.Markdown('<span style="color: red; font-size: larger;"> There are some problems with the Storage config! | 存储配置有一些问题! </span>', visible=False)

                export_button.click(
                    self.export, 
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
                    outputs=[basic_config_warring, username_input, data_preview, storage_button, storage_mode]
                )
                storage_button.click(
                    self.storage, 
                    inputs=[
                        storage_mode, 
                        header_input, 
                        excel_file_path,
                        host_input,
                        user_input,
                        password_input,
                        database_input,
                        table_name_input],
                    outputs=[storage_config_warring, database_input, table_name_input]
                )

            parser = argparse.ArgumentParser(description='JD-PersOrderExporter demo Launch')
            parser.add_argument('--server_name', type=str, default='0.0.0.0', help='Server name')
            parser.add_argument('--server_port', type=int, default=8888, help='Server port')
            args = parser.parse_args()

            demo.launch(inbrowser=True, server_name=args.server_name, server_port=args.server_port, share=False)


if __name__ == "__main__":
    webui = WebUI()
    webui.build()