import re
from enum import Enum

class Token(Enum):
    EOF = 0
    SEMI_COLON = 1
    COMMA = 2
    IDENT = 11
    CALL = 12
    VARIABLE = 13
    PRINT_ARI = 14
    LEFT_BRACKET = 25
    RIGHT_BRACKET = 26

token_table = {
    "$" : Token.EOF,
    "call" : Token.CALL,
    "variable" : Token.VARIABLE,
    "print_ari" : Token.PRINT_ARI,
    ';' : Token.SEMI_COLON, # "<semi_colon>",
    ',' : Token.COMMA,
    '{' : Token.LEFT_BRACKET, # "<left_paren>",
    '}' : Token.RIGHT_BRACKET # "<right_paren>"
}

def flatten(list: list) -> list:
    result = []
    for item in list:
        if type(item) is str:
            result.append(item)
        else:
            result.extend(item)
    return result

class lexical_analyzer:
    def __init__(self):
        self.parse = [] # 파싱한 lexeme List

        self.lexeme_i = -1
        self.lexeme = ""

        self.next_lexeme = "$"
        self.next_token = Token.EOF

        self.ident_list = []

        self.error_list = []

    def is_valid_identifier(self, lexeme: str) -> bool:
        preserved_list = [
            "asm", "auto", "break", "case", "char", "const", "continue", "default", "do",
            "double", "else", "else", "extern", "float", "for", "goto", "if", "int", "long", "register", "return",
            "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "void", "volatile", "while"
        ]  # C언어 예약어
        num_start_re = re.compile('[0-9].+')  # 숫자로 시작하는 변수
        only_alphabet_re = re.compile('[_|a-z|A-Z][_a-zA-Z0-9]{0,100}')  # 길이 제한 없음 -> 100글자 이내로

        for preserved in preserved_list:
            if preserved in lexeme:
                self.error_list.append("<identifier>가 C언어 예약어가 포함 되어 정의 되어 있습니다")
                return False
        if num_start_re.fullmatch(lexeme) != None:
            self.error_list.append("<identifier>가 숫자로 시작 하여 정의 되어 있습니다")
            return False
        if only_alphabet_re.fullmatch(lexeme) == None:
            self.error_list.append("<identifier>가 C언어 작명 규칙을 따르지 않습니다 \n https://learn.microsoft.com/en-us/cpp/c-language/c-identifiers?view=msvc-170#syntax 를 참조하세요")
            return False

        return True

    def get_token(self, lexeme: str):
        if token_table.get(lexeme, "Unknown") == "Unknown": # 1차 정의된 Token 확인
            if self.ident_list.count(lexeme) == 0: # ident 확인
                if self.is_valid_identifier(lexeme):
                    self.ident_list.append(lexeme)
                    return Token.IDENT
                else:
                    return None
            else: return Token.IDENT
        else: # 1차 정의된 Token에 있으면
           return token_table.get(lexeme) # 기존에 등록된 토큰 리턴

    def lexical(self):
        self.lexeme_i += 1

        self.lexeme = self.parse[self.lexeme_i]

        self.next_lexeme = self.parse[self.lexeme_i + 1]
        self.next_token = self.get_token(self.next_lexeme)

        # print("Next token is : ", self.next_token, ", Next lexeme is : ", self.next_lexeme)

    def parse_to_lexeme(self, input_string : str):
        self.parse = re.split('[\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008\u0009\u000A\u000B\u000C\u000D\u000E\u000F'
                              '\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019\u001A\u001B\u001C\u001D\u001E\u001F\t ]'
                              , input_string)

        self.parse = [lex for lex in self.parse if lex != ""] # 공스트링 제거
        temp = []
        temp.extend(self.parse)
        for idx, lex in enumerate(self.parse): # ';', ',' lexeme화
            if ';' in lex or ',' in lex:
                start = 0
                partial_lex = []

                for i in range(0, len(lex)):
                    if lex[i] == ',':
                        partial_lex.append(lex[start:i])
                        partial_lex.append(',')
                        start = i + 1
                    elif lex[i] == ';':
                        partial_lex.append(lex[start:i])
                        partial_lex.append(';')
                        start = i + 1

                temp.pop(idx)
                temp.insert(idx, partial_lex)
        self.parse = flatten(temp)

        self.parse.append("$") # EOF 추가

        # 첫 next 설정
        self.next_lexeme = self.parse[0]
        self.next_token = self.get_token(self.next_lexeme)