/**********************************************************************/
/*   ____  ____                                                       */
/*  /   /\/   /                                                       */
/* /___/  \  /                                                        */
/* \   \   \/                                                         */
/*  \   \        Copyright (c) 2003-2013 Xilinx, Inc.                 */
/*  /   /        All Right Reserved.                                  */
/* /---/   /\                                                         */
/* \   \  /  \                                                        */
/*  \___\/\___\                                                       */
/**********************************************************************/


#include "iki.h"
#include <string.h>
#include <math.h>
#ifdef __GNUC__
#include <stdlib.h>
#else
#include <malloc.h>
#define alloca _alloca
#endif
/**********************************************************************/
/*   ____  ____                                                       */
/*  /   /\/   /                                                       */
/* /___/  \  /                                                        */
/* \   \   \/                                                         */
/*  \   \        Copyright (c) 2003-2013 Xilinx, Inc.                 */
/*  /   /        All Right Reserved.                                  */
/* /---/   /\                                                         */
/* \   \  /  \                                                        */
/*  \___\/\___\                                                       */
/**********************************************************************/


#include "iki.h"
#include <string.h>
#include <math.h>
#ifdef __GNUC__
#include <stdlib.h>
#else
#include <malloc.h>
#define alloca _alloca
#endif
typedef void (*funcp)(char *, char *);
extern int main(int, char**);
extern void execute_2(char*, char *);
extern void execute_3(char*, char *);
extern void execute_4(char*, char *);
extern void execute_284(char*, char *);
extern void execute_285(char*, char *);
extern void execute_286(char*, char *);
extern void execute_287(char*, char *);
extern void execute_343(char*, char *);
extern void execute_344(char*, char *);
extern void execute_345(char*, char *);
extern void execute_346(char*, char *);
extern void execute_347(char*, char *);
extern void execute_348(char*, char *);
extern void execute_349(char*, char *);
extern void execute_350(char*, char *);
extern void execute_351(char*, char *);
extern void execute_352(char*, char *);
extern void execute_353(char*, char *);
extern void execute_354(char*, char *);
extern void execute_355(char*, char *);
extern void execute_356(char*, char *);
extern void execute_357(char*, char *);
extern void execute_358(char*, char *);
extern void execute_94(char*, char *);
extern void execute_95(char*, char *);
extern void execute_292(char*, char *);
extern void execute_293(char*, char *);
extern void execute_294(char*, char *);
extern void execute_295(char*, char *);
extern void execute_296(char*, char *);
extern void execute_297(char*, char *);
extern void execute_305(char*, char *);
extern void execute_306(char*, char *);
extern void execute_307(char*, char *);
extern void execute_308(char*, char *);
extern void execute_7(char*, char *);
extern void execute_9(char*, char *);
extern void execute_11(char*, char *);
extern void execute_13(char*, char *);
extern void execute_15(char*, char *);
extern void execute_17(char*, char *);
extern void execute_19(char*, char *);
extern void execute_21(char*, char *);
extern void execute_23(char*, char *);
extern void execute_25(char*, char *);
extern void execute_27(char*, char *);
extern void execute_29(char*, char *);
extern void execute_31(char*, char *);
extern void execute_33(char*, char *);
extern void execute_35(char*, char *);
extern void execute_37(char*, char *);
extern void execute_39(char*, char *);
extern void execute_41(char*, char *);
extern void execute_43(char*, char *);
extern void execute_45(char*, char *);
extern void execute_47(char*, char *);
extern void execute_49(char*, char *);
extern void execute_51(char*, char *);
extern void execute_53(char*, char *);
extern void execute_55(char*, char *);
extern void execute_57(char*, char *);
extern void execute_59(char*, char *);
extern void execute_61(char*, char *);
extern void execute_63(char*, char *);
extern void execute_65(char*, char *);
extern void execute_67(char*, char *);
extern void execute_69(char*, char *);
extern void execute_71(char*, char *);
extern void execute_73(char*, char *);
extern void execute_75(char*, char *);
extern void execute_77(char*, char *);
extern void execute_79(char*, char *);
extern void execute_81(char*, char *);
extern void execute_83(char*, char *);
extern void execute_85(char*, char *);
extern void execute_87(char*, char *);
extern void execute_298(char*, char *);
extern void execute_299(char*, char *);
extern void vlog_simple_process_execute_0_fast_no_reg_no_agg(char*, char*, char*);
extern void execute_90(char*, char *);
extern void execute_92(char*, char *);
extern void execute_301(char*, char *);
extern void execute_302(char*, char *);
extern void execute_303(char*, char *);
extern void execute_304(char*, char *);
extern void execute_97(char*, char *);
extern void execute_187(char*, char *);
extern void execute_188(char*, char *);
extern void execute_309(char*, char *);
extern void execute_310(char*, char *);
extern void execute_311(char*, char *);
extern void execute_312(char*, char *);
extern void execute_313(char*, char *);
extern void execute_314(char*, char *);
extern void execute_322(char*, char *);
extern void execute_323(char*, char *);
extern void execute_324(char*, char *);
extern void execute_325(char*, char *);
extern void execute_190(char*, char *);
extern void execute_289(char*, char *);
extern void execute_290(char*, char *);
extern void execute_291(char*, char *);
extern void execute_359(char*, char *);
extern void execute_360(char*, char *);
extern void execute_361(char*, char *);
extern void execute_362(char*, char *);
extern void execute_363(char*, char *);
extern void vlog_transfunc_eventcallback(char*, char*, unsigned, unsigned, unsigned, char *);
funcp funcTab[108] = {(funcp)execute_2, (funcp)execute_3, (funcp)execute_4, (funcp)execute_284, (funcp)execute_285, (funcp)execute_286, (funcp)execute_287, (funcp)execute_343, (funcp)execute_344, (funcp)execute_345, (funcp)execute_346, (funcp)execute_347, (funcp)execute_348, (funcp)execute_349, (funcp)execute_350, (funcp)execute_351, (funcp)execute_352, (funcp)execute_353, (funcp)execute_354, (funcp)execute_355, (funcp)execute_356, (funcp)execute_357, (funcp)execute_358, (funcp)execute_94, (funcp)execute_95, (funcp)execute_292, (funcp)execute_293, (funcp)execute_294, (funcp)execute_295, (funcp)execute_296, (funcp)execute_297, (funcp)execute_305, (funcp)execute_306, (funcp)execute_307, (funcp)execute_308, (funcp)execute_7, (funcp)execute_9, (funcp)execute_11, (funcp)execute_13, (funcp)execute_15, (funcp)execute_17, (funcp)execute_19, (funcp)execute_21, (funcp)execute_23, (funcp)execute_25, (funcp)execute_27, (funcp)execute_29, (funcp)execute_31, (funcp)execute_33, (funcp)execute_35, (funcp)execute_37, (funcp)execute_39, (funcp)execute_41, (funcp)execute_43, (funcp)execute_45, (funcp)execute_47, (funcp)execute_49, (funcp)execute_51, (funcp)execute_53, (funcp)execute_55, (funcp)execute_57, (funcp)execute_59, (funcp)execute_61, (funcp)execute_63, (funcp)execute_65, (funcp)execute_67, (funcp)execute_69, (funcp)execute_71, (funcp)execute_73, (funcp)execute_75, (funcp)execute_77, (funcp)execute_79, (funcp)execute_81, (funcp)execute_83, (funcp)execute_85, (funcp)execute_87, (funcp)execute_298, (funcp)execute_299, (funcp)vlog_simple_process_execute_0_fast_no_reg_no_agg, (funcp)execute_90, (funcp)execute_92, (funcp)execute_301, (funcp)execute_302, (funcp)execute_303, (funcp)execute_304, (funcp)execute_97, (funcp)execute_187, (funcp)execute_188, (funcp)execute_309, (funcp)execute_310, (funcp)execute_311, (funcp)execute_312, (funcp)execute_313, (funcp)execute_314, (funcp)execute_322, (funcp)execute_323, (funcp)execute_324, (funcp)execute_325, (funcp)execute_190, (funcp)execute_289, (funcp)execute_290, (funcp)execute_291, (funcp)execute_359, (funcp)execute_360, (funcp)execute_361, (funcp)execute_362, (funcp)execute_363, (funcp)vlog_transfunc_eventcallback};
const int NumRelocateId= 108;

