from lexical_analyzer import Token
from lexical_analyzer import lexical_analyzer

class syntax_analyzer:
    def __init__(self, lexical_analyzer: lexical_analyzer):
        self.lex = lexical_analyzer
        self.is_accept = True

        self.activation_record = {}
        self.statement_record = {}

        self.error_list = []

    def alert_error(self, where: str, exception: str):
        # print(f"<{where}> 비정상 종료")
        self.error_list.append(exception)
        self.is_accept = False

    def generate_parse_tree(self) -> bool:
        # print("<start> 시작")

        self.functions()

        # print("<start> 종료")

        if self.activation_record.get("main", "Unknown") == "Unknown":
            self.error_list.append("No starting function.")
            self.is_accept = False

        return self.is_accept

    def functions(self): # 시작 조건 : 없음, 중간 조건 : 없음, 종료 조건 : EOF
        # print("<functions> 시작")

        self.function()
        while self.lex.next_token == Token.IDENT: # (로직의 단순화를 위해 재귀 콜스택 평탄화 수행)
            if self.is_accept == False:
                return
            self.function()

        if self.lex.next_token == Token.EOF:
            # print("<functions> 종료")
            pass
        else:
            # print("<functions> 비정상 종료")
            return

    def function(self): # 시작 조건 : ident, 중간 조건 : {, 종료 조건 : }
        # print("<function> 시작")

        if self.lex.next_token == Token.IDENT:
            function_name = self.identifier('function')
        else:  # ident 필수
            self.alert_error("function", "<function>의 첫번째 요소에 <identifier>가 없습니다")
            return

        if self.lex.next_token == Token.LEFT_BRACKET:
            self.lex.lexical()

            self.var_definition(function_name)
            while self.lex.next_token == Token.VARIABLE: # (로직의 단순화를 위해 재귀 콜스택 평탄화 수행)
                self.var_definition(function_name)

            while (self.lex.next_token == Token.CALL
                   or self.lex.next_token == Token.PRINT_ARI
                   or self.lex.next_token == Token.IDENT): # (로직의 단순화를 위해 재귀 콜스택 평탄화 수행)
                self.statement(function_name)

        else: # '{' 필수
            self.alert_error("function", "<function>의 두번째 요소에 \'{\'가 없습니다")
            return

        if self.lex.next_token == Token.RIGHT_BRACKET:
            self.lex.lexical()
        else:  # '}' 필수
            self.alert_error("function", "<function>의 두번째 요소에 \'}\'가 없습니다")
            return

        # print("<function> 종료")

    def var_definition(self, function_name: str):
        # print("<var_definition> 시작")

        if self.lex.next_token == Token.VARIABLE:
            self.lex.lexical()

            if self.lex.next_token == Token.IDENT:
                local_var = self.identifier('var_definition')
                if self.activation_record.get(local_var, "Unknown") != "Unknown":  # 변수 명이 함수 명과 같이 정의 케이스 예외 처리
                    self.error_list.append(f"Duplicate declaration of the identifier or the function name: \'{local_var}\'")
                    return  # 중복 시 에러 출력 후 종료
                else: # 첫 지역 변수 정의 시, 같은 함수 내 변수 중복 정의 상황이 일어 날 수 없음.
                    self.activation_record[function_name].append(local_var)
            else: # ident 1개 필수
                self.alert_error("var_definition", "<var_definition>의 두번째 요소에 <identifier>가 없습니다")
                return

            while self.lex.next_token == Token.COMMA:
                self.lex.lexical()

                if self.lex.next_token == Token.IDENT:
                    local_var = self.identifier('var_definition')

                    if self.activation_record[function_name].count(local_var) != 0: # 같은 함수 내 변수 중복 정의 예외 처리
                        self.error_list.append(f"Duplicate declaration of the identifier name: \'{local_var}\'")
                        continue # 중복 시 에러 복구 후 계속 실행
                    elif self.activation_record.get(local_var, "Unknown") != "Unknown": # 변수 명이 함수 명과 같이 정의 케이스 예외 처리
                        self.error_list.append(f"Duplicate declaration of the identifier or the function name: \'{local_var}\'")
                        return # 중복 시 에러 출력 후 종료
                    else:
                        self.activation_record[function_name].append(local_var)
                else: # ident 1개 필수
                    self.alert_error("var_definition", "<var_definition>의 \',\'뒤에 <identifier>가 없습니다")
                    return

            if self.lex.next_token == Token.SEMI_COLON:
                self.lex.lexical()
            else: # ';' 1개 필수
                self.alert_error("var_definition", "<var_definition>의 마지막 요소에 \';\'가 없습니다")
                return

        else: # 'variable' 필수
            self.alert_error("var_definition", "<var_definition>의 첫번째 요소에 \'variable\'가 없습니다")
            self.lex.lexical()
            return

        # print("<var_definition> 종료")

    def statement(self, function_name: str):
        # print("<statement> 시작")

        if self.lex.next_token == Token.CALL:
            self.lex.lexical()

            if self.statement_record.get(function_name, "Unknown") == "Unknown":
                self.statement_record[function_name] = [ (Token.CALL, self.identifier('statement')) ]
            else:
                self.statement_record[function_name].append( (Token.CALL, self.identifier('statement')) )

        elif self.lex.next_token == Token.PRINT_ARI:
            if self.statement_record.get(function_name, "Unknown") == "Unknown":
                self.statement_record[function_name] = [ (Token.PRINT_ARI, self.lex.next_lexeme) ]
            else:
                self.statement_record[function_name].append( (Token.PRINT_ARI, self.lex.next_lexeme) )
            self.lex.lexical()

        elif self.lex.next_token == Token.IDENT:
            if self.statement_record.get(function_name, "Unknown") == "Unknown":
                self.statement_record[function_name] = [ (Token.VARIABLE, self.identifier('statement')) ]
            else:
                self.statement_record[function_name].append( (Token.VARIABLE, self.identifier('statement')) )

        else:
            self.alert_error("statement", "<statement>의 첫번째 요소에 \'call\' 또는 \'print_ari\' 또는 <identifier>가 없습니다")
            return

        if self.lex.next_token == Token.SEMI_COLON:
            self.lex.lexical()
        else:  # ';' 1개 필수
            self.alert_error("statement", "<statement>의 마지막 요소에 \';\'가 없습니다")
            return

        # print("<statement> 종료")

    def identifier(self, caller: str) -> str | None:
        # print("<identifier> 시작")
        ident = None

        if self.lex.next_token == Token.IDENT:

            if caller == 'function':
                if self.activation_record.get(self.lex.next_lexeme, "Unknown") != "Unknown":
                    self.error_list.append(f"Duplicate declaration of the function name: \'{self.lex.next_lexeme}\'")
                    return
                else:
                    self.activation_record[self.lex.next_lexeme] = [] # 함수 이름 등록
                    ident = self.lex.next_lexeme
            elif caller == 'var_definition': # 중복 처리는 var_definition에서
                ident = self.lex.next_lexeme
            elif caller == 'statement':
                ident = self.lex.next_lexeme

        else: # ident 필수
            self.alert_error("identifier", "<identifier>이 존재하지 않습니다")
            return None

        # print("<identifier> 종료")
        self.lex.lexical()
        return ident