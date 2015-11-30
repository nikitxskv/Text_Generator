# -*- coding: utf-8 -*-

import os
import pickle
import random
import sys
import time
import sys
import unicodedata
import math


def MakeStatistic(folder):
    ''' Подготавливает базу для генерации предложений. И сохраняет
        эту базу на диск.
        folder - название папки в которой лежит корпус текстов. '''

    whole_text = GetText(folder)
    word_list = MakeList(whole_text)
    words_distribution = AnalizeWords(word_list)
    words_distribution = DeliteBadWords(*words_distribution)
    words_distribution = MakeDistribution(*words_distribution)
    PickleDistribution(*words_distribution)


def GetText(folder):
    ''' Считывает текст из файла и возвращает его в виде строки. '''

    print 'Getting text...'

    whole_text = ''
    for author in os.listdir('./' + folder):
        if author[0] != '.':
            for book in os.listdir('./{}/{}'.format(folder, author)):
                with open('./{}/{}/{}'.format(folder, author, book), 'r') as f:
                    whole_text += ClearText(f.read())
    return whole_text


def ClearText(text):
    ''' Очищает текст от знаков пунктуации, оставляя только точки.
        Так же отпределяет какие точки являются окончанием предложения,
        а какие обоззначают сокращение слова. '''

    result_text = ''
    for letter in text:
        if (letter.isalpha() or letter.isdigit() or
           letter in ['\n', '.', '!', '?', ';']):
            if (letter == '.' and (result_text[-2:].isalpha() or
               result_text[-2:].isdigit())):
                result_text += ' . '
            elif letter in ['!', '?', ';']:
                result_text += ' . '
            else:
                if letter != '.' or (letter == '.' and result_text[-1] != '.'):
                    result_text += letter
        else:
            result_text += ' '
    result_text += '\n'
    return result_text


def MakeList(text):
    ''' Разделяет строку на слова и убирает точки вначале слов. '''

    print 'Making list of words...'

    text = text.lower()
    word_list = text.split()
    for i, element in enumerate(word_list):
        if len(element) > 1 and element[0] == '.':
            word_list[i] = element[1:]
    return word_list


def AnalizeWords(words):
    ''' Анализируются слова и для каждого слова и каждой пары слов составляется
        статистика слов встречающихся после него или них. Так же создается
        словарь со словами, которые могут стоять в начале предложения. '''

    print 'Analizing words...'

    first_words, after_word, after_words = [0, {}], {}, {}
    for i, word in enumerate(words):
        if i > 1:
            if words[i - 1] == '.':
                first_words[1].setdefault(word, 0)
                first_words[1][word] += 1
                first_words[0] += 1

            if words[i - 1] != '.':
                after_word.setdefault(words[i - 1], [0, {}])
                after_word[words[i - 1]][0] += 1

                after_word[words[i - 1]][1].setdefault(word, 0)
                after_word[words[i - 1]][1][word] += 1

            if words[i - 1] != '.' and words[i - 2] != '.':
                after_words.setdefault(words[i - 2] + ' ' + words[i - 1],
                                       [0, {}])
                after_words[words[i - 2] + ' ' + words[i - 1]][0] += 1

                after_words[words[i - 2] + ' ' +
                            words[i - 1]][1].setdefault(word, 0)
                after_words[words[i - 2] + ' ' + words[i - 1]][1][word] += 1
    return first_words, after_word, after_words


def DeliteBadWords(first_words, after_word, after_words):
    ''' Удаляет слова, встречающиеся один раз в тексте. '''

    print 'Deliting bad words...'

    for word, count in first_words[1].items():
        if count == 1:
            first_words[1].pop(word)
            first_words[0] -= 1

    for one_word, dictionary in after_word.items():
        if dictionary[0] == 1:
            after_word.pop(one_word)

    for two_words, dictionary in after_words.items():
        if dictionary[0] == 1:
            after_words.pop(two_words)

    return first_words, after_word, after_words


def MakeDistribution(first_words, after_word, after_words):
    ''' Для каждого слова и для каждо пары слов создает распределение слов,
        которые могу стоять после. А так же создает распределение слов,
        с которых предлоежние может начинаться. '''

    print 'Making distribution...'

    new_first_words = []
    current_distribution = 0
    for key, value in first_words[1].items():
        distribution = float(value) / first_words[0] + current_distribution
        current_distribution = distribution
        new_first_words.append((distribution, key))
    first_words = new_first_words

    for word, info in after_word.items():
        words_distribution = []
        current_distribution = 0
        for key, value in info[1].items():
            distribution = float(value) / info[0] + current_distribution
            current_distribution = distribution
            words_distribution.append((distribution, key))
        after_word[word] = words_distribution

    for word, info in after_words.items():
        words_distribution = []
        current_distribution = 0
        for key, value in info[1].items():
            distribution = float(value) / info[0] + current_distribution
            current_distribution = distribution
            words_distribution.append((distribution, key))
        after_words[word] = words_distribution

    return first_words, after_word, after_words


