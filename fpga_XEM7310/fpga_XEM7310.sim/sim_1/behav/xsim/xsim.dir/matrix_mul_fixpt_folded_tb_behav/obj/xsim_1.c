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
extern void execute_4(char*, char *);
extern void execute_5(char*, char *);
extern void execute_7(char*, char *);
extern void execute_9(char*, char *);
extern void execute_11(char*, char *);
extern void execute_12(char*, char *);
extern void execute_14(char*, char *);
extern void execute_16(char*, char *);
extern void execute_18(char*, char *);
extern void execute_19(char*, char *);
extern void execute_21(char*, char *);
extern void execute_23(char*, char *);
extern void execute_25(char*, char *);
extern void execute_26(char*, char *);
extern void execute_28(char*, char *);
extern void execute_30(char*, char *);
extern void execute_32(char*, char *);
extern void execute_33(char*, char *);
extern void execute_35(char*, char *);
extern void execute_37(char*, char *);
extern void execute_39(char*, char *);
extern void execute_41(char*, char *);
extern void execute_42(char*, char *);
extern void execute_44(char*, char *);
extern void execute_46(char*, char *);
extern void execute_48(char*, char *);
extern void execute_50(char*, char *);
extern void execute_145(char*, char *);
extern void execute_147(char*, char *);
extern void execute_149(char*, char *);
extern void execute_151(char*, char *);
extern void execute_152(char*, char *);
extern void execute_154(char*, char *);
extern void execute_156(char*, char *);
extern void execute_158(char*, char *);
extern void execute_159(char*, char *);
extern void execute_161(char*, char *);
extern void execute_163(char*, char *);
extern void execute_169(char*, char *);
extern void execute_170(char*, char *);
extern void execute_171(char*, char *);
extern void execute_172(char*, char *);
extern void execute_173(char*, char *);
extern void execute_174(char*, char *);
extern void execute_175(char*, char *);
extern void execute_176(char*, char *);
extern void execute_177(char*, char *);
extern void execute_178(char*, char *);
extern void execute_179(char*, char *);
extern void execute_180(char*, char *);
extern void execute_181(char*, char *);
extern void execute_182(char*, char *);
extern void execute_183(char*, char *);
extern void vlog_simple_process_execute_0_fast_no_reg_no_agg(char*, char*, char*);
extern void execute_185(char*, char *);
extern void execute_186(char*, char *);
extern void execute_187(char*, char *);
extern void execute_188(char*, char *);
extern void execute_206(char*, char *);
extern void execute_207(char*, char *);
extern void execute_208(char*, char *);
extern void execute_209(char*, char *);
extern void vlog_simple_process_execute_1_fast_no_reg_no_agg(char*, char*, char*);
extern void execute_211(char*, char *);
extern void execute_213(char*, char *);
extern void execute_214(char*, char *);
extern void execute_215(char*, char *);
extern void execute_216(char*, char *);
extern void execute_217(char*, char *);
extern void execute_218(char*, char *);
extern void execute_219(char*, char *);
extern void execute_141(char*, char *);
extern void execute_142(char*, char *);
extern void execute_189(char*, char *);
extern void execute_190(char*, char *);
extern void execute_191(char*, char *);
extern void execute_192(char*, char *);
extern void execute_193(char*, char *);
extern void execute_194(char*, char *);
extern void execute_202(char*, char *);
extern void execute_203(char*, char *);
extern void execute_204(char*, char *);
extern void execute_205(char*, char *);
extern void execute_54(char*, char *);
extern void execute_56(char*, char *);
extern void execute_58(char*, char *);
extern void execute_60(char*, char *);
extern void execute_62(char*, char *);
extern void execute_64(char*, char *);
extern void execute_66(char*, char *);
extern void execute_68(char*, char *);
extern void execute_70(char*, char *);
extern void execute_72(char*, char *);
extern void execute_74(char*, char *);
extern void execute_76(char*, char *);
extern void execute_78(char*, char *);
extern void execute_80(char*, char *);
extern void execute_82(char*, char *);
extern void execute_84(char*, char *);
extern void execute_86(char*, char *);
extern void execute_88(char*, char *);
extern void execute_90(char*, char *);
extern void execute_92(char*, char *);
extern void execute_94(char*, char *);
extern void execute_96(char*, char *);
extern void execute_98(char*, char *);
extern void execute_100(char*, char *);
extern void execute_102(char*, char *);
extern void execute_104(char*, char *);
extern void execute_106(char*, char *);
extern void execute_108(char*, char *);
extern void execute_110(char*, char *);
extern void execute_112(char*, char *);
extern void execute_114(char*, char *);
extern void execute_116(char*, char *);
extern void execute_118(char*, char *);
extern void execute_120(char*, char *);
extern void execute_122(char*, char *);
extern void execute_124(char*, char *);
extern void execute_126(char*, char *);
extern void execute_128(char*, char *);
extern void execute_130(char*, char *);
extern void execute_132(char*, char *);
extern void execute_134(char*, char *);
extern void execute_195(char*, char *);
extern void execute_196(char*, char *);
extern void execute_137(char*, char *);
extern void execute_139(char*, char *);
extern void execute_198(char*, char *);
extern void execute_199(char*, char *);
extern void execute_200(char*, char *);
extern void execute_201(char*, char *);
extern void execute_144(char*, char *);
extern void execute_166(char*, char *);
extern void execute_167(char*, char *);
extern void execute_168(char*, char *);
extern void execute_220(char*, char *);
extern void execute_221(char*, char *);
extern void execute_222(char*, char *);
extern void execute_223(char*, char *);
extern void execute_224(char*, char *);
extern void vlog_transfunc_eventcallback(char*, char*, unsigned, unsigned, unsigned, char *);
funcp funcTab[143] = {(funcp)execute_2, (funcp)execute_4, (funcp)execute_5, (funcp)execute_7, (funcp)execute_9, (funcp)execute_11, (funcp)execute_12, (funcp)execute_14, (funcp)execute_16, (funcp)execute_18, (funcp)execute_19, (funcp)execute_21, (funcp)execute_23, (funcp)execute_25, (funcp)execute_26, (funcp)execute_28, (funcp)execute_30, (funcp)execute_32, (funcp)execute_33, (funcp)execute_35, (funcp)execute_37, (funcp)execute_39, (funcp)execute_41, (funcp)execute_42, (funcp)execute_44, (funcp)execute_46, (funcp)execute_48, (funcp)execute_50, (funcp)execute_145, (funcp)execute_147, (funcp)execute_149, (funcp)execute_151, (funcp)execute_152, (funcp)execute_154, (funcp)execute_156, (funcp)execute_158, (funcp)execute_159, (funcp)execute_161, (funcp)execute_163, (funcp)execute_169, (funcp)execute_170, (funcp)execute_171, (funcp)execute_172, (funcp)execute_173, (funcp)execute_174, (funcp)execute_175, (funcp)execute_176, (funcp)execute_177, (funcp)execute_178, (funcp)execute_179, (funcp)execute_180, (funcp)execute_181, (funcp)execute_182, (funcp)execute_183, (funcp)vlog_simple_process_execute_0_fast_no_reg_no_agg, (funcp)execute_185, (funcp)execute_186, (funcp)execute_187, (funcp)execute_188, (funcp)execute_206, (funcp)execute_207, (funcp)execute_208, (funcp)execute_209, (funcp)vlog_simple_process_execute_1_fast_no_reg_no_agg, (funcp)execute_211, (funcp)execute_213, (funcp)execute_214, (funcp)execute_215, (funcp)execute_216, (funcp)execute_217, (funcp)execute_218, (funcp)execute_219, (funcp)execute_141, (funcp)execute_142, (funcp)execute_189, (funcp)execute_190, (funcp)execute_191, (funcp)execute_192, (funcp)execute_193, (funcp)execute_194, (funcp)execute_202, (funcp)execute_203, (funcp)execute_204, (funcp)execute_205, (funcp)execute_54, (funcp)execute_56, (funcp)execute_58, (funcp)execute_60, (funcp)execute_62, (funcp)execute_64, (funcp)execute_66, (funcp)execute_68, (funcp)execute_70, (funcp)execute_72, (funcp)execute_74, (funcp)execute_76, (funcp)execute_78, (funcp)execute_80, (funcp)execute_82, (funcp)execute_84, (funcp)execute_86, (funcp)execute_88, (funcp)execute_90, (funcp)execute_92, (funcp)execute_94, (funcp)execute_96, (funcp)execute_98, (funcp)execute_100, (funcp)execute_102, (funcp)execute_104, (funcp)execute_106, (funcp)execute_108, (funcp)execute_110, (funcp)execute_112, (funcp)execute_114, (funcp)execute_116, (funcp)execute_118, (funcp)execute_120, (funcp)execute_122, (funcp)execute_124, (funcp)execute_126, (funcp)execute_128, (funcp)execute_130, (funcp)execute_132, (funcp)execute_134, (funcp)execute_195, (funcp)execute_196, (funcp)execute_137, (funcp)execute_139, (funcp)execute_198, (funcp)execute_199, (funcp)execute_200, (funcp)execute_201, (funcp)execute_144, (funcp)execute_166, (funcp)execute_167, (funcp)execute_168, (funcp)execute_220, (funcp)execute_221, (funcp)execute_222, (funcp)execute_223, (funcp)execute_224, (funcp)vlog_transfunc_eventcallback};
const int NumRelocateId= 143;

void relocate(char *dp)
{
	iki_relocate(dp, "xsim.dir/matrix_mul_fixpt_folded_tb_behav/xsim.reloc",  (void **)funcTab, 143);

	/*Populate the transaction function pointer field in the whole net structure */
}

void sensitize(char *dp)
{
	iki_sensitize(dp, "xsim.dir/matrix_mul_fixpt_folded_tb_behav/xsim.reloc");
}

void simulate(char *dp)
{
	iki_schedule_processes_at_time_zero(dp, "xsim.dir/matrix_mul_fixpt_folded_tb_behav/xsim.reloc");
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
    iki_set_sv_type_file_path_name("xsim.dir/matrix_mul_fixpt_folded_tb_behav/xsim.svtype");
    iki_set_crvs_dump_file_path_name("xsim.dir/matrix_mul_fixpt_folded_tb_behav/xsim.crvsdump");
    void* design_handle = iki_create_design("xsim.dir/matrix_mul_fixpt_folded_tb_behav/xsim.mem", (void *)relocate, (void *)sensitize, (void *)simulate, 0, isimBridge_getWdbWriter(), 0, argc, argv);
     iki_set_rc_trial_count(100);
    (void) design_handle;
    return iki_simulate_design();
}
