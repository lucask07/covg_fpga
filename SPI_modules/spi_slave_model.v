//////////////////////////////////////////////////////////////////////
////                                                              ////
////  spi_slave_model.v                                           ////
////                                                              ////
////  This file is part of the SPI IP core project                ////
////  http://www.opencores.org/projects/spi/                      ////
////                                                              ////
////  Author(s):                                                  ////
////      - Simon Srot (simons@opencores.org)                     ////
////                                                              ////
////  All additional information is avaliable in the Readme.txt   ////
////  file.                                                       ////
////                                                              ////
//////////////////////////////////////////////////////////////////////
////                                                              ////
//// Copyright (C) 2002 Authors                                   ////
////                                                              ////
//// This source file may be used and distributed without         ////
//// restriction provided that this copyright statement is not    ////
//// removed from the file and that any derivative work contains  ////
//// the original copyright notice and the associated disclaimer. ////
////                                                              ////
//// This source file is free software; you can redistribute it   ////
//// and/or modify it under the terms of the GNU Lesser General   ////
//// Public License as published by the Free Software Foundation; ////
//// either version 2.1 of the License, or (at your option) any   ////
//// later version.                                               ////
////                                                              ////
//// This source is distributed in the hope that it will be       ////
//// useful, but WITHOUT ANY WARRANTY; without even the implied   ////
//// warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR      ////
//// PURPOSE.  See the GNU Lesser General Public License for more ////
//// details.                                                     ////
////                                                              ////
//// You should have received a copy of the GNU Lesser General    ////
//// Public License along with this source; if not, download it   ////
//// from http://www.opencores.org/lgpl.shtml                     ////
////                                                              ////
//////////////////////////////////////////////////////////////////////

`include "timescale.v"

module spi_slave_model (rst, ss, sclk, mosi, miso);

  input    wire     rst;            // reset
  input    wire     ss;             // slave select
  input    wire     sclk;           // serial clock
  input    wire     mosi;           // master out slave in
  output            miso;           // master in slave out

  reg           miso;

  reg           rx_negedge;     // slave receiving on negedge
  reg           tx_negedge;     // slave transmiting on negedge
  reg    [15:0] data;           // data register (used to be 32 bits)

  parameter     Tp = 0; //this used to be Tp = 1

  always @(posedge(sclk && !rx_negedge) or negedge(sclk && rx_negedge) or rst)
  begin
    if (rst)
      data <= #Tp 15'b0;//used to be 32
    else if (!ss)
      data <= #Tp {data[14:0], mosi};//used to be data [30:0]
  end

  always @(posedge(sclk && !tx_negedge) or negedge(sclk && tx_negedge) or negedge ss /*new here*/)
  begin
    if (!ss)
       miso <= #Tp data[15]; //this if statement is new
    else  
       miso <= #Tp data[15];//used to be data[31]
  end

endmodule
      
