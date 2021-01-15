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
static const char *ng0 = "C:/Users/iande/Desktop/covg_fpga/SPI_Master/spi_shift.v";
static unsigned int ng1[] = {1U, 0U};
static unsigned int ng2[] = {0U, 0U};
static unsigned int ng3[] = {128U, 0U};
static unsigned int ng4[] = {0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U};
static int ng5[] = {31, 0};
static int ng6[] = {24, 0};
static int ng7[] = {23, 0};
static int ng8[] = {16, 0};
static int ng9[] = {15, 0};
static int ng10[] = {8, 0};
static int ng11[] = {7, 0};
static int ng12[] = {0, 0};
static int ng13[] = {63, 0};
static int ng14[] = {56, 0};
static int ng15[] = {55, 0};
static int ng16[] = {48, 0};
static int ng17[] = {47, 0};
static int ng18[] = {40, 0};
static int ng19[] = {39, 0};
static int ng20[] = {32, 0};
static int ng21[] = {95, 0};
static int ng22[] = {88, 0};
static int ng23[] = {87, 0};
static int ng24[] = {80, 0};
static int ng25[] = {79, 0};
static int ng26[] = {72, 0};
static int ng27[] = {71, 0};
static int ng28[] = {64, 0};
static int ng29[] = {127, 0};
static int ng30[] = {120, 0};
static int ng31[] = {119, 0};
static int ng32[] = {112, 0};
static int ng33[] = {111, 0};
static int ng34[] = {104, 0};
static int ng35[] = {103, 0};
static int ng36[] = {96, 0};



