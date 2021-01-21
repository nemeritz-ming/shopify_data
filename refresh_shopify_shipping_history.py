import shopify
import time

# 获取shopify的验证session
session = shopify.Session('shopcider.myshopify.com', '2020-10', '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')

# 激活session
shopify.ShopifyResource.activate_session(session)

# 判断是否获取到物流信息
f_order = None

# 初始化获取第一页订单信息
orders = shopify.Order.find(limit=30, fulfillment_status='shipped', status='any')

# 循环遍历处理订单
while True:
    print(orders)
    for order in orders:

        # 记录物流信息获取重试次数
        get_track_inex = 0
        while True:
            # 最多重试3次
            if get_track_inex >= 3:
                break
            try:
                f_order = shopify.Fulfillment.find(order_id=order.id)
                break
            except Exception as e:
                print(e)
                time.sleep(5)
                get_track_inex += 1
                continue
        # 如果没有获取到物流信息，则该订单跳过
        if f_order is None:
            continue

        # 循环处理一个订单的每个物流包裹
        for f in f_order:
            i = 0
            for track_num in f.tracking_numbers:
                # 以JS开头的是极速的订单，我们才处理，否则我们不处理
                if str(f.tracking_numbers[i]).startswith('JS'):
                    print(order.id)
                    f.tracking_urls = [('https://t.17track.net/en#nums=' + str(f.tracking_numbers[i]))]
                    time.sleep(3)
                    f_index = 0
                    # 尝试修改重试最多3次
                    while True:
                        if f_index >= 3:
                            break
                        try:
                            f.save()
                            break
                        except Exception as e:
                            time.sleep(5)
                            print(e)
                            f_index += 1
                            continue
    # 判断是否有下一页数据
    if orders.has_next_page():
        page_index = 0
        # 获取下一页数据最多重试5次
        while True:
            if page_index >= 5:
                break
            try:
                time.sleep(3)
                orders = orders.next_page()
                break
            except Exception as e:
                print(e)
                page_index += 1
                continue
    else:
        break
shopify.ShopifyResource.clear_session()