void relocate(char *dp)
{
	iki_relocate(dp, "xsim.dir/observer_fixpt_folded_behav/xsim.reloc",  (void **)funcTab, 108);

	/*Populate the transaction function pointer field in the whole net structure */
}

void sensitize(char *dp)
{
	iki_sensitize(dp, "xsim.dir/observer_fixpt_folded_behav/xsim.reloc");
}

void simulate(char *dp)
{
	iki_schedule_processes_at_time_zero(dp, "xsim.dir/observer_fixpt_folded_behav/xsim.reloc");
	// Initialize Verilog nets in mixed simulation, for the cases when the value at time 0 should be propagated from the mixed language Vhdl net
	iki_execute_processes();

	// Schedule resolution functions for the multiply driven Verilog nets that have strength
	// Schedule transaction functions for the singly driven Verilog nets that have strength

}
#include "iki_bridge.h"
void relocate(char *);

void sensitize(char *);

void simulate(char *);

extern SYSTEMCLIB_IMP_DLLSPEC void local_register_implicit_channel(int, char*);
extern void implicit_HDL_SCinstatiate();

extern SYSTEMCLIB_IMP_DLLSPEC int xsim_argc_copy ;
extern SYSTEMCLIB_IMP_DLLSPEC char** xsim_argv_copy ;

int main(int argc, char **argv)
{
    iki_heap_initialize("ms", "isimmm", 0, 2147483648) ;
    iki_set_sv_type_file_path_name("xsim.dir/observer_fixpt_folded_behav/xsim.svtype");
    iki_set_crvs_dump_file_path_name("xsim.dir/observer_fixpt_folded_behav/xsim.crvsdump");
    void* design_handle = iki_create_design("xsim.dir/observer_fixpt_folded_behav/xsim.mem", (void *)relocate, (void *)sensitize, (void *)simulate, 0, isimBridge_getWdbWriter(), 0, argc, argv);
     iki_set_rc_trial_count(100);
    (void) design_handle;
    return iki_simulate_design();
}
