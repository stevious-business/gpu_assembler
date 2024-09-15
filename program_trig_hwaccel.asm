.init    , LDI $6 !1; # for increments
, LDI $7 !4; # for trig
, LDI $8 !32; # for adding
.xloop   , PLD @3 $1;

# calculate first y value
MUL $1 $7, WBL $2; # same as 2 lshifts but oh well
TRG $2   , RSH $2;
REG $2   , RSH $2;
ADD $2 $8, WBL $2;

# calculate second y value
ADD $1 $6, WBL $3;
MUL $3 $7, WBL $3; # same as 2 lshifts but oh well
TRG $3   , RSH $3;
REG $3   , RSH $3;
ADD $3 $8, WBL $3;

# HAHAHA LMAO IM A SHIT ASS PROGRAMMER
REG $1, PST @0;
REG $2, PST @1;
REG $1, PST @2;
REG $3, PST @3;
, PLD @2 $0;
, JMP .xloop;
