%{
#include <string>
#include "node.h"
#include "parser.hpp"

#define SAVE_TOKEN  yylval.string = new std::string(yytext, yyleng)
#define TOKEN(t)    (yylval.token = t)
%}

%option noyywrap

%%

[ \t\n]					        ;

"product"                       return TOKEN(TPRODUCT);
"name"				            return TOKEN(TNAME);
"description"				    return TOKEN(TDESCRIPTION);
"category"				        return TOKEN(TCATEGORY);
"price"				            return TOKEN(TPRICE);
"quantity"				        return TOKEN(TQUANTITY);
"type"				            return TOKEN(TTYPE);
"in"				            return TOKEN(TIN);
"out"				            return TOKEN(TOUT);
"rm"				            return TOKEN(TRM);
"print"				            return TOKEN(TPRINT);
"if"				            return TOKEN(TIF);
"while"				            return TOKEN(TWHILE);
"else"				            return TOKEN(TELSE);
"end"				            return TOKEN(TEND);
"function"				        return TOKEN(TFUNCTION);
"return"				        return TOKEN(TRETURN);
"or"				          	return TOKEN(TOR);
"and"				          	return TOKEN(TAND);
"not"				          	return TOKEN(TNOT);

[a-zA-Z_][a-zA-Z0-9_]*          SAVE_TOKEN; return TIDENTIFIER;
[0-9]+\.[0-9]* 			        SAVE_TOKEN; return TDOUBLE;
[0-9]+					        SAVE_TOKEN; return TINTEGER;
[.*]                            SAVE_TOKEN; return TSTRING;

"="						        return TOKEN(TEQUAL);
"=="				            return TOKEN(TCEQ);
"!="			                return TOKEN(TCNE);
"<"                             return TOKEN(TCLT);
"<="	          				return TOKEN(TCLE);
">"				          		return TOKEN(TCGT);
">="					        return TOKEN(TCGE);

"("	          					return TOKEN(TLPAREN);
")"					          	return TOKEN(TRPAREN);
"{"         					return TOKEN(TLBRACE);
"}"					          	return TOKEN(TRBRACE);

"."         					return TOKEN(TDOT);
","				          		return TOKEN(TCOMMA);
":"	                  		    return TOKEN(TCOLON);
";"	                  		    return TOKEN(TSEMICOLON);

"+"				          		return TOKEN(TPLUS);
"-"		          				return TOKEN(TMINUS);
"*"		          				return TOKEN(TMUL);
"/"				          		return TOKEN(TDIV);
"!"				          	    return TOKEN(TNOT);

.                               printf("Unknown token!\n"); yyterminate();

%%