static void Cont_80_0(char *t0)
{
    char *t1;
    char *t2;
    char *t3;
    char *t4;
    char *t5;
    char *t6;
    char *t7;
    char *t8;
    char *t9;
    char *t10;

LAB0:    t1 = (t0 + 5888U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(80, ng0);
    t2 = (t0 + 4968);
    t3 = (t2 + 56U);
    t4 = *((char **)t3);
    t5 = (t0 + 8664);
    t6 = (t5 + 56U);
    t7 = *((char **)t6);
    t8 = (t7 + 56U);
    t9 = *((char **)t8);
    xsi_vlog_bit_copy(t9, 0, t4, 0, 128);
    xsi_driver_vfirst_trans(t5, 0, 127);
    t10 = (t0 + 8440);
    *((int *)t10) = 1;

LAB1:    return;
}

static void Cont_82_1(char *t0)
{
    char t3[8];
    char t4[8];
    char t16[8];
    char t19[8];
    char t20[8];
    char t38[8];
    char t47[8];
    char *t1;
    char *t2;
    char *t5;
    unsigned int t6;
    unsigned int t7;
    unsigned int t8;
    unsigned int t9;
    unsigned int t10;
    char *t11;
    char *t12;
    unsigned int t13;
    unsigned int t14;
    unsigned int t15;
    char *t17;
    char *t18;
    char *t21;
    unsigned int t22;
    unsigned int t23;
    unsigned int t24;
    unsigned int t25;
    unsigned int t26;
    char *t27;
    char *t28;
    unsigned int t29;
    unsigned int t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    char *t34;
    char *t35;
    char *t36;
    char *t37;
    unsigned int t39;
    unsigned int t40;
    unsigned int t41;
    unsigned int t42;
    char *t43;
    char *t44;
    char *t45;
    char *t46;
    char *t48;
    char *t49;
    char *t50;
    char *t51;
    char *t52;
    unsigned int t53;
    unsigned int t54;
    char *t55;
    unsigned int t56;
    unsigned int t57;
    char *t58;
    unsigned int t59;
    unsigned int t60;
    char *t61;

LAB0:    t1 = (t0 + 6136U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(82, ng0);
    t2 = (t0 + 1848U);
    t5 = *((char **)t2);
    memset(t4, 0, 8);
    t2 = (t5 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB4;

LAB5:    if (*((unsigned int *)t2) != 0)
        goto LAB6;

LAB7:    t12 = (t4 + 4);
    t13 = *((unsigned int *)t4);
    t14 = *((unsigned int *)t12);
    t15 = (t13 || t14);
    if (t15 > 0)
        goto LAB8;

LAB9:    t39 = *((unsigned int *)t4);
    t40 = (~(t39));
    t41 = *((unsigned int *)t12);
    t42 = (t40 || t41);
    if (t42 > 0)
        goto LAB10;

LAB11:    if (*((unsigned int *)t12) > 0)
        goto LAB12;

LAB13:    if (*((unsigned int *)t4) > 0)
        goto LAB14;

LAB15:    memcpy(t3, t47, 8);

LAB16:    t48 = (t0 + 8728);
    t49 = (t48 + 56U);
    t50 = *((char **)t49);
    t51 = (t50 + 56U);
    t52 = *((char **)t51);
    memset(t52, 0, 8);
    t53 = 255U;
    t54 = t53;
    t55 = (t3 + 4);
    t56 = *((unsigned int *)t3);
    t53 = (t53 & t56);
    t57 = *((unsigned int *)t55);
    t54 = (t54 & t57);
    t58 = (t52 + 4);
    t59 = *((unsigned int *)t52);
    *((unsigned int *)t52) = (t59 | t53);
    t60 = *((unsigned int *)t58);
    *((unsigned int *)t58) = (t60 | t54);
    xsi_driver_vfirst_trans(t48, 0, 7);
    t61 = (t0 + 8456);
    *((int *)t61) = 1;

LAB1:    return;
LAB4:    *((unsigned int *)t4) = 1;
    goto LAB7;

LAB6:    t11 = (t4 + 4);
    *((unsigned int *)t4) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB7;

LAB8:    t17 = (t0 + 1688U);
    t18 = *((char **)t17);
    t17 = (t0 + 1688U);
    t21 = *((char **)t17);
    memset(t20, 0, 8);
    t17 = (t21 + 4);
    t22 = *((unsigned int *)t17);
    t23 = (~(t22));
    t24 = *((unsigned int *)t21);
    t25 = (t24 & t23);
    t26 = (t25 & 127U);
    if (t26 != 0)
        goto LAB17;

LAB18:    if (*((unsigned int *)t17) != 0)
        goto LAB19;

LAB20:    memset(t19, 0, 8);
    t28 = (t20 + 4);
    t29 = *((unsigned int *)t28);
    t30 = (~(t29));
    t31 = *((unsigned int *)t20);
    t32 = (t31 & t30);
    t33 = (t32 & 1U);
    if (t33 != 0)
        goto LAB24;

LAB22:    if (*((unsigned int *)t28) == 0)
        goto LAB21;

LAB23:    t34 = (t19 + 4);
    *((unsigned int *)t19) = 1;
    *((unsigned int *)t34) = 1;

LAB24:    xsi_vlogtype_concat(t16, 8, 8, 2U, t19, 1, t18, 7);
    t35 = (t0 + 4808);
    t36 = (t35 + 56U);
    t37 = *((char **)t36);
    memset(t38, 0, 8);
    xsi_vlog_unsigned_minus(t38, 8, t16, 8, t37, 8);
    goto LAB9;

LAB10:    t43 = (t0 + 4808);
    t44 = (t43 + 56U);
    t45 = *((char **)t44);
    t46 = ((char*)((ng1)));
    memset(t47, 0, 8);
    xsi_vlog_unsigned_minus(t47, 8, t45, 8, t46, 8);
    goto LAB11;

LAB12:    xsi_vlog_unsigned_bit_combine(t3, 8, t38, 8, t47, 8);
    goto LAB16;

LAB14:    memcpy(t3, t38, 8);
    goto LAB16;

LAB17:    *((unsigned int *)t20) = 1;
    goto LAB20;

LAB19:    t27 = (t20 + 4);
    *((unsigned int *)t20) = 1;
    *((unsigned int *)t27) = 1;
    goto LAB20;

LAB21:    *((unsigned int *)t19) = 1;
    goto LAB24;

}

static void Cont_83_2(char *t0)
{
    char t3[8];
    char t4[8];
    char t16[8];
    char t19[8];
    char t20[8];
    char t35[8];
    char t36[8];
    char t53[8];
    char t61[8];
    char t66[8];
    char t67[8];
    char t91[8];
    char *t1;
    char *t2;
    char *t5;
    unsigned int t6;
    unsigned int t7;
    unsigned int t8;
    unsigned int t9;
    unsigned int t10;
    char *t11;
    char *t12;
    unsigned int t13;
    unsigned int t14;
    unsigned int t15;
    char *t17;
    char *t18;
    char *t21;
    unsigned int t22;
    unsigned int t23;
    unsigned int t24;
    unsigned int t25;
    unsigned int t26;
    char *t27;
    char *t28;
    unsigned int t29;
    unsigned int t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    char *t34;
    char *t37;
    char *t38;
    unsigned int t39;
    unsigned int t40;
    unsigned int t41;
    unsigned int t42;
    unsigned int t43;
    char *t44;
    char *t45;
    unsigned int t46;
    unsigned int t47;
    unsigned int t48;
    char *t49;
    char *t50;
    char *t51;
    char *t52;
    unsigned int t54;
    unsigned int t55;
    unsigned int t56;
    unsigned int t57;
    char *t58;
    char *t59;
    char *t60;
    unsigned int t62;
    unsigned int t63;
    unsigned int t64;
    unsigned int t65;
    char *t68;
    char *t69;
    unsigned int t70;
    unsigned int t71;
    unsigned int t72;
    unsigned int t73;
    unsigned int t74;
    char *t75;
    char *t76;
    unsigned int t77;
    unsigned int t78;
    unsigned int t79;
    char *t80;
    char *t81;
    char *t82;
    unsigned int t83;
    unsigned int t84;
    unsigned int t85;
    unsigned int t86;
    char *t87;
    char *t88;
    char *t89;
    char *t90;
    char *t92;
    char *t93;
    char *t94;
    char *t95;
    char *t96;
    unsigned int t97;
    unsigned int t98;
    char *t99;
    unsigned int t100;
    unsigned int t101;
    char *t102;
    unsigned int t103;
    unsigned int t104;
    char *t105;

LAB0:    t1 = (t0 + 6384U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(83, ng0);
    t2 = (t0 + 1848U);
    t5 = *((char **)t2);
    memset(t4, 0, 8);
    t2 = (t5 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB4;

LAB5:    if (*((unsigned int *)t2) != 0)
        goto LAB6;

LAB7:    t12 = (t4 + 4);
    t13 = *((unsigned int *)t4);
    t14 = *((unsigned int *)t12);
    t15 = (t13 || t14);
    if (t15 > 0)
        goto LAB8;

LAB9:    t62 = *((unsigned int *)t4);
    t63 = (~(t62));
    t64 = *((unsigned int *)t12);
    t65 = (t63 || t64);
    if (t65 > 0)
        goto LAB10;

LAB11:    if (*((unsigned int *)t12) > 0)
        goto LAB12;

LAB13:    if (*((unsigned int *)t4) > 0)
        goto LAB14;

LAB15:    memcpy(t3, t66, 8);

LAB16:    t92 = (t0 + 8792);
    t93 = (t92 + 56U);
    t94 = *((char **)t93);
    t95 = (t94 + 56U);
    t96 = *((char **)t95);
    memset(t96, 0, 8);
    t97 = 255U;
    t98 = t97;
    t99 = (t3 + 4);
    t100 = *((unsigned int *)t3);
    t97 = (t97 & t100);
    t101 = *((unsigned int *)t99);
    t98 = (t98 & t101);
    t102 = (t96 + 4);
    t103 = *((unsigned int *)t96);
    *((unsigned int *)t96) = (t103 | t97);
    t104 = *((unsigned int *)t102);
    *((unsigned int *)t102) = (t104 | t98);
    xsi_driver_vfirst_trans(t92, 0, 7);
    t105 = (t0 + 8472);
    *((int *)t105) = 1;

LAB1:    return;
LAB4:    *((unsigned int *)t4) = 1;
    goto LAB7;

LAB6:    t11 = (t4 + 4);
    *((unsigned int *)t4) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB7;

LAB8:    t17 = (t0 + 1688U);
    t18 = *((char **)t17);
    t17 = (t0 + 1688U);
    t21 = *((char **)t17);
    memset(t20, 0, 8);
    t17 = (t21 + 4);
    t22 = *((unsigned int *)t17);
    t23 = (~(t22));
    t24 = *((unsigned int *)t21);
    t25 = (t24 & t23);
    t26 = (t25 & 127U);
    if (t26 != 0)
        goto LAB17;

LAB18:    if (*((unsigned int *)t17) != 0)
        goto LAB19;

LAB20:    memset(t19, 0, 8);
    t28 = (t20 + 4);
    t29 = *((unsigned int *)t28);
    t30 = (~(t29));
    t31 = *((unsigned int *)t20);
    t32 = (t31 & t30);
    t33 = (t32 & 1U);
    if (t33 != 0)
        goto LAB24;

LAB22:    if (*((unsigned int *)t28) == 0)
        goto LAB21;

LAB23:    t34 = (t19 + 4);
    *((unsigned int *)t19) = 1;
    *((unsigned int *)t34) = 1;

LAB24:    xsi_vlogtype_concat(t16, 8, 8, 2U, t19, 1, t18, 7);
    t37 = (t0 + 2488U);
    t38 = *((char **)t37);
    memset(t36, 0, 8);
    t37 = (t38 + 4);
    t39 = *((unsigned int *)t37);
    t40 = (~(t39));
    t41 = *((unsigned int *)t38);
    t42 = (t41 & t40);
    t43 = (t42 & 1U);
    if (t43 != 0)
        goto LAB25;

LAB26:    if (*((unsigned int *)t37) != 0)
        goto LAB27;

LAB28:    t45 = (t36 + 4);
    t46 = *((unsigned int *)t36);
    t47 = *((unsigned int *)t45);
    t48 = (t46 || t47);
    if (t48 > 0)
        goto LAB29;

LAB30:    t54 = *((unsigned int *)t36);
    t55 = (~(t54));
    t56 = *((unsigned int *)t45);
    t57 = (t55 || t56);
    if (t57 > 0)
        goto LAB31;

LAB32:    if (*((unsigned int *)t45) > 0)
        goto LAB33;

LAB34:    if (*((unsigned int *)t36) > 0)
        goto LAB35;

LAB36:    memcpy(t35, t60, 8);

LAB37:    memset(t61, 0, 8);
    xsi_vlog_unsigned_minus(t61, 8, t16, 8, t35, 8);
    goto LAB9;

LAB10:    t68 = (t0 + 2488U);
    t69 = *((char **)t68);
    memset(t67, 0, 8);
    t68 = (t69 + 4);
    t70 = *((unsigned int *)t68);
    t71 = (~(t70));
    t72 = *((unsigned int *)t69);
    t73 = (t72 & t71);
    t74 = (t73 & 1U);
    if (t74 != 0)
        goto LAB38;

LAB39:    if (*((unsigned int *)t68) != 0)
        goto LAB40;

LAB41:    t76 = (t67 + 4);
    t77 = *((unsigned int *)t67);
    t78 = *((unsigned int *)t76);
    t79 = (t77 || t78);
    if (t79 > 0)
        goto LAB42;

LAB43:    t83 = *((unsigned int *)t67);
    t84 = (~(t83));
    t85 = *((unsigned int *)t76);
    t86 = (t84 || t85);
    if (t86 > 0)
        goto LAB44;

LAB45:    if (*((unsigned int *)t76) > 0)
        goto LAB46;

LAB47:    if (*((unsigned int *)t67) > 0)
        goto LAB48;

LAB49:    memcpy(t66, t91, 8);

LAB50:    goto LAB11;

LAB12:    xsi_vlog_unsigned_bit_combine(t3, 8, t61, 8, t66, 8);
    goto LAB16;

LAB14:    memcpy(t3, t61, 8);
    goto LAB16;

LAB17:    *((unsigned int *)t20) = 1;
    goto LAB20;

LAB19:    t27 = (t20 + 4);
    *((unsigned int *)t20) = 1;
    *((unsigned int *)t27) = 1;
    goto LAB20;

LAB21:    *((unsigned int *)t19) = 1;
    goto LAB24;

LAB25:    *((unsigned int *)t36) = 1;
    goto LAB28;

LAB27:    t44 = (t36 + 4);
    *((unsigned int *)t36) = 1;
    *((unsigned int *)t44) = 1;
    goto LAB28;

LAB29:    t49 = (t0 + 4808);
    t50 = (t49 + 56U);
    t51 = *((char **)t50);
    t52 = ((char*)((ng1)));
    memset(t53, 0, 8);
    xsi_vlog_unsigned_add(t53, 8, t51, 8, t52, 8);
    goto LAB30;

LAB31:    t58 = (t0 + 4808);
    t59 = (t58 + 56U);
    t60 = *((char **)t59);
    goto LAB32;

LAB33:    xsi_vlog_unsigned_bit_combine(t35, 8, t53, 8, t60, 8);
    goto LAB37;

LAB35:    memcpy(t35, t53, 8);
    goto LAB37;

LAB38:    *((unsigned int *)t67) = 1;
    goto LAB41;

LAB40:    t75 = (t67 + 4);
    *((unsigned int *)t67) = 1;
    *((unsigned int *)t75) = 1;
    goto LAB41;

LAB42:    t80 = (t0 + 4808);
    t81 = (t80 + 56U);
    t82 = *((char **)t81);
    goto LAB43;

LAB44:    t87 = (t0 + 4808);
    t88 = (t87 + 56U);
    t89 = *((char **)t88);
    t90 = ((char*)((ng1)));
    memset(t91, 0, 8);
    xsi_vlog_unsigned_minus(t91, 8, t89, 8, t90, 8);
    goto LAB45;

LAB46:    xsi_vlog_unsigned_bit_combine(t66, 8, t82, 8, t91, 8);
    goto LAB50;

LAB48:    memcpy(t66, t82, 8);
    goto LAB50;

}

static void Cont_86_3(char *t0)
{
    char t3[8];
    char t4[8];
    char *t1;
    char *t2;
    char *t5;
    char *t6;
    char *t7;
    unsigned int t8;
    unsigned int t9;
    unsigned int t10;
    unsigned int t11;
    unsigned int t12;
    char *t13;
    char *t14;
    unsigned int t15;
    unsigned int t16;
    unsigned int t17;
    unsigned int t18;
    unsigned int t19;
    char *t20;
    char *t21;
    char *t22;
    char *t23;
    char *t24;
    char *t25;
    unsigned int t26;
    unsigned int t27;
    char *t28;
    unsigned int t29;
    unsigned int t30;
    char *t31;
    unsigned int t32;
    unsigned int t33;
    char *t34;

LAB0:    t1 = (t0 + 6632U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(86, ng0);
    t2 = (t0 + 4808);
    t5 = (t2 + 56U);
    t6 = *((char **)t5);
    memset(t4, 0, 8);
    t7 = (t6 + 4);
    t8 = *((unsigned int *)t7);
    t9 = (~(t8));
    t10 = *((unsigned int *)t6);
    t11 = (t10 & t9);
    t12 = (t11 & 255U);
    if (t12 != 0)
        goto LAB4;

LAB5:    if (*((unsigned int *)t7) != 0)
        goto LAB6;

LAB7:    memset(t3, 0, 8);
    t14 = (t4 + 4);
    t15 = *((unsigned int *)t14);
    t16 = (~(t15));
    t17 = *((unsigned int *)t4);
    t18 = (t17 & t16);
    t19 = (t18 & 1U);
    if (t19 != 0)
        goto LAB11;

LAB9:    if (*((unsigned int *)t14) == 0)
        goto LAB8;

LAB10:    t20 = (t3 + 4);
    *((unsigned int *)t3) = 1;
    *((unsigned int *)t20) = 1;

LAB11:    t21 = (t0 + 8856);
    t22 = (t21 + 56U);
    t23 = *((char **)t22);
    t24 = (t23 + 56U);
    t25 = *((char **)t24);
    memset(t25, 0, 8);
    t26 = 1U;
    t27 = t26;
    t28 = (t3 + 4);
    t29 = *((unsigned int *)t3);
    t26 = (t26 & t29);
    t30 = *((unsigned int *)t28);
    t27 = (t27 & t30);
    t31 = (t25 + 4);
    t32 = *((unsigned int *)t25);
    *((unsigned int *)t25) = (t32 | t26);
    t33 = *((unsigned int *)t31);
    *((unsigned int *)t31) = (t33 | t27);
    xsi_driver_vfirst_trans(t21, 0, 0);
    t34 = (t0 + 8488);
    *((int *)t34) = 1;

LAB1:    return;
LAB4:    *((unsigned int *)t4) = 1;
    goto LAB7;

LAB6:    t13 = (t4 + 4);
    *((unsigned int *)t4) = 1;
    *((unsigned int *)t13) = 1;
    goto LAB7;

LAB8:    *((unsigned int *)t3) = 1;
    goto LAB11;

}

static void Cont_88_4(char *t0)
{
    char t3[8];
    char t4[8];
    char t23[8];
    char t34[8];
    char t43[8];
    char t58[8];
    char t65[8];
    char t93[8];
    char t101[8];
    char *t1;
    char *t2;
    char *t5;
    unsigned int t6;
    unsigned int t7;
    unsigned int t8;
    unsigned int t9;
    unsigned int t10;
    char *t11;
    char *t12;
    unsigned int t13;
    unsigned int t14;
    unsigned int t15;
    char *t16;
    char *t17;
    unsigned int t18;
    unsigned int t19;
    unsigned int t20;
    unsigned int t21;
    char *t22;
    unsigned int t24;
    unsigned int t25;
    unsigned int t26;
    unsigned int t27;
    unsigned int t28;
    char *t29;
    char *t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    char *t35;
    char *t36;
    unsigned int t37;
    unsigned int t38;
    unsigned int t39;
    unsigned int t40;
    unsigned int t41;
    char *t42;
    char *t44;
    unsigned int t45;
    unsigned int t46;
    unsigned int t47;
    unsigned int t48;
    unsigned int t49;
    char *t50;
    char *t51;
    unsigned int t52;
    unsigned int t53;
    unsigned int t54;
    unsigned int t55;
    char *t56;
    char *t57;
    unsigned int t59;
    unsigned int t60;
    unsigned int t61;
    unsigned int t62;
    unsigned int t63;
    char *t64;
    unsigned int t66;
    unsigned int t67;
    unsigned int t68;
    char *t69;
    char *t70;
    char *t71;
    unsigned int t72;
    unsigned int t73;
    unsigned int t74;
    unsigned int t75;
    unsigned int t76;
    unsigned int t77;
    unsigned int t78;
    char *t79;
    char *t80;
    unsigned int t81;
    unsigned int t82;
    unsigned int t83;
    int t84;
    unsigned int t85;
    unsigned int t86;
    unsigned int t87;
    int t88;
    unsigned int t89;
    unsigned int t90;
    unsigned int t91;
    unsigned int t92;
    char *t94;
    unsigned int t95;
    unsigned int t96;
    unsigned int t97;
    unsigned int t98;
    unsigned int t99;
    char *t100;
    unsigned int t102;
    unsigned int t103;
    unsigned int t104;
    char *t105;
    char *t106;
    char *t107;
    unsigned int t108;
    unsigned int t109;
    unsigned int t110;
    unsigned int t111;
    unsigned int t112;
    unsigned int t113;
    unsigned int t114;
    char *t115;
    char *t116;
    unsigned int t117;
    unsigned int t118;
    unsigned int t119;
    unsigned int t120;
    unsigned int t121;
    unsigned int t122;
    unsigned int t123;
    unsigned int t124;
    int t125;
    int t126;
    unsigned int t127;
    unsigned int t128;
    unsigned int t129;
    unsigned int t130;
    unsigned int t131;
    unsigned int t132;
    char *t133;
    char *t134;
    char *t135;
    char *t136;
    char *t137;
    unsigned int t138;
    unsigned int t139;
    char *t140;
    unsigned int t141;
    unsigned int t142;
    char *t143;
    unsigned int t144;
    unsigned int t145;
    char *t146;

LAB0:    t1 = (t0 + 6880U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(88, ng0);
    t2 = (t0 + 2488U);
    t5 = *((char **)t2);
    memset(t4, 0, 8);
    t2 = (t5 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB4;

LAB5:    if (*((unsigned int *)t2) != 0)
        goto LAB6;

LAB7:    t12 = (t4 + 4);
    t13 = *((unsigned int *)t4);
    t14 = *((unsigned int *)t12);
    t15 = (t13 || t14);
    if (t15 > 0)
        goto LAB8;

LAB9:    t18 = *((unsigned int *)t4);
    t19 = (~(t18));
    t20 = *((unsigned int *)t12);
    t21 = (t19 || t20);
    if (t21 > 0)
        goto LAB10;

LAB11:    if (*((unsigned int *)t12) > 0)
        goto LAB12;

LAB13:    if (*((unsigned int *)t4) > 0)
        goto LAB14;

LAB15:    memcpy(t3, t22, 8);

LAB16:    memset(t23, 0, 8);
    t16 = (t3 + 4);
    t24 = *((unsigned int *)t16);
    t25 = (~(t24));
    t26 = *((unsigned int *)t3);
    t27 = (t26 & t25);
    t28 = (t27 & 1U);
    if (t28 != 0)
        goto LAB17;

LAB18:    if (*((unsigned int *)t16) != 0)
        goto LAB19;

LAB20:    t30 = (t23 + 4);
    t31 = *((unsigned int *)t23);
    t32 = *((unsigned int *)t30);
    t33 = (t31 || t32);
    if (t33 > 0)
        goto LAB21;

LAB22:    memcpy(t101, t23, 8);

LAB23:    t133 = (t0 + 8920);
    t134 = (t133 + 56U);
    t135 = *((char **)t134);
    t136 = (t135 + 56U);
    t137 = *((char **)t136);
    memset(t137, 0, 8);
    t138 = 1U;
    t139 = t138;
    t140 = (t101 + 4);
    t141 = *((unsigned int *)t101);
    t138 = (t138 & t141);
    t142 = *((unsigned int *)t140);
    t139 = (t139 & t142);
    t143 = (t137 + 4);
    t144 = *((unsigned int *)t137);
    *((unsigned int *)t137) = (t144 | t138);
    t145 = *((unsigned int *)t143);
    *((unsigned int *)t143) = (t145 | t139);
    xsi_driver_vfirst_trans(t133, 0, 0);
    t146 = (t0 + 8504);
    *((int *)t146) = 1;

LAB1:    return;
LAB4:    *((unsigned int *)t4) = 1;
    goto LAB7;

LAB6:    t11 = (t4 + 4);
    *((unsigned int *)t4) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB7;

LAB8:    t16 = (t0 + 2328U);
    t17 = *((char **)t16);
    goto LAB9;

LAB10:    t16 = (t0 + 2168U);
    t22 = *((char **)t16);
    goto LAB11;

LAB12:    xsi_vlog_unsigned_bit_combine(t3, 1, t17, 1, t22, 1);
    goto LAB16;

LAB14:    memcpy(t3, t17, 8);
    goto LAB16;

LAB17:    *((unsigned int *)t23) = 1;
    goto LAB20;

LAB19:    t29 = (t23 + 4);
    *((unsigned int *)t23) = 1;
    *((unsigned int *)t29) = 1;
    goto LAB20;

LAB21:    t35 = (t0 + 2808U);
    t36 = *((char **)t35);
    memset(t34, 0, 8);
    t35 = (t36 + 4);
    t37 = *((unsigned int *)t35);
    t38 = (~(t37));
    t39 = *((unsigned int *)t36);
    t40 = (t39 & t38);
    t41 = (t40 & 1U);
    if (t41 != 0)
        goto LAB27;

LAB25:    if (*((unsigned int *)t35) == 0)
        goto LAB24;

LAB26:    t42 = (t34 + 4);
    *((unsigned int *)t34) = 1;
    *((unsigned int *)t42) = 1;

LAB27:    memset(t43, 0, 8);
    t44 = (t34 + 4);
    t45 = *((unsigned int *)t44);
    t46 = (~(t45));
    t47 = *((unsigned int *)t34);
    t48 = (t47 & t46);
    t49 = (t48 & 1U);
    if (t49 != 0)
        goto LAB28;

LAB29:    if (*((unsigned int *)t44) != 0)
        goto LAB30;

LAB31:    t51 = (t43 + 4);
    t52 = *((unsigned int *)t43);
    t53 = (!(t52));
    t54 = *((unsigned int *)t51);
    t55 = (t53 || t54);
    if (t55 > 0)
        goto LAB32;

LAB33:    memcpy(t65, t43, 8);

LAB34:    memset(t93, 0, 8);
    t94 = (t65 + 4);
    t95 = *((unsigned int *)t94);
    t96 = (~(t95));
    t97 = *((unsigned int *)t65);
    t98 = (t97 & t96);
    t99 = (t98 & 1U);
    if (t99 != 0)
        goto LAB42;

LAB43:    if (*((unsigned int *)t94) != 0)
        goto LAB44;

LAB45:    t102 = *((unsigned int *)t23);
    t103 = *((unsigned int *)t93);
    t104 = (t102 & t103);
    *((unsigned int *)t101) = t104;
    t105 = (t23 + 4);
    t106 = (t93 + 4);
    t107 = (t101 + 4);
    t108 = *((unsigned int *)t105);
    t109 = *((unsigned int *)t106);
    t110 = (t108 | t109);
    *((unsigned int *)t107) = t110;
    t111 = *((unsigned int *)t107);
    t112 = (t111 != 0);
    if (t112 == 1)
        goto LAB46;

LAB47:
LAB48:    goto LAB23;

LAB24:    *((unsigned int *)t34) = 1;
    goto LAB27;

LAB28:    *((unsigned int *)t43) = 1;
    goto LAB31;

LAB30:    t50 = (t43 + 4);
    *((unsigned int *)t43) = 1;
    *((unsigned int *)t50) = 1;
    goto LAB31;

LAB32:    t56 = (t0 + 3288U);
    t57 = *((char **)t56);
    memset(t58, 0, 8);
    t56 = (t57 + 4);
    t59 = *((unsigned int *)t56);
    t60 = (~(t59));
    t61 = *((unsigned int *)t57);
    t62 = (t61 & t60);
    t63 = (t62 & 1U);
    if (t63 != 0)
        goto LAB35;

LAB36:    if (*((unsigned int *)t56) != 0)
        goto LAB37;

LAB38:    t66 = *((unsigned int *)t43);
    t67 = *((unsigned int *)t58);
    t68 = (t66 | t67);
    *((unsigned int *)t65) = t68;
    t69 = (t43 + 4);
    t70 = (t58 + 4);
    t71 = (t65 + 4);
    t72 = *((unsigned int *)t69);
    t73 = *((unsigned int *)t70);
    t74 = (t72 | t73);
    *((unsigned int *)t71) = t74;
    t75 = *((unsigned int *)t71);
    t76 = (t75 != 0);
    if (t76 == 1)
        goto LAB39;

LAB40:
LAB41:    goto LAB34;

LAB35:    *((unsigned int *)t58) = 1;
    goto LAB38;

LAB37:    t64 = (t58 + 4);
    *((unsigned int *)t58) = 1;
    *((unsigned int *)t64) = 1;
    goto LAB38;

LAB39:    t77 = *((unsigned int *)t65);
    t78 = *((unsigned int *)t71);
    *((unsigned int *)t65) = (t77 | t78);
    t79 = (t43 + 4);
    t80 = (t58 + 4);
    t81 = *((unsigned int *)t79);
    t82 = (~(t81));
    t83 = *((unsigned int *)t43);
    t84 = (t83 & t82);
    t85 = *((unsigned int *)t80);
    t86 = (~(t85));
    t87 = *((unsigned int *)t58);
    t88 = (t87 & t86);
    t89 = (~(t84));
    t90 = (~(t88));
    t91 = *((unsigned int *)t71);
    *((unsigned int *)t71) = (t91 & t89);
    t92 = *((unsigned int *)t71);
    *((unsigned int *)t71) = (t92 & t90);
    goto LAB41;

LAB42:    *((unsigned int *)t93) = 1;
    goto LAB45;

LAB44:    t100 = (t93 + 4);
    *((unsigned int *)t93) = 1;
    *((unsigned int *)t100) = 1;
    goto LAB45;

LAB46:    t113 = *((unsigned int *)t101);
    t114 = *((unsigned int *)t107);
    *((unsigned int *)t101) = (t113 | t114);
    t115 = (t23 + 4);
    t116 = (t93 + 4);
    t117 = *((unsigned int *)t23);
    t118 = (~(t117));
    t119 = *((unsigned int *)t115);
    t120 = (~(t119));
    t121 = *((unsigned int *)t93);
    t122 = (~(t121));
    t123 = *((unsigned int *)t116);
    t124 = (~(t123));
    t125 = (t118 & t120);
    t126 = (t122 & t124);
    t127 = (~(t125));
    t128 = (~(t126));
    t129 = *((unsigned int *)t107);
    *((unsigned int *)t107) = (t129 & t127);
    t130 = *((unsigned int *)t107);
    *((unsigned int *)t107) = (t130 & t128);
    t131 = *((unsigned int *)t101);
    *((unsigned int *)t101) = (t131 & t127);
    t132 = *((unsigned int *)t101);
    *((unsigned int *)t101) = (t132 & t128);
    goto LAB48;

}

static void Cont_89_5(char *t0)
{
    char t3[8];
    char t4[8];
    char t23[8];
    char t34[8];
    char t43[8];
    char t51[8];
    char *t1;
    char *t2;
    char *t5;
    unsigned int t6;
    unsigned int t7;
    unsigned int t8;
    unsigned int t9;
    unsigned int t10;
    char *t11;
    char *t12;
    unsigned int t13;
    unsigned int t14;
    unsigned int t15;
    char *t16;
    char *t17;
    unsigned int t18;
    unsigned int t19;
    unsigned int t20;
    unsigned int t21;
    char *t22;
    unsigned int t24;
    unsigned int t25;
    unsigned int t26;
    unsigned int t27;
    unsigned int t28;
    char *t29;
    char *t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    char *t35;
    char *t36;
    unsigned int t37;
    unsigned int t38;
    unsigned int t39;
    unsigned int t40;
    unsigned int t41;
    char *t42;
    char *t44;
    unsigned int t45;
    unsigned int t46;
    unsigned int t47;
    unsigned int t48;
    unsigned int t49;
    char *t50;
    unsigned int t52;
    unsigned int t53;
    unsigned int t54;
    char *t55;
    char *t56;
    char *t57;
    unsigned int t58;
    unsigned int t59;
    unsigned int t60;
    unsigned int t61;
    unsigned int t62;
    unsigned int t63;
    unsigned int t64;
    char *t65;
    char *t66;
    unsigned int t67;
    unsigned int t68;
    unsigned int t69;
    unsigned int t70;
    unsigned int t71;
    unsigned int t72;
    unsigned int t73;
    unsigned int t74;
    int t75;
    int t76;
    unsigned int t77;
    unsigned int t78;
    unsigned int t79;
    unsigned int t80;
    unsigned int t81;
    unsigned int t82;
    char *t83;
    char *t84;
    char *t85;
    char *t86;
    char *t87;
    unsigned int t88;
    unsigned int t89;
    char *t90;
    unsigned int t91;
    unsigned int t92;
    char *t93;
    unsigned int t94;
    unsigned int t95;
    char *t96;

LAB0:    t1 = (t0 + 7128U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(89, ng0);
    t2 = (t0 + 2648U);
    t5 = *((char **)t2);
    memset(t4, 0, 8);
    t2 = (t5 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB4;

LAB5:    if (*((unsigned int *)t2) != 0)
        goto LAB6;

LAB7:    t12 = (t4 + 4);
    t13 = *((unsigned int *)t4);
    t14 = *((unsigned int *)t12);
    t15 = (t13 || t14);
    if (t15 > 0)
        goto LAB8;

LAB9:    t18 = *((unsigned int *)t4);
    t19 = (~(t18));
    t20 = *((unsigned int *)t12);
    t21 = (t19 || t20);
    if (t21 > 0)
        goto LAB10;

LAB11:    if (*((unsigned int *)t12) > 0)
        goto LAB12;

LAB13:    if (*((unsigned int *)t4) > 0)
        goto LAB14;

LAB15:    memcpy(t3, t22, 8);

LAB16:    memset(t23, 0, 8);
    t16 = (t3 + 4);
    t24 = *((unsigned int *)t16);
    t25 = (~(t24));
    t26 = *((unsigned int *)t3);
    t27 = (t26 & t25);
    t28 = (t27 & 1U);
    if (t28 != 0)
        goto LAB17;

LAB18:    if (*((unsigned int *)t16) != 0)
        goto LAB19;

LAB20:    t30 = (t23 + 4);
    t31 = *((unsigned int *)t23);
    t32 = *((unsigned int *)t30);
    t33 = (t31 || t32);
    if (t33 > 0)
        goto LAB21;

LAB22:    memcpy(t51, t23, 8);

LAB23:    t83 = (t0 + 8984);
    t84 = (t83 + 56U);
    t85 = *((char **)t84);
    t86 = (t85 + 56U);
    t87 = *((char **)t86);
    memset(t87, 0, 8);
    t88 = 1U;
    t89 = t88;
    t90 = (t51 + 4);
    t91 = *((unsigned int *)t51);
    t88 = (t88 & t91);
    t92 = *((unsigned int *)t90);
    t89 = (t89 & t92);
    t93 = (t87 + 4);
    t94 = *((unsigned int *)t87);
    *((unsigned int *)t87) = (t94 | t88);
    t95 = *((unsigned int *)t93);
    *((unsigned int *)t93) = (t95 | t89);
    xsi_driver_vfirst_trans(t83, 0, 0);
    t96 = (t0 + 8520);
    *((int *)t96) = 1;

LAB1:    return;
LAB4:    *((unsigned int *)t4) = 1;
    goto LAB7;

LAB6:    t11 = (t4 + 4);
    *((unsigned int *)t4) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB7;

LAB8:    t16 = (t0 + 2328U);
    t17 = *((char **)t16);
    goto LAB9;

LAB10:    t16 = (t0 + 2168U);
    t22 = *((char **)t16);
    goto LAB11;

LAB12:    xsi_vlog_unsigned_bit_combine(t3, 1, t17, 1, t22, 1);
    goto LAB16;

LAB14:    memcpy(t3, t17, 8);
    goto LAB16;

LAB17:    *((unsigned int *)t23) = 1;
    goto LAB20;

LAB19:    t29 = (t23 + 4);
    *((unsigned int *)t23) = 1;
    *((unsigned int *)t29) = 1;
    goto LAB20;

LAB21:    t35 = (t0 + 2808U);
    t36 = *((char **)t35);
    memset(t34, 0, 8);
    t35 = (t36 + 4);
    t37 = *((unsigned int *)t35);
    t38 = (~(t37));
    t39 = *((unsigned int *)t36);
    t40 = (t39 & t38);
    t41 = (t40 & 1U);
    if (t41 != 0)
        goto LAB27;

LAB25:    if (*((unsigned int *)t35) == 0)
        goto LAB24;

LAB26:    t42 = (t34 + 4);
    *((unsigned int *)t34) = 1;
    *((unsigned int *)t42) = 1;

LAB27:    memset(t43, 0, 8);
    t44 = (t34 + 4);
    t45 = *((unsigned int *)t44);
    t46 = (~(t45));
    t47 = *((unsigned int *)t34);
    t48 = (t47 & t46);
    t49 = (t48 & 1U);
    if (t49 != 0)
        goto LAB28;

LAB29:    if (*((unsigned int *)t44) != 0)
        goto LAB30;

LAB31:    t52 = *((unsigned int *)t23);
    t53 = *((unsigned int *)t43);
    t54 = (t52 & t53);
    *((unsigned int *)t51) = t54;
    t55 = (t23 + 4);
    t56 = (t43 + 4);
    t57 = (t51 + 4);
    t58 = *((unsigned int *)t55);
    t59 = *((unsigned int *)t56);
    t60 = (t58 | t59);
    *((unsigned int *)t57) = t60;
    t61 = *((unsigned int *)t57);
    t62 = (t61 != 0);
    if (t62 == 1)
        goto LAB32;

LAB33:
LAB34:    goto LAB23;

LAB24:    *((unsigned int *)t34) = 1;
    goto LAB27;

LAB28:    *((unsigned int *)t43) = 1;
    goto LAB31;

LAB30:    t50 = (t43 + 4);
    *((unsigned int *)t43) = 1;
    *((unsigned int *)t50) = 1;
    goto LAB31;

LAB32:    t63 = *((unsigned int *)t51);
    t64 = *((unsigned int *)t57);
    *((unsigned int *)t51) = (t63 | t64);
    t65 = (t23 + 4);
    t66 = (t43 + 4);
    t67 = *((unsigned int *)t23);
    t68 = (~(t67));
    t69 = *((unsigned int *)t65);
    t70 = (~(t69));
    t71 = *((unsigned int *)t43);
    t72 = (~(t71));
    t73 = *((unsigned int *)t66);
    t74 = (~(t73));
    t75 = (t68 & t70);
    t76 = (t72 & t74);
    t77 = (~(t75));
    t78 = (~(t76));
    t79 = *((unsigned int *)t57);
    *((unsigned int *)t57) = (t79 & t77);
    t80 = *((unsigned int *)t57);
    *((unsigned int *)t57) = (t80 & t78);
    t81 = *((unsigned int *)t51);
    *((unsigned int *)t51) = (t81 & t77);
    t82 = *((unsigned int *)t51);
    *((unsigned int *)t51) = (t82 & t78);
    goto LAB34;

}

static void Always_92_6(char *t0)
{
    char t13[8];
    char t14[8];
    char t29[8];
    char t38[8];
    char t44[8];
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
    unsigned int t15;
    unsigned int t16;
    unsigned int t17;
    unsigned int t18;
    unsigned int t19;
    char *t20;
    char *t21;
    unsigned int t22;
    unsigned int t23;
    unsigned int t24;
    char *t25;
    char *t26;
    char *t27;
    char *t28;
    unsigned int t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    char *t34;
    char *t35;
    char *t36;
    char *t37;
    unsigned int t39;
    unsigned int t40;
    unsigned int t41;
    unsigned int t42;
    unsigned int t43;

LAB0:    t1 = (t0 + 7376U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(92, ng0);
    t2 = (t0 + 8536);
    *((int *)t2) = 1;
    t3 = (t0 + 7408);
    *((char **)t3) = t2;
    *((char **)t1) = &&LAB4;

LAB1:    return;
LAB4:    xsi_set_current_line(93, ng0);

LAB5:    xsi_set_current_line(94, ng0);
    t4 = (t0 + 1208U);
    t5 = *((char **)t4);
    t4 = (t5 + 4);
    t6 = *((unsigned int *)t4);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 != 0);
    if (t10 > 0)
        goto LAB6;

LAB7:    xsi_set_current_line(97, ng0);

LAB9:    xsi_set_current_line(98, ng0);
    t2 = (t0 + 4488);
    t3 = (t2 + 56U);
    t4 = *((char **)t3);
    t5 = (t4 + 4);
    t6 = *((unsigned int *)t5);
    t7 = (~(t6));
    t8 = *((unsigned int *)t4);
    t9 = (t8 & t7);
    t10 = (t9 != 0);
    if (t10 > 0)
        goto LAB10;

LAB11:    xsi_set_current_line(101, ng0);
    t2 = (t0 + 1688U);
    t3 = *((char **)t2);
    memset(t38, 0, 8);
    t2 = (t3 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t3);
    t9 = (t8 & t7);
    t10 = (t9 & 127U);
    if (t10 != 0)
        goto LAB26;

LAB27:    if (*((unsigned int *)t2) != 0)
        goto LAB28;

LAB29:    memset(t29, 0, 8);
    t5 = (t38 + 4);
    t15 = *((unsigned int *)t5);
    t16 = (~(t15));
    t17 = *((unsigned int *)t38);
    t18 = (t17 & t16);
    t19 = (t18 & 1U);
    if (t19 != 0)
        goto LAB33;

LAB31:    if (*((unsigned int *)t5) == 0)
        goto LAB30;

LAB32:    t11 = (t29 + 4);
    *((unsigned int *)t29) = 1;
    *((unsigned int *)t11) = 1;

LAB33:    memset(t14, 0, 8);
    t12 = (t29 + 4);
    t22 = *((unsigned int *)t12);
    t23 = (~(t22));
    t24 = *((unsigned int *)t29);
    t30 = (t24 & t23);
    t31 = (t30 & 1U);
    if (t31 != 0)
        goto LAB34;

LAB35:    if (*((unsigned int *)t12) != 0)
        goto LAB36;

LAB37:    t21 = (t14 + 4);
    t32 = *((unsigned int *)t14);
    t33 = *((unsigned int *)t21);
    t39 = (t32 || t33);
    if (t39 > 0)
        goto LAB38;

LAB39:    t40 = *((unsigned int *)t14);
    t41 = (~(t40));
    t42 = *((unsigned int *)t21);
    t43 = (t41 || t42);
    if (t43 > 0)
        goto LAB40;

LAB41:    if (*((unsigned int *)t21) > 0)
        goto LAB42;

LAB43:    if (*((unsigned int *)t14) > 0)
        goto LAB44;

LAB45:    memcpy(t13, t44, 8);

LAB46:    t28 = (t0 + 4808);
    xsi_vlogvar_wait_assign_value(t28, t13, 0, 0, 8, 0LL);

LAB12:
LAB8:    goto LAB2;

LAB6:    xsi_set_current_line(95, ng0);
    t11 = ((char*)((ng2)));
    t12 = (t0 + 4808);
    xsi_vlogvar_wait_assign_value(t12, t11, 0, 0, 8, 0LL);
    goto LAB8;

LAB10:    xsi_set_current_line(99, ng0);
    t11 = (t0 + 2168U);
    t12 = *((char **)t11);
    memset(t14, 0, 8);
    t11 = (t12 + 4);
    t15 = *((unsigned int *)t11);
    t16 = (~(t15));
    t17 = *((unsigned int *)t12);
    t18 = (t17 & t16);
    t19 = (t18 & 1U);
    if (t19 != 0)
        goto LAB13;

LAB14:    if (*((unsigned int *)t11) != 0)
        goto LAB15;

LAB16:    t21 = (t14 + 4);
    t22 = *((unsigned int *)t14);
    t23 = *((unsigned int *)t21);
    t24 = (t22 || t23);
    if (t24 > 0)
        goto LAB17;

LAB18:    t30 = *((unsigned int *)t14);
    t31 = (~(t30));
    t32 = *((unsigned int *)t21);
    t33 = (t31 || t32);
    if (t33 > 0)
        goto LAB19;

LAB20:    if (*((unsigned int *)t21) > 0)
        goto LAB21;

LAB22:    if (*((unsigned int *)t14) > 0)
        goto LAB23;

LAB24:    memcpy(t13, t36, 8);

LAB25:    t37 = (t0 + 4808);
    xsi_vlogvar_wait_assign_value(t37, t13, 0, 0, 8, 0LL);
    goto LAB12;

LAB13:    *((unsigned int *)t14) = 1;
    goto LAB16;

LAB15:    t20 = (t14 + 4);
    *((unsigned int *)t14) = 1;
    *((unsigned int *)t20) = 1;
    goto LAB16;

LAB17:    t25 = (t0 + 4808);
    t26 = (t25 + 56U);
    t27 = *((char **)t26);
    t28 = ((char*)((ng1)));
    memset(t29, 0, 8);
    xsi_vlog_unsigned_minus(t29, 8, t27, 8, t28, 8);
    goto LAB18;

LAB19:    t34 = (t0 + 4808);
    t35 = (t34 + 56U);
    t36 = *((char **)t35);
    goto LAB20;

LAB21:    xsi_vlog_unsigned_bit_combine(t13, 8, t29, 8, t36, 8);
    goto LAB25;

LAB23:    memcpy(t13, t29, 8);
    goto LAB25;

LAB26:    *((unsigned int *)t38) = 1;
    goto LAB29;

LAB28:    t4 = (t38 + 4);
    *((unsigned int *)t38) = 1;
    *((unsigned int *)t4) = 1;
    goto LAB29;

LAB30:    *((unsigned int *)t29) = 1;
    goto LAB33;

LAB34:    *((unsigned int *)t14) = 1;
    goto LAB37;

LAB36:    t20 = (t14 + 4);
    *((unsigned int *)t14) = 1;
    *((unsigned int *)t20) = 1;
    goto LAB37;

LAB38:    t25 = ((char*)((ng3)));
    goto LAB39;

LAB40:    t26 = (t0 + 1688U);
    t27 = *((char **)t26);
    t26 = ((char*)((ng2)));
    xsi_vlogtype_concat(t44, 8, 8, 2U, t26, 1, t27, 7);
    goto LAB41;

LAB42:    xsi_vlog_unsigned_bit_combine(t13, 8, t25, 8, t44, 8);
    goto LAB46;

LAB44:    memcpy(t13, t25, 8);
    goto LAB46;

}

static void Always_106_7(char *t0)
{
    char t13[8];
    char t17[8];
    char t36[8];
    char t44[8];
    char t84[8];
    char t85[8];
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
    unsigned int t14;
    unsigned int t15;
    unsigned int t16;
    char *t18;
    char *t19;
    unsigned int t20;
    unsigned int t21;
    unsigned int t22;
    unsigned int t23;
    unsigned int t24;
    char *t25;
    char *t26;
    char *t27;
    unsigned int t28;
    unsigned int t29;
    unsigned int t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    unsigned int t34;
    unsigned int t35;
    char *t37;
    unsigned int t38;
    unsigned int t39;
    unsigned int t40;
    unsigned int t41;
    unsigned int t42;
    char *t43;
    unsigned int t45;
    unsigned int t46;
    unsigned int t47;
    char *t48;
    char *t49;
    char *t50;
    unsigned int t51;
    unsigned int t52;
    unsigned int t53;
    unsigned int t54;
    unsigned int t55;
    unsigned int t56;
    unsigned int t57;
    char *t58;
    char *t59;
    unsigned int t60;
    unsigned int t61;
    unsigned int t62;
    unsigned int t63;
    unsigned int t64;
    unsigned int t65;
    unsigned int t66;
    unsigned int t67;
    int t68;
    int t69;
    unsigned int t70;
    unsigned int t71;
    unsigned int t72;
    unsigned int t73;
    unsigned int t74;
    unsigned int t75;
    char *t76;
    unsigned int t77;
    unsigned int t78;
    unsigned int t79;
    unsigned int t80;
    unsigned int t81;
    char *t82;
    char *t83;
    char *t86;
    char *t87;
    unsigned int t88;
    unsigned int t89;
    unsigned int t90;
    unsigned int t91;
    unsigned int t92;
    char *t93;
    char *t94;
    unsigned int t95;
    unsigned int t96;
    unsigned int t97;
    unsigned int t98;
    unsigned int t99;
    unsigned int t100;
    unsigned int t101;
    unsigned int t102;
    int t103;
    int t104;
    unsigned int t105;
    unsigned int t106;
    unsigned int t107;
    unsigned int t108;
    unsigned int t109;
    unsigned int t110;
    char *t111;
    unsigned int t112;
    unsigned int t113;
    unsigned int t114;
    unsigned int t115;
    unsigned int t116;
    char *t117;
    char *t118;

LAB0:    t1 = (t0 + 7624U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(106, ng0);
    t2 = (t0 + 8552);
    *((int *)t2) = 1;
    t3 = (t0 + 7656);
    *((char **)t3) = t2;
    *((char **)t1) = &&LAB4;

LAB1:    return;
LAB4:    xsi_set_current_line(107, ng0);

LAB5:    xsi_set_current_line(108, ng0);
    t4 = (t0 + 1208U);
    t5 = *((char **)t4);
    t4 = (t5 + 4);
    t6 = *((unsigned int *)t4);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 != 0);
    if (t10 > 0)
        goto LAB6;

LAB7:    xsi_set_current_line(110, ng0);
    t2 = (t0 + 2008U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t3 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t3);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB9;

LAB10:    if (*((unsigned int *)t2) != 0)
        goto LAB11;

LAB12:    t5 = (t13 + 4);
    t14 = *((unsigned int *)t13);
    t15 = *((unsigned int *)t5);
    t16 = (t14 || t15);
    if (t16 > 0)
        goto LAB13;

LAB14:    memcpy(t44, t13, 8);

LAB15:    t76 = (t44 + 4);
    t77 = *((unsigned int *)t76);
    t78 = (~(t77));
    t79 = *((unsigned int *)t44);
    t80 = (t79 & t78);
    t81 = (t80 != 0);
    if (t81 > 0)
        goto LAB29;

LAB30:    xsi_set_current_line(112, ng0);
    t2 = (t0 + 4488);
    t3 = (t2 + 56U);
    t4 = *((char **)t3);
    memset(t13, 0, 8);
    t5 = (t4 + 4);
    t6 = *((unsigned int *)t5);
    t7 = (~(t6));
    t8 = *((unsigned int *)t4);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB32;

LAB33:    if (*((unsigned int *)t5) != 0)
        goto LAB34;

LAB35:    t12 = (t13 + 4);
    t14 = *((unsigned int *)t13);
    t15 = *((unsigned int *)t12);
    t16 = (t14 || t15);
    if (t16 > 0)
        goto LAB36;

LAB37:    memcpy(t36, t13, 8);

LAB38:    memset(t44, 0, 8);
    t49 = (t36 + 4);
    t61 = *((unsigned int *)t49);
    t62 = (~(t61));
    t63 = *((unsigned int *)t36);
    t64 = (t63 & t62);
    t65 = (t64 & 1U);
    if (t65 != 0)
        goto LAB46;

LAB47:    if (*((unsigned int *)t49) != 0)
        goto LAB48;

LAB49:    t58 = (t44 + 4);
    t66 = *((unsigned int *)t44);
    t67 = *((unsigned int *)t58);
    t70 = (t66 || t67);
    if (t70 > 0)
        goto LAB50;

LAB51:    memcpy(t85, t44, 8);

LAB52:    t111 = (t85 + 4);
    t112 = *((unsigned int *)t111);
    t113 = (~(t112));
    t114 = *((unsigned int *)t85);
    t115 = (t114 & t113);
    t116 = (t115 != 0);
    if (t116 > 0)
        goto LAB60;

LAB61:
LAB62:
LAB31:
LAB8:    goto LAB2;

LAB6:    xsi_set_current_line(109, ng0);
    t11 = ((char*)((ng2)));
    t12 = (t0 + 4488);
    xsi_vlogvar_wait_assign_value(t12, t11, 0, 0, 1, 0LL);
    goto LAB8;

LAB9:    *((unsigned int *)t13) = 1;
    goto LAB12;

LAB11:    t4 = (t13 + 4);
    *((unsigned int *)t13) = 1;
    *((unsigned int *)t4) = 1;
    goto LAB12;

LAB13:    t11 = (t0 + 4488);
    t12 = (t11 + 56U);
    t18 = *((char **)t12);
    memset(t17, 0, 8);
    t19 = (t18 + 4);
    t20 = *((unsigned int *)t19);
    t21 = (~(t20));
    t22 = *((unsigned int *)t18);
    t23 = (t22 & t21);
    t24 = (t23 & 1U);
    if (t24 != 0)
        goto LAB19;

LAB17:    if (*((unsigned int *)t19) == 0)
        goto LAB16;

LAB18:    t25 = (t17 + 4);
    *((unsigned int *)t17) = 1;
    *((unsigned int *)t25) = 1;

LAB19:    t26 = (t17 + 4);
    t27 = (t18 + 4);
    t28 = *((unsigned int *)t18);
    t29 = (~(t28));
    *((unsigned int *)t17) = t29;
    *((unsigned int *)t26) = 0;
    if (*((unsigned int *)t27) != 0)
        goto LAB21;

LAB20:    t34 = *((unsigned int *)t17);
    *((unsigned int *)t17) = (t34 & 1U);
    t35 = *((unsigned int *)t26);
    *((unsigned int *)t26) = (t35 & 1U);
    memset(t36, 0, 8);
    t37 = (t17 + 4);
    t38 = *((unsigned int *)t37);
    t39 = (~(t38));
    t40 = *((unsigned int *)t17);
    t41 = (t40 & t39);
    t42 = (t41 & 1U);
    if (t42 != 0)
        goto LAB22;

LAB23:    if (*((unsigned int *)t37) != 0)
        goto LAB24;

LAB25:    t45 = *((unsigned int *)t13);
    t46 = *((unsigned int *)t36);
    t47 = (t45 & t46);
    *((unsigned int *)t44) = t47;
    t48 = (t13 + 4);
    t49 = (t36 + 4);
    t50 = (t44 + 4);
    t51 = *((unsigned int *)t48);
    t52 = *((unsigned int *)t49);
    t53 = (t51 | t52);
    *((unsigned int *)t50) = t53;
    t54 = *((unsigned int *)t50);
    t55 = (t54 != 0);
    if (t55 == 1)
        goto LAB26;

LAB27:
LAB28:    goto LAB15;

LAB16:    *((unsigned int *)t17) = 1;
    goto LAB19;

LAB21:    t30 = *((unsigned int *)t17);
    t31 = *((unsigned int *)t27);
    *((unsigned int *)t17) = (t30 | t31);
    t32 = *((unsigned int *)t26);
    t33 = *((unsigned int *)t27);
    *((unsigned int *)t26) = (t32 | t33);
    goto LAB20;

LAB22:    *((unsigned int *)t36) = 1;
    goto LAB25;

LAB24:    t43 = (t36 + 4);
    *((unsigned int *)t36) = 1;
    *((unsigned int *)t43) = 1;
    goto LAB25;

LAB26:    t56 = *((unsigned int *)t44);
    t57 = *((unsigned int *)t50);
    *((unsigned int *)t44) = (t56 | t57);
    t58 = (t13 + 4);
    t59 = (t36 + 4);
    t60 = *((unsigned int *)t13);
    t61 = (~(t60));
    t62 = *((unsigned int *)t58);
    t63 = (~(t62));
    t64 = *((unsigned int *)t36);
    t65 = (~(t64));
    t66 = *((unsigned int *)t59);
    t67 = (~(t66));
    t68 = (t61 & t63);
    t69 = (t65 & t67);
    t70 = (~(t68));
    t71 = (~(t69));
    t72 = *((unsigned int *)t50);
    *((unsigned int *)t50) = (t72 & t70);
    t73 = *((unsigned int *)t50);
    *((unsigned int *)t50) = (t73 & t71);
    t74 = *((unsigned int *)t44);
    *((unsigned int *)t44) = (t74 & t70);
    t75 = *((unsigned int *)t44);
    *((unsigned int *)t44) = (t75 & t71);
    goto LAB28;

LAB29:    xsi_set_current_line(111, ng0);
    t82 = ((char*)((ng1)));
    t83 = (t0 + 4488);
    xsi_vlogvar_wait_assign_value(t83, t82, 0, 0, 1, 0LL);
    goto LAB31;

LAB32:    *((unsigned int *)t13) = 1;
    goto LAB35;

LAB34:    t11 = (t13 + 4);
    *((unsigned int *)t13) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB35;

LAB36:    t18 = (t0 + 2808U);
    t19 = *((char **)t18);
    memset(t17, 0, 8);
    t18 = (t19 + 4);
    t20 = *((unsigned int *)t18);
    t21 = (~(t20));
    t22 = *((unsigned int *)t19);
    t23 = (t22 & t21);
    t24 = (t23 & 1U);
    if (t24 != 0)
        goto LAB39;

LAB40:    if (*((unsigned int *)t18) != 0)
        goto LAB41;

LAB42:    t28 = *((unsigned int *)t13);
    t29 = *((unsigned int *)t17);
    t30 = (t28 & t29);
    *((unsigned int *)t36) = t30;
    t26 = (t13 + 4);
    t27 = (t17 + 4);
    t37 = (t36 + 4);
    t31 = *((unsigned int *)t26);
    t32 = *((unsigned int *)t27);
    t33 = (t31 | t32);
    *((unsigned int *)t37) = t33;
    t34 = *((unsigned int *)t37);
    t35 = (t34 != 0);
    if (t35 == 1)
        goto LAB43;

LAB44:
LAB45:    goto LAB38;

LAB39:    *((unsigned int *)t17) = 1;
    goto LAB42;

LAB41:    t25 = (t17 + 4);
    *((unsigned int *)t17) = 1;
    *((unsigned int *)t25) = 1;
    goto LAB42;

LAB43:    t38 = *((unsigned int *)t36);
    t39 = *((unsigned int *)t37);
    *((unsigned int *)t36) = (t38 | t39);
    t43 = (t13 + 4);
    t48 = (t17 + 4);
    t40 = *((unsigned int *)t13);
    t41 = (~(t40));
    t42 = *((unsigned int *)t43);
    t45 = (~(t42));
    t46 = *((unsigned int *)t17);
    t47 = (~(t46));
    t51 = *((unsigned int *)t48);
    t52 = (~(t51));
    t68 = (t41 & t45);
    t69 = (t47 & t52);
    t53 = (~(t68));
    t54 = (~(t69));
    t55 = *((unsigned int *)t37);
    *((unsigned int *)t37) = (t55 & t53);
    t56 = *((unsigned int *)t37);
    *((unsigned int *)t37) = (t56 & t54);
    t57 = *((unsigned int *)t36);
    *((unsigned int *)t36) = (t57 & t53);
    t60 = *((unsigned int *)t36);
    *((unsigned int *)t36) = (t60 & t54);
    goto LAB45;

LAB46:    *((unsigned int *)t44) = 1;
    goto LAB49;

LAB48:    t50 = (t44 + 4);
    *((unsigned int *)t44) = 1;
    *((unsigned int *)t50) = 1;
    goto LAB49;

LAB50:    t59 = (t0 + 2168U);
    t76 = *((char **)t59);
    memset(t84, 0, 8);
    t59 = (t76 + 4);
    t71 = *((unsigned int *)t59);
    t72 = (~(t71));
    t73 = *((unsigned int *)t76);
    t74 = (t73 & t72);
    t75 = (t74 & 1U);
    if (t75 != 0)
        goto LAB53;

LAB54:    if (*((unsigned int *)t59) != 0)
        goto LAB55;

LAB56:    t77 = *((unsigned int *)t44);
    t78 = *((unsigned int *)t84);
    t79 = (t77 & t78);
    *((unsigned int *)t85) = t79;
    t83 = (t44 + 4);
    t86 = (t84 + 4);
    t87 = (t85 + 4);
    t80 = *((unsigned int *)t83);
    t81 = *((unsigned int *)t86);
    t88 = (t80 | t81);
    *((unsigned int *)t87) = t88;
    t89 = *((unsigned int *)t87);
    t90 = (t89 != 0);
    if (t90 == 1)
        goto LAB57;

LAB58:
LAB59:    goto LAB52;

LAB53:    *((unsigned int *)t84) = 1;
    goto LAB56;

LAB55:    t82 = (t84 + 4);
    *((unsigned int *)t84) = 1;
    *((unsigned int *)t82) = 1;
    goto LAB56;

LAB57:    t91 = *((unsigned int *)t85);
    t92 = *((unsigned int *)t87);
    *((unsigned int *)t85) = (t91 | t92);
    t93 = (t44 + 4);
    t94 = (t84 + 4);
    t95 = *((unsigned int *)t44);
    t96 = (~(t95));
    t97 = *((unsigned int *)t93);
    t98 = (~(t97));
    t99 = *((unsigned int *)t84);
    t100 = (~(t99));
    t101 = *((unsigned int *)t94);
    t102 = (~(t101));
    t103 = (t96 & t98);
    t104 = (t100 & t102);
    t105 = (~(t103));
    t106 = (~(t104));
    t107 = *((unsigned int *)t87);
    *((unsigned int *)t87) = (t107 & t105);
    t108 = *((unsigned int *)t87);
    *((unsigned int *)t87) = (t108 & t106);
    t109 = *((unsigned int *)t85);
    *((unsigned int *)t85) = (t109 & t105);
    t110 = *((unsigned int *)t85);
    *((unsigned int *)t85) = (t110 & t106);
    goto LAB59;

LAB60:    xsi_set_current_line(113, ng0);
    t117 = ((char*)((ng2)));
    t118 = (t0 + 4488);
    xsi_vlogvar_wait_assign_value(t118, t117, 0, 0, 1, 0LL);
    goto LAB62;

}

static void Always_117_8(char *t0)
{
    char t13[8];
    char t14[8];
    char t15[8];
    char t20[8];
    char t29[8];
    char t37[8];
    char t79[8];
    char t83[8];
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
    unsigned int t16;
    unsigned int t17;
    unsigned int t18;
    unsigned int t19;
    char *t21;
    char *t22;
    unsigned int t23;
    unsigned int t24;
    unsigned int t25;
    unsigned int t26;
    unsigned int t27;
    char *t28;
    char *t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    unsigned int t34;
    unsigned int t35;
    char *t36;
    unsigned int t38;
    unsigned int t39;
    unsigned int t40;
    char *t41;
    char *t42;
    char *t43;
    unsigned int t44;
    unsigned int t45;
    unsigned int t46;
    unsigned int t47;
    unsigned int t48;
    unsigned int t49;
    unsigned int t50;
    char *t51;
    char *t52;
    unsigned int t53;
    unsigned int t54;
    unsigned int t55;
    int t56;
    unsigned int t57;
    unsigned int t58;
    unsigned int t59;
    int t60;
    unsigned int t61;
    unsigned int t62;
    unsigned int t63;
    unsigned int t64;
    char *t65;
    unsigned int t66;
    unsigned int t67;
    unsigned int t68;
    unsigned int t69;
    unsigned int t70;
    char *t71;
    char *t72;
    unsigned int t73;
    unsigned int t74;
    unsigned int t75;
    char *t76;
    char *t77;
    char *t78;
    char *t80;
    char *t81;
    char *t82;
    char *t84;
    char *t85;
    char *t86;
    unsigned int t87;
    unsigned int t88;
    unsigned int t89;
    unsigned int t90;
    unsigned int t91;
    unsigned int t92;
    unsigned int t93;
    unsigned int t94;
    unsigned int t95;
    unsigned int t96;
    char *t97;
    char *t98;
    char *t99;
    char *t100;

LAB0:    t1 = (t0 + 7872U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(117, ng0);
    t2 = (t0 + 8568);
    *((int *)t2) = 1;
    t3 = (t0 + 7904);
    *((char **)t3) = t2;
    *((char **)t1) = &&LAB4;

LAB1:    return;
LAB4:    xsi_set_current_line(118, ng0);

LAB5:    xsi_set_current_line(119, ng0);
    t4 = (t0 + 1208U);
    t5 = *((char **)t4);
    t4 = (t5 + 4);
    t6 = *((unsigned int *)t4);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 != 0);
    if (t10 > 0)
        goto LAB6;

LAB7:    xsi_set_current_line(122, ng0);
    t2 = (t0 + 4088U);
    t3 = *((char **)t2);
    memset(t15, 0, 8);
    t2 = (t3 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t3);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB9;

LAB10:    if (*((unsigned int *)t2) != 0)
        goto LAB11;

LAB12:    t5 = (t15 + 4);
    t16 = *((unsigned int *)t15);
    t17 = (!(t16));
    t18 = *((unsigned int *)t5);
    t19 = (t17 || t18);
    if (t19 > 0)
        goto LAB13;

LAB14:    memcpy(t37, t15, 8);

LAB15:    memset(t14, 0, 8);
    t65 = (t37 + 4);
    t66 = *((unsigned int *)t65);
    t67 = (~(t66));
    t68 = *((unsigned int *)t37);
    t69 = (t68 & t67);
    t70 = (t69 & 1U);
    if (t70 != 0)
        goto LAB27;

LAB28:    if (*((unsigned int *)t65) != 0)
        goto LAB29;

LAB30:    t72 = (t14 + 4);
    t73 = *((unsigned int *)t14);
    t74 = *((unsigned int *)t72);
    t75 = (t73 || t74);
    if (t75 > 0)
        goto LAB31;

LAB32:    t93 = *((unsigned int *)t14);
    t94 = (~(t93));
    t95 = *((unsigned int *)t72);
    t96 = (t94 || t95);
    if (t96 > 0)
        goto LAB33;

LAB34:    if (*((unsigned int *)t72) > 0)
        goto LAB35;

LAB36:    if (*((unsigned int *)t14) > 0)
        goto LAB37;

LAB38:    memcpy(t13, t99, 8);

LAB39:    t100 = (t0 + 4648);
    xsi_vlogvar_wait_assign_value(t100, t13, 0, 0, 1, 0LL);

LAB8:    goto LAB2;

LAB6:    xsi_set_current_line(120, ng0);
    t11 = ((char*)((ng2)));
    t12 = (t0 + 4648);
    xsi_vlogvar_wait_assign_value(t12, t11, 0, 0, 1, 0LL);
    goto LAB8;

LAB9:    *((unsigned int *)t15) = 1;
    goto LAB12;

LAB11:    t4 = (t15 + 4);
    *((unsigned int *)t15) = 1;
    *((unsigned int *)t4) = 1;
    goto LAB12;

LAB13:    t11 = (t0 + 4488);
    t12 = (t11 + 56U);
    t21 = *((char **)t12);
    memset(t20, 0, 8);
    t22 = (t21 + 4);
    t23 = *((unsigned int *)t22);
    t24 = (~(t23));
    t25 = *((unsigned int *)t21);
    t26 = (t25 & t24);
    t27 = (t26 & 1U);
    if (t27 != 0)
        goto LAB19;

LAB17:    if (*((unsigned int *)t22) == 0)
        goto LAB16;

LAB18:    t28 = (t20 + 4);
    *((unsigned int *)t20) = 1;
    *((unsigned int *)t28) = 1;

LAB19:    memset(t29, 0, 8);
    t30 = (t20 + 4);
    t31 = *((unsigned int *)t30);
    t32 = (~(t31));
    t33 = *((unsigned int *)t20);
    t34 = (t33 & t32);
    t35 = (t34 & 1U);
    if (t35 != 0)
        goto LAB20;

LAB21:    if (*((unsigned int *)t30) != 0)
        goto LAB22;

LAB23:    t38 = *((unsigned int *)t15);
    t39 = *((unsigned int *)t29);
    t40 = (t38 | t39);
    *((unsigned int *)t37) = t40;
    t41 = (t15 + 4);
    t42 = (t29 + 4);
    t43 = (t37 + 4);
    t44 = *((unsigned int *)t41);
    t45 = *((unsigned int *)t42);
    t46 = (t44 | t45);
    *((unsigned int *)t43) = t46;
    t47 = *((unsigned int *)t43);
    t48 = (t47 != 0);
    if (t48 == 1)
        goto LAB24;

LAB25:
LAB26:    goto LAB15;

LAB16:    *((unsigned int *)t20) = 1;
    goto LAB19;

LAB20:    *((unsigned int *)t29) = 1;
    goto LAB23;

LAB22:    t36 = (t29 + 4);
    *((unsigned int *)t29) = 1;
    *((unsigned int *)t36) = 1;
    goto LAB23;

LAB24:    t49 = *((unsigned int *)t37);
    t50 = *((unsigned int *)t43);
    *((unsigned int *)t37) = (t49 | t50);
    t51 = (t15 + 4);
    t52 = (t29 + 4);
    t53 = *((unsigned int *)t51);
    t54 = (~(t53));
    t55 = *((unsigned int *)t15);
    t56 = (t55 & t54);
    t57 = *((unsigned int *)t52);
    t58 = (~(t57));
    t59 = *((unsigned int *)t29);
    t60 = (t59 & t58);
    t61 = (~(t56));
    t62 = (~(t60));
    t63 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t63 & t61);
    t64 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t64 & t62);
    goto LAB26;

LAB27:    *((unsigned int *)t14) = 1;
    goto LAB30;

LAB29:    t71 = (t14 + 4);
    *((unsigned int *)t14) = 1;
    *((unsigned int *)t71) = 1;
    goto LAB30;

LAB31:    t76 = (t0 + 4968);
    t77 = (t76 + 56U);
    t78 = *((char **)t77);
    t80 = (t0 + 4968);
    t81 = (t80 + 72U);
    t82 = *((char **)t81);
    t84 = (t0 + 3608U);
    t85 = *((char **)t84);
    memset(t83, 0, 8);
    t84 = (t83 + 4);
    t86 = (t85 + 4);
    t87 = *((unsigned int *)t85);
    t88 = (t87 >> 0);
    *((unsigned int *)t83) = t88;
    t89 = *((unsigned int *)t86);
    t90 = (t89 >> 0);
    *((unsigned int *)t84) = t90;
    t91 = *((unsigned int *)t83);
    *((unsigned int *)t83) = (t91 & 127U);
    t92 = *((unsigned int *)t84);
    *((unsigned int *)t84) = (t92 & 127U);
    xsi_vlog_generic_get_index_select_value(t79, 1, t78, t82, 2, t83, 7, 2);
    goto LAB32;

LAB33:    t97 = (t0 + 4648);
    t98 = (t97 + 56U);
    t99 = *((char **)t98);
    goto LAB34;

LAB35:    xsi_vlog_unsigned_bit_combine(t13, 1, t79, 1, t99, 1);
    goto LAB39;

LAB37:    memcpy(t13, t79, 8);
    goto LAB39;

}

static void Always_126_9(char *t0)
{
    char t13[8];
    char t15[8];
    char t24[8];
    char t35[8];
    char t43[8];
    char t83[8];
    char t97[8];
    char t108[8];
    char t109[8];
    char t110[8];
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
    unsigned int t14;
    unsigned int t16;
    unsigned int t17;
    unsigned int t18;
    unsigned int t19;
    unsigned int t20;
    unsigned int t21;
    unsigned int t22;
    unsigned int t23;
    char *t25;
    char *t26;
    char *t27;
    char *t28;
    unsigned int t29;
    unsigned int t30;
    unsigned int t31;
    unsigned int t32;
    unsigned int t33;
    char *t34;
    char *t36;
    unsigned int t37;
    unsigned int t38;
    unsigned int t39;
    unsigned int t40;
    unsigned int t41;
    char *t42;
    unsigned int t44;
    unsigned int t45;
    unsigned int t46;
    char *t47;
    char *t48;
    char *t49;
    unsigned int t50;
    unsigned int t51;
    unsigned int t52;
    unsigned int t53;
    unsigned int t54;
    unsigned int t55;
    unsigned int t56;
    char *t57;
    char *t58;
    unsigned int t59;
    unsigned int t60;
    unsigned int t61;
    unsigned int t62;
    unsigned int t63;
    unsigned int t64;
    unsigned int t65;
    unsigned int t66;
    int t67;
    int t68;
    unsigned int t69;
    unsigned int t70;
    unsigned int t71;
    unsigned int t72;
    unsigned int t73;
    unsigned int t74;
    char *t75;
    unsigned int t76;
    unsigned int t77;
    unsigned int t78;
    unsigned int t79;
    unsigned int t80;
    char *t81;
    char *t82;
    char *t84;
    unsigned int t85;
    unsigned int t86;
    unsigned int t87;
    unsigned int t88;
    unsigned int t89;
    unsigned int t90;
    char *t91;
    unsigned int t92;
    unsigned int t93;
    unsigned int t94;
    unsigned int t95;
    unsigned int t96;
    char *t98;
    char *t99;
    char *t100;
    unsigned int t101;
    unsigned int t102;
    unsigned int t103;
    unsigned int t104;
    unsigned int t105;
    unsigned int t106;
    char *t107;
    char *t111;
    char *t112;
    char *t113;
    char *t114;
    char *t115;
    char *t116;
    unsigned int t117;
    int t118;
    char *t119;
    unsigned int t120;
    int t121;
    int t122;
    char *t123;
    unsigned int t124;
    int t125;
    int t126;
    unsigned int t127;
    int t128;
    unsigned int t129;
    unsigned int t130;
    int t131;
    int t132;

LAB0:    t1 = (t0 + 8120U);
    t2 = *((char **)t1);
    if (t2 == 0)
        goto LAB2;

LAB3:    goto *t2;

LAB2:    xsi_set_current_line(126, ng0);
    t2 = (t0 + 8584);
    *((int *)t2) = 1;
    t3 = (t0 + 8152);
    *((char **)t3) = t2;
    *((char **)t1) = &&LAB4;

LAB1:    return;
LAB4:    xsi_set_current_line(127, ng0);

LAB5:    xsi_set_current_line(128, ng0);
    t4 = (t0 + 1208U);
    t5 = *((char **)t4);
    t4 = (t5 + 4);
    t6 = *((unsigned int *)t4);
    t7 = (~(t6));
    t8 = *((unsigned int *)t5);
    t9 = (t8 & t7);
    t10 = (t9 != 0);
    if (t10 > 0)
        goto LAB6;

LAB7:    xsi_set_current_line(131, ng0);
    t2 = (t0 + 1368U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 0);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 0);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    memset(t15, 0, 8);
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 & 1U);
    if (t20 != 0)
        goto LAB9;

LAB10:    if (*((unsigned int *)t5) != 0)
        goto LAB11;

LAB12:    t12 = (t15 + 4);
    t21 = *((unsigned int *)t15);
    t22 = *((unsigned int *)t12);
    t23 = (t21 || t22);
    if (t23 > 0)
        goto LAB13;

LAB14:    memcpy(t43, t15, 8);

LAB15:    t75 = (t43 + 4);
    t76 = *((unsigned int *)t75);
    t77 = (~(t76));
    t78 = *((unsigned int *)t43);
    t79 = (t78 & t77);
    t80 = (t79 != 0);
    if (t80 > 0)
        goto LAB27;

LAB28:    xsi_set_current_line(142, ng0);
    t2 = (t0 + 1368U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 1);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 1);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    memset(t15, 0, 8);
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 & 1U);
    if (t20 != 0)
        goto LAB51;

LAB52:    if (*((unsigned int *)t5) != 0)
        goto LAB53;

LAB54:    t12 = (t15 + 4);
    t21 = *((unsigned int *)t15);
    t22 = *((unsigned int *)t12);
    t23 = (t21 || t22);
    if (t23 > 0)
        goto LAB55;

LAB56:    memcpy(t43, t15, 8);

LAB57:    t75 = (t43 + 4);
    t76 = *((unsigned int *)t75);
    t77 = (~(t76));
    t78 = *((unsigned int *)t43);
    t79 = (t78 & t77);
    t80 = (t79 != 0);
    if (t80 > 0)
        goto LAB69;

LAB70:    xsi_set_current_line(153, ng0);
    t2 = (t0 + 1368U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 2);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 2);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    memset(t15, 0, 8);
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 & 1U);
    if (t20 != 0)
        goto LAB93;

LAB94:    if (*((unsigned int *)t5) != 0)
        goto LAB95;

LAB96:    t12 = (t15 + 4);
    t21 = *((unsigned int *)t15);
    t22 = *((unsigned int *)t12);
    t23 = (t21 || t22);
    if (t23 > 0)
        goto LAB97;

LAB98:    memcpy(t43, t15, 8);

LAB99:    t75 = (t43 + 4);
    t76 = *((unsigned int *)t75);
    t77 = (~(t76));
    t78 = *((unsigned int *)t43);
    t79 = (t78 & t77);
    t80 = (t79 != 0);
    if (t80 > 0)
        goto LAB111;

LAB112:    xsi_set_current_line(164, ng0);
    t2 = (t0 + 1368U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 3);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 3);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    memset(t15, 0, 8);
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 & 1U);
    if (t20 != 0)
        goto LAB135;

LAB136:    if (*((unsigned int *)t5) != 0)
        goto LAB137;

LAB138:    t12 = (t15 + 4);
    t21 = *((unsigned int *)t15);
    t22 = *((unsigned int *)t12);
    t23 = (t21 || t22);
    if (t23 > 0)
        goto LAB139;

LAB140:    memcpy(t43, t15, 8);

LAB141:    t75 = (t43 + 4);
    t76 = *((unsigned int *)t75);
    t77 = (~(t76));
    t78 = *((unsigned int *)t43);
    t79 = (t78 & t77);
    t80 = (t79 != 0);
    if (t80 > 0)
        goto LAB153;

LAB154:    xsi_set_current_line(234, ng0);
    t2 = (t0 + 3928U);
    t3 = *((char **)t2);
    memset(t15, 0, 8);
    t2 = (t3 + 4);
    t6 = *((unsigned int *)t2);
    t7 = (~(t6));
    t8 = *((unsigned int *)t3);
    t9 = (t8 & t7);
    t10 = (t9 & 1U);
    if (t10 != 0)
        goto LAB177;

LAB178:    if (*((unsigned int *)t2) != 0)
        goto LAB179;

LAB180:    t5 = (t15 + 4);
    t14 = *((unsigned int *)t15);
    t16 = *((unsigned int *)t5);
    t17 = (t14 || t16);
    if (t17 > 0)
        goto LAB181;

LAB182:    t18 = *((unsigned int *)t15);
    t19 = (~(t18));
    t20 = *((unsigned int *)t5);
    t21 = (t19 || t20);
    if (t21 > 0)
        goto LAB183;

LAB184:    if (*((unsigned int *)t5) > 0)
        goto LAB185;

LAB186:    if (*((unsigned int *)t15) > 0)
        goto LAB187;

LAB188:    memcpy(t13, t24, 8);

LAB189:    t48 = (t0 + 4968);
    t49 = (t0 + 4968);
    t57 = (t49 + 72U);
    t58 = *((char **)t57);
    t75 = (t0 + 3768U);
    t81 = *((char **)t75);
    memset(t83, 0, 8);
    t75 = (t83 + 4);
    t82 = (t81 + 4);
    t33 = *((unsigned int *)t81);
    t37 = (t33 >> 0);
    *((unsigned int *)t83) = t37;
    t38 = *((unsigned int *)t82);
    t39 = (t38 >> 0);
    *((unsigned int *)t75) = t39;
    t40 = *((unsigned int *)t83);
    *((unsigned int *)t83) = (t40 & 127U);
    t41 = *((unsigned int *)t75);
    *((unsigned int *)t75) = (t41 & 127U);
    xsi_vlog_generic_convert_bit_index(t43, t58, 2, t83, 7, 2);
    t84 = (t43 + 4);
    t44 = *((unsigned int *)t84);
    t67 = (!(t44));
    if (t67 == 1)
        goto LAB190;

LAB191:
LAB155:
LAB113:
LAB71:
LAB29:
LAB8:    goto LAB2;

LAB6:    xsi_set_current_line(129, ng0);
    t11 = ((char*)((ng4)));
    t12 = (t0 + 4968);
    xsi_vlogvar_wait_assign_value(t12, t11, 0, 0, 128, 0LL);
    goto LAB8;

LAB9:    *((unsigned int *)t15) = 1;
    goto LAB12;

LAB11:    t11 = (t15 + 4);
    *((unsigned int *)t15) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB12;

LAB13:    t25 = (t0 + 4488);
    t26 = (t25 + 56U);
    t27 = *((char **)t26);
    memset(t24, 0, 8);
    t28 = (t27 + 4);
    t29 = *((unsigned int *)t28);
    t30 = (~(t29));
    t31 = *((unsigned int *)t27);
    t32 = (t31 & t30);
    t33 = (t32 & 1U);
    if (t33 != 0)
        goto LAB19;

LAB17:    if (*((unsigned int *)t28) == 0)
        goto LAB16;

LAB18:    t34 = (t24 + 4);
    *((unsigned int *)t24) = 1;
    *((unsigned int *)t34) = 1;

LAB19:    memset(t35, 0, 8);
    t36 = (t24 + 4);
    t37 = *((unsigned int *)t36);
    t38 = (~(t37));
    t39 = *((unsigned int *)t24);
    t40 = (t39 & t38);
    t41 = (t40 & 1U);
    if (t41 != 0)
        goto LAB20;

LAB21:    if (*((unsigned int *)t36) != 0)
        goto LAB22;

LAB23:    t44 = *((unsigned int *)t15);
    t45 = *((unsigned int *)t35);
    t46 = (t44 & t45);
    *((unsigned int *)t43) = t46;
    t47 = (t15 + 4);
    t48 = (t35 + 4);
    t49 = (t43 + 4);
    t50 = *((unsigned int *)t47);
    t51 = *((unsigned int *)t48);
    t52 = (t50 | t51);
    *((unsigned int *)t49) = t52;
    t53 = *((unsigned int *)t49);
    t54 = (t53 != 0);
    if (t54 == 1)
        goto LAB24;

LAB25:
LAB26:    goto LAB15;

LAB16:    *((unsigned int *)t24) = 1;
    goto LAB19;

LAB20:    *((unsigned int *)t35) = 1;
    goto LAB23;

LAB22:    t42 = (t35 + 4);
    *((unsigned int *)t35) = 1;
    *((unsigned int *)t42) = 1;
    goto LAB23;

LAB24:    t55 = *((unsigned int *)t43);
    t56 = *((unsigned int *)t49);
    *((unsigned int *)t43) = (t55 | t56);
    t57 = (t15 + 4);
    t58 = (t35 + 4);
    t59 = *((unsigned int *)t15);
    t60 = (~(t59));
    t61 = *((unsigned int *)t57);
    t62 = (~(t61));
    t63 = *((unsigned int *)t35);
    t64 = (~(t63));
    t65 = *((unsigned int *)t58);
    t66 = (~(t65));
    t67 = (t60 & t62);
    t68 = (t64 & t66);
    t69 = (~(t67));
    t70 = (~(t68));
    t71 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t71 & t69);
    t72 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t72 & t70);
    t73 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t73 & t69);
    t74 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t74 & t70);
    goto LAB26;

