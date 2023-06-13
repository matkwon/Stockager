import sys
import re

def errfn(*a):
    print(*a, file=sys.stderr)
    exit()

class PrePro:
    @staticmethod
    def filter(source):
        return re.sub("\n", "", re.sub('#.*', '', source))

class Token:

    def __init__(self, value, type : str):
        self.value = value
        self.type = type

class Tokenizer:

    def __init__(self, source : str):
        self.source = source
        self.position = 0
        self.next = None
        self.types = ["Int", "Float", "String", "Product"]
        self.props = ["name", "description", "category", "price", "quantity"]
        self.default = {"Int" : 0, "Float" : 0, "String" : ""}
        self.reserved_words = ["print", "while", "if", "else", "do", "end", "return", "function", "in", "out", "rm", "product", "not", "and", "or"] + self.types
        self.LETTERS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
        self.DIGITS = "1234567890"
    
    def select_next(self):
        while True:
            if self.position >= len(self.source):
                self.next = Token('"', "EOF")
                return
            char = self.source[self.position]
            if char in [" ", "\t"]:
                self.position += 1
            else:
                break

        if char == "+":
            self.next = Token('+', "PLUS")
            self.position += 1
        elif char == "-":
            self.next = Token('-', "MINUS")
            self.position += 1
        elif char == "*":
            self.next = Token('*', "MULT")
            self.position += 1
        elif char == "/":
            self.next = Token('/', "DIV")
            self.position += 1
        elif char == ".":
            self.next = Token('.', "PROP")
            self.position += 1
        elif char == "(":
            self.next = Token('(', "OPAR")
            self.position += 1
        elif char == ")":
            self.next = Token(')', "CPAR")
            self.position += 1
        elif char == "{":
            self.next = Token('{', "OBRAC")
            self.position += 1
        elif char == "}":
            self.next = Token('}', "CBRAC")
            self.position += 1
        elif char == "=":
            if self.source[self.position+1] == "=":
                self.next = Token('==', "EQUAL")
                self.position += 2
            else:
                self.next = Token('=', "ASSIGN")
                self.position += 1
        elif char == ">":
            if self.source[self.position+1] == "=":
                self.next = Token('>=', "GTE")
                self.position += 2
            else:
                self.next = Token('>', "GT")
                self.position += 1
        elif char == "<":
            if self.source[self.position+1] == "=":
                self.next = Token('<=', "LTE")
                self.position += 2
            else:
                self.next = Token('<', "LT")
                self.position += 1
        elif char == "|":
            if self.source[self.position+1] == "|":
                self.next = Token('||', "OR")
                self.position += 2
            else:
                errfn(f"Expected '||', but got '|{self.source[self.position+1]}'.")
        elif char == "&":
            if self.source[self.position+1] == "&":
                self.next = Token('&&', "AND")
                self.position += 2
            else:
                errfn(f"Expected '&&', but got '&{self.source[self.position+1]}'.")
        elif char == "!":
            if self.source[self.position+1] == "=":
                self.next = Token('!=', "NEQUAL")
                self.position += 2
            else:
                self.next = Token('!', "NOT")
                self.position += 1
        elif char == ":":
            self.next = Token(':', "COLON")
            self.position += 1
        elif char == ";":
            self.next = Token(';', "SEMICOLON")
            self.position += 1
        elif char == ",":
            self.next = Token(',', "COMMA")
            self.position += 1
        elif char == "\"":
            i = 1
            while self.source[self.position + i] != "\"":
                i += 1
                if self.position + i > len(self.source):
                    break
            self.next = Token(self.source[self.position + 1 : self.position + i], "STRING")
            self.position += i + 1
        elif char == "\'":
            i = 1
            while self.source[self.position + i] != "\'":
                i += 1
                if self.position + i > len(self.source):
                    break
            self.next = Token(self.source[self.position + 1 : self.position + i], "STRING")
            self.position += i + 1
        elif char.isdigit():
            i = 1
            while self.source[self.position + i].isdigit():
                i += 1
                if self.position + i > len(self.source):
                    break
                if self.source[self.position + i] == ".":
                    i += 1
                    while self.source[self.position + i].isdigit():
                        i += 1
                        if self.position + i > len(self.source):
                            break
                    self.next = Token(float(self.source[self.position : self.position + i]), "FLOAT")
                    self.position += i
                    return
            self.next = Token(int(self.source[self.position : self.position + i]), "INT")
            self.position += i
        elif char in self.LETTERS or char == "_":
            i = 1
            while self.source[self.position + i] in self.LETTERS + self.DIGITS + "_":
                i += 1
                if self.position + i > len(self.source):
                    break
            word = self.source[self.position : self.position + i]
            self.next = Token(word, "IDENTIFIER")
            self.position += i
            if word in self.reserved_words:
                self.next.type = word.capitalize()
                if word in self.types:
                    self.next.type = "TYPE"
        else:
            errfn(f"Not a valid token ({char})")


