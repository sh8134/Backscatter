///////////////////////////////////////////////////////////////////////////////////////////////////
// Company: <Name>
//
// File: pattern110010.v
// File history:
//      <Revision number>: <Date>: <Comments>
//      <Revision number>: <Date>: <Comments>
//      <Revision number>: <Date>: <Comments>
//
// Description: 
//
// <Description here>
//
// Targeted device: <Family::IGLOO> <Die::AGLN250V2> <Package::100 VQFP>
// Author: <Name>
//
/////////////////////////////////////////////////////////////////////////////////////////////////// 

//`timescale <time_units> / <precision>
module LED1_ON (
    input wire clk,              // SmartDesign?? ???? clk
    output reg led1,
    output reg led2
);

    parameter CLK_FREQ = 25000000;   // 25MHz
    reg [25:0] counter = 0;
    reg [2:0] state = 0;              // 0~5 ??
    reg [5:0] pattern = 6'b110010;    // ??? ??

    always @(posedge clk) begin
        if (counter >= CLK_FREQ - 1) begin
            counter <= 0;

            if (state >= 5)
                state <= 0;
            else
                state <= state + 1;

        end else begin
            counter <= counter + 1;
        end
    end

    always @(*) begin
        led1 = 1;
        led2 = pattern[5 - state]; // MSB?? ?? ?? (??? ????)
    end

endmodule