LAB27:    xsi_set_current_line(132, ng0);

LAB30:    xsi_set_current_line(133, ng0);
    t81 = (t0 + 1528U);
    t82 = *((char **)t81);
    memset(t83, 0, 8);
    t81 = (t83 + 4);
    t84 = (t82 + 4);
    t85 = *((unsigned int *)t82);
    t86 = (t85 >> 3);
    t87 = (t86 & 1);
    *((unsigned int *)t83) = t87;
    t88 = *((unsigned int *)t84);
    t89 = (t88 >> 3);
    t90 = (t89 & 1);
    *((unsigned int *)t81) = t90;
    t91 = (t83 + 4);
    t92 = *((unsigned int *)t91);
    t93 = (~(t92));
    t94 = *((unsigned int *)t83);
    t95 = (t94 & t93);
    t96 = (t95 != 0);
    if (t96 > 0)
        goto LAB31;

LAB32:
LAB33:    xsi_set_current_line(135, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 2);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 2);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB36;

LAB37:
LAB38:    xsi_set_current_line(137, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 1);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 1);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB41;

LAB42:
LAB43:    xsi_set_current_line(139, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 0);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 0);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB46;

LAB47:
LAB48:    goto LAB29;

LAB31:    xsi_set_current_line(134, ng0);
    t98 = (t0 + 2968U);
    t99 = *((char **)t98);
    memset(t97, 0, 8);
    t98 = (t97 + 4);
    t100 = (t99 + 4);
    t101 = *((unsigned int *)t99);
    t102 = (t101 >> 24);
    *((unsigned int *)t97) = t102;
    t103 = *((unsigned int *)t100);
    t104 = (t103 >> 24);
    *((unsigned int *)t98) = t104;
    t105 = *((unsigned int *)t97);
    *((unsigned int *)t97) = (t105 & 255U);
    t106 = *((unsigned int *)t98);
    *((unsigned int *)t98) = (t106 & 255U);
    t107 = (t0 + 4968);
    t111 = (t0 + 4968);
    t112 = (t111 + 72U);
    t113 = *((char **)t112);
    t114 = ((char*)((ng5)));
    t115 = ((char*)((ng6)));
    xsi_vlog_convert_partindices(t108, t109, t110, ((int*)(t113)), 2, t114, 32, 1, t115, 32, 1);
    t116 = (t108 + 4);
    t117 = *((unsigned int *)t116);
    t118 = (!(t117));
    t119 = (t109 + 4);
    t120 = *((unsigned int *)t119);
    t121 = (!(t120));
    t122 = (t118 && t121);
    t123 = (t110 + 4);
    t124 = *((unsigned int *)t123);
    t125 = (!(t124));
    t126 = (t122 && t125);
    if (t126 == 1)
        goto LAB34;