def PickleDistribution(first_words, after_word, after_words):
    ''' Сохраняет три группы распределений на диск. '''

    print 'Pickling data...'

    if 'words_distribution' not in os.listdir('./'):
        os.mkdir('words_distribution')

    with open('./words_distribution/sentences_begins.pkl', 'wb') as f:
        pickle.dump(first_words, f)

    with open('./words_distribution/after_word.pkl', 'wb') as f:
        pickle.dump(after_word, f)

    with open('./words_distribution/after_words.pkl', 'wb') as f:
        pickle.dump(after_words, f)


def LoadPickle():
    ''' Загружает распределения слов с диска. '''

    print 'Loading data...'

    with open('./words_distribution/sentences_begins.pkl', 'rb') as f:
        first_words = pickle.load(f)
    with open('./words_distribution/after_word.pkl', 'rb') as f:
        after_word = pickle.load(f)
    with open('./words_distribution/after_words.pkl', 'rb') as f:
        after_words = pickle.load(f)
    return first_words, after_word, after_words


def GenerateText(sentences_count, words_distribution):
    ''' Генерирует текст заданной длины. '''

    text = '\t'
    for paragraph_size in GenerateParagraphesSizes(sentences_count):
        text += GenerateParagraph(paragraph_size, words_distribution) + '\n\t'
    return text


def GenerateParagraphesSizes(sentences_count):
    ''' Разбивает колличество предложений на группы от 7 до 15. '''

    paragraphes_sizes = []
    while sentences_count > 0:
        paragraphes_sizes.append(min(sentences_count,
                                     random.choice(range(7, 15))))
        sentences_count -= paragraphes_sizes[-1]
    return paragraphes_sizes


def GenerateParagraph(paragraph_size, words_distribution):
    ''' Генерирует абзац с заданным колличеством предложений. '''

    paragraph = ''
    for _ in range(paragraph_size):
        paragraph += GenerateSentence(*words_distribution)
    return paragraph


def GenerateSentence(first_words, after_word, after_words):
    ''' Генерирует предложение в котором слов от 5 до 30. '''

    while True:
        sentence = []
        sentence.append(GenerateWord(first_words))
        while sentence[-1] != '.':
            if (len(sentence) > 2 and sentence[-2] + ' ' +
               sentence[-1] in after_words):
                sentence.append(GenerateWord(after_words[sentence[-2] + ' ' +
                                                         sentence[-1]]))
            elif sentence[-1] in after_word:
                sentence.append(GenerateWord(after_word[sentence[-1]]))
            else:
                break

        if 5 <= len(sentence) <= 30:
            sentence = MakeSentenceBeautiful(sentence)
            return sentence


def GenerateWord(words):
    ''' Генерирует рандомное слово из words. '''

    random_value = random.uniform(0, 1)
    for value, word in words:
        if value > random_value:
            return word
    return words[-1]


def MakeSentenceBeautiful(sentence):
    ''' Делает первую букву предложения заглавной, а так же соединяет
        сокращения и слова. Например из "I" и "m" сделает "I'm". '''

    sentence[0] = sentence[0].capitalize()
    for i, word in enumerate(sentence):
        if i > 0 and word in ['ve', 's', 'll', 'm', 't', 'd', 're']:
            sentence[i - 1] += '\'' + word
            sentence.pop(i)
        if word == 'i':
            sentence[i] = 'I'
    sentence = ' '.join(sentence[:-1])
    sentence += '. '
    return sentence


def main():
    answer = raw_input('Do you want to update corpus? (y/n) : ')
    if answer == 'y':
        MakeStatistic('corpus')
    words_distribution = LoadPickle()

    answer = 'y'
    while answer == 'y':
        while True:
            try:
                sentences_count = int(raw_input('How much sentences do you ' +
                                                'want do generate? : '))
                break
            except ValueError:
                print 'You input incorrect data. Try again.'
        text = GenerateText(sentences_count, words_distribution)
        with open('generated_text.txt', 'w') as f:
            f.write(text)
        while True:
            answer = raw_input('Do you want to generate' +
                               'anotherone text? (y/n) : ')
            if answer == 'y' or answer == 'n':
                break
            print 'You input incorrect data. Try again.'

if __name__ == '__main__':
    main()
