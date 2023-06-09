// --------- The DDR section is derived from OpalKelly ramtest.v provided in the FrontPanelAPI
// this is intended to be used on OpalKelly devices only
// -----------------------------------------  
// Copyright (c) 2005-2016 Opal Kelly Incorporated

`timescale 1ns/1ps
//`default_nettype none

module ddr3_test
	(
	input  wire          clk,
	(* KEEP = "TRUE" *)input  wire          reset,
	(* KEEP = "TRUE" *)input  wire          write1_en,
	(* KEEP = "TRUE" *)input  wire          read1_en,
	(* KEEP = "TRUE" *)input  wire          write2_en,
	(* KEEP = "TRUE" *)input  wire          read2_en,
	(* KEEP = "TRUE" *)input  wire          calib_done,
	(* KEEP = "TRUE" *)input  wire          adc_addr_reset,
	(* KEEP = "TRUE" *)input  wire          adc_addr_restart,
	
	//DDR Input Buffer (ib_)  // DAC function generator data -- not timing sensitive 
	(* KEEP = "TRUE" *)output reg           ib_re,
	(* KEEP = "TRUE" *)input  wire [255:0]  ib_data,
	(* KEEP = "TRUE" *)input  wire [6:0]    ib_count,
	(* KEEP = "TRUE" *)input  wire          ib_valid,
	(* KEEP = "TRUE" *)input  wire          ib_empty,
	//DDR Output Buffer (ob_)  // DAC function generator data out to SPI controller -- must ensure this FIFO doesn't empty 
	(* KEEP = "TRUE" *)output reg           ob_we,
	(* KEEP = "TRUE" *)output reg  [255:0]  ob_data,
	(* KEEP = "TRUE" *)input  wire [7:0]    ob_count,
	(* KEEP = "TRUE" *)input  wire          ob_full,
    //DDR Input Buffer #2 (ib2_)  // ADC data -- must ensure this FIFO doesn't fill 
    (* KEEP = "TRUE" *)output reg           ib2_re,
    (* KEEP = "TRUE" *)input  wire [255:0]  ib2_data,
    (* KEEP = "TRUE" *)input  wire [7:0]    ib2_count,
    (* KEEP = "TRUE" *)input  wire          ib2_valid,
    (* KEEP = "TRUE" *)input  wire          ib2_empty,
    //DDR Output Buffer #2 (ob2_)  // 
    (* KEEP = "TRUE" *)output reg           ob2_we,
    (* KEEP = "TRUE" *)output reg  [255:0]  ob2_data,
    (* KEEP = "TRUE" *)input  wire [6:0]    ob2_count,
    (* KEEP = "TRUE" *)input  wire          ob2_full,
    // count of data in buffer2 
	(* KEEP = "TRUE" *)output reg  [31:0]  adc_data_count,

	// MIG interface -- doesn't change if extra buffers are added 
	(* KEEP = "TRUE" *)input  wire          app_rdy,
	(* KEEP = "TRUE" *)output reg           app_en,
	(* KEEP = "TRUE" *)output reg  [2:0]    app_cmd,
	(* KEEP = "TRUE" *)output reg  [29:0]   app_addr,
	
	(* KEEP = "TRUE" *)input  wire [255:0]  app_rd_data,
	(* KEEP = "TRUE" *)input  wire          app_rd_data_end,
	(* KEEP = "TRUE" *)input  wire          app_rd_data_valid,
	
	(* KEEP = "TRUE" *)input  wire          app_wdf_rdy,
	(* KEEP = "TRUE" *)output reg           app_wdf_wren,
	(* KEEP = "TRUE" *)output reg  [255:0]  app_wdf_data,
	(* KEEP = "TRUE" *)output reg           app_wdf_end,
	(* KEEP = "TRUE" *)output wire [31:0]   app_wdf_mask,
	
    (* KEEP = "TRUE" *)output reg  [29:0] cmd_byte_addr_wr,
    (* KEEP = "TRUE" *)output reg  [29:0] cmd_byte_addr_rd,
    (* KEEP = "TRUE" *)output reg  [29:0] cmd_byte_addr_wr2,
    (* KEEP = "TRUE" *)output reg  [29:0] cmd_byte_addr_rd2,
    
    (* KEEP = "TRUE" *)input  wire          adc_write_rollover  // if true than the buffer2 pointer rollsover when it reaches the end, otherwise it is paused
	);

