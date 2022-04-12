/* Global timing block 

Creates a counter for the AD7961 module for 200 ns sampling.
Creates a slower counter that counts 200 ns periods (cycle counts) to update what data enters the DDR.

*/ 
module global_timing
    (
        input wire          clk_sys,                    // 200 MHz timing clk
        input wire          reset_n_i,                  // Reset signal, active low
        output reg [31:0] adc_tcyc_cnt,
        output reg [4:0] cycle_cnt,
        output reg adc_rd_en_emulator
    );

//------------------------------------------------------------------------------
//----------- Local Parameters for 5 MSPS update (200 ns period) ---------------
//------------------------------------------------------------------------------
// FPGA Clock Frequency
parameter real          FPGA_CLOCK_FREQ         = 200;  // MHz
// Conversion signal generation
parameter real          TCYC_PERIOD                    = 0.200; // us 
parameter       [31:0]  ADC_CYC_CNT             = FPGA_CLOCK_FREQ * TCYC_PERIOD - 1;
parameter       [4:0]   CYCLE_CNT = 9;   // DDR cycles - 1 before repeat 
 
// Update conversion timing counters (this counter is then used by the AD7961 module)
always @(posedge clk_sys)
begin
    if(reset_n_i == 1'b0)
    begin
        adc_tcyc_cnt <= ADC_CYC_CNT;
    end
    else
    begin
        if(adc_tcyc_cnt != 32'd0)
        begin
            adc_tcyc_cnt <= adc_tcyc_cnt - 32'd1;
        end
        else
        begin
            adc_tcyc_cnt <= ADC_CYC_CNT; 
        end
    end
end 

// create an ADC data valid pulse for situations when the ADCs are not connector (or not powered)
always @(posedge clk_sys)
begin
    if(reset_n_i == 1'b0) adc_rd_en_emulator <= 1'b0;
    else if (adc_tcyc_cnt == 32'd17) adc_rd_en_emulator <= 1'b1; //TODO - verify 
    else adc_rd_en_emulator <= 1'b0;
end 

// slower cycle counter 
always @(posedge clk_sys)
begin
    if(reset_n_i == 1'b0) cycle_cnt <= CYCLE_CNT;
    else
    begin
        if(adc_tcyc_cnt == 32'd0)
        begin
            if (cycle_cnt != 5'd0) cycle_cnt <= cycle_cnt - 5'd1;
            else cycle_cnt <= CYCLE_CNT;
        end
    end
end

endmodule