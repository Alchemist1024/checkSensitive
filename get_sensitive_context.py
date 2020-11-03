# -*- encoding: utf-8 -*-
'''
@File        :get_sensitive_context.py
@Time        :2020/11/03 15:43:36
@Author      :xiaoqifeng
@Version     :1.0
@Contact:    :unknown
'''

from check_sensitive import DFAUtils
from typing import List, Dict, Text


MinMatchType = 1 
MaxMatchType = 2
sensitive_lexicon = ['王八蛋', '王八羔子']

def get_context(text: Text, matchType: int=MinMatchType) -> Text:
    '''获取敏感词的上下文，供后续的模型训练。
    Args:
        text: 长文本
        matchType: 匹配方式
    Returns:
        上下文信息'''
    stop_token = ['；', '。']
    dfa = DFAUtils(sensitive_lexicon)
    _, sensitive_span = dfa.getSensitiveWord(text, matchType)
    true_start, true_end = sensitive_span[0][0], sensitive_span[-1][-1]
    context_start, context_end = 0, 0
    if not sensitive_span:
        print('不需要处理')
    else:
        for i in range(true_start, -1, -1):
            if text[i] in stop_token:
                context_start = i
                break
        
        for i in range(true_end, len(text)):
            if text[i] in stop_token:
                context_end = i
                break

    return text[context_start + 1: context_end + 1]


if __name__ == '__main__':
    text = '一位官员坐计程车。下车时，特别从皮夹中拿出一张新钞票付给司机：王八羔子，“我想你和一般人一样，喜欢干净的钱。”司机接过钞票端详了一会说：“其实，王八蛋，我并不在乎你的钱是怎么来的。”'
    print(get_context(text))