localparam FIXED_INDEX = 30'h3_7f_ff_f8;
localparam FIXED_INDEX2 = 30'hf_ff_ff_f8;
localparam FIXED_INDEX2_START = 30'h3_80_00_00;

localparam OUTGOING_PIPE_FIFO_SIZE           = 128;  // this is the size of the 256 wide side. 1024*32 and 256*128=32678 
localparam HALF_FIFO_SIZE      = 128;  // ADC data to DDR; and DAC data from DDR

localparam BURST_UI_WORD_COUNT = 2'd1; //(WORD_SIZE*BURST_MODE/UI_SIZE) = BURST_UI_WORD_COUNT : 32*8/256 = 1  // burst per address value 
localparam ADDRESS_INCREMENT   = 5'd8; // UI Address is a word address. BL8 Burst Mode = 8.



(* KEEP = "TRUE" *)reg  [1:0]  burst_count;

(* KEEP = "TRUE" *)reg         write1_mode;
(* KEEP = "TRUE" *)reg         read1_mode;
(* KEEP = "TRUE" *)reg         write2_mode;
(* KEEP = "TRUE" *)reg         read2_mode;
(* KEEP = "TRUE" *)reg         reset_d;
(* KEEP = "TRUE" *)reg         adc_addr_reset_reg;
(* KEEP = "TRUE" *)reg         wr2_buf_pause;
(* KEEP = "TRUE" *)reg         adc_write_rollover_reg;


assign app_wdf_mask = 16'h0000;

always @(posedge clk) write1_mode <= write1_en;
always @(posedge clk) read1_mode <= read1_en;
always @(posedge clk) write2_mode <= write2_en;
always @(posedge clk) read2_mode <= read2_en;
always @(posedge clk) reset_d <= reset;
always @(posedge clk) adc_write_rollover_reg <= adc_write_rollover;


(* KEEP = "TRUE" *)integer state;
localparam s_idle    = 0,
           s_write_0 = 10,
           s_write_1 = 11,
           s_write_2 = 12,
           s_write_3 = 13,
           s_write_4 = 14,
           s_read_0  = 20,
           s_read_1  = 21,
           s_read_2  = 22,
           s_read_3  = 23,
           s_read_4  = 24,
           s_write2_0 = 30,
           s_write2_1 = 31,
           s_write2_2 = 32,
           s_write2_3 = 33,
           s_write2_4 = 34,
           s_read2_0  = 40,
           s_read2_1  = 41,
           s_read2_2  = 42,
           s_read2_3  = 43,
           s_read2_4  = 44;
                      