class SymbolTable:
    def __init__(self, parent):
        self.table = {}
        self.parent = parent
    
    def setter(self, name, tp, value):
        if name not in self.table.keys() and self.parent != None:
            st = self.parent.checker(name)
            if (st == None):
                self.table[name] = (tp, value)
            else:
                st.table[name] = (tp, value)
        else:
            self.table[name] = (tp, value)
    
    def checker(self, name):
        if name not in self.table.keys():
            if self.parent == None:
                return None
            else:
                return self.parent.checker(name)
        return self
    
    def getter(self, name):
        if name not in self.table.keys():
            if self.parent == None:
                errfn(f"'{name}' identifier not setted.")
            else:
                return self.parent.getter(name)
        return self.table[name]
    
    def remover(self, name):
        self.table.pop(name)

class FuncTable:
    table = {}
    
    @staticmethod
    def creator(name, value):
        FuncTable.table[name] = value
    
    @staticmethod
    def getter(name):
        if name not in FuncTable.table.keys():
            errfn(f"'{name}' function not created.")
        return FuncTable.table[name]


class Node:
    def __init__(self, value, children):
        self.value = value
        self.children = children
    
    def evaluate():
        pass

class NoOp(Node):
    def __init__(self):
        super().__init__(None, [])
    
    def evaluate(self, st):
        return self.value

class IntVal(Node):
    def __init__(self, value):
        super().__init__(value, [])
    
    def evaluate(self, st):
        if type(self.value) != int:
            errfn(f"Expected integer, but got {self.value[1]} of type {self.value[0]}.")
        return ("Int", self.value)

class FloatVal(Node):
    def __init__(self, value):
        super().__init__(value, [])
    
    def evaluate(self, st):
        if type(self.value) != float:
            errfn(f"Expected float, but got {self.value[1]} of type {self.value[0]}.")
        return ("Float", self.value)

class StringVal(Node):
    def __init__(self, value):
        super().__init__(value, [])
    
    def evaluate(self, st):
        if type(self.value) != str:
            errfn(f"Expected string, but got {self.value[1]} of type {self.value[0]}.")
        return ("String", self.value)

class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value, [child])
    
    def evaluate(self, st):
        if self.children[0].evaluate(st)[0] == "String":
            errfn(f"Cannot apply unary operator '{self.value}' to string value '{self.children[0][1]}'.")
        if self.value == "-":
            return ("Int", -self.children[0].evaluate(st)[1])
        elif self.value == "!":
            if not self.children[0].evaluate(st)[1]:
                return ("Int", 1)
            return ("Int", 0)
        return ("Int", self.children[0].evaluate(st)[1])

