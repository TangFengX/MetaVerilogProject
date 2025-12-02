#include "top_module_name.h"
#include "verilated.h"
#include "verilated_fst_c.h"
#include "sim_main.h"
#include "sim_config.h"
#include <stdarg.h>

VerilatedContext *contextp = new VerilatedContext;
Vtop *top = new Vtop(contextp);
VerilatedFstC *tfp = new VerilatedFstC;
vluint64_t T = 0;
vluint64_t clk = 0;

vluint64_t half_clk_T = HALF_CLK_CYCLE;

int main(int argc, char **argv)
{
    VERILATOR_INIT(argc, argv, true);
    VERILATOR_MAIN_LOOP();
end:
    VERILATOR_FREE();

    return 0;
}
