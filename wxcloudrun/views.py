from datetime import datetime
from flask import render_template, request, jsonify
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import time
import requests
def getAiMessage(msg):
    ARK_API_KEY = "bd8963b1-a15b-4497-8ac5-30f9f2a08b74"  # 直接写死

    url = "https://ark.cn-beijing.volces.com/api/v3/bots/chat/completions"
    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "bot-20250210201752-vdpfr",
        "stream": False,  # 关闭流式
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": msg}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    return data['choices'][0]['message']['content']

def send_mess(appid, mess):
    """
    发送微信客服消息
    appid: 微信小程序或公众号 appid
    mess: dict 消息内容
    """
    url = f"http://api.weixin.qq.com/cgi-bin/message/custom/send?from_appid={appid}"
    try:
        response = requests.post(url, json=mess)  # 自动把 dict 转 JSON
        response.raise_for_status()  # 如果状态码不是 200，会抛出异常
        app.logger.debug(f"接口返回内容: {response.text}")
        return response.json()
    except requests.RequestException as e:
        app.logger.debug(f"接口返回错误: {e}")
        return {"error": str(e)}
@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

@app.route('/api/wxMessage', methods=['POST'])
def message_post():
    data = request.get_json(force=True)

    ToUserName = data.get('ToUserName')
    FromUserName = data.get('FromUserName')
    Content = data.get('Content', '')
    CreateTime = data.get('CreateTime', int(time.time()))
    app.logger.debug("DEBUG: 搜到消息请求")
    app.logger.debug(FromUserName)
    app.logger.debug(ToUserName)
    # 无用户信息
    if not FromUserName:
        return jsonify({
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "CreateTime": CreateTime,
            "MsgType": "text",
            "Content": "无用户信息"
        })
    replyContent = getAiMessage(Content)
    app.logger.debug(replyContent)
    # print(replyContent)
    # replyJson = {
    #     "touser": FromUserName,
    #     "msgtype": 'text',
    #     "text": {
    #         "content": replyContent
    #     }
    # }
    # send_mess('wxbba632a8926a73d6', replyJson)
    return jsonify({
        "ToUserName": FromUserName,   # 回复给谁
        "FromUserName": ToUserName,   # 从哪个公众号回复
        "CreateTime": int(time.time()),
        "MsgType": "text",
        "Content": replyContent            # 原样返回
    })