class BinOp(Node):

    def __init__(self, value, children):
        super().__init__(value, children)
    
    def evaluate(self, st):
        if self.value == "==":
            if self.children[0].evaluate(st)[1] == self.children[1].evaluate(st)[1]:
                return ("Int", 1)
            return ("Int", 0)
        elif self.value == "!=":
            if self.children[0].evaluate(st)[1] != self.children[1].evaluate(st)[1]:
                return ("Int", 1)
            return ("Int", 0)
        elif self.value == ">":
            if self.children[0].evaluate(st)[0] == "Product" or self.children[1].evaluate(st)[0] == "Product":
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            if self.children[0].evaluate(st)[1] > self.children[1].evaluate(st)[1]:
                return ("Int", 1)
            return ("Int", 0)
        elif self.value == ">=":
            if self.children[0].evaluate(st)[0] == "Product" or self.children[1].evaluate(st)[0] == "Product":
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            if self.children[0].evaluate(st)[1] >= self.children[1].evaluate(st)[1]:
                return ("Int", 1)
            return ("Int", 0)
        elif self.value == "<":
            if self.children[0].evaluate(st)[0] == "Product" or self.children[1].evaluate(st)[0] == "Product":
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            if self.children[0].evaluate(st)[1] < self.children[1].evaluate(st)[1]:
                return ("Int", 1)
            return ("Int", 0)
        elif self.value == "<=":
            if self.children[0].evaluate(st)[0] == "Product" or self.children[1].evaluate(st)[0] == "Product":
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            if self.children[0].evaluate(st)[1] <= self.children[1].evaluate(st)[1]:
                return ("Int", 1)
            return ("Int", 0)
        elif self.value == "+":
            if self.children[0].evaluate(st)[0] == "Product" or self.children[1].evaluate(st)[0] == "Product":
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            elif self.children[0].evaluate(st)[0] == "String" or self.children[1].evaluate(st)[0] == "String":
                return ("String", str(self.children[0].evaluate(st)[1]) + str(self.children[1].evaluate(st)[1]))
            elif self.children[0].evaluate(st)[0] == "Float" or self.children[1].evaluate(st)[0] == "Float":
                return ("Float", float(self.children[0].evaluate(st)[1]) + float(self.children[1].evaluate(st)[1]))
            return ("Int", self.children[0].evaluate(st)[1] + self.children[1].evaluate(st)[1])
        elif self.value == "-":
            if self.children[0].evaluate(st)[0] in ["String", "Product"] or self.children[1].evaluate(st)[0] in ["String", "Product"]:
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            elif self.children[0].evaluate(st)[0] == "Float" or self.children[1].evaluate(st)[0] == "Float":
                return ("Float", float(self.children[0].evaluate(st)[1]) - float(self.children[1].evaluate(st)[1]))
            return ("Int", self.children[0].evaluate(st)[1] - self.children[1].evaluate(st)[1])
        elif self.value == "*":
            if self.children[0].evaluate(st)[0] in ["String", "Product"] or self.children[1].evaluate(st)[0] in ["String", "Product"]:
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            elif self.children[0].evaluate(st)[0] == "Float" or self.children[1].evaluate(st)[0] == "Float":
                return ("Float", float(self.children[0].evaluate(st)[1]) * float(self.children[1].evaluate(st)[1]))
            return ("Int", self.children[0].evaluate(st)[1] * self.children[1].evaluate(st)[1])
        elif self.value == "/":
            if self.children[0].evaluate(st)[0] in ["String", "Product"] or self.children[1].evaluate(st)[0] in ["String", "Product"]:
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            elif self.children[0].evaluate(st)[0] == "Float" or self.children[1].evaluate(st)[0] == "Float":
                return ("Float", float(self.children[0].evaluate(st)[1]) / float(self.children[1].evaluate(st)[1]))
            return ("Int", self.children[0].evaluate(st)[1] / self.children[1].evaluate(st)[1])
        elif self.value == "or":
            if self.children[0].evaluate(st)[0] in ["String", "Product"] or self.children[1].evaluate(st)[0] in ["String", "Product"]:
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            elif self.children[0].evaluate(st)[0] == "Float" or self.children[1].evaluate(st)[0] == "Float":
                return ("Float", float(self.children[0].evaluate(st)[1]) or float(self.children[1].evaluate(st)[1]))
            return ("Int", self.children[0].evaluate(st)[1] or self.children[1].evaluate(st)[1])
        elif self.value == "and":
            if self.children[0].evaluate(st)[0] in ["String", "Product"] or self.children[1].evaluate(st)[0] in ["String", "Product"]:
                errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")
            elif self.children[0].evaluate(st)[0] == "Float" or self.children[1].evaluate(st)[0] == "Float":
                return ("Float", float(self.children[0].evaluate(st)[1]) and float(self.children[1].evaluate(st)[1]))
            return ("Int", self.children[0].evaluate(st)[1] and self.children[1].evaluate(st)[1])
        else:
            errfn(f"Cannot apply binary operator '{self.value}' to values '{self.children[0].evaluate(st)[1]}' and '{self.children[1].evaluate(st)[1]}'.")

