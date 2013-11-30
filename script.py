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

class Syllabys:
    '''1. Один приголосний, що стоїть між голосними, завжди належить до наступного складу, наприклад: во-да, пе-ре-вал.
    2. Два шумні (обидва дзвінкі або обидва глухі) приголосні належать звичайно до наступного складу, наприклад: ті-сто, во-ско-вий, ді-жда-ти-ся.
    3. Два шумні (дзвінкі або глухі) приголосні, один з яких дзвінкий, а другий глухий, належать до різних складів, наприклад: рід-ко, каз-ка, греб-ти.
    4. Три приголосні, якщо перші два з них шумні (обидва дзвінкі або обидва глухі), а третій сонорний, належать до наступного складу, наприклад: ві-стря, за-шкли-ти, за-здро-щі.
    5. Якщо між голосними є два або більше приголосних, то сонорні звуки, що йдуть після голосного, належать до попереднього складу, а звуки, що стоять після них, – до наступного: кой-ка, май-стру-ва-ти, стов-пи, муль-ко, сум-ка, кон-то-ра.
    6. Якщо другим приголосним є сонорний, то разом з попереднім він належить до наступного складу: по-свист, ко-бра, ку-пля, по-смі-шка, пі-зній.
    7. Два сусідні сонорні приголосні належать до різних складів: мар-но, став-ний, зер-но, віль-но, гор-ло.
    8. Подовжені приголосні при складоподілі можуть розриватися: об-би-ти, зіл-ля, маз-зю.'''
    def __init__(self):
        self.dzv = list('бджзґ')
        self.glh = list('пткшщсхчцгф')
        self.snr = list('вмнлрй')
        self.glsn = list('іїиеєаяоую')

    def tokenize(self, text):
        file = re.sub('[0-9A-zь\'\"`’]', '', text.lower())
        return re.findall('\w+', file)

    def sklady(self, word):
        if len(word) <= 2: return word
        skl, word = word[0], word[1:]
        while skl[-1] not in self.glsn and len(word)>0:
            skl += word[0]
            word = word[1:]
        if all(i not in self.glsn for i in word):
            return skl+word
        elif skl in self.glsn and word[0] not in self.glsn:
            skl += word[0]+'-'+self.sklady(word[1:])
        elif len(word) <= 1:
            return skl+word
        elif word[0] not in self.glsn and word[1] in self.glsn:
            skl += '-'+self.sklady(word)
        elif word[0] in self.glsn:
            while len(word)>0 and word[0] in self.glsn:
                skl += word[0]
                word = word[1:]
            skl = skl[:-1]+'-'+self.sklady(skl[-1]+word)
        else:
            while word[0] not in self.glsn:
                skl += word[0]
                word = word[1:]
            if all(i not in skl[-3:] for i in self.glsn):
                if skl[-1] in self.snr and (all(i in self.dzv for i in word[-3:-1]) or all(i in self.glh for i in word[-3:-1])):
                    skl = skl[:-3]+'-'+self.sklady(skl[-3:]+word)
                else:
                    end = re.split(str('|'.join(self.glsn)), skl.replace('-', ''))[-1]
                    skl = skl[:-len(end)]
                    if end[0] in self.snr:
                        while len(end)>0 and end[0] in self.snr and not skl.endswith('й'):
                            skl += end[0]
                            end = end[1:]
                        skl += '-'+self.sklady(end+word)
                    else:
                        if len(end) == 3 and end[-1] in self.snr and (all(i in self.glh for i in end[:-1]) or all(i in self.dzv for i in end[:-1])):
                            skl += '-'+self.sklady(end+word)
                        else:
                            while (all(i in self.dzv for i in end[-2:]) or all(i in self.glh for i in end[-2:]) or all(i in self.snr for i in end[-2:])) and len(end) > 0:
                                word = end[-1:]+word
                                end = end[:-1]
                            try: skl += end[:-1]+'-'+self.sklady(end[-1]+word)
                            except: skl += '-'+self.sklady(word)
            else:
                if skl[-2]==skl[-1]:
                    skl = skl[:-2]+'-'+self.sklady(skl[-2:]+word)
                elif skl[-1] in self.snr and skl[-2] not in self.snr:
                    skl = skl[:-2]+'-'+self.sklady(skl[-2:]+word)
                elif all(i in self.snr for i in skl[-2:]):
                    skl = skl[:-1]+'-'+self.sklady(skl[-1:]+word)
                elif (skl[-1]in self.dzv and skl[-2]in self.dzv) or (skl[-1] in self.glh and skl[-2] in self.glh):
                    skl = skl[:-2]+'-'+self.sklady(skl[-2:]+word)
                elif ((skl[-1] not in self.dzv and skl[-2] in self.dzv) or (skl[-1] in self.dzv and skl[-2] not in self.dzv)) and skl[-2] not in self.snr:
                    skl = skl[:-1]+'-'+self.sklady(skl[-1:]+word)
                elif skl[-2] in self.snr and skl[-1] not in self.snr:
                    skl = skl[:-1]+'-'+self.sklady(skl[-1:]+word)
        return skl

    def syllabyze(self, word):
        return self.sklady(re.sub('[ь\'\"`’]', '', word)).split('-')
