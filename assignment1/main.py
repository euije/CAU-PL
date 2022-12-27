import re
import string
import sys
from enum import Enum

class Token(Enum):
    EOF = 0
    SEMI_COLON = 1
    INT_LIT = 10
    IDENT = 11
    ASSIGN_OP = 20
    ADD_OP = 21
    SUB_OP = 22
    MULT_OP = 23
    DIV_OP = 24
    LEFT_PAREN = 25
    RIGHT_PAREN = 26

token_table = {
    "$" : Token.EOF,
    #"123": Token.INT_LIT, # "<const>",
    #"47": Token.INT_LIT, # "<const>",
    #"var": Token.IDENT,
    #"total": Token.IDENT,
    #"abc" : Token.IDENT, # "<ident>",
    #"sum" : Token.IDENT, # "<ident>",
    ":=" : Token.ASSIGN_OP, # "<assignment_op>",
    ';' : Token.SEMI_COLON, # "<semi_colon>",
    '+' : Token.ADD_OP, # "<add_operator>",
    '-' : Token.SUB_OP, # "<add_operator>",
    '*' : Token.MULT_OP, # "<mult_operator>",
    '/' : Token.DIV_OP, # "<mult_operator>",
    '(' : Token.LEFT_PAREN, # "<left_paren>",
    ')' : Token.RIGHT_PAREN # "<right_paren>"
}

reversed_token_table = dict(map(reversed, token_table.items()))

def ident():
    global next_token

    global parse
    global lexeme_i
    global lexeme_length
    global token_string

    global error_list

    preserved_list = [
        "asm", "auto", "break", "case", "char", "const", "continue", "default", "do",
        "double", "else", "else", "extern", "float", "for", "goto", "if", "int", "long", "register", "return",
        "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "void", "volatile", "while"
    ] # C언어 예약어
    num_start_re = re.compile('[0-9].+') # 숫자로 시작하는 변수
    only_alphabet_re = re.compile('[_|a-z|A-Z][_a-zA-Z0-9]{1,30}') # C언어 표준 규칙 30글자 이내

    # print("<ident> 시작", end="")

    cur_ident = parse[lexeme_i]
    # print(f" \"{cur_ident}\" ", end="")

    if next_token == Token.IDENT:
        for preserved in preserved_list:
            if preserved in parse[lexeme_i]:
                error_list.append(f"(WARNING) : 변수 이름 \"{cur_ident}\" 이 C언어 예약어가 포함 되어 정의 되어 있습니다")
        if num_start_re.fullmatch(parse[lexeme_i]) != None:
            error_list.append(f"(WARNING) : 변수 이름 \"{cur_ident}\" 이 숫자로 시작 하여 정의 되어 있습니다")
        if only_alphabet_re.fullmatch(parse[lexeme_i]) == None:
            error_list.append(f"(WARNING) : 변수 이름 \"{cur_ident}\" 이 C언어 작명 규칙을 따르지 않습니다")
    else: # 비정상적 <ident> 호출
        pass
        # print("<ident> 비정상 종료")

    # print("<ident> 종료")

    return None # Terminal 명시적 종료

def calculate_result():
    global parse
    global lexeme_i

    global ident_dict
    global error_list

    id = 1
    const = 0
    op = 0

    result = parse[0:lexeme_i]
    eval_str = ""

    for idx in range(2, len(result)):
        cur_token = token_table[parse[idx]]
        if cur_token == Token.IDENT:
            id += 1
            var_value = ident_dict.get(str(parse[idx]), "Unknown")
            if var_value == "Unknown":
                error_list.append(f"Error : 정의 되지 않은 변수 {parse[idx]}가 참조 됨")
                ident_dict[str(parse[idx])] = "Unknown"
                eval_str = "Unknown"
            else:
                parse[idx] = var_value
        elif cur_token == Token.INT_LIT:
            const += 1
        elif cur_token == Token.ADD_OP or cur_token == Token.SUB_OP or cur_token == Token.MULT_OP or cur_token == Token.DIV_OP:
            op += 1

    if eval_str != "Unknown":
        for i in parse[2:lexeme_i]:
            eval_str += str(i)
    ident_dict[str(parse[0])] = eval(eval_str) if eval_str != "Unknown" else eval_str

    for i in result: print(f"{i} ", end="") # 프로그램에서 읽은 라인
    print(f"\nID : {id}, CONST : {const}, OP : {op}") # ID, CONST, OP 개수
    if len(error_list) == 0: # 파싱 결과
        print("(OK)")
    else:
        for i in error_list:
            print(i)
    print("Result ==> ", ident_dict, end="\n\n") # 계산 결과

def statements():
    global parse
    global lexeme_length
    global lexeme_i
    global token_string

    global next_token

    global error_list
    global ident_dict

    # print("<statements> 시작")

    statement()
    calculate_result()
    if next_token == Token.SEMI_COLON:
        lexical()

        for i in range(0, lexeme_i):
            parse.pop(0)

        lexeme_length = len(parse)
        lexeme_i = -1
        token_string = ""
        next_token = Token.EOF
        error_list = []

        lexical()

        # update_parse() + init_vars()

        delete_token_extra("statements", [Token.SEMI_COLON])
        statements()
    elif next_token == Token.EOF:
        pass
        # print("<statements> 종료")
    else:
        pass
        # print("<statements> 비정상 종료")

