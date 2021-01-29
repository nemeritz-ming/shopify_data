import time
import schedule
import FEISHU_CHAT_BOT


def send_message_job(title, text, send_time=False):
    """
    this is the function that sends message using fei_shu chat bot
    :param send_time: if it is true then send message at 16:00 every day else then send right now (boolean)
    :param title: project title (string)
    :param text: message or info about the project need to send (dict),
    example : text = {attribute 1:[val1, val2, val3], attribute 2:[str1, str2, str3], ......})
    """
    # import fei_shu chat bot
    bot = FEISHU_CHAT_BOT.FEISHU_CHAT_BOT()
    txt = ""

    # read the content into txt
    for keys in text:
        if text[keys]:
            txt += keys + '\n'
            for val in text[keys]:
                txt += '\t' + str(val) + '\n'
    if txt == "":
        txt += '无更新失败'

    def send_job():
        bot.send_post(msg=txt, title='{0}:\n'.format(title))

    if send_time:
        schedule.every().day.at('16:00').do(send_job)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        send_job()
