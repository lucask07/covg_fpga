//
// Vivado(TM)
// rundef.js: a Vivado-generated Runs Script for WSH 5.1/5.6
// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
//

var WshShell = new ActiveXObject( "WScript.Shell" );
var ProcEnv = WshShell.Environment( "Process" );
var PathVal = ProcEnv("PATH");
if ( PathVal.length == 0 ) {
  PathVal = "C:/Users/iande/Documents/SDK/2018.2/bin;C:/Users/iande/Documents/Vivado/2018.2/ids_lite/ISE/bin/nt64;C:/Users/iande/Documents/Vivado/2018.2/ids_lite/ISE/lib/nt64;C:/Users/iande/Documents/Vivado/2018.2/bin;";
} else {
  PathVal = "C:/Users/iande/Documents/SDK/2018.2/bin;C:/Users/iande/Documents/Vivado/2018.2/ids_lite/ISE/bin/nt64;C:/Users/iande/Documents/Vivado/2018.2/ids_lite/ISE/lib/nt64;C:/Users/iande/Documents/Vivado/2018.2/bin;" + PathVal;
}

ProcEnv("PATH") = PathVal;

var RDScrFP = WScript.ScriptFullName;
var RDScrN = WScript.ScriptName;
var RDScrDir = RDScrFP.substr( 0, RDScrFP.length - RDScrN.length - 1 );
var ISEJScriptLib = RDScrDir + "/ISEWrap.js";
eval( EAInclude(ISEJScriptLib) );


// pre-commands:
ISETouchFile( "write_bitstream", "begin" );
ISEStep( "vivado",
         "-log top_level_module.vdi -applog -m64 -product Vivado -messageDb vivado.pb -mode batch -source top_level_module.tcl -notrace" );





function EAInclude( EAInclFilename ) {
  var EAFso = new ActiveXObject( "Scripting.FileSystemObject" );
  var EAInclFile = EAFso.OpenTextFile( EAInclFilename );
  var EAIFContents = EAInclFile.ReadAll();
  EAInclFile.Close();
  return EAIFContents;
}
