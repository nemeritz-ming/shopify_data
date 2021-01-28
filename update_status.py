import requests
import time
import datetime as dt
from _datetime import datetime, timedelta
import pytz

# set header
header = {'Authorization': 'RichReturnsToken a21357fb-db8a-4f22-a81b-45a58802a7f4',
          'content-type': 'application/json'}

# set url
orignal_url = 'https://api.richcommerce.co/2020-05-25/returns?limit=40&order=ASC'
url = 'https://api.richcommerce.co/2020-05-25/returns?limit=40&order=ASC'
post_url ='https://api.richcommerce.co/2020-05-25/returns/'
# set time
cur_date = datetime.utcnow().replace(tzinfo=pytz.utc)
localDatetime = cur_date.astimezone(pytz.timezone('Asia/Shanghai'))

# 需要更新的时间应该是北京时间的前5天以前
updated_at = localDatetime - timedelta(days=5)

# 设置更新时间的范围
Min = dt.datetime(updated_at.year, updated_at.month, updated_at.day)

# 设置时区
tzObject = dt.timezone(dt.timedelta(hours=-8), name="CST")

# 改为ISO 8601 时间格式
cstTime = Min.replace(tzinfo=tzObject)
min_data = cstTime.isoformat('T', 'seconds')
print(min_data)


# set result list and error list
result_list = []
error_list = {'url_error': [], 'update_failed_id': [], 'update_success_id': []}
result = []
while True:
    get_num = 0
    while True:
        if get_num > 3:
            error_list['url_error'].append('wrong_get_url: ' + url)
            break
        try:
            r = requests.get(url, headers=header)
            result = r.json()['returns']
            break
        except Exception as e:
            time.sleep(3)
            get_num += 1
            continue
    if not result:
        break
    last_rma = ''
    err = ""
    for refund in result:
        last_rma = refund['rma']
        if refund['createdAt'] < min_data:
            if refund['status'] == 'Pending':
                print(last_rma + "｜" + refund['createdAt'] + "｜" + refund['status'])
                modify_num = 0
                while True:
                    if modify_num > 3:
                        error_list['update_failed_id'].append('Failed_order_id:' + refund['orderId'] + '| error_info: '+ str(err))
                        break
                    try:
                        response = requests.post(post_url + last_rma + '/approve', headers=header)
                        if response.json()['status'] == 'success':
                            error_list['update_success_id'].append('Success_order_id:' + refund['orderId'])
                        else:
                            error_list['update_failed_id'].append('Failed_order_id:' + refund['orderId'])
                        break
                    except Exception as e:
                        time.sleep(3)
                        err = e
                        continue

    url = orignal_url + '&sinceId=' + last_rma
    time.sleep(3)

# # test
# last_rma = 'RMA-2682492285110'
# response = requests.post(post_url + last_rma + '/approve', headers=header)
# print(response.json()['status'])
