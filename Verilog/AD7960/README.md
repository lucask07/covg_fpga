Investigations from Ian Bonequi Delgadillo, 2021/06/09

Information on clocks and the AD7960 code starting from the following [forum post](https://ez.analog.com/fpga/f/q-a/81511/ad7961-reference-design-gated-clock)

It was a post about the exact same AD7961.v file that is being used in the Verilog project, except the issue was, oddly enough, about the output clock, and not the input like we both observed when trying to run implementation/generate bit file.  The OP was also being given the same "quick fix" suggestion (given by the ISE application) about setting CLOCK\_DEDICATED\_ROUTE = FALSE in the constraints file.  However, another user suggested using an ODDR primitive -> OBUFDS in order to properly output the differential clock, and this user also stated that this is generally "the recommended method" to do.  At this point I was starting to wonder if there was also some sort of method similar to this for incoming differential clocks that would eliminate the implementation/clock dedicated route errors that the DCO\_N and DCO\_P signals were initially giving.

It took a good long while of sifting through many Xilinx forum threads before I found some issues that were particularly relevant to the issue we were running into, and that were clear enough for me to understand (these concepts are all very new to me).  However, I eventually found the following thread that gave me a better idea of the idea of ODDR primitive -> [OBUFDS for outputting clocks](https://forums.xilinx.com/t5/Other-FPGA-Architecture/Clock-capable-pin-pair-as-input-and-output/m-p/900002#M29713)

User avrumw states in the thread that the "best" way to output a clock is to use ODDR primitive, and this made me more confident in the whole idea of using the ODDR primitive when outputting the AD7961 differential clock.  I kept researching and I found out about the idea of "clock forwarding", which were the key words I was missing the whole time.  This is the name given to the whole idea of using the ODDR primitive -> OBUFDS to output the clock.

Here are some more threads that I found particularly helpful in explaining why the ODDR is used for [clock forwarding](https://forums.xilinx.com/t5/Timing-Analysis/Why-ODDR-for-forwarded-clock/td-p/756737)
[and](https://forums.xilinx.com/t5/Other-FPGA-Architecture/Output-differential-clock-kintex-7/m-p/771628#M22049) (the post by user avrumw is the one I found especially useful [here)](https://forums.xilinx.com/t5/Other-FPGA-Architecture/LVDS-CLK-P-N-be-routed-to-MRCC-SRCC-or-regular-differential-IOs/td-p/913220)

And here is another relevant error solution by Xilinx which explained clock forwarding that I found very [useful](
https://www.xilinx.com/support/answers/35032.html)

It is my understanding that when outputting clocks the ODDR is the best method because otherwise, the clock would have to go through the general routing fabric instead of staying on the dedicated clock network (introducing a myriad of issues).

Additionally, while reading through the threads, the collective conclusion was essentially that input clocks must be input through clock capable pins, but I think this should be no issue since we have already addressed this.
