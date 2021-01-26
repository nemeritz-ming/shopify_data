import feishu_real_time_messages
import time
import schedule
import test

bot = feishu_real_time_messages.FEISHU_CHAT_BOT()


# set time schedule
def logistics_update_failed_id_job():
    res = test.find_update_failed_info()
    text = "物流更新失败信息：\n"
    for keys in res:
        if res[keys]:
            text += keys + ': \n'
            for val in res[keys]:
                text += '\t' + str(val) + '\n'
    print(text)
    bot.send_text(msg=text)


schedule.every().day.at("16:30").do(logistics_update_failed_id_job)
while True:
    schedule.run_pending()
    time.sleep(1)