LAB35:    goto LAB33;

LAB34:    t127 = *((unsigned int *)t110);
    t128 = (t127 + 0);
    t129 = *((unsigned int *)t108);
    t130 = *((unsigned int *)t109);
    t131 = (t129 - t130);
    t132 = (t131 + 1);
    xsi_vlogvar_wait_assign_value(t107, t97, t128, *((unsigned int *)t109), t132, 0LL);
    goto LAB35;

LAB36:    xsi_set_current_line(136, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 16);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 16);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng7)));
    t42 = ((char*)((ng8)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB39;

LAB40:    goto LAB38;

LAB39:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB40;

LAB41:    xsi_set_current_line(138, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 8);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 8);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng9)));
    t42 = ((char*)((ng10)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB44;

LAB45:    goto LAB43;

LAB44:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB45;

LAB46:    xsi_set_current_line(140, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 0);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 0);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng11)));
    t42 = ((char*)((ng12)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB49;

LAB50:    goto LAB48;

LAB49:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB50;

LAB51:    *((unsigned int *)t15) = 1;
    goto LAB54;

LAB53:    t11 = (t15 + 4);
    *((unsigned int *)t15) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB54;

LAB55:    t25 = (t0 + 4488);
    t26 = (t25 + 56U);
    t27 = *((char **)t26);
    memset(t24, 0, 8);
    t28 = (t27 + 4);
    t29 = *((unsigned int *)t28);
    t30 = (~(t29));
    t31 = *((unsigned int *)t27);
    t32 = (t31 & t30);
    t33 = (t32 & 1U);
    if (t33 != 0)
        goto LAB61;

LAB59:    if (*((unsigned int *)t28) == 0)
        goto LAB58;

LAB60:    t34 = (t24 + 4);
    *((unsigned int *)t24) = 1;
    *((unsigned int *)t34) = 1;

LAB61:    memset(t35, 0, 8);
    t36 = (t24 + 4);
    t37 = *((unsigned int *)t36);
    t38 = (~(t37));
    t39 = *((unsigned int *)t24);
    t40 = (t39 & t38);
    t41 = (t40 & 1U);
    if (t41 != 0)
        goto LAB62;

LAB63:    if (*((unsigned int *)t36) != 0)
        goto LAB64;

LAB65:    t44 = *((unsigned int *)t15);
    t45 = *((unsigned int *)t35);
    t46 = (t44 & t45);
    *((unsigned int *)t43) = t46;
    t47 = (t15 + 4);
    t48 = (t35 + 4);
    t49 = (t43 + 4);
    t50 = *((unsigned int *)t47);
    t51 = *((unsigned int *)t48);
    t52 = (t50 | t51);
    *((unsigned int *)t49) = t52;
    t53 = *((unsigned int *)t49);
    t54 = (t53 != 0);
    if (t54 == 1)
        goto LAB66;

LAB67:
LAB68:    goto LAB57;

LAB58:    *((unsigned int *)t24) = 1;
    goto LAB61;

LAB62:    *((unsigned int *)t35) = 1;
    goto LAB65;

LAB64:    t42 = (t35 + 4);
    *((unsigned int *)t35) = 1;
    *((unsigned int *)t42) = 1;
    goto LAB65;

LAB66:    t55 = *((unsigned int *)t43);
    t56 = *((unsigned int *)t49);
    *((unsigned int *)t43) = (t55 | t56);
    t57 = (t15 + 4);
    t58 = (t35 + 4);
    t59 = *((unsigned int *)t15);
    t60 = (~(t59));
    t61 = *((unsigned int *)t57);
    t62 = (~(t61));
    t63 = *((unsigned int *)t35);
    t64 = (~(t63));
    t65 = *((unsigned int *)t58);
    t66 = (~(t65));
    t67 = (t60 & t62);
    t68 = (t64 & t66);
    t69 = (~(t67));
    t70 = (~(t68));
    t71 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t71 & t69);
    t72 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t72 & t70);
    t73 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t73 & t69);
    t74 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t74 & t70);
    goto LAB68;

