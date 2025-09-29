from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TemplateMessage,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    Emoji,
    StickerMessage,
    TextMessage,
    VideoMessage,
    FlexMessage,
    FlexContainer,
    ImagemapArea, #新增的部分
    ImagemapBaseSize,
    ImagemapExternalLink,
    ImagemapMessage,
    ImagemapVideo,   
    URIImagemapAction,   #Imagemap獨有的Action
    MessageImagemapAction,
    QuickReply, #新增的部分
    QuickReplyItem,
    MessageAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
    MessagingApiBlob, #新增的部分
    RichMenuSize,
    RichMenuRequest,
    RichMenuArea,
    RichMenuBounds,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent 
)

import requests
import json
import os
load_dotenv()
app = Flask(__name__)

channel_secret = os.getenv('CHANNEL_SECRET')
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')

print("channel_secret:", channel_secret)
print("channel_access_token:", channel_access_token)

configuration = Configuration(access_token=channel_access_token)
line_handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK', 200


def create_rich_menu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api_blob = MessagingApiBlob(api_client)
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=29, y=42, width=809, height=791),
                action=MessageAction(text='Action 1')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=849, y=42, width=809, height=791),
                action=MessageAction(text='Action 2')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1687, y=42, width=809, height=791),
                action=MessageAction(text='Action 3')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=29, y=863, width=809, height=791),
                action=MessageAction(text='Action 4')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=849, y=863, width=809, height=791),
                action=MessageAction(text='Action 5')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1687, y=863, width=809, height=791),
                action=MessageAction(text='Action 6')
            ),
        ]
        rich_menu_to_create=RichMenuRequest(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,   #預設顯示此選單
            name='Rich Menu 1',
            chat_bar_text='To see more!',
            areas=areas
        )
        rich_menu_id=line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_create
        ).rich_menu_id
        with open('./static/richmenu.jpg', 'rb') as image:
            line_bot_api_blob.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/jpeg'}
            )
        line_bot_api.set_default_rich_menu(rich_menu_id)
