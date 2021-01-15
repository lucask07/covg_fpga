/**********************************************************************/
/*   ____  ____                                                       */
/*  /   /\/   /                                                       */
/* /___/  \  /                                                        */
/* \   \   \/                                                       */
/*  \   \        Copyright (c) 2003-2009 Xilinx, Inc.                */
/*  /   /          All Right Reserved.                                 */
/* /---/   /\                                                         */
/* \   \  /  \                                                      */
/*  \___\/\___\                                                    */
/***********************************************************************/

/* This file is designed for use with ISim build 0x7708f090 */

#define XSI_HIDE_SYMBOL_SPEC true
#include "xsi.h"
#include <memory.h>
#ifdef __GNUC__
#include <stdlib.h>
#else
#include <malloc.h>
#define alloca _alloca
#endif
static const char *ng0 = "C:/Users/iande/Desktop/covg_fpga/SPI_Master/WbSignal_converter.v";
static unsigned int ng1[] = {0U, 0U};
static unsigned int ng2[] = {1U, 0U};
static unsigned int ng3[] = {4U, 0U};
static unsigned int ng4[] = {2U, 0U};
static unsigned int ng5[] = {3U, 0U};
static unsigned int ng6[] = {15U, 0U};
static unsigned int ng7[] = {5U, 0U};
static unsigned int ng8[] = {6U, 0U};
static unsigned int ng9[] = {7U, 0U};
static unsigned int ng10[] = {8U, 0U};
static unsigned int ng11[] = {9U, 0U};
static unsigned int ng12[] = {10U, 0U};
static unsigned int ng13[] = {11U, 0U};
static unsigned int ng14[] = {1U, 0U, 2U, 0U};
static unsigned int ng15[] = {0U, 0U, 0U, 0U};



static void Always_52_0(char *t0)
{
    char *t1;
    char *t2;
    char *t3;
    char *t4;
    char *t5;
    unsigned int t6;
    unsigned int t7;
    unsigned int t8;
    unsigned int t9;
    unsigned int t10;
    char *t11;
    char *t12;

LAB0:    t1 = (t0 + 5256U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(52, ng0);
    t2 = (t0 + 6072);
    *((int *)t2) = 1;
    t3 = (t0 + 5288);
    *((char **)t3) = t2;
    *((char **)t1) = &&LAB4;

LAB1:    return;
LAB4:    xsi_set_current_line(52, ng0);

LAB5:    xsi_set_current_line(53, ng0);
    t4 = (t0 + 2976U);
    t5 = *((char **)t4);
    t4 = (t5 + 4);
    t6 = *((unsigned int *)t4);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 != 0);
    if (t10 > 0)
        goto LAB6;

LAB7:    xsi_set_current_line(56, ng0);

LAB10:    xsi_set_current_line(57, ng0);
    t2 = (t0 + 4336);
    t3 = (t2 + 56U);
    t4 = *((char **)t3);
    t5 = (t0 + 4176);
    xsi_vlogvar_wait_assign_value(t5, t4, 0, 0, 5, 0LL);

LAB8:    goto LAB2;

LAB6:    xsi_set_current_line(53, ng0);

LAB9:    xsi_set_current_line(54, ng0);
    t11 = ((char*)((ng1)));
    t12 = (t0 + 4176);
    xsi_vlogvar_wait_assign_value(t12, t11, 0, 0, 5, 0LL);
    goto LAB8;

}

