#include "top_module_name.h"             // Verilator 生成的模型头文件
#include "verilated.h"        // Verilator 基础类
#include "verilated_fst_c.h"  // 【新】FST 跟踪头文件


vluint64_t main_time = 0;

const vluint64_t MAX_TIME = 20;
//#define FST_TRACE_OUTPUT
int main(int argc, char** argv) {
    VerilatedContext* contextp = new VerilatedContext;

    contextp->commandArgs(argc, argv);

    
    Verilated::traceEverOn(true); // 开启波形跟踪的全局支持
    Vtop* top = new Vtop(contextp);
    VerilatedFstC* tfp = new VerilatedFstC; 
    top->trace(tfp, 99); 
    tfp->open(WAVEFILE); 
    printf("used");
    
    
    while (!contextp->gotFinish() && main_time < MAX_TIME) {
        switch(main_time){
            case 0:top->a=0;top->b=0;break;
            case 5:top->a=1;top->b=0;break;
            case 10:top->a=0;top->b=1;break;
            case 15:top->a=1;top->b=1;break;
        }
        // 2. 评估模型 (对于组合逻辑，只需调用 eval) 对时序逻辑要在每一次clk变化后都进行评估
        top->eval();
        
    
        tfp->dump(contextp->time()); // 【新】转储当前时间的信号值
    

        main_time++;
        contextp->timeInc(1); // 推进 Verilator 内部时间
    }

    
   
        tfp->close(); 
        delete tfp;
   
    
    delete top;
    delete contextp;
    return 0;
}
