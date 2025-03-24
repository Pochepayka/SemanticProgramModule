import re
from typing import List, Tuple


class GraphematicAnalyzer:
    def __init__(self):
        self.text = ""
        self.tokens = []
        self.special_chars = {
            ' ': '␣',
            '\t': '→',
            '\n': '↵'
        }
        # Списки союзов
        self.subordinating_conjunctions = [
            "что", "чтобы", "как", "когда", "если", "хотя", "потому что",
            "так как", "несмотря на то что", "в то время как", "пока",
            "лишь", "будто", "чем", "дабы", "словно", "едва",
            "как будто", "ибо", "оттого что", "для того чтобы",
            "тогда как", "затем что", "по мере того как", "с тех пор как"
        ]
        self.coordinating_conjunctions = [
            "и", "а", "но", "да", "или", "либо", "тоже",
            "также", "не только, но и", "как...так и",
            "то ли...то ли", "или...или", "да и",
            "однако", "зато", "притом", "причем"
        ]

    def analyze(self, text) -> List[Tuple[str, str]]:
        self.text = text
        self.tokenize()
        self.process_contextual_descriptors()
        self.detect_sentences()
        return self.format_results()

    def tokenize(self):
        conjunction_pattern = r'\b(?:' + '|'.join(
            re.escape(conj) for conj in self.subordinating_conjunctions + self.coordinating_conjunctions) + r')\b'

        patterns = [
            (conjunction_pattern, 'CONJ'),  # Союзы
            (r'(?i)(https?://|www\.)\S+', 'URL'),
            (r'\b[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}\b', 'EA'),
            (r'(?:[a-zA-Z]:\\|\\\\|/)[^\s\\/]*(?:/[^\s\\/]*)*', 'FILE'),
            (r'\b\d+[a-zA-Z]+\w*\b', 'DSC'),
            (r'\d+(?:[.,]\d+)*', 'DC'),
            (r'[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*', 'RLE'),
            (r'[A-Za-z]+(?:-[A-Za-z]+)*', 'LLE'),
            (r'[!?.]+', 'PUN'),
            (r'[«»"“”‘’\'()\[\]{}—–−-]', 'PUN'),  # Все виды кавычек и дефисов
            (r'\s+', 'DEL/SPC'),
            (r'\n', 'DEL/EOLN'),
            (r'\t', 'DEL/TAB'),
            (r'[:;,]', 'PUN'),
            (r'[!?#$%^&*=+~]', 'GRAUNK'),
        ]

        position = 0
        text_len = len(self.text)
        while position < text_len:
            for pattern, token_type in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                match = regex.match(self.text, position)
                if match:
                    value = match.group(0)
                    main_type = token_type.split('/')[0]
                    sub_type = self.get_subtype(value, main_type)

                    # Проверяем на союзы
                    if value.lower() in self.subordinating_conjunctions:
                        main_type = 'SUB_CONJ'
                    elif value.lower() in self.coordinating_conjunctions:
                        main_type = 'COORD_CONJ'

                    self.tokens.append({
                        'text': value,
                        'descriptors': [main_type] + ([sub_type] if sub_type else []),
                        'start': position,
                        'end': position + len(value)
                    })
                    position += len(value)
                    break
            else:
                position += 1

    def get_subtype(self, text: str, token_type: str) -> str:
        if token_type in ('RLE', 'LLE'):
            if text.isupper():
                return 'AA'
            elif text[0].isupper() and text[1:].islower():
                return 'Aa'
            elif text.islower():
                return 'aa'
        elif token_type == 'DEL':
            if '\n' in text:
                return 'EOLN'
            elif text.isspace():
                return 'SPC'
        elif token_type == 'PUN':
            if text in '([{«“':
                return 'OPN'
            elif text in ')]}»”':
                return 'CLS'
            elif text in ('-', '—'):
                return 'HYP'
            elif text in (':'):
                return 'COL'
            if len(text) > 1:
                return 'PLP' if len(text) <= 20 else 'DPUN'
        return ''

    def process_contextual_descriptors(self):
        if self.tokens:
            self.tokens[0]['descriptors'].append('BEG')

        for i, token in enumerate(self.tokens):
            descriptors = token['descriptors']
            text = token['text']

            if text == ';':
                descriptors.append('EOP')

            if descriptors[0] in ('RLE', 'LLE') and 'Aa' in descriptors:
                prev_has_sent_end = False
                for prev_token in reversed(self.tokens[:i]):
                    if prev_token['descriptors'][0] not in ('DEL', 'PUN'):
                        prev_has_sent_end = 'SENT_END' in prev_token['descriptors']
                        break
                if not prev_has_sent_end:
                    descriptors.append('NAM?')

    def detect_sentences(self):
        quote_stack = []
        for i, token in enumerate(self.tokens):
            text = token['text']
            desc = token['descriptors']

            if any(t in desc for t in ['URL', 'EA', 'FILE']):
                continue

            if self.is_sentence_end_mark(text):
                next_idx = i + 1
                if next_idx < len(self.tokens) and self.tokens[next_idx]['text'] in '”’"\'»':
                    self.tokens[next_idx]['descriptors'].append('SENT_END')
                else:
                    token['descriptors'].append('SENT_END')

            if text in """«“‘"'""":
                quote_stack.append(text)
            elif text in """»”’"'""" and quote_stack:
                quote_stack.pop()

    def is_sentence_end_mark(self, text: str) -> bool:
        return any(c in text for c in '.!?') and not text.startswith('...')

    def format_results(self) -> List[Tuple[str, str]]:
        formatted = []
        for token in self.tokens:
            # Заменяем только пробельные символы
            processed_text = token['text'].translate(
                str.maketrans(self.special_chars)
            )
            desc = ' '.join(token['descriptors'])
            formatted.append((processed_text, desc))
        return formatted


# Пример использования
if __name__ == "__main__":

    text = """
    Когда солнце взошло, мы отправились в путь, и дорога оказалась удивительно красивой. 
    http://ya.ru www.youtube.com ya@ya.com. Осень. Иван ушёл. Мама кричала: 'Вернёшься?!' Вечер - чудесное время!
    """

    analyzer = GraphematicAnalyzer()
    results = analyzer.analyze(text)

    print("\nГрафематический анализ:")
    for graphem in results:
        print(f"{graphem[0]}\t{graphem[1]}")