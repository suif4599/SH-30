from enum import Enum
from typing import Any

import re

class MultiValue(tuple):
    """
    Represents a multi-value in OpenFOAM.

    Example:

        blocks
        (
            hex (0 1 2 3 4 5 6 7)
                (20 20 1)
                simpleGrading (1 1 1)
        );
    
    will be

        Pair(
            "hex",
            MultiValue(
                (0, 1, 2, 3, 4, 5, 6, 7),
                (20, 20, 1),
                "simpleGrading",
                (1, 1, 1)
            )
        )
    """

class DictTuple(dict):
    """
    Represents a parenthesis containing some pairs.
    
    Example:

        boundary
        (
            movingWall
            {
                type wall;
                faces
                (
                    (3 7 6 2)
                );
            }
            fixedWalls
            {
                type wall;
                faces
                (
                    (0 4 7 3)
                    (2 6 5 1)
                    (1 5 4 0)
                );
            }
            frontAndBack
            {
                type empty;
                faces
                (
                    (0 3 2 1)
                    (4 5 6 7)
                );
            }
        );
    
    will be
    
        Pair(
            "boundary",
            DictTuple(
                "movingWall": {
                    "type": "wall",
                    "faces": ((3, 7, 6, 2),)
                },
                "fixedWalls": {
                    "type": "wall",
                    "faces": (
                        (0, 4, 7, 3),
                        (2, 6, 5, 1),
                        (1, 5, 4, 0)
                    )
                },
                "frontAndBack": {
                    "type": "empty",
                    "faces": ((0, 3, 2, 1), (4, 5, 6, 7))
                }
            )
        )
    """

class TokenType(Enum):
    # Lexical
    PUNCTUATION = "punctuation"
    NAME = "name"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    # Parser
    VALUE = "value"
    PAIR = "pair"


class Token:
    def __init__(self, type: TokenType, value: Any) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f"{self.type.value}({self.value})"

    def __repr__(self) -> str:
        return self.__str__()

class FOAMLexer:
    def __init__(self, input_str: str) -> None:
        self.input = input_str
        self.pos = 0
        self.tokens = []
    
    def tokenize(self) -> list[Token]:
        while self.pos < len(self.input):
            current_char = self.input[self.pos]
            # Space and comments
            if current_char.isspace():
                self.pos += 1
                continue
            if self._try_skip_comment():
                continue
            # Punctuation
            if current_char in '(){}[];\'"':
                self.tokens.append(Token(TokenType.PUNCTUATION, current_char))
                self.pos += 1
                if current_char == '}':
                    if self.input[self.pos] == ';':
                        self.pos += 1 # See '};' as '}'
                    self.tokens.append(Token(TokenType.PUNCTUATION, ';')) # Add semicolon after "}"
                continue
            # Number (integer/float)
            if num_token := self._try_get_number():
                self.tokens.append(num_token)
                continue
            # String (quoted)
            if str_token := self._try_get_quoted_string():
                self.tokens.append(str_token)
                continue
            # Name (unquoted string)
            name_token = self._get_name()
            self.tokens.append(name_token)
            
        return self.tokens
    
    def _try_skip_comment(self) -> bool:
        # Single-line comment
        if self.input[self.pos:self.pos+2] == '//':
            end = self.input.find('\n', self.pos)
            self.pos = end if end != -1 else len(self.input)
            return True
            
        # multi-line comment
        if self.input[self.pos:self.pos+2] == '/*':
            end = self.input.find('*/', self.pos)
            if end == -1:
                self.pos = len(self.input)
            else:
                self.pos = end + 2
            return True
            
        return False
    
    def _try_get_number(self) -> Token | None:
        start = self.pos
        
        # Sign
        if self.input[self.pos] in '+-':
            self.pos += 1
        # Integer
        num_digits = 0
        while self.pos < len(self.input) and self.input[self.pos].isdigit():
            num_digits += 1
            self.pos += 1
        # Decimal point
        has_dot = self.pos < len(self.input) and self.input[self.pos] == '.'
        if has_dot:
            self.pos += 1
            # Digits after decimal point
            while self.pos < len(self.input) and self.input[self.pos].isdigit():
                num_digits += 1
                self.pos += 1

        # Scientific notation
        has_exp = False
        if self.pos < len(self.input) and self.input[self.pos] in 'eE':
            has_exp = True
            self.pos += 1
            # Exponent sign
            if self.pos < len(self.input) and self.input[self.pos] in '+-':
                self.pos += 1
            # Exponent digits
            exp_digits = 0
            while self.pos < len(self.input) and self.input[self.pos].isdigit():
                exp_digits += 1
                self.pos += 1
            if exp_digits == 0:
                has_exp = False
                
        # Valid check
        if num_digits > 0 or (has_dot and self.pos > start + 1):
            value = self.input[start:self.pos]
            if has_dot or has_exp:
                return Token(TokenType.FLOAT, float(value))
            return Token(TokenType.INT, int(value))

        # If no valid number found, reset position
        self.pos = start
        return None
    
    def _try_get_quoted_string(self) -> Token | None:
        if self.input[self.pos] not in ('"', "'"):
            return None
        quote_char = self.input[self.pos]
        self.pos += 1
        value = []
        escape = False
        while self.pos < len(self.input):
            current_char = self.input[self.pos]
            if escape:
                value.append(current_char)
                escape = False
                self.pos += 1
                continue
            if current_char == '\\':
                # Begin escape sequence
                escape = True
                self.pos += 1
                continue
            if current_char == quote_char:
                # End of string
                self.pos += 1
                return Token(TokenType.STRING, ''.join(value))
            value.append(current_char)
            self.pos += 1
        # Unterminated string
        return Token(TokenType.STRING, ''.join(value))
    
    def _get_name(self) -> Token:
        start = self.pos
        valid_chars = re.compile(r'[^\s(){}[\]\'";]')
        
        while self.pos < len(self.input) and valid_chars.match(self.input[self.pos]):
            self.pos += 1
            
        value = self.input[start:self.pos]
        return Token(TokenType.NAME, value)

