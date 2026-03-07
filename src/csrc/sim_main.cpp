#include "top_module_name.h"
#include "verilated.h"
#include "verilated_fst_c.h"
#include "sim_main.h"
#include "sim_config.h"
#include <stdarg.h>
#ifdef NVBOARD
#include <nvboard.h>
#endif 
#include <stdio.h>
#include <cstdlib>
#include <csignal>
#ifdef NVBOARD
void nvboard_bind_all_pins(Vtop *top);
#endif 
VerilatedContext *contextp = new VerilatedContext;
Vtop *top = new Vtop(contextp);
VerilatedFstC *tfp = new VerilatedFstC;
vluint64_t T = 0;
vluint64_t clk = 0;

void close_wave()
{
    VERILATOR_FREE();
    printf("\n[Waveform] FST file has been closed successfully via atexit.\n");
}
void signal_handler(int sig) {
    std::exit(0); 
}
int main(int argc, char **argv)
{
    std::atexit(close_wave);
    std::signal(SIGINT, signal_handler);  
    std::signal(SIGTSTP, signal_handler);
    printf("Start\n");
#ifdef NVBOARD
    nvboard_bind_all_pins(top);
    nvboard_init();
#endif 
    VERILATOR_INIT(argc, argv, true);
    VERILATOR_MAIN_INITIAL_BLOCK();
    VERILATOR_MAIN_FOREVER_BLOCK();
end:
    exit(0);
    return 0;
}
