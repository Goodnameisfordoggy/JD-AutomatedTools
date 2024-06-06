# JD-PersDataExporter
[**ÖÐÎÄ¼òÌå**](./README.md) | [**English**](./README.en.md)

## Space safety claim
1. Any scripts involved in the project `JD_PersDataExporter` published by this warehouse are for testing and study only, prohibited for commercial use, and cannot guarantee its legality, accuracy, completeness and validity. Please make your own judgment according to the situation.

2. All resource files within the project are prohibited from any form of reprinting or publishing by any public account or we media.

3. `Goodnameisfordoggy | huo dong jun | HDJ` is not responsible for any scripting problems, including but not limited to any loss or damage caused by any scripting errors.

4. Any user who indirectly uses the script, including but not limited to the creation of VPS or the dissemination of certain acts in violation of national laws or relevant regulations, `Goodnameisfordoggy | huo dong jun | HDJ` shall not be responsible for any privacy disclosure or other consequences arising therefrom.

5. Do not use any of the contents of the `JD_PersDataExporter` program for commercial or illegal purposes at your own risk.

6. If any unit or individual thinks that the script of the project may be suspected of violating its rights, it shall promptly notify and provide proof of identity and proof of ownership, and we will delete the relevant script after receiving the certification document.

7. This statement should be read carefully by anyone who views this item in any way or by any users of scripts that directly or indirectly use the `JD_PersDataExporter` item. `Goodnameisfordoggy | huo dong jun | HDJ` reserves the right to change or supplement this disclaimer at any time. You are deemed to have accepted this disclaimer once you have used and copied any related scripts or the `JD_PersDataExporter` item.

8. You must completely delete the above content from your device within 24 hours after downloading it.

9. This project complies with the Apache-2.0 License agreement. If there is any conflict between this special notice and the Apache-2.0 License agreement, this special notice shall prevail.

## One-sentence introduction
- The project is a local automated tool for exporting order information for personal accounts on JD.com.


## instructions
Follow these instructions after downloading the unzipped project package
- Open config.json (configuration file)
- Fill in the complete account name in "" after "" user_name" ". This account name is used only for login verification.
- Writes the time grouping of the order to be fetched in [] after `date_range`. Must write full option field! If this parameter is not set, order information of the last three months is obtained by default. \
Example: `["ALL"]` will get all order information in the account; `["2022 order ", "2023 order ", "2016 order "]` will obtain all order information for the three years 2023, 2022, 2016.

| Time groups optional (same as on my order page)|
|---|
|ALL (added)
| Orders in the last three months
| Order within this year
| Order for 2023
| Orders for 2022
| Orders for 2021
| Order for 2020
| Orders for 2019
| Orders for 2018
| Orders for 2017
| Orders for 2016
| Orders for 2015
| Orders for 2014
| Order for 2023
| Orders made before 2014
- In '[]' after 'header', set the type of information you want to get the order. By default, all is obtained. \
Example: '["product_name", "order_id", "amount"]' The generated Excel file has the product name in the first column, the order number in the second column, and the total amount (actual payment) in the third column.

| | is optional. The information type is |
|---|---|
order_id| The order number
product_name| Product name
goods_number| Product quantity
amount| Total amount (paid)
order_time| Order time
order_status| The status of the order
consignee_name| Recipient name
consignee_address| The receiving address
consignee_phone_number| The recipient's contact information (the source is desensitized)
- '"filter_config"' subentry allows you to select the type of filter order, which will eventually affect the output result.
Example: If 'Remove Coupon (package) class order' is set to 'true', then the output order will not contain coupon (package) class order. \
In addition, custom filtering by keyword is also set, where the value of 'header_item' can only be the name of the existing header_item; '"keyword"' Enters one or more keywords to filter. \
Example: If 'header_item' has a value of 'product_name' and 'keyword' has a value of '[' millet', 'effervescent tablets'], then only orders with' millet 'or' effervescent tablets' in the item name will be retained.
- 'masking_intensity' The value of the subterm represents the desensitization intensity of the information. The value is of type int.

| optional | Intensity |
|:---:|:---:|
0| none
1| weak
2| strong

If you need to export to the same file multiple times, ensure that the desensitization intensity is consistent each time (at least order_id).

- The value of "export_mode" is used to set the data export mode.

| optional |
|---|
|excel
|mysql

Select 'mysql' to configure the relevant information in the 'mysql_user.ini' file.

1. Start the tool and use it
- Double-click the exe file and wait until the login page is displayed.
- Login to your Jingdong account, it is recommended to use the scan code login (convenient and quick), other ways are also OK.
- Some accounts may have secondary security verification. Such as: graphic verification, slider verification, mobile phone number verification code again login verification, the first few digits and the last few digits of ID card verification. (Again, all information is used and processed locally, please be assured of security verification)
- Wait for the program to execute without closing the browser window (which can be minimized); The end of the program will automatically close the terminal window, at this time in the exe file directory can find the Excel file containing the order information.

## Environment and dependence
- python version: 3.12.0
- Chrome: indicates the chromedriver corresponding to Chrome
- Some packages are of newer versions, but this does not mean that earlier versions are unavailable.

    |name|versions|
    |:---:|:---:|
    parsel|1.9.1
    selenium|4.21.0
    openpyxl|3.1.2
    pandas|2.2.2
    mysql-connector-python|8.4.0