class Printer(Node):
    def __init__(self, child):
        super().__init__("Print", [child])
    
    def evaluate(self, st):
        print(self.children[0].evaluate(st)[1])

class Assignment(Node):
    def __init__(self, children):
        super().__init__("Assignment", children)
    
    def evaluate(self, st):
        val = self.children[1].evaluate(st)
        st.setter(self.children[0].value, val[0], val[1])
            
class Identifier(Node):
    def __init__(self, value):
        super().__init__(value, [])
    
    def evaluate(self, st):
        return st.getter(self.value)

class FuncDec(Node):
    def __init__(self, children):
        super().__init__("Function", children)
    
    def evaluate(self, st):
        FuncTable.creator(self.children[0].value, self)

class FuncCall(Node):
    def __init__(self, name, children):
        super().__init__(name, children)
    
    def evaluate(self, st):
        funcDec = FuncTable.getter(self.value)
        newSt = SymbolTable(st)
        if len(self.children) != len(funcDec.children)-2:
            errfn(f"Expected {len(funcDec.children)-2} arguments, but got {len(self.children)}.")
        for i in range(len(funcDec.children)-2):
            newVar = self.children[i].evaluate(st)
            newSt.setter(funcDec.children[i+1].value, newVar[0], newVar[1])
        return funcDec.children[-1].evaluate(newSt)

class While(Node):
    loop_id = 0
    def __init__(self, children):
        super().__init__("While", children)
    
    def evaluate(self, st):
        while self.children[0].evaluate(st)[1]:
            self.children[1].evaluate(st)

class If(Node):
    if_id = 0
    def __init__(self, children):
        super().__init__("If", children)
    
    def evaluate(self, st):
        if self.children[0].evaluate(st)[1]:
            self.children[1].evaluate(st)
        elif len(self.children) == 3:
            self.children[2].evaluate(st)

class Return(Node):
    def __init__(self, child):
        super().__init__("Return", [child])
    
    def evaluate(self, st):
        return self.children[0].evaluate(st)

class Block(Node):
    def __init__(self, children):
        super().__init__("Block", children)
    
    def evaluate(self, st):
        for child in self.children:
            if child.value == "Return":
                return child.evaluate(st)
            child.evaluate(st)

class VarType(Node):
    def __init__(self, value):
        super().__init__(value, [])
    
    def evaluate(self, st):
        return ("String", st.getter(self.value)[0])

class ProdDec(Node):
    def __init__(self, iden, children):
        super().__init__(iden, children)
    
    def evaluate(self, st):
        prod = {}
        prod["name"] = self.children["name"].evaluate(st)
        prod["description"] = self.children["description"].evaluate(st)
        prod["category"] = self.children["category"].evaluate(st)
        prod["price"] = self.children["price"].evaluate(st)
        prod["quantity"] = self.children["quantity"].evaluate(st)
        if prod["name"][0] != "String":
            errfn(f"Cannot create product with non-string name '{prod['name'][1]}'.")
        elif prod["description"][0] != "String":
            errfn(f"Cannot create product with non-string description '{prod['description'][1]}'.")
        elif prod["category"][0] != "String":
            errfn(f"Cannot create product with non-string category '{prod['category'][1]}'.")
        elif prod["price"][0] == "String":
            errfn(f"Cannot create product with string price '{prod['price'][1]}'.")
        elif prod["quantity"][0] == "String":
            errfn(f"Cannot create product with string quantity '{prod['quantity'][1]}'.")
        if prod["price"][1] < 0:
            errfn(f"Cannot create product with negative price.")
        elif prod["quantity"][1] < 0:
            errfn(f"Cannot create product with negative quantity.")
        st.setter(self.value.value, "Product", prod)

