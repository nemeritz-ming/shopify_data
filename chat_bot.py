import FEISHU_CHAT_BOT
import time
import schedule
import test


# set time schedule
bot = FEISHU_CHAT_BOT.FEISHU_CHAT_BOT()


def logistics_update_failed_id_job():
    res = test.find_update_failed_info()
    text = ""
    for keys in res:
        if res[keys]:
            text += keys + '\n'
            for val in res[keys]:
                text += '\t' + str(val) + '\n'
    if text == "":
        text += '无更新失败信息'
    bot.send_post(msg = 'text', title='物流更新信息:\n')


if __name__ == '__main__':
    logistics_update_failed_id_job()

# schedule.every().day.at("16:30").do(logistics_update_failed_id_job)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
