from datetime import datetime, timedelta
import datetime as dt
import pytz
import ssl

# remove validation for ssl
ssl._create_default_https_context = ssl._create_unverified_context

import shopify

# 获取shopify的验证session
session = shopify.Session('shopcider.myshopify.com', '2020-10', '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')

# 激活session
shopify.ShopifyResource.activate_session(session)

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
Min = cstTimeMin.isoformat('T', 'seconds')
Max = cstTimeMax.isoformat('T', 'seconds')
print(Min)
print(Max)
# 提取满足更新时间的订单
orders = shopify.Order.find(limit=30, fulfillment_status='shipped', status='any', updated_at_max=Max,
                            updated_at_min=Min)
# 订单需要更新的总数
num = 0

# 遍历所有订单
while True:
    if len(orders) != 0:
        for i in range(30):
            try:
                # 提取物流信息
                logistics = shopify.Fulfillment.find(order_id=orders[i].id)
                for l in logistics:
                    # 提取该订单物流的最近更新时间
                    print(l.updated_at)
                num += 1
                print(num)
            except Exception as e:
                print(e)
                pass
    if orders.has_next_page():
        orders = orders.next_page()
    else:
        break