def statement():
    global next_token

    global parse
    global token_string
    global lexeme_i
    global lexeme_length

    # print("<statement> 시작")

    delete_token_until_require("statement", [Token.IDENT, Token.ASSIGN_OP])
    if next_token == Token.IDENT:
        ident()
    else:
        insert_token(Token.IDENT)
    lexical()

    if next_token == Token.ASSIGN_OP:
        pass
        # print("<assign_op> 시작 종료")
    else:
        insert_token(Token.ASSIGN_OP)

    lexical()

    # 시작은 (, ident, const 가 only 케이스
    delete_token_until_require("statement", [Token.LEFT_PAREN, Token.IDENT, Token.INT_LIT])
    if next_token != Token.EOF:
        expression()
    #delete_token_until_require("statement", [Token.SEMI_COLON, Token.EOF])
    # print("<statement> 종료")

def expression():
    global next_token

    global parse
    global lexeme_length
    global lexeme_i
    global token_string

    # print("<expression> 시작")

    flag = term()
    while (next_token == Token.ADD_OP or next_token == Token.SUB_OP):
        lexical()
        flag = term()
        while flag != None:
            flag = term()

    # print("<expression> 종료")
    return flag

def term():
    global next_token

    global parse
    global lexeme_length
    global lexeme_i
    global token_string

    # print("<term> 시작")

    #flag = None

    flag = factor()
    while flag == None and (next_token == Token.MULT_OP or next_token == Token.DIV_OP):
        lexical()
        flag = factor()
        while flag != None:
            flag = factor()

    # print("<term> 종료")
    return flag

def factor() -> Token | None:
    global next_token

    global parse
    global token_string
    global lexeme_i
    global lexeme_length

    global error_list

    # print("<factor> 시작")

    if next_token == Token.IDENT:
        ident()
        lexical()
        delete_token_extra("factor", [Token.ASSIGN_OP, Token.IDENT, Token.INT_LIT])
    elif next_token == Token.INT_LIT:
        # print("<INT> 시작 종료")
        lexical()
        delete_token_extra("factor", [Token.ASSIGN_OP, Token.IDENT, Token.INT_LIT])
    elif next_token == Token.LEFT_PAREN:
        lexical()
        expression()
        if next_token == Token.RIGHT_PAREN:
            lexical()
        else:
            error_list.append("ERROR : ( 과 매칭 되는 ) 가 없습니다")
            error_list.append("ERROR : statement 후미에 )를 추가 하여 파스 트리 복구 및 계산을 진행합니다")
            for lex in range(0, len(parse)):
                if parse[lex] == ';' or parse[lex] == '$':
                    parse.insert(lex, ")")
                    lexeme_length += 1
    else:
        if next_token == Token.RIGHT_PAREN:
            error_list.append("WARNING : ) 과 매칭 되는 ( 가 없습니다")
        else:
            error_list.append("WARNING : 2개 이상의 중복 연산자를 사용하였습니다")
        temp = delete_next_token("factor")
        # print("<factor> 종료")
        return temp

    # print("<factor> 종료")
    return None

def lexical():
    global parse # 파싱한 lexeme List

    global token_string
    global lexeme_i

    global next_token

    # 1차 정규 표현식 확인
    #indent_re = re.compile('[a-z]+')
    const_re = re.compile('\u2212?\d+') # '(\u2212?\d+|\\u002B?\d+)' '+10은 invalid 인풋'

    # 크게 <ident> 와 <const>로 분류함.
    # <const>는 예외 없이 등록이 됨.
    # <indent>는 해당 함수에서 예외처리하여 ERROR 발생함.

    if lexeme_i == -1:
        token_string = "$"
    else:
        token_string = parse[lexeme_i]

    if token_table.get(parse[(lexeme_i + 1)], "Unknown") == "Unknown": # 연산자 및 EOF가 아니면 / 혹은 기존에 등록된 숫자 및 변수라
        if const_re.fullmatch(parse[lexeme_i + 1]) != None: # 숫자 확인
            token_table[parse[lexeme_i + 1]] = Token.INT_LIT # 숫자 등록
            next_token = Token.INT_LIT
        else: # 숫자도 아니다 -> <ident>로 1차 분류
            token_table[parse[lexeme_i + 1]] = Token.IDENT  # ident 등록
            next_token = Token.IDENT
    else:
        next_token = token_table.get(parse[lexeme_i + 1]) # 기존에 등록된 토큰 등록

    # print("Next token is : ", next_token, ", Next lexeme is : ", parse[lexeme_i + 1])

    lexeme_i += 1

