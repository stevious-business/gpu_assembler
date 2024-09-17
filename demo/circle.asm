.init , LDI $10 !255;
, LDI $11 !16;
, LDI $12 !32;
, LDI $13 !1;
, LDI $14 !64;
# function: 2sqrt(255-(x/2-16)²)+32
.xloop , PLD @3 $1; # $1 = x
SUB $14 $1, BNE .notend;
, PLD @0 $0;
.notend
# x/2 - 16
SUB $1 $13, WBL $3;
REG $1, RSH $1;
SUB $1 $11, WBL $2;
, BGE .positive1; # x/2 > 16 -> skip inversion
SUB $0 $2, WBL $2;
.positive1
MUL $2 $2, WBL $2;
, WBH $4;
REG $4, BNE .xloop; # skip if we had a result >255
SUB $10 $2, WBL $2;
SQR $2, WBL $2;
ADD $2 $2, WBL $2; # $2 = 2sqrt(255-(x/2-16)²)
REG $3, PST @0;
REG $3, PST @2;
ADD $12 $2, PST @1;
ADD $2 $13, WBL $2;
SUB $12 $2, PST @3;

, PLD @2 $0;

, JMP .xloop;