create_rich_menu()

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text=event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if text=='文字':
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='Hello, world!')]
                )
            )
        elif text=='表情符號':
            emojis=[
                Emoji(index=0, product_id='5ac1bfd5040ab15980c9b435', emoji_id='001'),
                Emoji(index=8, product_id='5ac1bfd5040ab15980c9b435', emoji_id='002')
            ]  
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='$ Hello $', emojis=emojis)]
                )
            )
        elif text=='貼圖':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[StickerMessage(package_id='789', sticker_id='10859')] 
                )
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TemplateMessage(alt_text='Confirm alt text', template=confirm_template)]
                )
        )
        elif text=='影片':
            url=request.url_root+'static/fire.mp4'
            url=url.replace('http://', 'https://')
            app.logger.info('url='+url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        VideoMessage(original_content_url=url, preview_image_url=url)
                    ]
                )
            )
        #confirm template
        elif text=='confirm':
            confirm_template=ConfirmTemplate(
                text='你喜歡狗嗎?',
                actions=[
                    MessageAction(label='Yes', text='Yes!'),
                    MessageAction(label='No', text='No!')
                ]
            )
            template_message=TemplateMessage(
                alt_text='確認內容', 
                template=confirm_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        #buttons template
        elif text=='buttons':
            url=request.url_root+'static/fire.png'
            url=url.replace('http://', 'https://')
            app.logger.info('url='+url)
            buttons_template=ButtonsTemplate(
                thumbnail_image_url=url,
                title='菜單',
                text='看屁？選擇啊！',
                actions=[
                    MessageAction(label='Say Hello', text='Hello!'),
                    URIAction(label='連結', uri='https://youtu.be/dQw4w9WgXcQ?si=qQL7E_0mTxlvanmP'),
                    PostbackAction(label='Buy', data='ping', displaytext='傳送完成!'),
                    DatetimePickerAction(label='Select date', data='action=select_date', mode='date')
                ]
            )
            template_message=TemplateMessage(
                alt_text='按鈕樣板', 
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        #carousel template
        elif text=='carousel':
            t_url=request.url_root+'static/calendar.png'
            t_url=t_url.replace('http', 'https')
            m_url=request.url_root+'static/chat.png'
            m_url=m_url.replace('http', 'https')
            b_url=request.url_root+'static/return.png'
            b_url=b_url.replace('http', 'https')
            carousel_template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=b_url,
                        title='迴轉',
                        text='postback',
                        actions=[
                            MessageAction(label='Say Hello', text='Hello!'),
                            URIAction(label='連結', uri='https://youtu.be/dQw4w9WgXcQ?si=qQL7E_0mTxlvanmP')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=m_url,
                        title='聊天',
                        text='chat',
                        actions=[
                            PostbackAction(label='Buy', data='ping', displaytext='傳送完成!'),
                            DatetimePickerAction(label='Select date', data='action=select_date', mode='date')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=t_url,
                        title='返回',
                        text='return',
                        actions=[
                            MessageAction(label='Say Hello', text='Hello!'),
                            URIAction(label='連結', uri='https://youtu.be/dQw4w9WgXcQ?si=qQL7E_0mTxlvanmP')
                        ]
                    )
                ]
            )
            template_message=TemplateMessage(
                alt_text='輪播樣板', 
                template=carousel_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        #image carousel template
        elif text=='image carousel':
            url=request.url_root+'/static'
            url=url.replace('http', 'https')
            app.logger.info('url='+ url)
            image_carousel_template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url=url+'/fire.png',
                        action=MessageAction(label='fire', text='fire!')
                    ),
                    ImageCarouselColumn(
                        image_url=url+'/snow.png',
                        action=URIAction(label='snow', uri='https://youtu.be/dQw4w9WgXcQ?si=qQL7E_0mTxlvanmP')
                    ),
                    ImageCarouselColumn(
                        image_url=url+'/wind.png',
                        action=MessageAction(label='wind', text='呼呼!')
                    ),
                ]
            )
            template_message=TemplateMessage(
                alt_text='圖片輪播樣板', 
                template=image_carousel_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        elif text=='flex':
            line_flex_json={
  "type": "bubble",
  "hero": {
    "type": "image",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "url": "https://www.nses.cyc.edu.tw/html/fish/e7b4abe88ab1e985a2e6bcbfe88d89.jpg"
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "森林系",
        "weight": "bold",
        "size": "xl",
        "contents": [
          {
            "type": "span",
            "text": "森林系  ",
            "size": "xl",
            "style": "normal"
          },
          {
            "type": "span",
            "text": "自然資源",
            "size": "xs"
          }
        ]
      },
      {
        "type": "box",
        "layout": "baseline",
        "margin": "md",
        "contents": [
          {
            "type": "icon",
            "size": "sm",
            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
          },
          {
            "type": "icon",
            "size": "sm",
            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
          },
          {
            "type": "icon",
            "size": "sm",
            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
          },
          {
            "type": "icon",
            "size": "sm",
            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
          },
          {
            "type": "icon",
            "size": "sm",
            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
          },
          {
            "type": "text",
            "text": "5.0",
            "size": "sm",
            "color": "#999999",
            "margin": "md",
            "flex": 0
          }
        ]
      },
      {
        "type": "box",
        "layout": "vertical",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "Place",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 1
              },
              {
                "type": "text",
                "text": "Flex Tower, 7-7-4 Midori-ku, Tokyo",
                "wrap": True,
                "color": "#666666",
                "size": "sm",
                "flex": 5
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "Time",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 1
              },
              {
                "type": "text",
                "text": "10:00 - 23:00",
                "wrap": True,
                "color": "#666666",
                "size": "sm",
                "flex": 5
              }
            ]
          }
        ]
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "horizontal",
    "contents": [
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "action",
          "uri": "http://linecorp.com/"
        },
        "style": "primary",
        "margin": "lg"
      },
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "生生不息",
          "uri": "https://live.staticflickr.com/2715/5813899587_6f29081186_b.jpg"
        },
        "style": "secondary",
        "margin": "lg"
      }
    ]
  }
}
            line_flex_str=json.dumps(line_flex_json)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text='Flex message', contents=FlexContainer.from_json(line_flex_str))]
                )
            )
        elif text=='imagemap': #永遠圖片無法讀取！！！
            imagemap_base_url=request.url_root+'/static/imagemap'
            imagemap_base_url=imagemap_base_url.replace('http', 'https')
            video_url=request.url_root+'/static/fire.mp4'
            video_url=video_url.replace('http', 'https')
            preview_image_url=request.url_root+'/static/fire.png'
            preview_image_url=preview_image_url.replace('http', 'https')

            imagemap_message=ImagemapMessage(
                base_url=imagemap_base_url,
                alt_text='這是Imagemap',
                base_size=ImagemapBaseSize(height=1040, width=1040),
                video=ImagemapVideo(
                    original_content_url=video_url,   #影片網址
                    preview_image_url=preview_image_url,   #預覽圖網址
                    area=ImagemapArea(
                        x=16, y=17, width=495, height=495
                    ),
                    external_link=ImagemapExternalLink(    #影片結束後連結
                        label='Go to line.me', 
                        link_uri='https://line.me'
                    )
                ),
                actions=[
                    URIImagemapAction(
                        link_uri='https://youtu.be/dQw4w9WgXcQ?si=qQL7E_0mTxlvanmP',
                        area=ImagemapArea(
                            x=527, y=18, width=495, height=495
                        )
                    ),
                    MessageImagemapAction(
                        text='你點到我了!',
                        area=ImagemapArea(x=12, y=530, width=495, height=495)
                    ),
                    MessageImagemapAction(
                        text='你點到機器人了!',
                        area=ImagemapArea(x=527, y=530, width=495, height=495)
                    )

                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[imagemap_message]
                )
            )
        elif text=='quick': 
            quickReply=QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(
                            label='fire-postback', 
                            data='fire-postback',
                            display_text='fire!'
                        ),
                       
                    ),
                    QuickReplyItem(
                        action=MessageAction(
                            label='snow', 
                            text='snow!'
                        ),
                       
                    ),
                    QuickReplyItem(
                        action=DatetimePickerAction(
                            label='robot-Date',
                            data='datetime',   #同PostbackAction
                            mode='datetime',   #date日期、time時間、datetime日期時間
                            initial='2024-06-18T00:00',   #下三可不寫
                            min='2023-12-31T00:00',
                            max='2025-01-01T00:00'
                        ),
                       
                    ),
                    QuickReplyItem(
                        action=CameraAction(
                            label='robot-Camera'
                        ),
                    ),
                    QuickReplyItem(
                        action=CameraRollAction(label='CameraRollAction'),
                    ),
                    QuickReplyItem(
                        action=LocationAction(label='LocationAction'),
                    )
                    
                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='選擇項目',
                        quick_reply=quickReply
                    )]
                )
            )  
        else:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )

@line_handler.add(PostbackEvent)
def handle_postback(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        postback_data=event.postback.data 
        if postback_data=='fire-postback':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='fire-postback Received!')]
                )
            )
            
        elif postback_data=='datetime':
            datetime=event.postback.params['datetime']
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=datetime)]
                )
            ) 

if __name__ == "__main__":
    app.run(port=5001, debug=True)