LAB69:    xsi_set_current_line(143, ng0);

LAB72:    xsi_set_current_line(144, ng0);
    t81 = (t0 + 1528U);
    t82 = *((char **)t81);
    memset(t83, 0, 8);
    t81 = (t83 + 4);
    t84 = (t82 + 4);
    t85 = *((unsigned int *)t82);
    t86 = (t85 >> 3);
    t87 = (t86 & 1);
    *((unsigned int *)t83) = t87;
    t88 = *((unsigned int *)t84);
    t89 = (t88 >> 3);
    t90 = (t89 & 1);
    *((unsigned int *)t81) = t90;
    t91 = (t83 + 4);
    t92 = *((unsigned int *)t91);
    t93 = (~(t92));
    t94 = *((unsigned int *)t83);
    t95 = (t94 & t93);
    t96 = (t95 != 0);
    if (t96 > 0)
        goto LAB73;

LAB74:
LAB75:    xsi_set_current_line(146, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 2);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 2);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB78;

LAB79:
LAB80:    xsi_set_current_line(148, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 1);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 1);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB83;

LAB84:
LAB85:    xsi_set_current_line(150, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 0);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 0);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB88;

LAB89:
LAB90:    goto LAB71;

LAB73:    xsi_set_current_line(145, ng0);
    t98 = (t0 + 2968U);
    t99 = *((char **)t98);
    memset(t97, 0, 8);
    t98 = (t97 + 4);
    t100 = (t99 + 4);
    t101 = *((unsigned int *)t99);
    t102 = (t101 >> 24);
    *((unsigned int *)t97) = t102;
    t103 = *((unsigned int *)t100);
    t104 = (t103 >> 24);
    *((unsigned int *)t98) = t104;
    t105 = *((unsigned int *)t97);
    *((unsigned int *)t97) = (t105 & 255U);
    t106 = *((unsigned int *)t98);
    *((unsigned int *)t98) = (t106 & 255U);
    t107 = (t0 + 4968);
    t111 = (t0 + 4968);
    t112 = (t111 + 72U);
    t113 = *((char **)t112);
    t114 = ((char*)((ng13)));
    t115 = ((char*)((ng14)));
    xsi_vlog_convert_partindices(t108, t109, t110, ((int*)(t113)), 2, t114, 32, 1, t115, 32, 1);
    t116 = (t108 + 4);
    t117 = *((unsigned int *)t116);
    t118 = (!(t117));
    t119 = (t109 + 4);
    t120 = *((unsigned int *)t119);
    t121 = (!(t120));
    t122 = (t118 && t121);
    t123 = (t110 + 4);
    t124 = *((unsigned int *)t123);
    t125 = (!(t124));
    t126 = (t122 && t125);
    if (t126 == 1)
        goto LAB76;

