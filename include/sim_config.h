#ifndef __SIM_CONFIG__
#define __SIM_CONFIG__
#include "sim_main.h"
#include "verilated.h"

#define ENABLE_LIMIT_TIME_STIMULATION 0
#define MAX_TIME_SIM 20
#define HALF_CLK_CYCLE 1
#define ENABLE_CLK_INPUT 1
#define CLK_PIN_NAME clk
#define ENABLE_INITIAL_BLOCK 1
#define INITIAL_BLOCK_MAX_STIMULATE_TIME 20
#define ENABLE_FOREVER_BLOCK 1
#define FOREVER_BLOCK_CYCLE 20
#define ENABLE_WAVEFROM_ACQUISITION 1

#define VERILATOR_MAIN_INITIAL_BLOCK()                                   \
    do                                                                   \
    {                                                                    \
            if (!ENABLE_INITIAL_BLOCK) \
                break; \
            VERILATOR_SWITCH_INPUT_TO(rst, 1); \
            nvboard_update(); \
            VERILATOR_STEP_AND_EVAL_UNTIL(10); \
            VERILATOR_SWITCH_INPUT_TO(rst, 0); \
            nvboard_update(); \
            VERILATOR_STEP_AND_EVAL_UNTIL(INITIAL_BLOCK_MAX_STIMULATE_TIME); \
    } while (0)

#define VERILATOR_MAIN_FOREVER_BLOCK()                               \
    vluint64_t T_start;                                              \
    do                                                               \
    {                                                                \
        T_start = T;                                                 \
            if (!ENABLE_FOREVER_BLOCK) \
                break; \
            VERILATOR_STEP_AND_EVAL_UNTIL(FOREVER_BLOCK_CYCLE + T_start); \
    } while (1)

#endif //__SIM_CONFIG__
