import datetime
import json
import logging
import requests
import urllib3

urllib3.disable_warnings()


def not_null(content):
    """
    非空字符串
    :param content: 字符串
    :return: 字符串是否为空
    """
    if content and content.strip():
        return True
    else:
        return False


# feishu chat bot class
class FEISHU_CHAT_BOT(object):
    web_hook = 'https://open.feishu.cn/open-apis/bot/v2/hook/d6b4ab6a-1258-4bc3-880c-0064f091bb9c'
    key_word = '项目管理'

    def __init__(self, website_hook=web_hook, keyword=key_word):
        """
        机器人初始化
        :param website_hook: 传入飞书群自定义机器人web_hook地址
        :param keyword: 飞书机器人安全设定自定义关键词
        """
        super(FEISHU_CHAT_BOT, self).__init__()
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.web_hook = website_hook
        self.keyword = keyword
        self.time = datetime.datetime.now().date()

    def send_text(self, msg):
        """
        消息类型为text类型
        :param msg: 消息内容
        :return: 返回消息发送结果
        """
        data = {"msg_type": "text"}
        if not_null(msg):  # 传入msg非空
            data["content"] = {"text": "项目管理: " + msg}
        else:
            logging.error("text类型的消息内容为空！")
            raise ValueError("text类型，消息内容不能为空！")

        logging.debug('text类型：%s' % data)
        return self.post(data)

    def send_post(self, msg, title, link=""):
        """
        消息类型为post类型
        :param link: 内容链接
        :param title: 消息题目
        :param msg: 消息内容
        :return: 返回消息发送结果
        """
        data = {"msg_type": "post"}
        if not_null(msg):
            data["content"] = {"post": {"zh_cn": {"title": "{0} 项目管理".format(self.time), "content": [[
                {"tag": "text", "text": title},
                {"tag": "a", "text": "{0} 请查看".format(msg), "href": link}]]
                                                  }}}
        else:
            logging.error("post类型的消息内容为空！")
            raise ValueError("post类型，消息内容不能为空！")
        logging.debug('post类型：%s' % data)
        return self.post(data)

    def send_picture(self, pic_key):
        """
        消息类型为image类型
        :param pic_key: 例如:"img_ecffc3b9-8f14-400f-a014-05eca1a4310g" , 通过Upload image API 获取
        :return: 返回消息发送结果
        """
        data = {"msg_type": "image"}
        if not_null(pic_key):
            data["content"] = {
                "image_key": pic_key
            }
        else:
            logging.error("image类型的消息内容为空！")
            raise ValueError("image类型，消息内容不能为空！")
        logging.debug('image类型：%s' % data)
        return self.post(data)

    def send_card(self, msg, titles, link, link_title):
        """
        :param link_title: 卡片链接标题
        :param msg: 卡片内容
        :param titles: 卡片标题
        :param link: 卡片链接
        :return: 返回消息发送结果
        """
        data = {"msg_type": "interactive"}
        config = {
            "wide_screen_mode": True,
            "enable_forward": True}
        elements = [{"tag": "div",
                     "text": {
                         "content": msg,
                         "tag": "lark_md"
                     }},
                    {"actions": [{
                        "tag": "button",
                        "text": {
                            "content": link_title + ":玫瑰:",
                            "tag": "lark_md"
                        },
                        "url": link,
                        "type": "default",
                        "value": {}
                    }],
                        "tag": "action"
                    }]
        header = {
            "title": {
                "content": "项目管理:{0}".format(titles) + "\n {0}".format(self.time),
                "tag": "plain_text"
            }
        }

        data["card"] = {
            "config": config, "elements": elements, "header": header}
        return self.post(data)

    def post(self, data):
        """
        发送消息（内容UTF-8编码）
        :param data: 消息数据
        :return: 返回消息发送结果
        """
        try:
            post_data = json.dumps(data)
            response = requests.post(self.web_hook, headers=self.headers, data=post_data, verify=False)
        except requests.exceptions as exc:
            print(exc)
            pass
        else:
            try:
                result = response.json()
            except Exception as e:
                print(e)
                pass
            else:
                logging.debug('发送结果：%s' % result)
                return result


# test
if __name__ == '__main__':
    feishu = FEISHU_CHAT_BOT()
    feishu.send_text("项目更新:飞书消息测试")
    # feishu.send_post(title='退货项目更新', msg='退货分析',
    # link="https://gzr917xylb.feishu.cn/sheets/shtcnWpjd4rpObS0EosYF1UumUh/")
    # feishu.send_card(titles='项目更新', msg='退货分析',
    #                  link="https://gzr917xylb.feishu.cn/sheets/shtcnWpjd4rpObS0EosYF1UumUh/", link_title="详情请点击链接")
