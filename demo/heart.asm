.init
# load constants
, LDI $10 !16;
, LDI $11 !24;
, LDI $12 !32;
, LDI $13 !48;
, LDI $14 !64;
, LDI $15 !-40;
.xloop , PLD @3 $1;
SUB $10 $1, BGT .xloop;
SUB $13 $1, BLT .xloop;
REG $1, PST @0;
REG $1, PST @2;
# calculate bottom value
SUB $12 $1, BLT .greater32;
SUB $13 $1, PST @1; # 48-x
, JMP .after_bottom_value;
.greater32
SUB $1 $10, PST @1; # x-16
.after_bottom_value
# calculate top value

SUB $12 $1, BLT .greater32_2;
SUB $11 $1, WBL $2;
, JMP .after_top_value;
.greater32_2
ADD $15 $1, WBL $2;
.after_top_value

REG $2, BGE .positive1;
SUB $0 $2, WBL $2;
.positive1
MUL $2 $2, WBL $2; # square it!
, WBH $4;
REG $4, BNE .xloop; # skip if we had a result >255
SUB $14 $2, WBL $2;
SQR $2, WBL $2;
ADD $2 $12, WBL $2; # 2 = sqrt(64-(24-x)²)+32
REG $2, PST @3;
, PLD @2 $0;

, JMP .xloop;
