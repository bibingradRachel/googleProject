from database.auto_complete_database import AutoCompleteDatabase

import re

from get_best_k_completions.menipulation import Menipulation


class Scores:
    def __init__(self):
        self.__database = AutoCompleteDatabase()
        self.__scores = {}
        self.__sen_content = {}
        self.__regex = re.compile('[^a-zA-Z0-9]')

    def clean_sentence(self, sen):
        return self.__regex.sub('', sen).lower()

    def get_clean_sentence(self, sen_id):
        return self.clean_sentence(self.__database.get_sen(sen_id)['sentence'])

    @staticmethod
    def insert_efficient_score(sentence, index, new_score, word_scores, word_indexes):
        if sentence not in word_scores:
            word_scores[sentence] = new_score
            word_indexes[sentence] = index
        else:
            if new_score > word_scores[sentence]:
                word_scores[sentence] = new_score
                word_indexes[sentence] = index

    def manipulation_word_scores(self, manipulation, manipulation_score, word_scores, word_indexes):
        sens_contain_manipulation = self.__database.get_word(manipulation.lower())
        for sen_contain_manipulation in sens_contain_manipulation:
            self.insert_efficient_score(sen_contain_manipulation, manipulation, manipulation_score, word_scores,
                                        word_indexes)

    def manipulations_word_scores(self, word, word_scores={}, word_indexes={}):
        word_manipulation = Menipulation().menipulation(word)
        for man_word, score in word_manipulation.items():
            self.manipulation_word_scores(man_word, score, word_scores, word_indexes)
        return word_scores, word_indexes

    def get_best_k_completions(self, query: str):
        sen_contain_fill_query = []
        self.__scores = {}
        self.__sen_content = {}
        query_words = query.split()
        query_length = len(query_words)

        for i in range(len(query_words)):
            tmp_scores = {}
            tmp_content = {}
            word = query_words[i]
            word_scores, word_indexes = self.manipulations_word_scores(word, {}, {})
            for sen_contain_word_man, contain_word_man_score in word_scores.items():
                if i == 0:
                    tmp_scores[sen_contain_word_man] = contain_word_man_score
                    tmp_content[sen_contain_word_man] = [word_indexes[sen_contain_word_man]]
                    # self.__scores[sen_contain_word_man] = contain_word_man_score
                    # self.__sen_content[sen_contain_word_man] = [word_indexes[sen_contain_word_man]]
                elif sen_contain_word_man in self.__scores:
                    # if not prev or sen_contain_word_man in prev:
                    tmp_scores[sen_contain_word_man] = self.__scores[sen_contain_word_man] + contain_word_man_score
                    tmp_content[sen_contain_word_man] = self.__sen_content[sen_contain_word_man] + [
                        word_indexes[sen_contain_word_man]]
            self.__scores = tmp_scores
            self.__sen_content = tmp_content
        # increase
        for sen_index, content in self.__sen_content.items():
            cleaned_query = self.clean_sentence(''.join(content))
            cleaned_sentence = self.get_clean_sentence(sen_index)
            if cleaned_query in cleaned_sentence:
                sen_contain_fill_query.append(sen_index)
                self.__scores.pop(sen_index)
                if len(sen_contain_fill_query) == 5:
                    break
        worse_sen = sorted(self.__scores, key=self.__scores.get, reverse=True)[:5 - len(sen_contain_fill_query)]
        return [self.__database.get_sen(item) for item in
                sen_contain_fill_query + worse_sen]
