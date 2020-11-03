# -*- encoding: utf-8 -*-
'''
@File        :check_sensitive.py
@Time        :2020/11/03 10:09:51
@Author      :xiaoqifeng
@Version     :1.0
@Contact:    :unknown
'''

from typing import List, Dict, Text, Union


MinMatchType = 1  # 最小匹配规则，如：敏感词库["中国", "中国人"]，语句："我是中国人"，匹配结果：我是[中国]人
MaxMatchType = 2  # 最大匹配规则，如：敏感词库["中国", "中国人"]，语句："我是中国人"，匹配结果：我是[中国人]

class DFAUtils(object):
    '''DFA算法实现敏感词过滤
    '''
    def __init__(self, sensitive_lexicon: List[Text]) -> None:
        '''算法初始化
           完成DFA hash表的构建
           Args:
                sensitive_lexicon:敏感词库
           Returns:
                None
        '''
        self.lexicon = {} # 词库，DFA的词库是通过hash的形式存储
        self.meaningless_lexicon = [' ', '&', '!', '！', '@', '#', '$', '￥', '*', '^', 
        '%', '?', '？', '<', '>', "《", '》'] # 无意义词库，在检测中要跳过
        # 初始化词库，以单词为单位，每次构建一个word的hash的时候都是从根节点开始构建，也就是从最外层的字典开始。
        for word in sensitive_lexicon:
            self.add_word(word)

    def add_word(self, word: Text) -> None:
        '''构建hash词库
           Args:
                Text
           Returns:
                None
        '''
        cur_node = self.lexicon
        token_cnt = len(word)
        for i in range(token_cnt):
            token = word[i]
            if token in cur_node.keys() and i < token_cnt - 1: # 对于新词的判断
                # 如果存在key，直接赋值，用于下一个循环获取
                cur_node = cur_node[word[i]]
                cur_node['is_end'] = False
            elif token in cur_node.keys() and i == token_cnt - 1:
                cur_node = cur_node[word[i]]
                cur_node['is_end'] = True
            else:
                # 不存在则构建一个dict
                new_node = {}

                if i == token_cnt - 1:
                    new_node['is_end'] = True
                else:
                    new_node['is_end'] = False

                cur_node[token] = new_node
                cur_node = new_node

    def checkSensitiveWord(self, txt: Text, begin_index: int, match_type: int=MinMatchType) -> Union[bool, int]:
        '''检查文字中是否包含敏感字符，这是个辅助函数，表示从txt的begin_index开始检测句子中是否有敏感词，其中begin_index必须为敏感词的开始。
           Args:
               txt: 待检测文本
               begin_index: 从某个字开始后面有没有敏感词，文本检测的开始。
               match_type: 匹配规则 1：最小匹配规则 2：最大匹配规则
           Returns:
               如果存在，则返回匹配字符串的长度，不存在返回0
        '''
        flag = False
        match_len = 0 # 匹配字符的长度
        cur_map = self.lexicon
        tmp_flag = 0 # 包括特殊字符的敏感词的长度

        for i in range(begin_index, len(txt)):
            token = txt[i]

            if token in self.meaningless_lexicon and len(cur_map) < 100: # 检查是否是特殊字符，eg"法&&轮&功..."
                # len(cur_map) < 100 保证已经找到这个词的开头之后出现的特殊字符
                # eg"情节中,法&&轮&功..."这个逗号不会被检测
                tmp_flag += 1
                continue

            # 获取指定key
            cur_map = cur_map.get(token)
            if cur_map: # 存在，则判断是否为最后一个
                # 找到相应key，匹配标识+1
                match_len += 1
                tmp_flag += 1
                # 如果为最后一个匹配规则，结束循环，返回匹配标识数
                if cur_map.get('is_end'):
                    # 结束标志位为true
                    flag = True
                    # 最小规则，直接返回,最大规则还需继续查找
                    if match_type == MinMatchType:
                        break
            else: # 不存在，直接返回
                break
        
        if tmp_flag < 2 or not flag: # 长度必须大于等于1，为词
            tmp_flag = 0

        return tmp_flag

    def is_contains(self, txt: Text, matchType: int=MinMatchType) -> bool:
        '''判断文字是否包含敏感字符
        Args:
            txt: 待检测文本
            matchType: 匹配规则 1: 最小匹配规则 2: 最大匹配规则
        Returns:
            若包含返回true，否则返回false
        '''
        flag = False
        for i in range(len(txt)):
            matchFlag = self.checkSensitiveWord(txt, i, matchType)
            if matchFlag > 0:
                flag = True

        return True

    def getSensitiveWord(self, txt: Text, matchType: int=MinMatchType) -> List[Text]:
        '''获取文本中的敏感词
        Args:
            txt: 待检测文本
            matchType: 匹配规则 1: 最小匹配规则 2: 最大匹配规则
        Returns:
            文本中的敏感词
        '''
        sensitiveWordList = []
        sensitive_span = []
        for i in range(len(txt)):
            length = self.checkSensitiveWord(txt, i, matchType)
            if length > 0:
                sensitiveWord = txt[i: i+length]
                sensitiveWordList.append(sensitiveWord)
                sensitive_span.append([i, i+length])
                i = i + length

        return sensitiveWordList, sensitive_span

    def replaceSensitiveWord(self, txt: Text, replaceChar: Text, matchType: int=MinMatchType) -> Text:
        '''把敏感字符替换成其他字符
        Args:
            txt: 待检测文本
            replaceChar: 用于替换的字符，匹配的敏感词以字符逐个替换，如"你是大王八"，敏感词"王八"，替换字符*，替换结果"你是大**"
            matchType: 匹配规则 1: 最小匹配规则 2: 最大匹配规则
        Returns:
            替换敏感字符后的文本'''
        sensitiveWordList, _ = self.getSensitiveWord(txt, matchType)
        resultTxt = ''
        if len(sensitiveWordList) > 0:
            for word in sensitiveWordList:
                replaceString = len(word) * replaceChar
                resultTxt = txt.replace(word, replaceString)
        else:
            resultTxt = txt

        return resultTxt


if __name__ == '__main__':
    test = ['王八羔子', '王八蛋']
    a = DFAUtils(test)
    print(a.lexicon)
    print(a.getSensitiveWord('你是王八蛋王八羔子'))