LAB77:    goto LAB75;

LAB76:    t127 = *((unsigned int *)t110);
    t128 = (t127 + 0);
    t129 = *((unsigned int *)t108);
    t130 = *((unsigned int *)t109);
    t131 = (t129 - t130);
    t132 = (t131 + 1);
    xsi_vlogvar_wait_assign_value(t107, t97, t128, *((unsigned int *)t109), t132, 0LL);
    goto LAB77;

LAB78:    xsi_set_current_line(147, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 16);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 16);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng15)));
    t42 = ((char*)((ng16)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB81;

LAB82:    goto LAB80;

LAB81:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB82;

LAB83:    xsi_set_current_line(149, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 8);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 8);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng17)));
    t42 = ((char*)((ng18)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB86;

LAB87:    goto LAB85;

LAB86:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB87;

LAB88:    xsi_set_current_line(151, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 0);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 0);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng19)));
    t42 = ((char*)((ng20)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB91;

LAB92:    goto LAB90;

LAB91:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB92;

LAB93:    *((unsigned int *)t15) = 1;
    goto LAB96;

LAB95:    t11 = (t15 + 4);
    *((unsigned int *)t15) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB96;

LAB97:    t25 = (t0 + 4488);
    t26 = (t25 + 56U);
    t27 = *((char **)t26);
    memset(t24, 0, 8);
    t28 = (t27 + 4);
    t29 = *((unsigned int *)t28);
    t30 = (~(t29));
    t31 = *((unsigned int *)t27);
    t32 = (t31 & t30);
    t33 = (t32 & 1U);
    if (t33 != 0)
        goto LAB103;

LAB101:    if (*((unsigned int *)t28) == 0)
        goto LAB100;

LAB102:    t34 = (t24 + 4);
    *((unsigned int *)t24) = 1;
    *((unsigned int *)t34) = 1;

LAB103:    memset(t35, 0, 8);
    t36 = (t24 + 4);
    t37 = *((unsigned int *)t36);
    t38 = (~(t37));
    t39 = *((unsigned int *)t24);
    t40 = (t39 & t38);
    t41 = (t40 & 1U);
    if (t41 != 0)
        goto LAB104;

LAB105:    if (*((unsigned int *)t36) != 0)
        goto LAB106;

LAB107:    t44 = *((unsigned int *)t15);
    t45 = *((unsigned int *)t35);
    t46 = (t44 & t45);
    *((unsigned int *)t43) = t46;
    t47 = (t15 + 4);
    t48 = (t35 + 4);
    t49 = (t43 + 4);
    t50 = *((unsigned int *)t47);
    t51 = *((unsigned int *)t48);
    t52 = (t50 | t51);
    *((unsigned int *)t49) = t52;
    t53 = *((unsigned int *)t49);
    t54 = (t53 != 0);
    if (t54 == 1)
        goto LAB108;

LAB109:
LAB110:    goto LAB99;

LAB100:    *((unsigned int *)t24) = 1;
    goto LAB103;

LAB104:    *((unsigned int *)t35) = 1;
    goto LAB107;

LAB106:    t42 = (t35 + 4);
    *((unsigned int *)t35) = 1;
    *((unsigned int *)t42) = 1;
    goto LAB107;

LAB108:    t55 = *((unsigned int *)t43);
    t56 = *((unsigned int *)t49);
    *((unsigned int *)t43) = (t55 | t56);
    t57 = (t15 + 4);
    t58 = (t35 + 4);
    t59 = *((unsigned int *)t15);
    t60 = (~(t59));
    t61 = *((unsigned int *)t57);
    t62 = (~(t61));
    t63 = *((unsigned int *)t35);
    t64 = (~(t63));
    t65 = *((unsigned int *)t58);
    t66 = (~(t65));
    t67 = (t60 & t62);
    t68 = (t64 & t66);
    t69 = (~(t67));
    t70 = (~(t68));
    t71 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t71 & t69);
    t72 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t72 & t70);
    t73 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t73 & t69);
    t74 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t74 & t70);
    goto LAB110;

