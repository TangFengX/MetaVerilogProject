## Verilog项目模板--Nvboard兼容版本
# 介绍
本项目是一个基于verilator的verilog项目模板，该版本对[NVboard][https://github.com/NJU-ProjectN/nvboard]进行了兼容，旨在为模拟提供一个简单易用的GUI界面。如果只需要使用verilator仿真，可以使用命令`git switch verilator-only`切换到仅verilator分支
# Structure
```
.
├── LICENSE
├── Makefile
├── README.md
├── include
│   ├── sim_config.h        #项目配置头文件，自动生成
│   ├── sim_main.h          #包含常用的宏，不可更改
│   └── top_module_name.h   #用于兼容不同名称的顶层模块，自动生成
├── pin
│   └── top.nxdc            #引脚约束文件，根据需求更改
├── src
│   ├── csrc
│   │   ├── auto_bind.cpp   #引脚绑定文件文件，自动生成
│   │   └── sim_main.cpp    #主流程，不可更改
│   └── vsrc
│       ├── top.v           #用户的Verilog项目
│       └── ...          
└── testbench
    ├── csv2c.py            #配置生成脚本，不可更改
    └── testbench.csv       #配置文件，可更改
```
# 安装

1. 将本项目下载到本地
```
git clone https://github.com/NJU-ProjectN/nvboard.git --recursive
```
2. 确定依赖是否安装
```
make check
```
你可能需要提前安装部分NVBOARD所需要的依赖
```
#Linux
apt-get install libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev 

yum install SDL2-devel SDL2_image-devel SDL2_ttf-devel

#Macos
brew install sdl2 sdl2_image sdl2_ttf
```
# 示例
你可以直接使用以下代码构建本项目中示例的代码
```
make cleanall
make
```

# 使用教程
1. 将Verilog项目全部代码放在`/src/vsrc/`下（替换示例中的`top.v`，或在构建时修改`VERILOG_FILES`相关参数以包括相关文件。
2. 修改`/testbench/testbench.csv`,具体的语法说明见 Testbench与Configure结构 节。
3. 修改`/pin/top.nxdc`,具体语法见`NVBOARD`项目的`README`文件。
4. 使用`make`构建。

# 其他命令

本项目提供了多个 `make` 命令来简化开发流程。以下是所有可用的命令及其功能：

## 构建相关命令

| 命令 | 功能说明 | 使用场景 |
|------|----------|----------|
| `make` 或 `make all` | 完整构建项目，生成可执行文件 | 首次构建或代码修改后重新构建 |
| `make toc` | 使用 Verilator 将 Verilog 代码转换为 C++ 文件 | 仅需生成中间文件时使用 |
| `make run` | 运行已构建的可执行文件 | 快速测试已构建的程序 |

## 仿真与波形查看

| 命令 | 功能说明 | 使用场景 |
|------|----------|----------|
| `make sim` | 运行仿真并在 gtkwave 中显示波形 | 需要查看波形分析时序时 |
| `make tb` | 从 `testbench.csv` 生成 `sim_config.h` 配置文件 | 修改测试激励后更新配置 |

## 清理命令

| 命令 | 功能说明 | 使用场景 |
|------|----------|----------|
| `make clean` | 清理构建文件和二进制文件 | 需要重新构建时 |
| `make cleanlib` | 清理 nvboard 库文件 | 需要更新 nvboard 库时 |
| `make cleanall` | 清理所有文件（包括库） | 完全重新构建项目时 |

## 代码分析与验证

| 命令 | 功能说明 | 使用场景 |
|------|----------|----------|
| `make lint` | 使用 Verilator 分析 Verilog 代码语法 | 检查代码规范性和潜在问题 |
| `make bind` | 生成引脚绑定文件 `auto_bind.cpp` | 修改引脚约束文件后更新绑定 |

## 环境检查命令

| 命令 | 功能说明 | 使用场景 |
|------|----------|----------|
| `make check` | 检查所有环境依赖 | 首次使用或环境配置后验证 |
| `make check_commands` | 检查必要的命令行工具 | 验证 gcc、g++、python 等工具 |
| `make check_libs` | 检查 SDL2 头文件 | 验证图形界面依赖 |
| `make check_python_modules` | 检查 Python 模块 | 验证脚本运行环境 |
| `make check_libraries` | 检查动态链接库 | 验证库文件链接 |
| `make check_verilator` | 检查 Verilator 版本和功能 | 验证仿真工具 |
| `make check_all` | 执行所有检查并汇总结果 | 全面环境验证 |



# Testbench 与 Configure 结构
项目的Testbench与Configure由`/testbench/testbench.csv`定义，该文件通过`/testbench/csv2c.py`脚本解析并生成`/include/sim_config.h`配置文件。

## testbench.csv 数据结构

`testbench.csv`文件采用CSV格式，包含三个主要部分：INITIAL事件、FOREVER事件和Configuration配置。文件结构如下：

| INITIAL部分 | | | | | FOREVER部分 | | | | | Configuration部分 | | |
|------------|-|-|-|-|-------------|-|-|-|-|------------------|-|-|
| Time(ps) | Pin | Value | Note | | Time(ps) | Pin | Value | Note | | Configuration | Value | Note |

### 1. INITIAL 事件块
- **功能**：定义仿真开始时的初始激励信号
- **格式**：`时间(ps), 引脚名, 值, 备注`
- **示例**：
  ```
  ,0,rst,1,复位信号置高
  ,10,rst,0,复位信号置低
  ```
- **说明**：
  - 时间单位为皮秒(ps)
  - 引脚名必须与Verilog模块中的输入端口名称一致
  - 值为此时刻引脚改变的数值，
  - 同一时间点不能对同一引脚多次赋值
  - INITIAL块只执行一次，所有激励事件的时间是相对于0时刻的事件，INITIAL块在FOREVER块之前执行

### 2. FOREVER 事件块
- **功能**：定义周期性重复的激励信号
- **格式**：`时间(ps), 引脚名, 值, 备注`
- **示例**：可用于生成时钟信号等周期性波形
- **说明**：
  - FOREVER块会循环执行其中的事件，定义的所有事件的时间定义是基于周期开始的相对时间


### 3. Configuration 配置块
- **功能**：定义仿真和测试的各种参数配置
- **格式**：`配置名, 值, 备注`

## 配置项详解

以下为testbench.csv中可用的配置项及其功能：

| 配置名 | 功能说明  | 参数类型  |
| :--- | :--- | :--- |
| enable limit time stimulation | 启用仿真总时间限制。0=禁用，1=启用。 | `bool` |
| max stimulate time | 最大仿真时间（单位：ps），当启用仿真总时间限制时生效。 | `int` |
| enable clock input | 启用时钟输入。0=禁用，1=启用。 | `bool` |
| half clock cycle | 半时钟周期（单位：ps），当启用时钟输入时生效。 | `int` |
| clock pin name | 时钟引脚名称，必须与 Verilog 模块中的时钟输入端口名称一致。 | `str` |
| enable INITIAL block | 启用 `INITIAL` 事件块。0=禁用，1=启用。 | `bool` |
| INITIAL block max stimulate time | `INITIAL` 块的最大仿真时间（单位：ps）。 | `int` |
| enable FOREVER block | 启用 `FOREVER` 事件块。0=禁用，1=启用。 | `bool` |
| FOREVER block cycle | `FOREVER` 块的循环周期（单位：ps）。 | `int` |
| enable wavefrom acquisition | 启用波形采集。0=禁用，1=启用。 | `bool` |


## 注意事项

1. 时间值必须为整数，单位为皮秒(ps)
2. 引脚名称必须与Verilog模块中的输入端口完全一致
3. 同一时间点不能对同一引脚多次赋值
4. 激励信号改变事件的事件在表格中不必按时间顺序从上到下排列,只要是在仿真的时间范围内都可以被找到,但是被判定在仿真时间范围外的数据会被丢弃

# 引脚定义

NVBoard 提供了丰富的虚拟外设接口，所有引脚定义遵循行业标准命名规范。引脚分为输入（Input）和输出（Output）两类，分别对应从 NVBoard 到 RTL 设计的信号和从 RTL 设计到 NVBoard 的信号。

## 引脚命名规则

NVBoard 的引脚命名采用以下规则：
1. **按钮（Buttons）**：`BTNC`（中心）、`BTNU`（上）、`BTND`（下）、`BTNL`（左）、`BTNR`（右）
2. **开关（Switches）**：`SW0`-`SW15`（16位拨码开关）
3. **普通LED**：`LD0`-`LD15`（16个单色LED）
4. **RGB LED**：`R16`、`G16`、`B16`、`R17`、`G17`、`B17`（2个RGB LED，每个包含红、绿、蓝三色）
5. **七段数码管（7-Segment Display）**：
   - 段选信号：`SEG0A`-`SEG0G`、`SEG1A`-`SEG1G`、...、`SEG7A`-`SEG7G`（8个数码管，每个7段）
   - 小数点：`DEC0P`-`DEC7P`（8个数码管的小数点）
6. **VGA接口**：
   - 同步信号：`VGA_VSYNC`（垂直同步）、`VGA_HSYNC`（水平同步）、`VGA_BLANK_N`（消隐信号）
   - 颜色信号：`VGA_R0`-`VGA_R7`（8位红色）、`VGA_G0`-`VGA_G7`（8位绿色）、`VGA_B0`-`VGA_B7`（8位蓝色）
7. **UART串口**：`UART_TX`（发送）、`UART_RX`（接收）
8. **PS/2键盘接口**：`PS2_CLK`（时钟）、`PS2_DAT`（数据）

## 引脚方向说明

| 引脚类型 | 方向 | 说明 |
|---------|------|------|
| `BTNC`, `BTNU`, `BTND`, `BTNL`, `BTNR` | 输入 | 按钮信号，按下时为高电平 |
| `SW0`-`SW15` | 输入 | 拨码开关，向上为高电平 |
| `LD0`-`LD15` | 输出 | 普通LED，高电平点亮 |
| `R16`, `G16`, `B16`, `R17`, `G17`, `B17` | 输出 | RGB LED颜色分量，高电平点亮对应颜色 |
| `SEG0A`-`SEG7G`, `DEC0P`-`DEC7P` | 输出 | 七段数码管段选信号，低电平点亮对应段 |
| `VGA_VSYNC`, `VGA_HSYNC`, `VGA_BLANK_N` | 输出 | VGA同步和消隐信号 |
| `VGA_R0`-`VGA_R7`, `VGA_G0`-`VGA_G7`, `VGA_B0`-`VGA_B7` | 输出 | VGA颜色信号 |
| `UART_TX` | 输出 | UART发送数据 |
| `UART_RX` | 输入 | UART接收数据 |
| `PS2_CLK`, `PS2_DAT` | 输入 | PS/2键盘时钟和数据信号 |


## 使用注意事项

1. 引脚名称在约束文件（`.nxdc`）中必须完全匹配，包括大小写
2. 输入引脚在 RTL 设计中应定义为 `input` 端口
3. 输出引脚在 RTL 设计中应定义为 `output` 端口
4. 七段数码管为共阳极设计，段选信号低电平有效
5. VGA 信号时序需符合标准 VGA 时序规范
6. 复位信号 `RST` 未包含在引脚列表中，因为 NVBoard 包含内部状态，仅复位 RTL 设计会导致状态不一致。全系统复位可通过退出并重新运行 NVBoard 实现。

# 注意事项
1. 建议保持Verilog项目的顶层模块被命名为`top`,包含顶层模块的文件名为`top.v`。尽管项目被设计支持通过修改`Makefile`中的`TOPNAME`变量来适应不同名称的顶层模块，但没有经过严格测试，仍然可能存在一定的兼容性问题。
