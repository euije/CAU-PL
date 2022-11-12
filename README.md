## ※ 처리 조건
- 각 문장들이 파싱된 이후,
  1. 입력된 문장과
  2. 그 문장에 포함된 식별자(IDENT),
  3. 숫자(CONST),
  4. 그리고 연산자(OP)의 개수를 출력한다.

- 파싱된 문장이
  - 문법에 적합하면 `<OK>`,
  - 적합하지 않으면
    - 적절한 에러 `<ERROR>` 메시지나
    - 경고 `<WARNING>` 메시지를 출력한다.

- 위에서 주어진 문법에 의거 오류가 발견된 경우,
  - 오류를 가능한 한 *복구*한 다음, *파싱을 계속*한다.
    - 예를 들어, `x = a + + b`일 경우,
      - “+” 연산자가 한 개가 더 존재하므로 “+” 기호를 제거한 다음
      - 적절한 `경고(Warning) 메시지`를 출력한 후, 파싱을 계속한다.

- 오류 복구가 불가능한 경우
  - `에러(Error) 메시지`를 출력하고 *파싱을 계속*하되,
  - 이 경우 해당 식별자(<IDENT>)의 값은 *‘Unknown’으로 결정*된다.

## ※ 오류 조건
- 문장이 포함하고 있는 **모든** 오류에 대해 경고 또는 에러 메시지를 출력해야 한다.
  - 가능한 한 오류를 복구해야 하고, 불가능한 경우만 에러 메시지를 출력한다.
  - 에러나 오류 메시지 내용은 각자 적절히 정의한다(문서에 표기해야 함).
  - 처리된 오류 각각에 대해 추가 점수가 부여된다.
  - 프로그램에 속한 일부 문장이 문법에 적합하지 않더라도 오류 복구를 통해 프로그램이 끝까지 전부 파싱되어야 한다.

## 세부 요건
- 파싱 트리 생성 후, 모든 <IDENT> 값이 출력되어야 한다. 
  - 단, <IDENT>의 값이 정의되지 않은 경우, “Unknown"으로 표시한다.
    - <IDENT>의 현재 값을 저장하기 위해 심볼 테이블(symbol table)을 구축해야 한다.
    
- 어휘분석기(lexical analyzer)의 소스 코드는 
  - 정수 변수 next_token, 
  - 문자열 변수 token_string,
  - 함수 lexical()을 포함하여야 한다. 
    - 함수 lexical()은 
      - 입력 스트림을 분석하여 하나의 lexeme을 찾아낸 뒤,
      - 그것의 token type을 next_token에 저장하고,
      - lexeme 문자열을 token_string에 저장하는 함수이다.
    
- 기타 구현 시 요구되는 세부 사항은 직접 결정하고, Internal 및 External Document에 기술한다.

## 생각 해야할 예외 케이스
- 재귀 하강 파싱 트리에 루트부터 아래로 예외 케이스를 생각했다.
1. EOF 이전에 세미콜론이 없는 경우 : <statement> (<semi_colon><statements>)
2. ident로 시작하지 않는 경우 : <ident><assignment_op><expression>
   3. := 가 없는 경우
4. 


1. 정의 되지 않은 변수가 참조 되었을 때
2. 연산자가 중복 되었을 때
3. ';' 세미 콜론이 문장에 없을 경우
4. ident 앞에  
