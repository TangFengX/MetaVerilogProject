#ifndef _SIM_MAIN_H_
#define _SIM_MAIN_H_

#define VERILATOR_INIT(argc, argv, max_T, trace_on,half_clk_cycle)    \
    VerilatedContext *contextp = new VerilatedContext; \
    contextp->commandArgs(argc, argv);                 \
    Verilated::traceEverOn(trace_on);                  \
    Vtop *top = new Vtop(contextp);                    \
    VerilatedFstC *tfp = new VerilatedFstC;            \
    top->trace(tfp, 99);                               \
    tfp->open(WAVEFILE);                               \
    vluint64_t T = 0;                                  \
    const vluint64_t MAX_TIME = max_T ;\
    vluint64_t clk = 0;\
    vluint64_t half_clk_T =half_clk_cycle


#define VERILATOR_TOGGLE_CLK() if(T%half_clk_T==0)  clk=clk==0
      

#define VERILATOR_EVAL_AND_DUMP() \
    top->eval();                  \
    tfp->dump(contextp->time())

#define VERILATOR_STEP() \
    T++;                 \
    contextp->timeInc(1)

#define VERILATOR_FREE() \
    tfp->close();        \
    delete tfp;          \
    delete top;          \
    delete contextp

#define VERILATOR_VALID_STIMULATION_RANGE() !contextp->gotFinish() && T < MAX_TIME

#define VERILATOR_SWITCH_INPUT_TO(input,value) top->input = value


#define VERILATOR_SWITCH_INPUT_TO_AT(input, time,value) \
    do                                               \
    {                                                \
        if (T == time)                               \
        {                                            \
            VERILATOR_SWITCH_INPUT_TO(input,value);                          \
        }                                            \
    } while (0)




#endif // _SIM_MAIN_H_