class ProdRm(Node):
    def __init__(self, iden):
        super().__init__(iden, [])
    
    def evaluate(self, st):
        st.remover(self.value.value)

class StockOp(Node):
    def __init__(self, iden, children):
        super().__init__(iden, children)
    
    def evaluate(self, st):
        var = self.children[1].evaluate(st)
        if var[0] == "String":
            errfn(f"Cannot apply stock operation with string value '{var[1]}'.")
        prod = st.getter(self.value.value)
        if prod[0] != "Product":
            errfn(f"Cannot apply stock operation with non-product '{self.value.value}' with value '{prod[1]}'.")
        if self.children[0] == "in":
            if prod[1]["quantity"][0] == "Float" or var[0] == "Float":
                prod[1]["quantity"] = ("Float", float(prod[1]["quantity"][1]) + float(var[1]))
            else:
                prod[1]["quantity"] = ("Int", prod[1]["quantity"][1] + var[1])
        elif self.children[0] == "out":
            if prod[1]["quantity"][0] == "Float" or var[0] == "Float":
                prod[1]["quantity"] = ("Float", float(prod[1]["quantity"][1]) - float(var[1]))
            else:
                prod[1]["quantity"] = ("Int", prod[1]["quantity"][1] - var[1])
        if prod[1]["quantity"][1] < 0:
            errfn(f"Cannot apply stock operation to result negative quantity.")
        st.setter(self.value.value, "Product", prod[1])

class PropAssign(Node):
    def __init__(self, iden, children):
        super().__init__(iden, children)
    
    def evaluate(self, st):
        prod = st.getter(self.value.value)
        prop = self.children[0]
        if prod[0] != "Product":
            errfn(f"Cannot apply property assignment to non-product '{self.value.value}' with value '{prod[1]}'.")
        elif prop not in ["name", "description", "category", "price", "quantity"]:
            errfn(f"Cannot apply property assignment to non-property '{prop}'.")
        newVal = self.children[1].evaluate(st)
        if prop in ["price", "quantity"] and newVal[0] == "String":
            errfn(f"Cannot apply property assignment with string value '{newVal[1]}'.")
        elif prop in ["name", "description", "category"] and newVal[0] != "String":
            errfn(f"Cannot apply property assignment with non-string value '{newVal[1]}'.")
        prod[1][prop] = newVal
        st.setter(self.value.value, "Product", prod[1])

class PropVal(Node):
    def __init__(self, iden, prop):
        super().__init__(iden, prop)
    
    def evaluate(self, st):
        prod = st.getter(self.value.value)
        if prod[0] != "Product":
            errfn(f"Cannot apply property value to non-product '{self.value.value}' with value '{prod[1]}'.")
        return prod[1][self.children[0]]


