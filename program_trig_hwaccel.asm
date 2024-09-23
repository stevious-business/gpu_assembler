.init    , LDI $6 !1; # for increments
, LDI $7 !4; # for trig
, LDI $8 !32; # for adding
, LDI $9 !0; # frame no.
, LDI $10 !0; # for help with frame shit
, LDI $11 !1;
, LDI $14 !64; # for ending
.xloop   , PLD @3 $1;

SUB $14 $10, BNE .checkover64;      # if page == 64:
    # check under 64
    SUB $14 $1, BGT .new_frame_under; # if x < 64:
    , JMP .frame_continue;
        .new_frame_under
        , LDI $10 !0;                 # page = 0
        , JMP .new_frame;             # new frame type shi
    # check over 64                 # else:
    .checkover64
    SUB $1 $14, BGE .new_frame_over; # if x >= 64:
    , JMP .frame_continue;
        .new_frame_over
        , LDI $10 !64;                 # page = 64
    .new_frame
    , PLD @1 $0; # buffer synchronise
    ADD $11 $9, WBL $9;
.frame_continue

REG $1, WBL $12; # 18
SUB $1 $9, WBL $1;

# calculate first y value
MUL $1 $7, WBL $2; # same as 2 lshifts but oh well
TRG $2   , RSH $2;
REG $2   , RSH $2;
ADD $2 $8, WBL $2;

# calculate second y value
ADD $1 $6, WBL $3;
MUL $3 $7, WBL $3;
TRG $3   , RSH $3;
REG $3   , RSH $3;
ADD $3 $8, WBL $3;

REG $12, PST @0;
REG $2, PST @1;
REG $12, PST @2;
REG $3, PST @3;
, PLD @2 $0;
, JMP .xloop;
