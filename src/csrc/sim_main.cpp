#include "top_module_name.h"
#include "verilated.h"
#include "verilated_fst_c.h"
#include "sim_main.h"
#include "sim_config.h"
#include <nvboard.h>



void nvboard_bind_all_pins(Vtop* top);
VerilatedContext *contextp = new VerilatedContext;
Vtop *top = new Vtop(contextp);
VerilatedFstC *tfp = new VerilatedFstC;
vluint64_t T = 0;
vluint64_t clk = 0;

int main(int argc, char **argv)
{
    nvboard_bind_all_pins(top);
    nvboard_init();
    VERILATOR_INIT(argc, argv, true);
    VERILATOR_MAIN_INITIAL_BLOCK();
    VERILATOR_MAIN_FOREVER_BLOCK();
end:
    VERILATOR_FREE();
    nvboard_quit();
    return 0;
}
