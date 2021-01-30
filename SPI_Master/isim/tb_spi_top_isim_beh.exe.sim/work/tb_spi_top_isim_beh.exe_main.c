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

#include "xsi.h"

struct XSI_INFO xsi_info;



int main(int argc, char **argv)
{
    xsi_init_design(argc, argv);
    xsi_register_info(&xsi_info);

    xsi_register_min_prec_unit(-12);
    work_m_00000000000125864305_1320439738_init();
    work_m_00000000004018639662_2052137201_init();
    work_m_00000000003782124487_1224910743_init();
    work_m_00000000003053683010_4124128745_init();
    work_m_00000000002389827953_3599914142_init();
    xilinxcorelib_ver_m_00000000000200492576_2247654869_init();
    xilinxcorelib_ver_m_00000000001647451333_0428709936_init();
    xilinxcorelib_ver_m_00000000001562617919_0534955664_init();
    xilinxcorelib_ver_m_00000000001291582275_0927312278_init();
    work_m_00000000000840594279_1921273648_init();
    work_m_00000000000517601819_2669345608_init();
    work_m_00000000002060826706_2305576791_init();
    work_m_00000000002586628517_1858427038_init();
    work_m_00000000002735913337_2943448091_init();
    work_m_00000000000371345029_0644216324_init();
    work_m_00000000004134447467_2073120511_init();


    xsi_register_tops("work_m_00000000000371345029_0644216324");
    xsi_register_tops("work_m_00000000004134447467_2073120511");


    return xsi_run_simulation(argc, argv);

}
