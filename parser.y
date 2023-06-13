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
	std::vector<NVarAssignment*> *varvec;
	std::vector<NExpression*> *exprvec;
	std::string *string;
	int token;
}

/* Define our terminal symbols (tokens). This should
   match our tokens.l lex file. We also define the node type
   they represent.
 */
%token <string> TIDENTIFIER TINTEGER TDOUBLE TSTRING
%token <token> TPRODUCT TNAME TDESCRIPTION TCATEGORY TPRICE TQUANTITY TTYPE
%token <token> TIN TOUT TRM TPRINT TIF TELSE TWHILE TCOLON TEND TSEMICOLON TCOLON TFUNCTION
%token <token> TCEQ TCNE TCLT TCLE TCGT TCGE TEQUAL
%token <token> TLPAREN TRPAREN TLBRACE TRBRACE TCOMMA TDOT
%token <token> TPLUS TMINUS TMUL TDIV
%token <token> TRETURN TEXTERN

/* Define the type of node our nonterminal symbols represent.
   The types refer to the %union declaration above. Ex: when
   we call an ident (defined by union type ident) we are really
   calling an (NIdentifier*). It makes the compiler happy.
 */
%type <string> string
%type <expr> numeric ident expr stock_delta rel_expr term factor
%type <varvec> func_decl_args
%type <exprvec> call_args
%type <block> program stmts block
%type <stmt> stmt product_def product_rm stock_op var_assignment print if while func_decl function_call
%type <token> property_name

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

stmt : product_def { $$ = new NProductDeclaration(*$2); }
	 | product_rm { $$ = new NProductRm(*$2); }
	 | stock_op { $$ = new NStockOpStatement(*$2); }
	 | var_assignment { $$ = new NVarAssignment(*$2); }
	 | print { $$ = new NPrint(*$2); }
	 | if { $$ = new NIf(*$2); }
	 | while { $$ = new NLoopStatement(*$2); }
	 | func_decl { $$ = new NFunctionDeclaration(*$2); }
	 | function_call { $$ = new NFuncCallStatement(*$2); }
	 | TRETURN rel_expr { $$ = new NReturnStatement(*$2); }
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

stock_delta : numeric | ident | rel_expr
			;

var_assignment : ident TEQUAL rel_expr TSEMICOLON { $$ = new NVariableAssignment(*$1, *$3); }
			   | ident TDOT property_name TEQUAL rel_expr TSEMICOLON { $$ = new NVariableAssignment(*$1, *$3, *$5); }
			   ;

property_name : TNAME | TDESCRIPTION | TCATEGORY | TPRICE | TQUANTITY
			  ;

print : TPRINT string TSEMICOLON { $$ = new NPrintStatement(*$2); }
	  | TPRINT rel_expr TSEMICOLON { $$ = new NPrintStatement(*$2); }
	  ;
	  
if : TIF rel_expr TCOLON stmts TEND TSEMICOLON { $$ = new NIfStatement(*$2, *$4); }
   | TIF rel_expr TCOLON stmts TELSE TCOLON stmts TEND TSEMICOLON { $$ = new NIfStatement(*$2, *$4, *$7); }
   ;

while : TWHILE rel_expr TCOLON stmts TEND TSEMICOLON { $$ = new NWhileStatement(*$2, *$4); }
	  ;

func_decl : TFUNCTION ident TLPAREN func_decl_args TRPAREN TCOLON stmts TEND TSEMICOLON 
			{ $$ = new NFunctionDeclaration(*$2, *$4, *$7); delete $4; }
		  ;
	
func_decl_args : /*blank*/  { $$ = new VariableList(); }
		  | var_assignment { $$ = new VariableList(); $$->push_back($<var_assignment>1); }
		  | func_decl_args TCOMMA var_assignment { $1->push_back($<var_assignment>3); }
		  ;
	
rel_expr : expr
		 | rel_expr TOR expr { $$ = new BinaryOperator(*$1, "||", *$3); }
		 | rel_expr TAND expr { $$ = new BinaryOperator(*$1, "&&", *$3); }
		 | rel_expr TCEQ expr { $$ = new BinaryOperator(*$1, "==", *$3); }
		 | rel_expr TCNE expr { $$ = new BinaryOperator(*$1, "!=", *$3); }
		 | rel_expr TCLT expr { $$ = new BinaryOperator(*$1, "<", *$3); }
		 | rel_expr TCLE expr { $$ = new BinaryOperator(*$1, "<=", *$3); }
		 | rel_expr TCGT expr { $$ = new BinaryOperator(*$1, ">", *$3); }
		 | rel_expr TCGE expr { $$ = new BinaryOperator(*$1, ">=", *$3); }
		 ;
	
expr : term
	 | rel_expr TPLUS term { $$ = new BinaryOperator(*$1, "+", *$3); }
	 | rel_expr TMINUS term { $$ = new BinaryOperator(*$1, "-", *$3); }
	 | rel_expr TOR term { $$ = new BinaryOperator(*$1, "||", *$3); }
	 ;
	
term : factor
	 | term TMUL factor { $$ = new BinaryOperator(*$1, "*", *$3); }
	 | term TDIV factor { $$ = new BinaryOperator(*$1, "/", *$3); }
	 | term TAND factor { $$ = new BinaryOperator(*$1, "&&", *$3); }
	 ;

factor : TPLUS factor { $$ = new UnaryOperator("+", *$2); }
	   | TMINUS factor { $$ = new UnaryOperator("-", *$2); }
	   | TNOT factor { $$ = new UnaryOperator("!", *$2); }
	   | numeric
	   | TLPAREN rel_expr TRPAREN {}
	   | ident {}
	   | ident TDOT property_name { $$ = new NProductAttribute(*$1, *$3); }
	   | ident TDOT TTYPE { $$ = new NVarType(*$1); }
	   | function_call {}
	   ;

function_call : ident TLPAREN call_args TRPAREN { $$ = new NFunctionCall(*$1, *$3); }
			  ;
	
call_args : /*blank*/  { $$ = new ExpressionList(); }
		  | rel_expr { $$ = new ExpressionList(); $$->push_back($1); }
		  | call_args TCOMMA rel_expr  { $1->push_back($3); }
		  ;

ident : TIDENTIFIER { $$ = new NIdentifier(*$1); delete $1; }
	  ;

numeric : TINTEGER { $$ = new NInteger(atol($1->c_str())); delete $1; }
		| TDOUBLE { $$ = new NDouble(atof($1->c_str())); delete $1; }
		;

string : TSTRING { $$ = new NString(*$1); delete $1; }
	   ;

%%
