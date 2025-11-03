module LED1_ON (
    input wire clk,              // SmartDesign?? ??? clk
    output reg led1,
    output reg led2
);

    parameter CLK_FREQ = 20000000;   // 50MHz
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
        led1 = 1;
        led2 = state;
    end

endmodule