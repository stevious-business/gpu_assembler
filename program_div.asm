.init    , LDI $6 !1; # for increments
, LDI $7 !64; # for division
.xloop   , PLD @3 $1;

# calculate first y value
ADD $1 $6, WBL $1; # add one to x value for not breaking reasons
DIV $7 $1, WBH $2;

# calculate second y value
ADD $1 $6, WBL $3;
DIV $7 $3, WBH $3;

# find min and max of two y values
SUB $2 $3, BLT .b_larger;
REG $2   , WBL $5; # a larger
REG $3   , WBL $4;
         , JMP .postminmax;
.b_larger
REG $3   , WBL $5;
REG $2   , WBL $4;
.postminmax
SUB $1 $6, PST @0;
.yloop
SUB $4 $5, BGT .xloop; # if y > max y, exit
REG $4   , PST @1;
         , PLD @2 $0; # draw to screen
ADD $4 $6, WBL $4; # increment y value
         , JMP .yloop;
