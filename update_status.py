import requests
import time
import datetime as dt
from _datetime import datetime, timedelta
import pytz


def update_refund_status():
    """
    this is the function to update the pending refund status over the periods from 2020-08-01 to
    5 days before today
    :return: a dictionary store all error info
    """
    # set header
    header = {'Authorization': 'RichReturnsToken a21357fb-db8a-4f22-a81b-45a58802a7f4',
              'content-type': 'application/json'}
    # set url
    original_url = 'https://api.richcommerce.co/2020-05-25/returns?limit=40&order=ASC'
    url = 'https://api.richcommerce.co/2020-05-25/returns?limit=40&order=ASC'
    post_url = 'https://api.richcommerce.co/2020-05-25/returns/'

    # set time
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


    # set result list and error list
    error_list = {'url_error': [], 'update_failed_id': [], 'update_success_id': []}
    err = ''

    # set time constraint and status
    status = 'Pending'
    url = url + '&status=' + status + '&createdAtMin=' + createdAtMin + '&createdAtMax=' + createdAtMax
    original_url = original_url + '&status=' + status + '&createdAtMin=' + createdAtMin + '&createdAtMax=' + createdAtMax
    while True:
        result = []
        get_num = 0
        while True:
            # 尝试3次get url
            if get_num > 3:
                error_list['url_error'].append('wrong_get_url: ' + url + 'error_info: ' + str(err))
                break
            try:
                r = requests.get(url, headers=header)
                result = r.json()['returns']
                break
            except Exception as e:
                err = e
                time.sleep(3)
                get_num += 1
                continue
        if result == []:
            break
        last_rma = ''
        for refund in result:
            last_rma = refund['rma']
            modify_num = 0
            while True:
                if modify_num > 3:
                    # 尝试3次修改退货状态
                    error_list['update_failed_id'].append(
                        'Failed_order_id:' + refund['orderId'] + '| error_info: ' + str(err))
                    break
                try:
                    print(last_rma + "｜" + refund['orderId'] + "|" + refund['createdAt'] + "｜" + refund['status'])
                    # response = requests.post(post_url + last_rma + '/approve', headers=header)
                    # if response.json()['status'] == 'success':
                    #     error_list['update_success_id'].append('Success_order_id:' + refund['orderId'])
                    # else:
                    #     error_list['update_failed_id'].append('Failed_order_id:' + refund['orderId'])
                    break
                except Exception as e:
                    time.sleep(3)
                    err = e
                    modify_num += 1
                    continue
        # 翻页
        url = original_url + '&sinceId=' + last_rma
        time.sleep(3)
    return error_list


update_refund_status()
# # test
# last_rma = 'RMA-2682492285110'
# response = requests.post(post_url + last_rma + '/approve', headers=header)
# print(response.json()['status'])
