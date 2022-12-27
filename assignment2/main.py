import lexical_analyzer as lex
from lexical_analyzer import Token
import syntax_analyzer as syn
import sys

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

    parser = lex.lexical_analyzer()
    parser.parse_to_lexeme(input)
    # print(parser.parse)

    syntax = syn.syntax_analyzer(parser)
    accepted = syntax.generate_parse_tree()
    if accepted:
        ARI = []

        print("Syntax O.K.\n")
        if len(syntax.error_list) != 0: print("Syntax 경고 리스트 : ", syntax.error_list)
        # print(syntax.statement_record)
        # print(syntax.activation_record)

        ARI.append( {"main" : syntax.activation_record["main"]} )

        func = "main"
        # while True:
        i = 0
        while len(ARI) != 0:
            if i < len(syntax.statement_record[func]):
                (token, ident) = syntax.statement_record[func][i]
                if token == Token.CALL:
                    if syntax.activation_record.get(ident, "Unknown") == "Unknown":
                        print(f"Call to undefined function: {ident}")
                        break
                    else:
                        instance = syntax.activation_record[ident]
                        instance.insert(0, len(list(ARI[len(ARI) - 1].values())))
                        instance.insert(0, {list(ARI[len(ARI) - 1].keys())[0] : i + 1})
                        ARI.append({ident : instance})
                        func = ident # 실행(process)의 통제권을 ARI의 TOP에게 준다
                        i = 0
                elif token == Token.PRINT_ARI:
                    for p in reversed(range(len(ARI))):
                        for key, val in ARI[p].items():
                            print(f"-----{key}-----")
                            if key == "main":
                                for q in reversed(range(len(val))):
                                    print(f"Local variable: {val[q]}")
                            else:
                                for q in reversed(range(2, len(val))):
                                    print(f"Local variable: {val[q]}")
                                print(f"Dynamic Link: {val[1]}")
                                print(f"Return Address: {val[0]}")
                            print("\n", end='')

                    i += 1
                elif token == Token.VARIABLE:
                    flag = 0

                    for p in reversed(range(len(ARI))):
                        if list(ARI[p].keys())[0] == "main": start = 0
                        else: start = 2
                        for q in range(start, len(list(ARI[p].values())[0])):
                            if list(ARI[p].values())[0][q] == ident:
                                print(f"{func}:{ident} => {len(ARI) - 1 - p}, {q}\n")
                                flag = 1
                                i += 1
                                break

                    if flag == 0:
                        print(f"Call to undefined the identifier: {ident}")
                        i += 1
            else:
                if func == "main":
                    break
                return_address = list(ARI[len(ARI) - 1].values())[0]
                func = list(return_address[0].keys())[0]
                i = list(return_address[0].values())[0]
                ARI.pop(len(ARI) - 1) # 실행(process)의 통제권을 ARI의 TOP에게 준다

    else:
        print("Syntax Error")
        print("identifier 에러 리스트 : ", parser.error_list)
        print("Syntax 에러 리스트 : ", syntax.error_list)

    f.close()

if __name__ == "__main__":
    main()