LAB111:    xsi_set_current_line(154, ng0);

LAB114:    xsi_set_current_line(155, ng0);
    t81 = (t0 + 1528U);
    t82 = *((char **)t81);
    memset(t83, 0, 8);
    t81 = (t83 + 4);
    t84 = (t82 + 4);
    t85 = *((unsigned int *)t82);
    t86 = (t85 >> 3);
    t87 = (t86 & 1);
    *((unsigned int *)t83) = t87;
    t88 = *((unsigned int *)t84);
    t89 = (t88 >> 3);
    t90 = (t89 & 1);
    *((unsigned int *)t81) = t90;
    t91 = (t83 + 4);
    t92 = *((unsigned int *)t91);
    t93 = (~(t92));
    t94 = *((unsigned int *)t83);
    t95 = (t94 & t93);
    t96 = (t95 != 0);
    if (t96 > 0)
        goto LAB115;

LAB116:
LAB117:    xsi_set_current_line(157, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 2);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 2);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB120;

LAB121:
LAB122:    xsi_set_current_line(159, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 1);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 1);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB125;

LAB126:
LAB127:    xsi_set_current_line(161, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 0);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 0);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB130;

LAB131:
LAB132:    goto LAB113;

LAB115:    xsi_set_current_line(156, ng0);
    t98 = (t0 + 2968U);
    t99 = *((char **)t98);
    memset(t97, 0, 8);
    t98 = (t97 + 4);
    t100 = (t99 + 4);
    t101 = *((unsigned int *)t99);
    t102 = (t101 >> 24);
    *((unsigned int *)t97) = t102;
    t103 = *((unsigned int *)t100);
    t104 = (t103 >> 24);
    *((unsigned int *)t98) = t104;
    t105 = *((unsigned int *)t97);
    *((unsigned int *)t97) = (t105 & 255U);
    t106 = *((unsigned int *)t98);
    *((unsigned int *)t98) = (t106 & 255U);
    t107 = (t0 + 4968);
    t111 = (t0 + 4968);
    t112 = (t111 + 72U);
    t113 = *((char **)t112);
    t114 = ((char*)((ng21)));
    t115 = ((char*)((ng22)));
    xsi_vlog_convert_partindices(t108, t109, t110, ((int*)(t113)), 2, t114, 32, 1, t115, 32, 1);
    t116 = (t108 + 4);
    t117 = *((unsigned int *)t116);
    t118 = (!(t117));
    t119 = (t109 + 4);
    t120 = *((unsigned int *)t119);
    t121 = (!(t120));
    t122 = (t118 && t121);
    t123 = (t110 + 4);
    t124 = *((unsigned int *)t123);
    t125 = (!(t124));
    t126 = (t122 && t125);
    if (t126 == 1)
        goto LAB118;

