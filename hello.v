module WORD_SERIAL_SIMPLE #(
    parameter integer CLK_FREQ = 20000000,
    parameter integer BIT_HZ   = 1,
    parameter integer STR_LEN  = 5,
    parameter [8*STR_LEN-1:0] INPUT_STR = "hello"
)(
    input  wire clk,
    output wire bit_out,
    output wire LED_EDGE
);

    localparam integer TICKS_PER_BIT = (CLK_FREQ / BIT_HZ);
    localparam integer TOTAL_BITS    = 12 * STR_LEN;
    localparam integer EDGE_LED_MS   = 100;
    localparam integer PULSE_TICKS   = (CLK_FREQ/1000) * EDGE_LED_MS;

    function [4:0] alpha5;
        input [7:0] c;
        begin
            if (c >= "a" && c <= "z") alpha5 = c - "a";
            else if (c >= "A" && c <= "Z") alpha5 = c - "A";
            else alpha5 = 5'd0;
        end
    endfunction

    reg [12*STR_LEN-1:0] pattern;
    integer i;
    reg [7:0]  ch;
    reg [11:0] frame12;

    always @(*) begin
        pattern = {12*STR_LEN{1'b0}};
        for (i = 0; i < STR_LEN; i = i + 1) begin
            ch      = INPUT_STR[8*(STR_LEN-i)-1 -: 8];
            frame12 = {6'b000000, 1'b1, alpha5(ch)};
            pattern[12*(STR_LEN-i)-1 -: 12] = frame12;
        end
    end

    reg [31:0] tick_cnt = 32'd0;
    reg [31:0] state    = 32'd0;
    reg [3:0]  bit_pos  = 4'd0;

    wire bit_tick_pulse = (tick_cnt == TICKS_PER_BIT-1);

    always @(posedge clk) begin
        if (bit_tick_pulse) tick_cnt <= 32'd0;
        else                tick_cnt <= tick_cnt + 32'd1;
    end

    wire next_bit = pattern[TOTAL_BITS-1 - state];

    reg bit_out_r = 1'b0;
    always @(posedge clk) begin
        if (bit_tick_pulse) bit_out_r <= next_bit;
    end
    assign bit_out = bit_out_r;

    always @(posedge clk) begin
        if (bit_tick_pulse) begin
            if (state == TOTAL_BITS - 1) state <= 32'd0;
            else                         state <= state + 32'd1;

            if (bit_pos == 4'd11) bit_pos <= 4'd0;
            else                   bit_pos <= bit_pos + 4'd1;
        end
    end

    wire char_boundary_pulse = bit_tick_pulse && (bit_pos == 4'd11);

    reg [$clog2(PULSE_TICKS+1)-1:0] pulse_cnt = 'd0;
    reg edge_led = 1'b0;
    always @(posedge clk) begin
        if (char_boundary_pulse)         pulse_cnt <= PULSE_TICKS - 1;
        else if (pulse_cnt != 0)         pulse_cnt <= pulse_cnt - 1;
        edge_led <= (pulse_cnt != 0);
    end
    assign LED_EDGE = edge_led;

endmodule
