.init    , LDI $6 !1; # for increments
.xloop   , PLD @3 $1;
ADD $1 $1, WBL $2;
ADD $2 $6, WBL $2;
ADD $1 $6, WBL $3;
ADD $3 $3, WBL $3;
ADD $3 $6, WBL $3;
SUB $2 $3, BLT .b_larger;
REG $2   , WBL $5; # a larger
REG $3   , WBL $4;
         , JMP .postminmax;
.b_larger
REG $3   , WBL $5;
REG $2   , WBL $4;
.postminmax
REG $1   , PST @0;
.yloop
SUB $4 $5, BEQ .xloop; # if y == max y, exit
REG $4   , PST @1;
         , PLD @2 $0; # draw to screen
ADD $4 $6, WBL $4; # increment y value
         , JMP .yloop;
