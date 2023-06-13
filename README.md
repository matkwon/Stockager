# Stockager
Developed by Matheus Kwon

---
## Introduction
Stockager is a stock management DSL (Domain-Specific Language), developed for the Computer Engineering subject Computational Logic. It is focused on making stock flow in a product based business model easier. The main feature functionalities of Stockager are to create the definition of a product, increase or decrease its quantity, change its properties and to remove its definition. Other than that, it has the functionalities of variable assignment, conditional operations, looping and function definition and call.

## EBNF

```
program            = { statement } ;
statement          = product_def | product_rm | stock_op | var_assignment | print | if_statement | loop_chain | function_def | function_call | return ;

product_def        = "product", identifier, "{", product_properties, "}" ;
product_properties = "name", ":", string, ";", "description", ":", string, ";", "category", ":", string, ";", "price", ":", rel_expression, ";", "quantity", ":", rel_expression, ";";

product_rm         = "rm", identifier, ";" ;

stock_op           = ("in" | "out"), identifier, rel_expression, ";" ;

var_assignment     = identifier, [ ".", property_name ], "=", rel_expression ;
property_name      = "name" | "description" | "category" | "price" | "quantity" ;

print              = "print", rel_expression, ";" ;

if_statement       = "if", rel_expression, ":", program, [ "else", ":", program ], "end", ";" ;
loop_chain         = "while", rel_expression, ":", program, "end", ";" ;

function_def       = "function", identifier, "(", [ param_list ], ")", ":", program, "end", ";" ;
param_list         = identifier, { "," identifier } ;

rel_expression     = expression, { (">" | "<" | "==" | "!=" | ">=" | "<="), expression } ;
expression         = term, { ("+" | "-" | "or"), term } ;
term               = factor, { ("*" | "/" | "and"), factor } ;
factor             = (("+" | "-" | "not"), factor) | number | string | "(", rel_expression, ")" | identifier, [ ".", (property_name | "type") ] | function_call ;

function_call      = identifier, "(", [ arg_list ], ")", ";" ;
arg_list           = rel_expression, { "," rel_expression } ;

return             = "return", rel_expression, ";";

identifier         = letter, { letter | digit | "_" } ;
string             = ("\'" | "\"") { letter | digit | special } ("\'" | "\"") ;
number             = digit, { digit }, [ ".", digit, { digit } ] ;
letter             = "A" | "B" | ... | "Z" | "a" | "b" | ... | "z" ;
digit              = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
special            = " " | "!" | "?" | "/" | "\" | "," | "." | """ | ";" | ":" | "+" | "=" | "-" | "_" | "@" | "#" | "$" | "%" | "^" | "&" | "*" | "(" | ")" | "[" | "]" | "{" | "}" | "|" | "<" | ">" | "`" | "~" ;
```

## Examples

- Creating the definition of an optical mouse and changing its stock quantity:
```js
product mouse { 
    name: 'Optical Mouse'; 
    description: 'Mouse with optical technology'; 
    category: 'Accessories'; 
    price: 29.99; 
    quantity: 100; 
}

in mouse 10;
out mouse 5;
```

- Removing the definition of products that are no longer in the company's portfolio:
```js
rm laptop;
rm mouse;
rm webcam;
```

- Defining a function for cart pricing:
```js
function cart_price(prod):
    return prod.price * prod.quantity;
    end;
```

- Defining a function for a combo promotion and calling it:
```js
function peripherals_combo_promotion():
    out monitor 1;
    out keyboard 1;
    out mouse 1;
    end;

peripherals_combo_promotion()
```

## Testing
Test with:
```sh
python main.py test.st
```