def parser(input_string : string):
    global parse
    global lexeme_length

    global token_string
    global next_token

    #input_string = "operand1 := 3 ; operand2 := operand1 + 2 ; target := operand1 + operand2 * 3"
    #input_string = "operand2 := operand1 + 2 ; target := operand1 + operand2 * 3"
    #input_string = "operand1 := 1 ; operand2 := ( operand1 * 3 ) + 2 ; target := operand1 + operand2 * 3"
    #input_string = "operand1 := 3 ; operand2 := operand1 + + 2 ; target := operand1 + operand2 * 3"

    #input_string = "op1 := 10 + 2 ; op2 := 1 + 1"
    #inputString = input()
    #input_string = "var := ( sum + 47 / char123"
    #input_string = ":= sum ) abc := ) / + * ) / - * + / ) 47 ) / ) char123"
    #input_string = ":= ( sum num ) + - - - - - ) ) 47 / char123 ; ; := ( sum num ) + - - - - - ) ) 47 / char123 ;"

    # input_string = "var := ( 1 ) + ( sum ) ) + ) 47 ) / ) char123"

    parse = re.split('[\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008'
                     '\u0009\u000A\u000B\u000C\u000D\u000E\u000F\u0010\u0011'
                     '\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019'
                     '\u001A\u001B\u001C\u001D\u001E\u001F ]', input_string)
    parse.append("$")
    lexeme_length = len(parse)

    # print(parse)

def delete_next_token(cur_tree : string):
    global parse
    global lexeme_length
    global lexeme_i
    global next_token
    global token_string

    global error_list
    error_list.append(f"ERROR : <{cur_tree}>에서 파스 트리의 <{next_token}>를 제거합니다")
    error_list.append(f"ERROR : {parse[lexeme_i]}를 제거하며 파스 트리를 복구 및 계산합니다")

    # print(parse)
    # print("before :", lexeme_i, next_token, lexeme_length, token_string)

    lexeme_length -= 1
    temp = parse.pop(lexeme_i)
    lexeme_i -= 1
    lexical()

    # print(parse)
    # print("after :", lexeme_i, next_token, lexeme_length, token_string)
    return temp

def delete_token_until_require(cur_tree : string, require_token_list : list[Token]):
    global parse
    global lexeme_length
    global lexeme_i
    global next_token

    global error_list

    while next_token not in require_token_list:
        if next_token == Token.EOF:
            return False

        error_list.append(f"ERROR : <{cur_tree}>에서 <{next_token}>이 <{require_token_list}>가 아닙니다")
        error_list.append(f"ERROR : {parse[lexeme_i]}를 제거하며 파스 트리를 복구 및 계산합니다")

        # print(parse)
        # print("before :", lexeme_i, next_token, lexeme_length, token_string)

        parse.pop(lexeme_i)
        lexeme_length -= 1
        lexeme_i -= 1
        lexical()

        # print(parse)
        # print("after :", lexeme_i, next_token, lexeme_length, token_string)

    return True

def delete_token_extra(cur_tree : string, extra_list : list[Token]):
    global parse
    global lexeme_length
    global lexeme_i
    global next_token

    global error_list

    while next_token in extra_list:
        error_list.append(f"ERROR : <{cur_tree}>의 현재 위치에서 <{extra_list}>가 추가로 존재합니다")
        error_list.append(f"ERROR : <{extra_list}>를 제거하며 파스 트리를 복구 및 계산합니다")

        # print(parse)
        # print("before :", lexeme_i, next_token, lexeme_length, token_string)

        parse.pop(lexeme_i)
        lexeme_length -= 1
        lexeme_i -= 1
        lexical()

        # print(parse)
        # print("after :", lexeme_i, next_token, lexeme_length, token_string)

def insert_token(token : Token): # token을 next_token의 앞에 삽입합니다.
    global parse
    global lexeme_length
    global lexeme_i
    global next_token
    global token_string

    global error_list

    error_list.append(f"ERROR : <{token}> 가 없습니다")
    error_list.append(f"ERROR : <{token}> 를 삽입하여 파스 트리를 복구합니다")

    # print(parse)
    # print("before :", lexeme_i, next_token, lexeme_length, token_string)

    inserted_token = "ErrorVar" if token == Token.IDENT else reversed_token_table[token]

    parse.insert(lexeme_i, inserted_token)
    lexeme_length += 1
    token_string = ":="

    # print(parse)
    # print("after :", lexeme_i, next_token, lexeme_length, token_string)

############ 전역 변수 ############

parse = []
lexeme_length = 0

lexeme_i = -1
token_string = ""

next_token = Token.EOF

error_list = []
ident_dict = {}

############ 전역 변수 ############

def main():
    input = ""

    file_path = sys.argv[1]

    if len(sys.argv) != 2:
        print("Insufficient arguments")
        sys.exit()

    f = open(file_path, 'r')
    lines = f.readlines()
    for line in lines:
        input += str(line)

    parser(input)

    # print("<program> 시작")

    lexical()
    statements()

    # print("<program> 종료")
    f.close()

if __name__ == "__main__":
    main()
