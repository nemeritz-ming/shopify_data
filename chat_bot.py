import feishu_real_time_messages
import time
import schedule

a = feishu_real_time_messages.FEISHU_CHAT_BOT()


# set time schedule
def job():
    print("I'm working on ...")


schedule.every().day.at("16:30").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)