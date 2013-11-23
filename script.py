__author__ = 'Gor'
import re

vowel = list('іїиеєаяоую')
consonant = list('йцкнгшщзхфвпрлджчсмтб')
ends = {1:vowel,
          2:['ою','ею','єю','ам','ах','ям','ях','ом','ів','ем','ей','ми','ій','іх'],
          3:['ами','ями','ові','еві','има']}

class UaNounLemma:
    def __init__(self, input_file, output_file):
        self.input = input_file
        self.output = output_file
        self.process()

    def tokenize(self):
        file = open(self.input, encoding='utf-8').read().lower()
        file = re.sub('[0-9A-zь\'\"`]', '', file)
        return re.findall('\w+', file)

    def noun_lemma(self,noun):
        lenght = len(noun)
        if lenght <= 3: return noun, ''
        elif any(noun.endswith(i) for i in consonant if i not in 'мхвй'): return noun, ''
        elif lenght >= 6 and any(noun.endswith(i) for i in ends[3]): return noun, noun[:-3], noun[-3:]
        elif lenght >= 5 and any(noun.endswith(i) for i in ends[2]): return noun, noun[:-2], noun[-2:]
        elif any(noun.endswith(i) for i in ends[1]): return noun, noun[:-1], noun[-1:]
        else: return noun, "!!!НЕ ОПИСАННЫЙ СЛУЧАЙ!!!"

    def process(self):
        file = open(self.output, 'w')
        for i in self.tokenize():
            file.write('\t'.join(self.noun_lemma(i))+'\n')
        file.close()

a = UaNounLemma('input.txt', 'output.txt')