LAB119:    goto LAB117;

LAB118:    t127 = *((unsigned int *)t110);
    t128 = (t127 + 0);
    t129 = *((unsigned int *)t108);
    t130 = *((unsigned int *)t109);
    t131 = (t129 - t130);
    t132 = (t131 + 1);
    xsi_vlogvar_wait_assign_value(t107, t97, t128, *((unsigned int *)t109), t132, 0LL);
    goto LAB119;

LAB120:    xsi_set_current_line(158, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 16);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 16);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng23)));
    t42 = ((char*)((ng24)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB123;

LAB124:    goto LAB122;

LAB123:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB124;

LAB125:    xsi_set_current_line(160, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 8);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 8);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng25)));
    t42 = ((char*)((ng26)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB128;

LAB129:    goto LAB127;

LAB128:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB129;

LAB130:    xsi_set_current_line(162, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 0);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 0);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng27)));
    t42 = ((char*)((ng28)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB133;

LAB134:    goto LAB132;

LAB133:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB134;

LAB135:    *((unsigned int *)t15) = 1;
    goto LAB138;

LAB137:    t11 = (t15 + 4);
    *((unsigned int *)t15) = 1;
    *((unsigned int *)t11) = 1;
    goto LAB138;

LAB139:    t25 = (t0 + 4488);
    t26 = (t25 + 56U);
    t27 = *((char **)t26);
    memset(t24, 0, 8);
    t28 = (t27 + 4);
    t29 = *((unsigned int *)t28);
    t30 = (~(t29));
    t31 = *((unsigned int *)t27);
    t32 = (t31 & t30);
    t33 = (t32 & 1U);
    if (t33 != 0)
        goto LAB145;

LAB143:    if (*((unsigned int *)t28) == 0)
        goto LAB142;

LAB144:    t34 = (t24 + 4);
    *((unsigned int *)t24) = 1;
    *((unsigned int *)t34) = 1;

LAB145:    memset(t35, 0, 8);
    t36 = (t24 + 4);
    t37 = *((unsigned int *)t36);
    t38 = (~(t37));
    t39 = *((unsigned int *)t24);
    t40 = (t39 & t38);
    t41 = (t40 & 1U);
    if (t41 != 0)
        goto LAB146;

LAB147:    if (*((unsigned int *)t36) != 0)
        goto LAB148;

LAB149:    t44 = *((unsigned int *)t15);
    t45 = *((unsigned int *)t35);
    t46 = (t44 & t45);
    *((unsigned int *)t43) = t46;
    t47 = (t15 + 4);
    t48 = (t35 + 4);
    t49 = (t43 + 4);
    t50 = *((unsigned int *)t47);
    t51 = *((unsigned int *)t48);
    t52 = (t50 | t51);
    *((unsigned int *)t49) = t52;
    t53 = *((unsigned int *)t49);
    t54 = (t53 != 0);
    if (t54 == 1)
        goto LAB150;

LAB151:
LAB152:    goto LAB141;

LAB142:    *((unsigned int *)t24) = 1;
    goto LAB145;

LAB146:    *((unsigned int *)t35) = 1;
    goto LAB149;

LAB148:    t42 = (t35 + 4);
    *((unsigned int *)t35) = 1;
    *((unsigned int *)t42) = 1;
    goto LAB149;

LAB150:    t55 = *((unsigned int *)t43);
    t56 = *((unsigned int *)t49);
    *((unsigned int *)t43) = (t55 | t56);
    t57 = (t15 + 4);
    t58 = (t35 + 4);
    t59 = *((unsigned int *)t15);
    t60 = (~(t59));
    t61 = *((unsigned int *)t57);
    t62 = (~(t61));
    t63 = *((unsigned int *)t35);
    t64 = (~(t63));
    t65 = *((unsigned int *)t58);
    t66 = (~(t65));
    t67 = (t60 & t62);
    t68 = (t64 & t66);
    t69 = (~(t67));
    t70 = (~(t68));
    t71 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t71 & t69);
    t72 = *((unsigned int *)t49);
    *((unsigned int *)t49) = (t72 & t70);
    t73 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t73 & t69);
    t74 = *((unsigned int *)t43);
    *((unsigned int *)t43) = (t74 & t70);
    goto LAB152;

LAB153:    xsi_set_current_line(165, ng0);

LAB156:    xsi_set_current_line(166, ng0);
    t81 = (t0 + 1528U);
    t82 = *((char **)t81);
    memset(t83, 0, 8);
    t81 = (t83 + 4);
    t84 = (t82 + 4);
    t85 = *((unsigned int *)t82);
    t86 = (t85 >> 3);
    t87 = (t86 & 1);
    *((unsigned int *)t83) = t87;
    t88 = *((unsigned int *)t84);
    t89 = (t88 >> 3);
    t90 = (t89 & 1);
    *((unsigned int *)t81) = t90;
    t91 = (t83 + 4);
    t92 = *((unsigned int *)t91);
    t93 = (~(t92));
    t94 = *((unsigned int *)t83);
    t95 = (t94 & t93);
    t96 = (t95 != 0);
    if (t96 > 0)
        goto LAB157;

LAB158:
LAB159:    xsi_set_current_line(168, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 2);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 2);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB162;

LAB163:
LAB164:    xsi_set_current_line(170, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 1);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 1);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB167;

LAB168:
LAB169:    xsi_set_current_line(172, ng0);
    t2 = (t0 + 1528U);
    t3 = *((char **)t2);
    memset(t13, 0, 8);
    t2 = (t13 + 4);
    t4 = (t3 + 4);
    t6 = *((unsigned int *)t3);
    t7 = (t6 >> 0);
    t8 = (t7 & 1);
    *((unsigned int *)t13) = t8;
    t9 = *((unsigned int *)t4);
    t10 = (t9 >> 0);
    t14 = (t10 & 1);
    *((unsigned int *)t2) = t14;
    t5 = (t13 + 4);
    t16 = *((unsigned int *)t5);
    t17 = (~(t16));
    t18 = *((unsigned int *)t13);
    t19 = (t18 & t17);
    t20 = (t19 != 0);
    if (t20 > 0)
        goto LAB172;

LAB173:
LAB174:    goto LAB155;

LAB157:    xsi_set_current_line(167, ng0);
    t98 = (t0 + 2968U);
    t99 = *((char **)t98);
    memset(t97, 0, 8);
    t98 = (t97 + 4);
    t100 = (t99 + 4);
    t101 = *((unsigned int *)t99);
    t102 = (t101 >> 24);
    *((unsigned int *)t97) = t102;
    t103 = *((unsigned int *)t100);
    t104 = (t103 >> 24);
    *((unsigned int *)t98) = t104;
    t105 = *((unsigned int *)t97);
    *((unsigned int *)t97) = (t105 & 255U);
    t106 = *((unsigned int *)t98);
    *((unsigned int *)t98) = (t106 & 255U);
    t107 = (t0 + 4968);
    t111 = (t0 + 4968);
    t112 = (t111 + 72U);
    t113 = *((char **)t112);
    t114 = ((char*)((ng29)));
    t115 = ((char*)((ng30)));
    xsi_vlog_convert_partindices(t108, t109, t110, ((int*)(t113)), 2, t114, 32, 1, t115, 32, 1);
    t116 = (t108 + 4);
    t117 = *((unsigned int *)t116);
    t118 = (!(t117));
    t119 = (t109 + 4);
    t120 = *((unsigned int *)t119);
    t121 = (!(t120));
    t122 = (t118 && t121);
    t123 = (t110 + 4);
    t124 = *((unsigned int *)t123);
    t125 = (!(t124));
    t126 = (t122 && t125);
    if (t126 == 1)
        goto LAB160;

LAB161:    goto LAB159;

LAB160:    t127 = *((unsigned int *)t110);
    t128 = (t127 + 0);
    t129 = *((unsigned int *)t108);
    t130 = *((unsigned int *)t109);
    t131 = (t129 - t130);
    t132 = (t131 + 1);
    xsi_vlogvar_wait_assign_value(t107, t97, t128, *((unsigned int *)t109), t132, 0LL);
    goto LAB161;

LAB162:    xsi_set_current_line(169, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 16);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 16);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng31)));
    t42 = ((char*)((ng32)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB165;

LAB166:    goto LAB164;

LAB165:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB166;

LAB167:    xsi_set_current_line(171, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 8);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 8);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng33)));
    t42 = ((char*)((ng34)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB170;

LAB171:    goto LAB169;

LAB170:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB171;

LAB172:    xsi_set_current_line(173, ng0);
    t11 = (t0 + 2968U);
    t12 = *((char **)t11);
    memset(t15, 0, 8);
    t11 = (t15 + 4);
    t25 = (t12 + 4);
    t21 = *((unsigned int *)t12);
    t22 = (t21 >> 0);
    *((unsigned int *)t15) = t22;
    t23 = *((unsigned int *)t25);
    t29 = (t23 >> 0);
    *((unsigned int *)t11) = t29;
    t30 = *((unsigned int *)t15);
    *((unsigned int *)t15) = (t30 & 255U);
    t31 = *((unsigned int *)t11);
    *((unsigned int *)t11) = (t31 & 255U);
    t26 = (t0 + 4968);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = ((char*)((ng35)));
    t42 = ((char*)((ng36)));
    xsi_vlog_convert_partindices(t24, t35, t43, ((int*)(t34)), 2, t36, 32, 1, t42, 32, 1);
    t47 = (t24 + 4);
    t32 = *((unsigned int *)t47);
    t67 = (!(t32));
    t48 = (t35 + 4);
    t33 = *((unsigned int *)t48);
    t68 = (!(t33));
    t118 = (t67 && t68);
    t49 = (t43 + 4);
    t37 = *((unsigned int *)t49);
    t121 = (!(t37));
    t122 = (t118 && t121);
    if (t122 == 1)
        goto LAB175;

LAB176:    goto LAB174;

LAB175:    t38 = *((unsigned int *)t43);
    t125 = (t38 + 0);
    t39 = *((unsigned int *)t24);
    t40 = *((unsigned int *)t35);
    t126 = (t39 - t40);
    t128 = (t126 + 1);
    xsi_vlogvar_wait_assign_value(t26, t15, t125, *((unsigned int *)t35), t128, 0LL);
    goto LAB176;

LAB177:    *((unsigned int *)t15) = 1;
    goto LAB180;

LAB179:    t4 = (t15 + 4);
    *((unsigned int *)t15) = 1;
    *((unsigned int *)t4) = 1;
    goto LAB180;

LAB181:    t11 = (t0 + 3448U);
    t12 = *((char **)t11);
    goto LAB182;

LAB183:    t11 = (t0 + 4968);
    t25 = (t11 + 56U);
    t26 = *((char **)t25);
    t27 = (t0 + 4968);
    t28 = (t27 + 72U);
    t34 = *((char **)t28);
    t36 = (t0 + 3768U);
    t42 = *((char **)t36);
    memset(t35, 0, 8);
    t36 = (t35 + 4);
    t47 = (t42 + 4);
    t22 = *((unsigned int *)t42);
    t23 = (t22 >> 0);
    *((unsigned int *)t35) = t23;
    t29 = *((unsigned int *)t47);
    t30 = (t29 >> 0);
    *((unsigned int *)t36) = t30;
    t31 = *((unsigned int *)t35);
    *((unsigned int *)t35) = (t31 & 127U);
    t32 = *((unsigned int *)t36);
    *((unsigned int *)t36) = (t32 & 127U);
    xsi_vlog_generic_get_index_select_value(t24, 1, t26, t34, 2, t35, 7, 2);
    goto LAB184;

LAB185:    xsi_vlog_unsigned_bit_combine(t13, 1, t12, 1, t24, 1);
    goto LAB189;

LAB187:    memcpy(t13, t12, 8);
    goto LAB189;

LAB190:    xsi_vlogvar_wait_assign_value(t48, t13, 0, *((unsigned int *)t43), 1, 0LL);
    goto LAB191;

}


extern void work_m_00000000003782124487_1224910743_init()
{
	static char *pe[] = {(void *)Cont_80_0,(void *)Cont_82_1,(void *)Cont_83_2,(void *)Cont_86_3,(void *)Cont_88_4,(void *)Cont_89_5,(void *)Always_92_6,(void *)Always_106_7,(void *)Always_117_8,(void *)Always_126_9};
	xsi_register_didat("work_m_00000000003782124487_1224910743", "isim/tb_spi_top_isim_beh.exe.sim/work/m_00000000003782124487_1224910743.didat");
	xsi_register_executes(pe);
}
