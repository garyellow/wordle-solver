import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# create dictionary of words
# key value is word, value is word with letters in alphabetical order to help unscramble letters
# currently, the list in the repository only has potential answers listed in it
dic = {}
file = open("words.txt", "r")
loc = 0
for word in file:
    for char in word:
        data = word[loc:loc + 5]
        loc = loc + 6
        dic.update({data.lower(): ''.join(sorted(data.lower()))})

del dic['']


# next 4 functions are helper functions for my method (algorithm) function

# remove double letters from a guess
def clean(let):
    result = "".join(dic.fromkeys(let))
    return result


# unscrabble the letters
def jumble(word, dic):
    list_ = []
    word = ''.join(sorted(word))  # set guess in alphabetical order of characters

    for key in dic:
        if dic[key] == word:  # check if guess matches dictionary value in alphabetical order
            list_.append(key)  # add actial dictionary value if so

    return list_


# clean array based on correct placements
# only removes one value per call
def remove(guesses, wrong_guess, final):
    for n in range(0, len(guesses)):
        for i in range(0, 5):
            for j in range(0, len(wrong_guess[i])):
                if ((guesses[n][i] != final[i] and final[i] != '')
                        or guesses[n][i] == wrong_guess[i][j]):
                    del guesses[n]
                    return
                # add new possible answers to list of possible answers


def append_answers(guesses, wrong_guess, final, answers):
    # remove incorrect answers
    for n in range(0, len(guesses)):
        remove(guesses, wrong_guess, final)
    # add said list to list of possible answers
    for i in range(0, len(guesses)):
        answers.append(guesses[i])


# check to see what possible answers are available after a given guess
def check_answers(let, wrong_guess, final, answers):
    # call append answers if you know all 5 values
    if len(let) == 5:
        append_answers(jumble(let, dic), wrong_guess, final, answers)
    # call append answers guessing for each unknown letter and a double of each known letter
    elif len(let) == 4:
        for i in range(0, 4):
            append_answers(jumble(let + let[i], dic), wrong_guess, final, answers)
        append_answers(jumble(let + 'v', dic), wrong_guess, final, answers)
        append_answers(jumble(let + 'j', dic), wrong_guess, final, answers)
        append_answers(jumble(let + 'x', dic), wrong_guess, final, answers)
        append_answers(jumble(let + 'z', dic), wrong_guess, final, answers)
    # call this function to raise let up to four letters then move through append answers
    elif len(let) == 3:
        for i in range(0, 3):
            check_answers(let + let[i], wrong_guess, final, answers)
        check_answers(let + 'v', wrong_guess, final, answers)
        check_answers(let + 'j', wrong_guess, final, answers)
        check_answers(let + 'x', wrong_guess, final, answers)
        check_answers(let + 'z', wrong_guess, final, answers)


# main solving operation
# guess 5 set words to remove almost all possible letters
# unscramble the known letters to get possible guess
# change this function to test your own algorythm
def method():
    let = ''
    # 5 words that are guessed before program creates final guess
    words = ['quick', 'brown', 'shady', 'cleft', 'gimps']
    final = ['', '', '', '', '']
    wrong_guess = [[''], [''], [''], [''], ['']]
    answers = []
    # test the words in the array
    for i in range(0, 5):
        test = words[i]
        let = enter_word(test, let, final, wrong_guess)
        let = clean(let)

    check_answers(let, wrong_guess, final, answers)
    print(wrong_guess)
    print(final)
    # print feedback on the game
    print(answers)

    return answers[0]


# open wordle website and start playing game
# change 'Firefox' to 'Chromium' to open with chrome/chromium
# NOTE: you must download selenium and a web driver to use selenium: https://selenium-python.readthedocs.io/
browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get('https://www.powerlanguage.co.uk/wordle/')
time.sleep(1)

Elem = browser.find_element(By.TAG_NAME, 'html')
Elem.click()
time.sleep(1)


# final array is array of 5 characters consisting of the currently known (green) letters
# wrong_guess array is array of arrays of currently present (yellow) letters
# word is the guess to input
# let is a string of both known and present letters in a meaningless order
# enters guess into wordle and returns known letters/changes final and wrong_guess arrays
def enter_word(word, let, final, wrong_guess):
    Elem.send_keys(word)
    Elem.send_keys(Keys.ENTER)

    time.sleep(1)

    host = browser.find_element(By.TAG_NAME, "game-app")
    first_host = browser.find_element(By.TAG_NAME, "game-app")
    game = browser.execute_script("return arguments[0].shadowRoot.getElementById('game')", host)

    keyboard = game.find_element(By.TAG_NAME, "game-keyboard")

    keys = browser.execute_script("return arguments[0].shadowRoot.getElementById('keyboard')", keyboard)

    time.sleep(2)
    # store data of all the letters (match, match in different location, no match)
    keydata = browser.execute_script("return arguments[0].innerHTML;", keys)
    # get array of matches and matches in different locations using janky regex logic
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

    # add known values to arrays used in method
    for i in range(0, 5):
        for j in range(0, 5):
            if word[i] == matches[j]:
                final[i] = word[i]
                let = ''.join((let, final[i]))
            if word[i] == nearmatches[j]:
                wrong_guess[i].append(word[i])
                let = ''.join((let, word[i]))
    print(final)
    print(wrong_guess)
    return let


# give time for user to cancel and add suspense
time.sleep(1)
# input final guess
Elem.send_keys(method())
Elem.send_keys(Keys.ENTER)

# allow time to celebrate solving it
time.sleep(8)

browser.close()
