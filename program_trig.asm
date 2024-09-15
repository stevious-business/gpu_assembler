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

# find min and max of two y values
SUB $2 $3, BLT .b_larger;
REG $2   , WBL $5; # a larger
REG $3   , WBL $4;
         , JMP .postminmax;
.b_larger
REG $3   , WBL $5;
REG $2   , WBL $4;
.postminmax
REG $1, PST @0;
.yloop
SUB $4 $5, BGT .xloop; # if y > max y, exit
REG $4   , PST @1;
         , PLD @2 $0; # draw to screen
ADD $4 $6, WBL $4; # increment y value
         , JMP .yloop;
