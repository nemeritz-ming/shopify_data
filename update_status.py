import requests
import time
import datetime as dt
from _datetime import datetime, timedelta
import pytz
import chat_bot


def update_refund_status():
    """
    this is the function to update the pending refund status over the periods from 2020-08-01 to
    5 days before today
    :return: a dictionary storing all error info
    """

    # 设置header
    header = {'Authorization': 'RichReturnsToken a21357fb-db8a-4f22-a81b-45a58802a7f4',
              'content-type': 'application/json'}
    # 设置url
    original_url = 'https://api.richcommerce.co/2020-05-25/returns?limit=40&order=ASC'
    url = 'https://api.richcommerce.co/2020-05-25/returns?limit=40&order=ASC'
    post_url = 'https://api.richcommerce.co/2020-05-25/returns/'

    # 设置时间
    cur_date = datetime.utcnow().replace(tzinfo=pytz.utc)
    localDatetime = cur_date.astimezone(pytz.timezone('Asia/Shanghai'))

    # 需要更新的时间应该是北京时间的前5天以前
    updated_at = localDatetime - timedelta(days=6)

    # 设置更新时间的范围
    Max = dt.datetime(updated_at.year, updated_at.month, updated_at.day)
    createdAtMin = '2020-08-01'
    createdAtMax = str(Max.date())
    print(createdAtMin)
    print(createdAtMax)

    # 设置error_list储存错误信息
    error_list = {'URL错误': [], '更新失败订单id': [], '更新成功订单id': []}
    err = ''

    # 设置退货时间和状态筛选需求
    status = 'Pending'
    url += '&status=' + status + '&createdAtMin=' + createdAtMin + '&createdAtMax=' + createdAtMax
    original_url += '&status=' + status + '&createdAtMin=' + createdAtMin + '&createdAtMax=' + createdAtMax
    while True:
        result = []
        get_num = 0
        while True:
            # 尝试3次获取订单，
            if get_num > 3:
                error_list['URL错误'].append('错误的url: ' + url + '错误详情: ' + str(err))
                break
            try:
                # 尝试获取40个满足条件订单
                r = requests.get(url, headers=header)
                # 获取退货信息
                result = r.json()['returns']
                break
            except Exception as e:
                err = e
                time.sleep(3)
                get_num += 1
                continue
        if not result:
            break
        last_rma = ''
        for refund in result:
            # 获取rma订单
            last_rma = refund['rma']
            modify_num = 0
            while True:

                # 对于修改失败的退货订单，尝试3次修改退货状态，如若不行加入到错误信息列表
                if modify_num > 3:
                    error_list['更新失败订单id'].append(
                        '订单id:' + refund['orderId'] + ' | 错误详情: ' + str(err))
                    break
                try:
                    print(last_rma + "｜" + refund['orderId'] + "|" + refund['createdAt'] + "｜" + refund['status'])
                    # 尝试修改退货状态
                    time.sleep(3)
                    response = requests.post(post_url + last_rma + '/approve', headers=header)
                    # 判断是否修改成功
                    if response.json()['status'] == 'success':
                        error_list['更新成功订单id'].append('订单id:' + refund['orderId'])
                    else:
                        error_list['更新失败订单id'].append('订单id:' + refund['orderId'])
                    break
                except Exception as e:
                    print(e)
                    time.sleep(3)
                    err = e
                    modify_num += 1
                    continue
        # 翻页
        url = original_url + '&sinceId=' + last_rma
        time.sleep(3)
    return error_list


if __name__ == '__main__':
    text = update_refund_status()
    title = '退货状态更新测试'
    send_time = False
    chat_bot.send_message_job(title=title, text=text, send_time=send_time)
