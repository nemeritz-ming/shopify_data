import requests
import time
from urllib.parse import urlparse
from datetime import datetime, timedelta
import datetime as dt
import pytz
import chat_bot
import json


def find_update_failed_info():
    """
    this is the function updates shopify failed shipping history
    :return: a dictionary storing all error info
    """
    # 获取当前时间(北京时间)
    cur_date = datetime.utcnow().replace(tzinfo=pytz.utc)
    localDatetime = cur_date.astimezone(pytz.timezone('Asia/Shanghai'))

    # 需要更新的时间应该是北京时间的昨天一整天
    updated_at_min = localDatetime - timedelta(days=1)

    # 设置更新时间的范围
    Min = dt.datetime(updated_at_min.year, updated_at_min.month, updated_at_min.day)
    Max = Min + timedelta(days=1)
    # 设置时区
    tzObject = dt.timezone(dt.timedelta(hours=-8), name="CST")

    # 改为ISO 8601 时间格式
    cstTimeMin = Min.replace(tzinfo=tzObject)
    cstTimeMax = Max.replace(tzinfo=tzObject)
    min_data = cstTimeMin.isoformat('T', 'seconds')
    max_data = cstTimeMax.isoformat('T', 'seconds')
    print(min_data)
    print(max_data)

    shipping_status = ['shipped', 'partial']
    orders = None
    error = {'订单URL错误': [], '运输URL错误': [], '更新失败订单ID': []}
    error_info = ''
    for ship_status in shipping_status:
        # 获取更新时间为昨天的订单url
        order_url = 'https://cbc3e9686911d1cadbce71005e884660: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@shopcider.myshopify.com/admin/api/2020-10/orders.json?fulfillment_status={0}&status=any&created_at_min={1}&created_at_max={2}&limit=10'.format(
            ship_status, min_data, max_data)
        while True:
            get_order_num = 0
            while True:
                # 最多尝试5次获取订单
                if get_order_num >= 5:
                    error['订单URL错误'].append('失败URL:' + order_url + ' | 错误详情:' + str(error_info))
                    break
                try:
                    # time.sleep(3)
                    orders = requests.get(order_url, timeout=300)
                    break
                except Exception as e:
                    # print(e)
                    error_info = e
                    # time.sleep(5)
                    get_order_num += 1
                    continue
            if orders is None:
                break
            for order in orders.json()['orders'] if 'orders' in orders.json() else []:
                order_id = order['id']
                print(order_id)
                shipping_url = 'https://cbc3e9686911d1cadbce71005e884660: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' \
                               '@shopcider.myshopify.com/admin/api/2021-01/orders' \
                               '/{}/fulfillments.json'.format(str(order_id))
                get_ship_num = 0
                shipping = None
                while True:
                    if get_ship_num >= 5:
                        error['运输URL错误'].append(
                            '失败shipping URL:' + shipping_url + ' | 错误详情:' + str(error_info))
                        break
                    try:
                        # time.sleep(3)
                        shipping = requests.get(shipping_url, timeout=120)
                        break
                    except Exception as e:
                        # print(e)
                        error_info = e
                        # time.sleep(5)
                        get_ship_num += 1
                        continue
                if shipping is None:
                    total_shipping = []
                elif 'fulfillments' in shipping.json():
                    total_shipping = shipping.json()['fulfillments']
                else:
                    total_shipping = []
                for single_shipping in total_shipping:
                    shipping_id = single_shipping['id']
                    for track_num in single_shipping['tracking_numbers']:
                        if track_num.startswith('JS'):
                            tracking_urls = ['https://t.17track.net/en#nums=' + str(track_num)]
                            print(tracking_urls)
                            # time.sleep(3)
                            f_index = 0
                            # 尝试修改重试最多3次
                            while True:
                                if f_index >= 3:
                                    error['更新失败订单ID'].append(
                                        '订单ID:' + str(order_id) + 'shipping ID:' + str(shipping_id) + ' | 错误详情:' + str(
                                            error_info))
                                    break
                                try:
                                    header = {'Content-Type': 'application/json; charset=utf-8',
                                              'X-Shopify-Access-Token': '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'}
                                    data = {'fulfillment': {'tracking_urls': tracking_urls}}
                                    time.sleep(3)
                                    print(json.dumps(data))
                                    rr = requests.put('https://shopcider.myshopify.com/admin/api/2021-01/orders/{0}/fulfillments/{1}.json'.format(str(order_id), str(shipping_id)), data=json.dumps(data), headers=header, timeout=30)
                                    print('put success')
                                    print(rr.json())
                                    break
                                except Exception as e:
                                    time.sleep(5)
                                    error_info = e
                                    # print(e)
                                    f_index += 1
                                    continue
            if orders.headers is None:
                break
            # 翻页
            if 'Link' in orders.headers:
                url = orders.headers['Link'].split(';')[0].replace('>', '').replace('<', '') \
                    if 'next' in orders.headers['Link'].split(',')[0] else None
                if url is None and len(orders.headers['Link'].split(',')) > 1:
                    url = orders.headers['Link'].split(',')[1].split(';')[0].replace('>', '').replace('<', '') \
                        if 'next' in orders.headers['Link'].split(',')[1] else None
                # print(url)
                if url is not None:
                    order_url = 'https://cbc3e9686911d1cadbce71005e884660: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@shopcider.myshopify.com/admin/api/2020-10/orders.json?&' + urlparse(
                        url).query
                else:
                    break
            else:
                break
    return error


if __name__ == '__main__':
    text = find_update_failed_info()
    title = '物流信息更新测试'
    send_time = False
    chat_bot.send_message_job(title=title, text=text, send_time=send_time)