class FOAMParser:
    """
    A simple parser for OpenFOAM files.
    This parser can tokenize OpenFOAM syntax and provide a structured representation.
    """
    
    def __init__(self, input_str: str) -> None:
        self.lexer = FOAMLexer(input_str)
        self.tokens = self.lexer.tokenize()
        self.value = self._parse(self.tokens)
    
    def _parse(self, tokens: list[Token]) -> dict[str, Any]:
        """
        Parse the input string and return a list of tokens.
        """
        if not tokens:
            return {}
        
        # Quoted string
        while True:
            single_quote = False
            double_quote = False
            start = end = -1
            for i, token in enumerate(tokens):
                if token.type == TokenType.PUNCTUATION and token.value in ('"', "'"):
                    if token.value == '"' and not single_quote:
                        if double_quote:
                            end = i
                            break
                        double_quote = True
                        start = i + 1
                    elif token.value == "'" and not double_quote:
                        if single_quote:
                            end = i
                            break
                        single_quote = True
                        start = i + 1
            else:
                if start >= 0:
                    raise ValueError("Unmatched quote in input")
                break
            # Valid quoted string tokens[start:end]
            tokens[start - 1: end + 1] = [
                Token(
                    TokenType.STRING,
                    ''.join(str(token.value) for token in tokens[start:end])
                )
            ]

        # Subdictionary (greedy)
        while True:
            stack_cnt = 0
            start = end = -1
            for i, token in enumerate(tokens):
                if token.type == TokenType.PUNCTUATION:
                    if token.value == '{':
                        stack_cnt += 1
                        if stack_cnt == 1:
                            start = i + 1
                    elif token.value == '}':
                        stack_cnt -= 1
                        if stack_cnt == 0:
                            end = i
                            break
                        if stack_cnt < 0:
                            raise ValueError("Unmatched '}' in input")
            else:
                if stack_cnt > 0:
                    raise ValueError("Unmatched '{' in input")
                break
            # Valid subdictionary tokens[start:end]
            tokens[start - 1: end + 1] = [
                Token(
                    TokenType.VALUE,
                    self._parse(tokens[start:end])
                )
            ]
        
        # Tuple (lazy)
        while True:
            start = end = -1
            for i, token in enumerate(tokens):
                if token.type == TokenType.PUNCTUATION:
                    if token.value == '(':
                        start = i + 1
                    elif token.value == ')':
                        if start < 0:
                            raise ValueError("Unmatched ')' in input")
                        end = i
                        break
            else:
                if start >= 0:
                    raise ValueError("Unmatched '(' in input")
                break
            
            # Valid tuple tokens[start:end]
            if any(
                mid.type == TokenType.PUNCTUATION # Won't have PAIR type
                for mid in tokens[start:end]
            ):
                value = DictTuple(self._parse(tokens[start:end]))
            else:
                value = tuple(token.value for token in tokens[start:end])
            
            tokens[start - 1: end + 1] = [
                Token(
                    TokenType.VALUE,
                    value
                )
            ]
        
        # List (lazy), same as tuple
        while True:
            start = end = -1
            for i, token in enumerate(tokens):
                if token.type == TokenType.PUNCTUATION:
                    if token.value == '[':
                        start = i + 1
                    elif token.value == ']':
                        if start < 0:
                            raise ValueError("Unmatched ']' in input")
                        end = i
                        break
            else:
                if start >= 0:
                    raise ValueError("Unmatched '[' in input")
                break

            # Valid list tokens[start:end]
            if any(
                mid.type == TokenType.PUNCTUATION # Won't have PAIR type
                for mid in tokens[start:end]
            ):
                value = self._parse(tokens[start:end])
            else:
                value = [token.value for token in tokens[start:end]]

            tokens[start - 1: end + 1] = [
                Token(
                    TokenType.VALUE,
                    value
                )
            ]

        # Pair
        while True:
            start = end = -1
            for i, token in enumerate(tokens):
                if token.type == TokenType.NAME:
                    if start < 0:
                        start = i
                elif token.type == TokenType.PUNCTUATION:
                    if token.value == ';':
                        if start < 0:
                            raise ValueError("Unmatched ';' in input")
                        if end < 0:
                            end = i
                        break
                    raise ValueError(f"Unexpected token {token} in input")
            else:
                if start >= 0:
                    raise ValueError("Unmatched name in input")
                break
            if end == start + 1:
                raise ValueError("Unmatched name in input")
            tokens[start:end + (tokens[end].type == TokenType.PUNCTUATION)] = [
                Token(
                    TokenType.PAIR,
                    (tokens[start], tokens[start + 1:end])
                )
            ]
        
        # Dictionary
        if all(
            token.type == TokenType.PAIR
            for token in tokens
        ):
            return {
                key.value: value[0].value if len(value) == 1 else MultiValue(v.value for v in value)
                for key, value in (
                    token.value for token in tokens
                )
            }
        raise ValueError("Unmatched name in input")