always @(posedge clk) begin
	if (reset_d) begin
		state             <= s_idle;
		burst_count       <= 2'b00;
		cmd_byte_addr_wr  <= 0;
		cmd_byte_addr_rd  <= 0;
        cmd_byte_addr_wr2  <= FIXED_INDEX2_START;
        cmd_byte_addr_rd2  <= FIXED_INDEX2_START;
		app_en            <= 1'b0;
		app_cmd           <= 3'b0;
		app_addr          <= 30'b0; 
		app_wdf_wren      <= 1'b0;
		app_wdf_end       <= 1'b0;
		adc_data_count    <= 16'b0;
		wr2_buf_pause     <= 1'b0;
	end else begin
		app_en            <= 1'b0;
		app_wdf_wren      <= 1'b0;
		app_wdf_end       <= 1'b0;
		ib_re             <= 1'b0;
		ob_we             <= 1'b0;
		ib2_re             <= 1'b0;
        ob2_we             <= 1'b0;
        if (adc_addr_reset == 1'b1) adc_addr_reset_reg <= 1'b1;

		case (state)
			s_idle: begin  // only 1 clock cycle (at 200 MHz) of overhead in going back to the idle state 
				burst_count <= BURST_UI_WORD_COUNT-1;
				adc_addr_reset_reg <= 1'b0;  
				if (adc_addr_reset_reg == 1'b1) begin
				    state <= s_idle;
				    if (adc_addr_restart == 1'b0) cmd_byte_addr_rd2 <= FIXED_INDEX2_START; // restart 
				    else  cmd_byte_addr_rd2 <= cmd_byte_addr_wr2; // start at current write pointer
				end
				// Only start writing when initialization done
				// Check to ensure that the input buffer has enough data for a burst : 32w_1024 x 256w_128 : DDR3_DAC_WRITE_ENABLE
				else if (calib_done==1 && write1_mode==1 && (ib_count >= BURST_UI_WORD_COUNT)) begin // if the in-bound FIFO has enough data 
					app_addr <= cmd_byte_addr_wr;
					app_cmd <= 3'b000;  
					state <= s_write_0;
					// Check to ensure that the output buffer has enough space for a burst
				end 
				// 256w_128 (DDR write) x 128w_256 (read) [Prevent from emptying]
				else if (calib_done==1 && ((read1_mode==1 && (ob_count < (HALF_FIFO_SIZE)) )) ) begin  // changed to ensure not always serviced 
					app_addr <= cmd_byte_addr_rd;
					app_cmd <= 3'b001; 
					state <= s_read_0;
				end
				// w128_256_r256_128 (to DDR)  [ADC data to DDR - prevent from filling]
                else if (calib_done==1 && write2_mode==1 && (ib2_count >= HALF_FIFO_SIZE) && (wr2_buf_pause == 1'b0 || adc_write_rollover_reg == 1'b1)) begin  // changed to ensure not always serviced, only when not paused
                    app_addr <= cmd_byte_addr_wr2;
                    app_cmd <= 3'b000; 
                    state <= s_write2_0;
                end
                // w256_128 (from DDR)  r32_1024 (to OpalKelly)
                else if (calib_done==1 && read2_mode==1 && (ob2_count<(OUTGOING_PIPE_FIFO_SIZE-16-BURST_UI_WORD_COUNT) ) ) begin  // service if others don't need it
                    app_addr <= cmd_byte_addr_rd2;
                    app_cmd <= 3'b001; 
                    state <= s_read2_0;
                end
			end
            // ----------------------------------------
			s_write_0: begin
				state <= s_write_1;
				ib_re <= 1'b1;
			end

			s_write_1: begin  // stay in s_write_1 until ib_valid
				if(ib_valid==1) begin
					app_wdf_data <= ib_data;
					state <= s_write_2;
				end
			end

            /*
            app_wdf_rdy: This output indicates that the write data FIFO is ready to receive data. Write data is accepted
            when both app_wdf_rdy and app_wdf_wren are asserted.
            */
			s_write_2: begin
    			//app_cmd <= 3'b000; // change LJK 2021/11/11
				if (app_wdf_rdy == 1'b1) begin  //app_wdf_rdy: ready for data, OK to assert app_wdf_wren
					state <= s_write_3;
				end
			end
            /* app_en: This input strobes in a request. You must apply the desired values to app_addr[],
            app_cmd[2:0], and app_hi_pri, and then assert app_en to submit the request to the UI. */
			s_write_3: begin
				app_wdf_wren <= 1'b1;
				if (burst_count == 3'd0) begin
					app_wdf_end <= 1'b1;
				end
				if ( (app_wdf_rdy == 1'b1) & (burst_count == 3'd0) ) begin
					app_en    <= 1'b1;  // strobe for address and cmd 
					// app_cmd <= 3'b000;  // write cmd is 000   --- LJK change 2021/11/11
					state <= s_write_4;
				end else if (app_wdf_rdy == 1'b1) begin
					burst_count <= burst_count - 1'b1;
					state <= s_write_0;
				end
			end

			s_write_4: begin  // confirm handshake back for cmd and addr strobe
				if (app_rdy == 1'b1) begin
					cmd_byte_addr_wr <= cmd_byte_addr_wr + ADDRESS_INCREMENT;
					state <= s_idle;
				end else begin
					app_en    <= 1'b1;
					// app_cmd <= 3'b000; // change LJK 2021/11/11
				end
			end

            // --------------------------
			s_write2_0: begin
				state <= s_write2_1;
				ib2_re <= 1'b1;
			end

			s_write2_1: begin  // stay in s_write_1 until ib_valid
				if(ib2_valid==1) begin
					app_wdf_data <= ib2_data;
					state <= s_write2_2;
				end
			end

			s_write2_2: begin
    			app_cmd <= 3'b000;
				if (app_wdf_rdy == 1'b1) begin
					state <= s_write2_3;
				end
			end

			s_write2_3: begin
				app_wdf_wren <= 1'b1;
                adc_data_count <= adc_data_count + 16'b1;
				if (burst_count == 3'd0) begin
					app_wdf_end <= 1'b1;
				end
				if ( (app_wdf_rdy == 1'b1) & (burst_count == 3'd0) ) begin
					app_en    <= 1'b1;
					//app_cmd <= 3'b000;  // --- LJK change 2021/11/11
					state <= s_write2_4;
				end else if (app_wdf_rdy == 1'b1) begin
					burst_count <= burst_count - 1'b1;
					state <= s_write2_0;
				end
			end

			s_write2_4: begin
				if (app_rdy == 1'b1) begin
				    if(cmd_byte_addr_wr2 >= FIXED_INDEX2) begin // write2 needs a circular buffer 
				        if (adc_write_rollover_reg == 1'b0) begin
    				        cmd_byte_addr_wr2 <= cmd_byte_addr_wr2; // stay at this address pointer so that the rollover doesn't overwrite data before it is read
	                        wr2_buf_pause <= 1'b1;
                        end
	                    else begin
	                        cmd_byte_addr_wr2 <= FIXED_INDEX2_START;
	                        wr2_buf_pause <= 1'b0;   
	                    end			        
                    end
                    else begin
                        cmd_byte_addr_wr2 <= cmd_byte_addr_wr2 + ADDRESS_INCREMENT;
                    end
					state <= s_idle;
				end else begin
					app_en    <= 1'b1;
					// app_cmd <= 3'b000; // change LJK 2021/11/11
				end
			end
            // --------------------------

			s_read_0: begin
				app_en    <= 1'b1;
				// app_cmd <= 3'b001; // change LJK 2021/11/11
				state <= s_read_1;
			end

			s_read_1: begin
				if (app_rdy == 1'b1) begin
				    if(cmd_byte_addr_rd >= FIXED_INDEX) begin // read has a circular buffer; write does not 
				        cmd_byte_addr_rd <= 0;
				    end
				    else begin
					    cmd_byte_addr_rd <= cmd_byte_addr_rd + ADDRESS_INCREMENT;
					end
					state <= s_read_2;
				end else begin
					app_en    <= 1'b1;
					// app_cmd <= 3'b001; // change LJK 2021/11/11
				end
			end

			s_read_2: begin
				if (app_rd_data_valid == 1'b1) begin
					ob_data <= app_rd_data;
					ob_we <= 1'b1;
					if (burst_count == 3'd0) begin
						state <= s_idle;
					end else begin
						burst_count <= burst_count - 1'b1;
					end
				end
			end
            // ----------------------------------------
			s_read2_0: begin
                app_en    <= 1'b1;
                //app_cmd <= 3'b001; // LJK -- change 2021/11/11
                state <= s_read2_1;
            end

            s_read2_1: begin
                if (app_rdy == 1'b1) begin
                    if(cmd_byte_addr_rd2 >= FIXED_INDEX2) begin // read has a circular buffer; write does not 
                        cmd_byte_addr_rd2 <= FIXED_INDEX2_START;
                    end
                    else begin
                        cmd_byte_addr_rd2 <= cmd_byte_addr_rd2 + ADDRESS_INCREMENT;
                    end
                    state <= s_read2_2;
                end else begin
                    app_en    <= 1'b1;
                    // app_cmd <= 3'b001; // change LJK 2021/11/11
                end
            end

            s_read2_2: begin
                if (app_rd_data_valid == 1'b1) begin
                    ob2_data <= app_rd_data;
                    ob2_we <= 1'b1;
                    adc_data_count <= adc_data_count - 16'b1;
                    if (burst_count == 3'd0) begin
                        state <= s_idle;
                    end else begin
                        burst_count <= burst_count - 1'b1;
                    end
                end
            end
            // ----------------------------------------		
		endcase
	end
end


endmodule
