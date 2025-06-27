module LED1_ON (
    input wire clk,              // SmartDesign에서 연결될 clk
    output reg led1,
    output reg led2,
    output reg led3,
    output reg led4,
    output reg led5,
    output reg led6
);

    parameter CLK_FREQ = 50000000;   // 50MHz
    reg [25:0] counter = 0;
    reg state = 0;

    always @(posedge clk) begin
        if (counter >= CLK_FREQ - 1) begin
            counter <= 0;
            state <= ~state;
        end else begin
            counter <= counter + 1;
        end
    end

    always @(*) begin
        led1 = state;
        led2 = state;
        led3 = state;
        led4 = state;
        led5 = state;
        led6 = state;
    end

endmodule