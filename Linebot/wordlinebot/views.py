# Create your views here.

import re
import time

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == "POST":
        message = []

        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")

        message.append(TextSendMessage(text=str(body)))
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent) and not event.message.text == "請稍等半分鐘":
                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text="選擇模式",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://imgcdn.cna.com.tw/www/WebPhotos/1024/20220127/1280x1021_161223061652.jpg",
                            title="點擊下方按鈕獲得今天的答案",
                            text="有極小機率是錯的，可以多按幾次",
                            actions=[
                                PostbackAction(
                                    label="點我點我",
                                    text="請稍等半分鐘",
                                    data="wordle"
                                )
                            ]
                        )
                    )
                )

            elif isinstance(event, PostbackEvent):
                if event.postback.data == "wordle":
                    dic = {}
                    file = open("words.txt", "r")
                    loc = 0
                    for word in file:
                        for _ in word:
                            data = word[loc:loc + 5]
                            loc = loc + 6
                            dic.update({data.lower(): ''.join(sorted(data.lower()))})

                    del dic['']

                    def clean(let):
                        result = "".join(dic.fromkeys(let))
                        return result

                    def jumble(word, dic):
                        list_ = []
                        word = ''.join(sorted(word))

                        for key in dic:
                            if dic[key] == word:
                                list_.append(key)

                        return list_

                    def remove(guesses, wrong_guess, final):
                        for n in range(0, len(guesses)):
                            for i in range(0, 5):
                                for j in range(0, len(wrong_guess[i])):
                                    if (guesses[n][i] != final[i] and final[i] != '') or guesses[n][i] == wrong_guess[i][j]:
                                        del guesses[n]
                                        return

                    def append_answers(guesses, wrong_guess, final, answers):
                        for n in range(0, len(guesses)):
                            remove(guesses, wrong_guess, final)
                        for i in range(0, len(guesses)):
                            answers.append(guesses[i])

                    def check_answers(let, wrong_guess, final, answers):
                        if len(let) == 5:
                            append_answers(jumble(let, dic), wrong_guess, final, answers)
                        elif len(let) == 4:
                            for i in range(0, 4):
                                append_answers(jumble(let + let[i], dic), wrong_guess, final, answers)
                            append_answers(jumble(let + 'v', dic), wrong_guess, final, answers)
                            append_answers(jumble(let + 'j', dic), wrong_guess, final, answers)
                            append_answers(jumble(let + 'x', dic), wrong_guess, final, answers)
                            append_answers(jumble(let + 'z', dic), wrong_guess, final, answers)
                        elif len(let) == 3:
                            for i in range(0, 3):
                                check_answers(let + let[i], wrong_guess, final, answers)
                            check_answers(let + 'v', wrong_guess, final, answers)
                            check_answers(let + 'j', wrong_guess, final, answers)
                            check_answers(let + 'x', wrong_guess, final, answers)
                            check_answers(let + 'z', wrong_guess, final, answers)

                    def method():
                        let = ''
                        words = ['quick', 'brown', 'shady', 'cleft', 'gimps']
                        final = ['', '', '', '', '']
                        wrong_guess = [[''], [''], [''], [''], ['']]
                        answers = []
                        for i in range(0, 5):
                            test = words[i]
                            let = enter_word(test, let, final, wrong_guess)
                            let = clean(let)

                        check_answers(let, wrong_guess, final, answers)

                        before = 'abcdefghijklmnopqrstuvwxyz'
                        after = '🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩'
                        encode = str.maketrans(before, after)
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answers.__str__()[2:7].translate(encode)))

                        return answers[0]

                    browser = webdriver.Chrome(ChromeDriverManager().install())
                    browser.get('https://www.powerlanguage.co.uk/wordle/')
                    time.sleep(1)

                    elem = browser.find_element(By.TAG_NAME, 'html')
                    elem.click()
                    time.sleep(1)

                    def enter_word(word, let, final, wrong_guess):
                        elem.send_keys(word)
                        elem.send_keys(Keys.ENTER)

                        time.sleep(1)

                        host = browser.find_element(By.TAG_NAME, "game-app")
                        game = browser.execute_script("return arguments[0].shadowRoot.getElementById('game')", host)

                        keyboard = game.find_element(By.TAG_NAME, "game-keyboard")

                        keys = browser.execute_script("return arguments[0].shadowRoot.getElementById('keyboard')", keyboard)

                        time.sleep(2)
                        keydata = browser.execute_script("return arguments[0].innerHTML;", keys)
                        correct_regex = re.compile('...............correct', re.VERBOSE)

                        matches = ['', '', '', '', '']
                        n = 0
                        for groups in correct_regex.findall(keydata):
                            if (groups[0] != final[0] and groups[0] != final[1] and groups[0] != final[2] and groups[0] != final[3] and
                                    groups[0] != final[4]):
                                matches[n] = (groups[0])
                            n = n + 1

                        present_regex = re.compile('...............present', re.VERBOSE)

                        nearmatches = ['', '', '', '', '']

                        n = 0
                        for groups in present_regex.findall(keydata):
                            nearmatches[n] = (groups[0])
                            n = n + 1

                        for i in range(0, 5):
                            for j in range(0, 5):
                                if word[i] == matches[j]:
                                    final[i] = word[i]
                                    let = ''.join((let, final[i]))
                                if word[i] == nearmatches[j]:
                                    wrong_guess[i].append(word[i])
                                    let = ''.join((let, word[i]))

                        return let

                    time.sleep(1)
                    elem.send_keys(method())
                    elem.send_keys(Keys.ENTER)
                    browser.close()

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
