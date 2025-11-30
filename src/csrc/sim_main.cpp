#include "top_module_name.h" 
#include "verilated.h"       
#include "verilated_fst_c.h" 
#include "sim_main.h"
#include <stdarg.h>

int main(int argc, char **argv)
{
    VERILATOR_INIT(argc, argv,20,true,2);//half_clk_cycle should larger than 1
    

    while (VERILATOR_VALID_STIMULATION_RANGE())
    {
        VERILATOR_SWITCH_INPUT_TO_AT(a,0,0);
        VERILATOR_SWITCH_INPUT_TO_AT(b,0,0);
        VERILATOR_SWITCH_INPUT_TO_AT(a,5,1);
        VERILATOR_SWITCH_INPUT_TO_AT(b,10,1);
        VERILATOR_SWITCH_INPUT_TO_AT(a,10,0);
        VERILATOR_SWITCH_INPUT_TO_AT(a,15,1);
        
        VERILATOR_TOGGLE_CLK();
        //VERILATOR_SWITCH_INPUT_TO(clk,clk);
        VERILATOR_EVAL_AND_DUMP();
        VERILATOR_STEP();

        
    }
    VERILATOR_FREE();
    
    return 0;
}