static void Always_62_1(char *t0)
{
    char *t1;
    char *t2;
    char *t3;
    char *t4;
    char *t5;
    char *t6;
    char *t7;
    int t8;
    char *t9;
    char *t10;
    unsigned int t11;
    unsigned int t12;
    unsigned int t13;
    unsigned int t14;
    unsigned int t15;
    char *t16;
    char *t17;

LAB0:    t1 = (t0 + 5504U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(62, ng0);
    t2 = (t0 + 6088);
    *((int *)t2) = 1;
    t3 = (t0 + 5536);
    *((char **)t3) = t2;
    *((char **)t1) = &&LAB4;

LAB1:    return;
LAB4:    xsi_set_current_line(62, ng0);

LAB5:    xsi_set_current_line(63, ng0);
    t4 = (t0 + 4176);
    t5 = (t4 + 56U);
    t6 = *((char **)t5);

LAB6:    t7 = ((char*)((ng1)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t7, 5);
    if (t8 == 1)
        goto LAB7;

LAB8:    t2 = ((char*)((ng2)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB9;

LAB10:    t2 = ((char*)((ng4)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB11;

LAB12:    t2 = ((char*)((ng5)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB13;

LAB14:    t2 = ((char*)((ng6)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB15;

LAB16:    t2 = ((char*)((ng3)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB17;

LAB18:    t2 = ((char*)((ng7)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB19;

LAB20:    t2 = ((char*)((ng8)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB21;

LAB22:    t2 = ((char*)((ng9)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB23;

LAB24:    t2 = ((char*)((ng10)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB25;

LAB26:    t2 = ((char*)((ng11)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB27;

LAB28:    t2 = ((char*)((ng12)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB29;

LAB30:    t2 = ((char*)((ng13)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB31;

LAB32:
LAB34:
LAB33:    xsi_set_current_line(111, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 4336);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 5);

LAB35:    goto LAB2;

LAB7:    xsi_set_current_line(64, ng0);

LAB36:    xsi_set_current_line(65, ng0);
    t9 = (t0 + 3296U);
    t10 = *((char **)t9);
    t9 = (t10 + 4);
    t11 = *((unsigned int *)t9);
    t12 = (~(t11));
    t13 = *((unsigned int *)t10);
    t14 = (t13 & t12);
    t15 = (t14 != 0);
    if (t15 > 0)
        goto LAB37;

LAB38:    xsi_set_current_line(68, ng0);
    t2 = (t0 + 3456U);
    t3 = *((char **)t2);
    t2 = (t3 + 4);
    t11 = *((unsigned int *)t2);
    t12 = (~(t11));
    t13 = *((unsigned int *)t3);
    t14 = (t13 & t12);
    t15 = (t14 != 0);
    if (t15 > 0)
        goto LAB41;

LAB42:    xsi_set_current_line(71, ng0);

LAB45:    xsi_set_current_line(72, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 4336);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 5);

LAB43:
LAB39:    goto LAB35;

LAB9:    xsi_set_current_line(75, ng0);

LAB46:    xsi_set_current_line(76, ng0);
    t3 = ((char*)((ng4)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB11:    xsi_set_current_line(78, ng0);

LAB47:    xsi_set_current_line(79, ng0);
    t3 = ((char*)((ng5)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB13:    xsi_set_current_line(81, ng0);

LAB48:    xsi_set_current_line(82, ng0);
    t3 = ((char*)((ng6)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB15:    xsi_set_current_line(84, ng0);

LAB49:    xsi_set_current_line(85, ng0);
    t3 = ((char*)((ng1)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB17:    xsi_set_current_line(87, ng0);

LAB50:    xsi_set_current_line(88, ng0);
    t3 = ((char*)((ng7)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB19:    xsi_set_current_line(90, ng0);

LAB51:    xsi_set_current_line(91, ng0);
    t3 = ((char*)((ng8)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB21:    xsi_set_current_line(93, ng0);

LAB52:    xsi_set_current_line(94, ng0);
    t3 = ((char*)((ng9)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB23:    xsi_set_current_line(96, ng0);

LAB53:    xsi_set_current_line(97, ng0);
    t3 = ((char*)((ng10)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB25:    xsi_set_current_line(99, ng0);

LAB54:    xsi_set_current_line(100, ng0);
    t3 = ((char*)((ng11)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB27:    xsi_set_current_line(102, ng0);

LAB55:    xsi_set_current_line(103, ng0);
    t3 = ((char*)((ng12)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB29:    xsi_set_current_line(105, ng0);

LAB56:    xsi_set_current_line(106, ng0);
    t3 = ((char*)((ng13)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB31:    xsi_set_current_line(108, ng0);

LAB57:    xsi_set_current_line(109, ng0);
    t3 = ((char*)((ng1)));
    t4 = (t0 + 4336);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 5);
    goto LAB35;

LAB37:    xsi_set_current_line(65, ng0);

LAB40:    xsi_set_current_line(66, ng0);
    t16 = ((char*)((ng2)));
    t17 = (t0 + 4336);
    xsi_vlogvar_assign_value(t17, t16, 0, 0, 5);
    goto LAB39;

LAB41:    xsi_set_current_line(68, ng0);

LAB44:    xsi_set_current_line(69, ng0);
    t4 = ((char*)((ng3)));
    t5 = (t0 + 4336);
    xsi_vlogvar_assign_value(t5, t4, 0, 0, 5);
    goto LAB43;

}

static void Always_116_2(char *t0)
{
    char t9[16];
    char t10[8];
    char t21[8];
    char *t1;
    char *t2;
    char *t3;
    char *t4;
    char *t5;
    char *t6;
    char *t7;
    int t8;
    char *t11;
    char *t12;
    char *t13;
    unsigned int t14;
    unsigned int t15;
    unsigned int t16;
    unsigned int t17;
    unsigned int t18;
    unsigned int t19;
    char *t20;
    char *t22;
    char *t23;
    char *t24;
    unsigned int t25;
    unsigned int t26;
    unsigned int t27;
    unsigned int t28;
    unsigned int t29;
    unsigned int t30;
    char *t31;

LAB0:    t1 = (t0 + 5752U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(116, ng0);
    t2 = (t0 + 6104);
    *((int *)t2) = 1;
    t3 = (t0 + 5784);
    *((char **)t3) = t2;
    *((char **)t1) = &&LAB4;

LAB1:    return;
LAB4:    xsi_set_current_line(116, ng0);

LAB5:    xsi_set_current_line(117, ng0);
    t4 = (t0 + 4176);
    t5 = (t4 + 56U);
    t6 = *((char **)t5);

LAB6:    t7 = ((char*)((ng1)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t7, 5);
    if (t8 == 1)
        goto LAB7;

LAB8:    t2 = ((char*)((ng2)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB9;

LAB10:    t2 = ((char*)((ng4)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB11;

LAB12:    t2 = ((char*)((ng5)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB13;

LAB14:    t2 = ((char*)((ng6)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB15;

LAB16:    t2 = ((char*)((ng3)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB17;

LAB18:    t2 = ((char*)((ng7)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB19;

LAB20:    t2 = ((char*)((ng8)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB21;

LAB22:    t2 = ((char*)((ng9)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB23;

LAB24:    t2 = ((char*)((ng10)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB25;

LAB26:    t2 = ((char*)((ng11)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB27;

LAB28:    t2 = ((char*)((ng12)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB29;

LAB30:    t2 = ((char*)((ng13)));
    t8 = xsi_vlog_unsigned_case_compare(t6, 5, t2, 5);
    if (t8 == 1)
        goto LAB31;

LAB32:
LAB34:
LAB33:    xsi_set_current_line(170, ng0);

LAB49:    xsi_set_current_line(171, ng0);
    t2 = (t0 + 4016);
    t3 = (t2 + 56U);
    t4 = *((char **)t3);
    t5 = (t0 + 4016);
    xsi_vlogvar_assign_value(t5, t4, 0, 0, 34);
    xsi_set_current_line(172, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);

LAB35:    goto LAB2;

LAB7:    xsi_set_current_line(118, ng0);

LAB36:    xsi_set_current_line(119, ng0);
    t11 = (t0 + 3136U);
    t12 = *((char **)t11);
    memset(t10, 0, 8);
    t11 = (t10 + 4);
    t13 = (t12 + 4);
    t14 = *((unsigned int *)t12);
    t15 = (t14 >> 0);
    *((unsigned int *)t10) = t15;
    t16 = *((unsigned int *)t13);
    t17 = (t16 >> 0);
    *((unsigned int *)t11) = t17;
    t18 = *((unsigned int *)t10);
    *((unsigned int *)t10) = (t18 & 1073741823U);
    t19 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t19 & 1073741823U);
    t20 = ((char*)((ng1)));
    t22 = (t0 + 3136U);
    t23 = *((char **)t22);
    memset(t21, 0, 8);
    t22 = (t21 + 4);
    t24 = (t23 + 4);
    t25 = *((unsigned int *)t23);
    t26 = (t25 >> 30);
    *((unsigned int *)t21) = t26;
    t27 = *((unsigned int *)t24);
    t28 = (t27 >> 30);
    *((unsigned int *)t22) = t28;
    t29 = *((unsigned int *)t21);
    *((unsigned int *)t21) = (t29 & 3U);
    t30 = *((unsigned int *)t22);
    *((unsigned int *)t22) = (t30 & 3U);
    xsi_vlogtype_concat(t9, 34, 34, 3U, t21, 2, t20, 2, t10, 30);
    t31 = (t0 + 4016);
    xsi_vlogvar_assign_value(t31, t9, 0, 0, 34);
    xsi_set_current_line(120, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB9:    xsi_set_current_line(122, ng0);

LAB37:    xsi_set_current_line(123, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(124, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB11:    xsi_set_current_line(126, ng0);

LAB38:    xsi_set_current_line(127, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(128, ng0);
    t2 = ((char*)((ng2)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB13:    xsi_set_current_line(130, ng0);

LAB39:    xsi_set_current_line(131, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(132, ng0);
    t2 = ((char*)((ng2)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB15:    xsi_set_current_line(134, ng0);

LAB40:    xsi_set_current_line(135, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(136, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB17:    xsi_set_current_line(138, ng0);

LAB41:    xsi_set_current_line(139, ng0);
    t3 = ((char*)((ng14)));
    t4 = (t0 + 4016);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 34);
    xsi_set_current_line(140, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB19:    xsi_set_current_line(142, ng0);

LAB42:    xsi_set_current_line(143, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(144, ng0);
    t2 = ((char*)((ng2)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB21:    xsi_set_current_line(146, ng0);

LAB43:    xsi_set_current_line(147, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(148, ng0);
    t2 = ((char*)((ng2)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB23:    xsi_set_current_line(150, ng0);

LAB44:    xsi_set_current_line(151, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(152, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB25:    xsi_set_current_line(154, ng0);

LAB45:    xsi_set_current_line(155, ng0);
    t3 = ((char*)((ng15)));
    t4 = (t0 + 4016);
    xsi_vlogvar_assign_value(t4, t3, 0, 0, 34);
    xsi_set_current_line(156, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB27:    xsi_set_current_line(158, ng0);

LAB46:    xsi_set_current_line(159, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(160, ng0);
    t2 = ((char*)((ng2)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB29:    xsi_set_current_line(162, ng0);

LAB47:    xsi_set_current_line(163, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(164, ng0);
    t2 = ((char*)((ng2)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

LAB31:    xsi_set_current_line(166, ng0);

LAB48:    xsi_set_current_line(167, ng0);
    t3 = (t0 + 4016);
    t4 = (t3 + 56U);
    t5 = *((char **)t4);
    t7 = (t0 + 4016);
    xsi_vlogvar_assign_value(t7, t5, 0, 0, 34);
    xsi_set_current_line(168, ng0);
    t2 = ((char*)((ng1)));
    t3 = (t0 + 3856);
    xsi_vlogvar_assign_value(t3, t2, 0, 0, 1);
    goto LAB35;

}


extern void work_m_00000000000517601819_2669345608_init()
{
	static char *pe[] = {(void *)Always_52_0,(void *)Always_62_1,(void *)Always_116_2};
	xsi_register_didat("work_m_00000000000517601819_2669345608", "isim/tb_spi_top_isim_beh.exe.sim/work/m_00000000000517601819_2669345608.didat");
	xsi_register_executes(pe);
}
