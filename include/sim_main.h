#ifndef _SIM_MAIN_H_
#define _SIM_MAIN_H_
#include "sim_config.h"
#define VERILATOR_INIT(argc, argv, trace_on) \
    contextp->commandArgs(argc, argv);       \
    Verilated::traceEverOn(trace_on);        \
    top->trace(tfp, 99);                     \
    tfp->open(WAVEFILE);

#ifdef NVBOARD
#define NVBOARD_UPDATE nvboard_update()
#define NVBOARD_QUIT nvboard_quit()
#else
#define NVBOARD_UPDATE
#define NVBOARD_QUIT
#endif // DEBUG
#define VERILATOR_TOGGLE_CLK()       \
    do                               \
    {                                \
        if (T % HALF_CLK_CYCLE == 0) \
        {                            \
            clk = clk == 0;          \
        }                            \
    } while (0)

#define VERILATOR_EVAL_AND_DUMP()         \
    top->eval();                          \
    NVBOARD_UPDATE;                     \
    do                                    \
    {                                     \
        if (!ENABLE_WAVEFROM_ACQUISITION) \
        {                                 \
            break;                        \
        }                                 \
        tfp->dump(contextp->time());      \
    } while (0)

#define VERILATOR_STEP() \
    T++;                 \
    contextp->timeInc(1)

#define VERILATOR_FREE() \
    tfp->close();        \
    delete tfp;          \
    delete top;          \
    delete contextp;    \
    NVBOARD_QUIT;
#if ENABLE_LIMIT_TIME_STIMULATION == 1
#define VERILATOR_VALID_STIMULATION_RANGE() !contextp->gotFinish() && T < MAX_TIME_SIM
#else
#define VERILATOR_VALID_STIMULATION_RANGE() !contextp->gotFinish()
#endif

#define VERILATOR_SWITCH_INPUT_TO(input, value) top->input = value

#define VERILATOR_SWITCH_INPUT_TO_AT(input, time, value) \
    do                                                   \
    {                                                    \
        if (T == time)                                   \
        {                                                \
            VERILATOR_SWITCH_INPUT_TO(input, value);     \
        }                                                \
    } while (0)

#define VERILATOR_END_CHECK()                       \
    do                                              \
    {                                               \
        if (!(VERILATOR_VALID_STIMULATION_RANGE())) \
        {                                           \
            goto end;                               \
        }                                           \
    } while (0)

#define VERILATOR_STEP_AND_EVAL_UNTIL(t) \
    do                                   \
    {                                    \
        VERILATOR_END_CHECK();           \
        VERILATOR_TOGGLE_CLK();          \
        VERILATOR_CLK_INPUT(clk);        \
        VERILATOR_EVAL_AND_DUMP();       \
        VERILATOR_STEP();                \
    } while (T < t)

#if ENABLE_CLK_INPUT == 1
#define VERILATOR_CLK_INPUT(clk) \
    VERILATOR_SWITCH_INPUT_TO(CLK_PIN_NAME, clk)
#else
#define VERILATOR_CLK_INPUT(clk)
#endif

#endif // _SIM_MAIN_H_