class FOAMBuilder:
    """
    A builder for OpenFOAM files.
    This builder can create OpenFOAM syntax from a structured representation.
    """
    
    def __init__(self, dictionary: dict[str, Any]) -> None:
        self.dictionary = dictionary
        self.content = self._build(dictionary)
    
    def _build(self, d: dict[str, Any]) -> str:
        """
        Build OpenFOAM syntax from a dictionary.
        """
        lines = []
        for key, value in d.items():
            value_str = self._build_value(value)
            if '\n' in value_str:
                lines.append(key)
                if isinstance(value, dict) and not isinstance(value, DictTuple):
                    lines.append(value_str)
                else:
                    lines.append(value_str + ';')
            else:
                lines.append(f"{key} {value_str};")
        return '\n'.join(lines)
    
    def _build_value(self, value: Any) -> str:
        if value is None:
            return ""
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Quote strings containing special characters
            if any(char.isspace() or char in '{}[];()"\'\\' for char in value):
                escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            return value
        elif isinstance(value, list):
            items = [self._build_value(item) for item in value]
            return '[' + ' '.join(items) + ']'
        elif isinstance(value, tuple):
            # MultiValue (tuple subclass) should be output without parentheses
            if isinstance(value, MultiValue):
                items = [self._build_value(item) for item in value]
                return ' '.join(items)
            # Regular tuple
            items = [self._build_value(item) for item in value]
            return '(' + ' '.join(items) + ')'
        elif isinstance(value, dict):
            if not value:
                return '{}'
            inner = self._build(value)
            if isinstance(value, DictTuple):
                return '(\n' + inner + '\n)'
            return '{\n' + inner + '\n}'
        else:
            # Fallback for unknown types
            return str(value)
        
    
   

if __name__ == "__main__":
    # Example usage
    demo = r'''
    /*--------------------------------*- C++ -*----------------------------------*\
    | =========                 |                                                 |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  v2206                                 |
    |   \\  /    A nd           | Website:  www.openfoam.com                      |
    |    \\/     M anipulation  |                                                 |
    \*---------------------------------------------------------------------------*/
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        object      blockMeshDict;
    }
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    scale   0.1; // 全局缩放因子: 相当于将所有坐标缩小到原来的十分之一

    vertices
    (
        (0 0 0) // 0
        (1 0 0) // 1
        (1 1 0)
        (0 1 0)
        (0 0 0.1)
        (1 0 0.1)
        (1 1 0.1)
        (0 1 0.1) // 7
    );

    blocks
    (
        hex (0 1 2 3 4 5 6 7) // hexahedron（六面体） 顶点顺序
            (20 20 1) // 网格划分: 在x方向和y方向各划分20个单元，z方向不划分
            simpleGrading (1 1 1) // 网格渐变比例 (均匀网格)
    );

    edges
    (
    ); // 曲线边定义（此例为空）

    boundary
    (
        movingWall
        {
            type wall;
            faces
            (
                (3 7 6 2)
            );
        }
        fixedWalls
        {
            type wall;
            faces
            (
                (0 4 7 3)
                (2 6 5 1)
                (1 5 4 0)
            );
        }
        frontAndBack
        {
            type empty;
            faces
            (
                (0 3 2 1)
                (4 5 6 7)
            );
        }
    );


    // ************************************************************************* //

    '''

    import json
    dictionary = FOAMParser(demo).value
    print(
        json.dumps(
            dictionary,
            indent=4
        )
    )
    content = FOAMBuilder(dictionary).content
    print(content)