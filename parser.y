%{
	#include "node.h"
        #include <cstdio>
        #include <cstdlib>
	NBlock *programBlock; /* the top level root node of our final AST */

	extern int yylex();
	void yyerror(const char *s) { std::printf("Error: %s\n", s);std::exit(1); }
%}

/* Represents the many different ways we can access our data */
%union {
	Node *node;
	NBlock *block;
	NExpression *expr;
	NStatement *stmt;
	NIdentifier *ident;
	NVariableDeclaration *var_assignment;
	std::vector<NVariableDeclaration*> *varvec;
	std::vector<NExpression*> *exprvec;
	std::string *string;
	int token;
}

/* Define our terminal symbols (tokens). This should
   match our tokens.l lex file. We also define the node type
   they represent.
 */
%token <string> TIDENTIFIER TINTEGER TDOUBLE TSTRING
%token <token> TPRODUCT TNAME TDESCRIPTION TCATEGORY TPRICE TQUANTITY
%token <token> TIN TOUT TRM TPRINT TIF TELSE TWHILE TDO TEND TSEMICOLON TCOLON TFUNCTION
%token <token> TCEQ TCNE TCLT TCLE TCGT TCGE TEQUAL
%token <token> TLPAREN TRPAREN TLBRACE TRBRACE TCOMMA TDOT
%token <token> TPLUS TMINUS TMUL TDIV
%token <token> TRETURN TEXTERN

/* Define the type of node our nonterminal symbols represent.
   The types refer to the %union declaration above. Ex: when
   we call an ident (defined by union type ident) we are really
   calling an (NIdentifier*). It makes the compiler happy.
 */
%type <ident> ident
%type <expr> numeric expr 
%type <varvec> func_decl_args
%type <exprvec> call_args
%type <block> program stmts block
%type <stmt> stmt var_assignment func_decl extern_decl
%type <token> comparison

/* Operator precedence for mathematical operators */
%left TPLUS TMINUS
%left TMUL TDIV

%start program

%%

program : stmts { programBlock = $1; }
		;
		
stmts : stmt { $$ = new NBlock(); $$->statements.push_back($<stmt>1); }
	  | stmts stmt { $1->statements.push_back($<stmt>2); }
	  ;

stmt : product_def { $$ = new NProdDefStatement(*$2); }
	 | product_rm { $$ = new NProdRmStatement(*$2); }
	 | stock_op { $$ = new NStockOpStatement(*$2); }
	 | var_assignment { $$ = new NVarAssignStatement(*$2); }
	 | print { $$ = new NPrintStatement(*$2); }
	 | if_statement { $$ = new NIfStatement(*$2); }
	 | loop_chain { $$ = new NLoopStatement(*$2); }
	 | function_def { $$ = new NFuncDefStatement(*$2); }
	 | function_call { $$ = new NFuncCallStatement(*$2); }
	 | TRETURN expr { $$ = new NReturnStatement(*$2); }
     ;

product_def : TPRODUCT ident TLBRACE 
			  TNAME TCOLON string TSEMICOLON 
			  TDESCRIPTION TCOLON string TSEMICOLON 
			  TCATEGORY TCOLON string TSEMICOLON 
			  TPRICE TCOLON numeric TSEMICOLON 
			  TQUANTITY TCOLON numeric TSEMICOLON 
			  TRBRACE { $$ = new NProductDeclaration(*$2, *$6, *$10, *$14, *$18, *$22); }
			  ;

product_rm : TRM ident TSEMICOLON { $$ = new NProductRemoval(*$2); }
		   ;

stock_op : TIN ident stock_delta TSEMICOLON { $$ = new NStockIn(*$2, *$3); }
		 | TOUT ident stock_delta TSEMICOLON { $$ = new NStockOut(*$2, *$3); }
		 ;

stock_delta : numeric | ident | expr
			;

var_assignment : ident TEQUAL expr TSEMICOLON { $$ = new NVariableAssignment(*$1, *$3); }
			   | ident TDOT property_name TEQUAL expr TSEMICOLON { $$ = new NVariableAssignment(*$1, *$3, *$5); }
			   ;

property_name : TNAME | TDESCRIPTION | TCATEGORY | TPRICE | TQUANTITY
			  ;

print : TPRINT string TSEMICOLON { $$ = new NPrintStatement(*$2); }
	  | TPRINT expr TSEMICOLON { $$ = new NPrintStatement(*$2); }
	  ;
	  
if : TIF comparison TDO stmts TEND TSEMICOLON { $$ = new NIfStatement(*$2, *$4); }
   | TIF comparison TDO stmts TELSE stmts TEND TSEMICOLON { $$ = new NIfStatement(*$2, *$4, *$6); }
   ;

while : TWHILE comparison TDO stmts TEND TSEMICOLON { $$ = new NWhileStatement(*$2, *$4); }
	  ;

comparison : expr TCEQ expr { $$ = new NBinaryOperator(*$1, "==", *$3); }
		   | expr TCNE expr { $$ = new NBinaryOperator(*$1, "!=", *$3); }
		   | expr TCLT expr { $$ = new NBinaryOperator(*$1, "<", *$3); }
		   | expr TCLE expr { $$ = new NBinaryOperator(*$1, "<=", *$3); }
		   | expr TCGT expr { $$ = new NBinaryOperator(*$1, ">", *$3); }
		   | expr TCGE expr { $$ = new NBinaryOperator(*$1, ">=", *$3); }
		   ;

func_decl : TFUNCTION ident TLPAREN func_decl_args TRPAREN stmts TEND TSEMICOLON 
			{ $$ = new NFunctionDeclaration(*$1, *$2, *$4, *$6); delete $4; }
		  ;
	
func_decl_args : /*blank*/  { $$ = new VariableList(); }
		  | var_assignment { $$ = new VariableList(); $$->push_back($<var_assignment>1); }
		  | func_decl_args TCOMMA var_assignment { $1->push_back($<var_assignment>3); }
		  ;
	
expr : term
	 | expr TPLUS term { $$ = new BinaryOperator(*$1, "+", *$3); }
	 | expr TMINUS term { $$ = new BinaryOperator(*$1, "-", *$3); }
	 ;
	
term : factor
	 | term TMUL factor { $$ = new BinaryOperator(*$1, "*", *$3); }
	 | term TDIV factor { $$ = new BinaryOperator(*$1, "/", *$3); }
	 ;

factor : TPLUS factor { $$ = new UnaryOperator("+", *$2); }
	   | TMINUS factor { $$ = new UnaryOperator("-", *$2); }
	   | numeric
	   | TLPAREN expr TRPAREN {}
	   | ident {}
	   | ident TDOT property_name { $$ = new NProductAttribute(*$1, *$3); }
	   | function_call {}
	   ;

function_call : ident TLPAREN call_args TRPAREN { $$ = new NFunctionCall(*$1, *$3); }
			  ;
	
call_args : /*blank*/  { $$ = new ExpressionList(); }
		  | expr { $$ = new ExpressionList(); $$->push_back($1); }
		  | call_args TCOMMA expr  { $1->push_back($3); }
		  ;

ident : TIDENTIFIER { $$ = new NIdentifier(*$1); delete $1; }
	  ;

numeric : TINTEGER { $$ = new NInteger(atol($1->c_str())); delete $1; }
		| TDOUBLE { $$ = new NDouble(atof($1->c_str())); delete $1; }
		;

string : TSTRING { $$ = new NString(*$1); delete $1; }
	   ;

%%
