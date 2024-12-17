'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-12-17 11:12:00
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\JD-AutomaticEvaluate.py
Description: 

				*		写字楼里写字间，写字间里程序员；
				*		程序人员写程序，又拿程序换酒钱。
				*		酒醒只在网上坐，酒醉还来网下眠；
				*		酒醉酒醒日复日，网上网下年复年。
				*		但愿老死电脑间，不愿鞠躬老板前；
				*		奔驰宝马贵者趣，公交自行程序员。
				*		别人笑我忒疯癫，我笑自己命太贱；
				*		不见满街漂亮妹，哪个归得程序员？    
Copyright (c) 2024 by HDJ, All Rights Reserved. 
'''
import argparse
from src.AutomaticEvaluate import AutomaticEvaluate

class ShowSupportedTableAction(argparse.Action):
    """自定义命令行参数动作，用于显示支持的AI组和模型"""

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        import sys
        # 表格整体缩进两个Tab
        table = """
									Currently supported
		+========================+======================+=======================+
		| Group                  | Model                | Required env variables|
		+========================+======================+=======================+
		| None(default)          | None(default)        | None                  |
		+------------------------+----------------------+-----------------------+			
		| XAI                    | grok-beta            | XAI_API_KEY           |
		|                        | grok-vision-beta     |                       |
		|                        | grok-2-vision-1212   |                       |
		|                        | grok-2-1212     (Rec)|                       |
		+------------------------+----------------------+-----------------------+
		| SparkAI                | Lite            (Rec)| SparkAI_WS_APP_ID     |
		|                        | Pro                  | SparkAI_WS_API_Secret |
		|                        | Pro-128K             | SparkAI_WS_API_KEY    |
		|                        | Max                  |                       |
		|                        | Max-32K              |                       |
		|                        | 4.0-Ultra            |                       |
		+------------------------+----------------------+-----------------------+
"""
        print(table)
        sys.exit(0)  # 显示后退出程序
    
if __name__ == '__main__':
	parser = argparse.ArgumentParser(
        description="https://github.com/Goodnameisfordoggy/JD-AutomatedTools/tree/main/JD-AutomaticEvaluate", 
        prog="JD-AutomaticEvaluate")
    
	parser.add_argument('-v', '--version', action='version', version='%(prog)s version: 2.3.7')
	parser.add_argument('-T', '--supported-table', action=ShowSupportedTableAction, help="show supported AI groups and models")
    
	group1 = parser.add_argument_group(title="限制条件(默认值)")
	group1.add_argument('-md', '--min-descriptions', type=int, default=15, dest="min_descriptions", help="商品已有文案的最少数量(15) | 真实评论文案多余这个数脚本才会正常获取已有文案。")
	group1.add_argument('-mi', '--min-images', type=int, default=15, dest="min_images", help="商品已有图片的最少数量(15) | 真实评论图片多余这个数脚本才会正常获取已有图片。")
	group1.add_argument('-mc', '--min-charcount', type=int, default=60, dest="min_charcount", help="评论文案的最少字数(60) | 在已有评论中随机筛选文案的限制条件，JD:优质评价要求60字以上。")
	
	group2 = parser.add_argument_group(title="自动化设置")
	# 使用 store_true 动作：如果命令行传入 --auto-commit 参数，则 auto_commit 为 True，否则为 False
	group2.add_argument('-scpc', '--select-current-product-close', action='store_true', default=False, dest="select_current_product_close", help="关闭仅查看当前商品 | 启用此设置，在获取已有评论文案与图片时将查看商品所有商品评论信息，关闭可能会导致评论准确性降低")
	group2.add_argument('-acc', '--auto-commit-close', action='store_true', default=False, dest="auto_commit_close", help="关闭自动提交 | 启用此设置，在自动填充完评价页面后将不会自动点击提交按钮")

	group3 = parser.add_argument_group(title="AI设置", description="-g 与 -m 需同时设置;")
	group3.add_argument('-g', '--ai-group', type=str, default=None, dest="ai_group", help="AI模型的组别名称 | 使用AI模型生成评论文案")
	group3.add_argument('-m', '--ai-model', type=str, default=None, dest="ai_model", help="AI模型的名称 | 使用AI模型生成评论文案")
	args = parser.parse_args() # 解析命令行参数

	QwQ = AutomaticEvaluate()
	QwQ.MIN_EXISTING_PRODUCT_DESCRIPTIONS = args.min_descriptions
	QwQ.MIN_EXISTING_PRODUCT_IMAGES = args.min_images
	QwQ.MIN_DESCRIPTION_CHAR_COUNT = args.min_charcount
	QwQ.SELECT_CURRENT_PRODUCT_CLOSE = args.select_current_product_close
	QwQ.AUTO_COMMIT_CLOSE = args.auto_commit_close
	QwQ.CURRENT_AI_GROUP = args.ai_group
	QwQ.CURRENT_AI_MODEL = args.ai_model
	QwQ.exec_()