class Parser:

    def __init__(self, tokenizer : Tokenizer = None):
        self.tokenizer = tokenizer
    
    @staticmethod
    def parseFactor():
        if Parser.tokenizer.next.type == "INT":
            ret = IntVal(Parser.tokenizer.next.value)
        elif Parser.tokenizer.next.type == "FLOAT":
            ret = FloatVal(Parser.tokenizer.next.value)
        elif Parser.tokenizer.next.type == "STRING":
            ret = StringVal(Parser.tokenizer.next.value)
        elif Parser.tokenizer.next.type == "IDENTIFIER":
            ret = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value == "(":
                Parser.tokenizer.select_next()
                args = []
                if Parser.tokenizer.next.value != ")":
                    args.append(Parser.parseRelExpr())
                    while Parser.tokenizer.next.value == ",":
                        Parser.tokenizer.select_next()
                        args.append(Parser.parseRelExpr())
                    if Parser.tokenizer.next.value != ")":
                        errfn(f"Expected ')', got '{Parser.tokenizer.next.value}'")
                ret = FuncCall(ret.value, args)
                Parser.tokenizer.select_next()
            elif Parser.tokenizer.next.value == ".":
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.value == "type":
                    Parser.tokenizer.select_next()
                    return VarType(ret.value)
                elif Parser.tokenizer.next.value not in Parser.tokenizer.props:
                    errfn("Expected a valid property name.")
                ret = PropVal(ret, [Parser.tokenizer.next.value])
                Parser.tokenizer.select_next()
            return ret
        elif Parser.tokenizer.next.value == "-":
            Parser.tokenizer.select_next()
            return UnOp("-", Parser.parseFactor())
        elif Parser.tokenizer.next.value == "+":
            Parser.tokenizer.select_next()
            return UnOp("+", Parser.parseFactor())
        elif Parser.tokenizer.next.value in ["!", "not"]:
            Parser.tokenizer.select_next()
            return UnOp("!", Parser.parseFactor())
        elif Parser.tokenizer.next.value == "(":
            Parser.tokenizer.select_next()
            ret = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ")":
                errfn(f"Expected ')', got '{Parser.tokenizer.next.value}'")
        else:
            errfn(f"Not valid token: {Parser.tokenizer.next.value}")
        Parser.tokenizer.select_next()
        return ret
    
    @staticmethod
    def parseTerm():
        res = Parser.parseFactor()
        while True:
            if Parser.tokenizer.next.value == "*":
                Parser.tokenizer.select_next()
                res = BinOp("*", [res, Parser.parseFactor()])
            elif Parser.tokenizer.next.value == "/":
                Parser.tokenizer.select_next()
                res = BinOp("/", [res, Parser.parseFactor()])
            elif Parser.tokenizer.next.value == "and":
                Parser.tokenizer.select_next()
                res = BinOp("and", [res, Parser.parseFactor()])
            else:
                return res
    
    @staticmethod
    def parseExpression():
        res = Parser.parseTerm()
        while True:
            if Parser.tokenizer.next.value == "+":
                Parser.tokenizer.select_next()
                res = BinOp("+", [res, Parser.parseTerm()])
            elif Parser.tokenizer.next.value == "-":
                Parser.tokenizer.select_next()
                res = BinOp("-", [res, Parser.parseTerm()])
            elif Parser.tokenizer.next.value == "or":
                Parser.tokenizer.select_next()
                res = BinOp("or", [res, Parser.parseTerm()])
            else:
                return res
    
    @staticmethod
    def parseRelExpr():
        res = Parser.parseExpression()
        while True:
            if Parser.tokenizer.next.value == "==":
                Parser.tokenizer.select_next()
                res = BinOp("==", [res, Parser.parseExpression()])
            elif Parser.tokenizer.next.value == "!=":
                Parser.tokenizer.select_next()
                res = BinOp("!=", [res, Parser.parseExpression()])
            elif Parser.tokenizer.next.value == ">":
                Parser.tokenizer.select_next()
                res = BinOp(">", [res, Parser.parseExpression()])
            elif Parser.tokenizer.next.value == ">=":
                Parser.tokenizer.select_next()
                res = BinOp(">=", [res, Parser.parseExpression()])
            elif Parser.tokenizer.next.value == "<":
                Parser.tokenizer.select_next()
                res = BinOp("<", [res, Parser.parseExpression()])
            elif Parser.tokenizer.next.value == "<=":
                Parser.tokenizer.select_next()
                res = BinOp("<=", [res, Parser.parseExpression()])
            else:
                return res
    
    @staticmethod
    def parseStatement():
        if Parser.tokenizer.next.value == "product":
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "IDENTIFIER":
                errfn("Expected identifier.")
            iden = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "OBRAC":
                errfn("Expected '{' after identifier.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != "name":
                errfn("Expected 'name' after '{'.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "COLON":
                errfn("Expected ':' after 'name'.")
            Parser.tokenizer.select_next()
            name = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected ';' after name.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != "description":
                errfn("Expected 'description' after '{'.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "COLON":
                errfn("Expected ':' after 'description'.")
            Parser.tokenizer.select_next()
            description = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected ';' after description.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != "category":
                errfn("Expected 'category' after '{'.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "COLON":
                errfn("Expected ':' after 'category'.")
            Parser.tokenizer.select_next()
            category = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected ';' after category.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != "price":
                errfn("Expected 'price' after '{'.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "COLON":
                errfn("Expected ':' after 'price'.")
            Parser.tokenizer.select_next()
            price = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected ';' after price.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != "quantity":
                errfn("Expected 'quantity' after '{'.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "COLON":
                errfn("Expected ':' after 'quantity'.")
            Parser.tokenizer.select_next()
            quantity = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected ';' after quantity.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "CBRAC":
                errfn("Expected '}' after product declaration.")
            return ProdDec(iden, {"name": name, "description": description, "category": category, "price": price, "quantity": quantity})
        elif Parser.tokenizer.next.value == "rm":
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "IDENTIFIER":
                errfn("Expected product identifier.")
            iden = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected ';' after product identifier.")
            return ProdRm(iden)
        elif Parser.tokenizer.next.value in ["in", "out"]:
            flow = Parser.tokenizer.next.value
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "IDENTIFIER":
                errfn("Expected product identifier.")
            iden = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.select_next()
            var = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected ';' after stock operation.")
            return StockOp(iden, [flow, var])
        elif Parser.tokenizer.next.type == "IDENTIFIER":
            iden = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value == ".":
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.value not in Parser.tokenizer.props:
                    errfn("Expected a valid property name.")
                prop = Parser.tokenizer.next.value
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.value != "=":
                    errfn("Expected '=' after property name.")
                Parser.tokenizer.select_next()
                ass_node = PropAssign(iden, [prop, Parser.parseRelExpr()])
                if Parser.tokenizer.next.value != ";":
                    errfn("Expected ';' after stock operation.")
                return ass_node
            elif Parser.tokenizer.next.value == "(":
                Parser.tokenizer.select_next()
                args = []
                if Parser.tokenizer.next.value != ")":
                    args.append(Parser.parseRelExpr())
                    while Parser.tokenizer.next.value == ",":
                        Parser.tokenizer.select_next()
                        args.append(Parser.parseRelExpr())
                    if Parser.tokenizer.next.value != ")":
                        errfn(f"Expected ')', got '{Parser.tokenizer.next.value}'")
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.value != ";":
                    errfn(f"Expected ';' after function call.")
                return FuncCall(iden.value, args)
            elif Parser.tokenizer.next.value == "=":
                Parser.tokenizer.select_next()
                ass_node = Assignment([iden, Parser.parseRelExpr()])
                if Parser.tokenizer.next.value != ";":
                    errfn("Expected a ';' after assignment.")
                return ass_node
            else:
                errfn("Expected a '=' or a '.' or a '(' token after identifier.")
        elif Parser.tokenizer.next.value == "return":
            Parser.tokenizer.select_next()
            ret_node = Return(Parser.parseRelExpr())
            if Parser.tokenizer.next.value != ";":
                errfn(f"Expected ';' after return.")
            return ret_node
        elif Parser.tokenizer.next.value == "print":
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != "(":
                errfn(f"Expected '(', got '{Parser.tokenizer.next.value}'")
            Parser.tokenizer.select_next()
            print_node = Printer(Parser.parseRelExpr())
            if Parser.tokenizer.next.value != ")":
                errfn(f"Expected ')', got '{Parser.tokenizer.next.value}'")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != ";":
                errfn(f"Expected ';' after print.")
            return print_node
        elif Parser.tokenizer.next.value == "while":
            Parser.tokenizer.select_next()
            child0 = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ":":
                errfn("Expected a ':' token after the 'while' condition.")
            block_children = []
            Parser.tokenizer.select_next()
            while Parser.tokenizer.next.value != "end":
                block_children.append(Parser.parseStatement())
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.type == "EOF":
                    errfn("Expected an 'end' token to close the 'while' block.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected a ';' after the 'end' token.")
            return While([child0, Block(block_children)])
        elif Parser.tokenizer.next.value == "if":
            Parser.tokenizer.select_next()
            child0 = Parser.parseRelExpr()
            if Parser.tokenizer.next.value != ":":
                errfn("Expected a ':' token after the 'if' condition.")
            block_children = []
            Parser.tokenizer.select_next()
            while Parser.tokenizer.next.value != "end" and Parser.tokenizer.next.value != "else":
                block_children.append(Parser.parseStatement())
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.type == "EOF":
                    errfn("Expected an 'end' token to close the 'if' block.")
            if_node = If([child0, Block(block_children)])
            if Parser.tokenizer.next.value == "else":
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.value != ":":
                    errfn("Expected a ':' after the 'else' token.")
                block_children2 = []
                Parser.tokenizer.select_next()
                while Parser.tokenizer.next.value != "end":
                    block_children2.append(Parser.parseStatement())
                    Parser.tokenizer.select_next()
                    if Parser.tokenizer.next.type == "EOF":
                        errfn("Expected an 'end' token to close the 'else' block.")
                if_node = If([child0, Block(block_children), Block(block_children2)])
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected a ';' after the 'end' token.")
            return if_node
        elif Parser.tokenizer.next.value == "function":
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.type != "IDENTIFIER":
                errfn("Expected identifier.")
            funcName = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != "(":
                errfn("Expected '(' after identifier.")
            Parser.tokenizer.select_next()
            params = []
            if Parser.tokenizer.next.value != ")":
                if Parser.tokenizer.next.type != "IDENTIFIER":
                    errfn("Expected identifier.")
                params.append(Identifier(Parser.tokenizer.next.value))
                Parser.tokenizer.select_next()
                while Parser.tokenizer.next.value == ",":
                    Parser.tokenizer.select_next()
                    if Parser.tokenizer.next.value != ")":
                        if Parser.tokenizer.next.type != "IDENTIFIER":
                            errfn("Expected identifier.")
                        params.append(Identifier(Parser.tokenizer.next.value))
                        Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != ")":
                errfn("Expected ')' after the parameter listing.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != ":":
                errfn("Expected a ':' after the function introduction.")
            block_children = []
            Parser.tokenizer.select_next()
            while Parser.tokenizer.next.value != "end":
                block_children.append(Parser.parseStatement())
                Parser.tokenizer.select_next()
                if Parser.tokenizer.next.type == "EOF":
                    errfn("Expected an 'end' token to close the 'function' block.")
            Parser.tokenizer.select_next()
            if Parser.tokenizer.next.value != ";":
                errfn("Expected a ';' after the 'end' token.")
            return FuncDec([funcName] + params + [Block(block_children)])
                        
        elif Parser.tokenizer.next.value == ";":
            return NoOp()
        else:
            errfn(f"Not valid token: {Parser.tokenizer.next.value}")
    
    @staticmethod
    def parseBlock():
        children = []
        Parser.tokenizer.select_next()
        while Parser.tokenizer.next.type != "EOF":
            children.append(Parser.parseStatement())
            Parser.tokenizer.select_next()
        return Block(children)

    @staticmethod
    def run(source):
        Parser.tokenizer = Tokenizer(source)
        return Parser.parseBlock()

if __name__ == "__main__":
    parser = Parser()
    preprocessing = PrePro()
    with open(sys.argv[1], "r") as file:
        parser.run(preprocessing.filter(file.read())).evaluate(SymbolTable(None))
