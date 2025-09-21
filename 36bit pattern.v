module LED1_ON (
    input  wire clk,              // 클럭 입력
    output reg  led1,
    output reg  led2
);

    parameter CLK_FREQ = 20000000;   // 20MHz
    reg [25:0] counter = 0;
    reg [5:0]  state   = 0;          // 0~35 (36패턴)

    // 입력 문자열 (5글자)
    reg [8*5-1:0] input_str = "abcde";

    // 최종 36비트 패턴
    reg [35:0] pattern;

    integer i;
    reg [7:0] char;
    reg [4:0] code;
    reg [5:0] code6 [0:4];

    // 문자열을 36비트 패턴으로 변환
    always @(*) begin
        for (i = 0; i < 5; i = i + 1) begin
            char    = input_str[8*(5-i)-1 -: 8];  // i번째 문자 추출
            code    = char - "a";                 // 'a' → 0, 'b' → 1 ...
            code6[i] = {1'b0, code};              // 앞에 0 붙여서 6비트
        end
        // 최종 패턴 = 111111 + code6[0..4]
        pattern = {6'b111111, code6[0], code6[1], code6[2], code6[3], code6[4]};
    end

    // 카운터: CLK_FREQ마다 state 증가
    always @(posedge clk) begin
        if (counter >= CLK_FREQ - 1) begin
            counter <= 0;

            if (state >= 35)
                state <= 0;
            else
                state <= state + 1;

        end else begin
            counter <= counter + 1;
        end
    end

    // LED 출력
    always @(*) begin
        led1 = 1;                             // 항상 ON
        led2 = pattern[35 - state];           // MSB부터 순차적으로 출력
    end

endmodule