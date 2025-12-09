import sys
import csv
import re
import os
from collections import defaultdict

# CSV中的配置名到宏定义名的映射
CONFIG_MAPPING = {
    'enable limit time stimulation': 'ENABLE_LIMIT_TIME_STIMULATION',
    'max stimulate time': 'MAX_TIME_SIM',
    'half clock cycle': 'HALF_CLK_CYCLE',
    'enable clock input': 'ENABLE_CLK_INPUT',
    'clock pin name': 'CLK_PIN_NAME',
    'enable INITIAL block': 'ENABLE_INITIAL_BLOCK',
    'INITIAL block max stimulate time': 'INITIAL_BLOCK_MAX_STIMULATE_TIME',
    'enable FOREVER block': 'ENABLE_FOREVER_BLOCK',
    'FOREVER block cycle': 'FOREVER_BLOCK_CYCLE',
    'enable wavefrom acquisition':'ENABLE_WAVEFROM_ACQUISITION'
}

def parse_testbench_csv(csv_path):
    """解析testbench.csv文件，返回配置、INITIAL事件和FOREVER事件"""
    initial_events = []
    forever_events = []
    config = {}
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        
        # 读取第一行（表头）
        try:
            header = next(reader)
        except StopIteration:
            return config, initial_events, forever_events
        
        # 读取后续行
        for row in reader:
            # 解析INITIAL部分（列0-4）
            if len(row) > 1 and row[1].strip():  # 有时间值
                time_ps = row[1].strip()
                pin = row[2].strip() if len(row) > 2 else ""
                value = row[3].strip() if len(row) > 3 else ""
                note = row[4].strip() if len(row) > 4 else ""
                
                if time_ps and pin and value:
                    initial_events.append({
                        'time': time_ps,
                        'pin': pin,
                        'value': value,
                        'note': note
                    })
            
            # 解析FOREVER部分（列5-9）
            if len(row) > 6 and row[6].strip():  # 有时间值
                time_ps = row[6].strip()
                pin = row[7].strip() if len(row) > 7 else ""
                value = row[8].strip() if len(row) > 8 else ""
                note = row[9].strip() if len(row) > 9 else ""
                
                if time_ps and pin and value:
                    forever_events.append({
                        'time': time_ps,
                        'pin': pin,
                        'value': value,
                        'note': note
                    })
            
            # 解析Configuration部分（列10-12）
            if len(row) > 10 and row[10].strip():  # 有配置名
                config_name = row[10].strip().lower()
                config_value = row[11].strip() if len(row) > 11 else ""
                note = row[12].strip() if len(row) > 12 else ""
                
                if config_name and config_value:
                    # 使用映射表转换为标准宏名
                    macro_name = CONFIG_MAPPING.get(config_name, config_name.upper().replace(' ', '_'))
                    config[macro_name] = config_value
    
    return config, initial_events, forever_events

def parse_sim_config_h(config_h_path):
    """解析现有的sim_config.h文件（如果需要）"""
    config = {}
    if config_h_path and os.path.exists(config_h_path):
        try:
            with open(config_h_path, 'r') as f:
                content = f.read()
                # 提取宏定义
                pattern = r'#define\s+(\w+)\s+(.+)'
                matches = re.findall(pattern, content)
                for name, value in matches:
                    # 去除注释
                    value = value.split('//')[0].strip()
                    # 处理多行宏定义（以\结尾的）
                    if value.endswith('\\'):
                        # 收集多行宏
                        full_value = value
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('#define'):
                                continue
                            if '\\' in line:
                                full_value += '\n' + line.strip()
                            else:
                                break
                        config[name] = full_value
                    else:
                        config[name] = value
        except Exception as e:
            print(f"警告: 解析sim_config.h时出错: {e}")
    return config

def validate_and_sort_events(events, max_time_config_name, config, block_name):
    """验证事件并排序，检查同时同引脚的赋值冲突，验证时间合法性"""
    if not events:
        return []
    
    # 获取最大时间
    max_time = None
    if max_time_config_name in config:
        try:
            max_time = int(config[max_time_config_name])
        except ValueError:
            print(f"警告: {max_time_config_name} 的值 '{config[max_time_config_name]}' 不是有效的整数")
    
    # 按时间分组
    time_groups = defaultdict(list)
    
    for event in events:
        time_str = event['time']
        pin = event['pin']
        
        # 检查时间是否为数字
        try:
            time_val = int(time_str)
        except ValueError:
            raise ValueError(f"{block_name}块中时间 '{time_str}' 不是有效的整数")
        
        # 检查时间是否超过最大时间
        if max_time is not None and time_val >= max_time:
            print(f"警告: {block_name}块中时间 {time_val} >= {max_time_config_name}({max_time})，事件将被忽略")
            continue
        
        time_groups[time_str].append(event)
    
    # 检查冲突
    valid_events = []
    for time_str, time_events in time_groups.items():
        pins = {}
        for event in time_events:
            pin = event['pin']
            if pin in pins:
                raise ValueError(f"{block_name}块中时间 {time_str} 时，引脚 {pin} 被多次赋值")
            pins[pin] = event['value']
            valid_events.append(event)
    
    # 按时间排序（转为整数比较）
    try:
        sorted_events = sorted(valid_events, key=lambda x: int(x['time']))
    except ValueError:
        # 如果时间不是数字，按字符串排序
        sorted_events = sorted(valid_events, key=lambda x: x['time'])
    
    return sorted_events

def generate_initial_block_code(events, config):
    """生成VERILATOR_MAIN_INITIAL_BLOCK宏的代码"""
    lines = []
    
    # 添加ENABLE_INITIAL_BLOCK检查
    lines.append("    if (!ENABLE_INITIAL_BLOCK)")
    lines.append("        break;")
    
    if not events:
        # 如果没有事件，直接STEP到最大时间
        lines.append("    VERILATOR_STEP_AND_EVAL_UNTIL(INITIAL_BLOCK_MAX_STIMULATE_TIME);")
        return lines
    
    # 获取所有引脚
    pins = set()
    for event in events:
        pins.add(event['pin'])
    
    # t=0时的显式赋值
    zero_time_assignments = {}
    for event in events:
        if event['time'] == '0':
            zero_time_assignments[event['pin']] = event['value']
    
    # 为t=0时未显式赋值的引脚赋值为0
    for pin in pins:
        if pin not in zero_time_assignments:
            lines.append(f"    VERILATOR_SWITCH_INPUT_TO({pin}, 0);")
    
    # 添加t=0时的显式赋值
    for pin, value in zero_time_assignments.items():
        lines.append(f"    VERILATOR_SWITCH_INPUT_TO({pin}, {value});")
    
    # 按时间顺序处理事件（排除t=0）
    non_zero_events = [e for e in events if e['time'] != '0']
    
    if non_zero_events:
        # 按时间分组
        time_events = defaultdict(list)
        for event in non_zero_events:
            time_events[event['time']].append(event)
        
        # 获取所有时间并排序
        times = list(time_events.keys())
        try:
            times.sort(key=lambda x: int(x))
        except ValueError:
            times.sort()
        
        # 处理每个时间点的事件
        current_time = '0'
        for time in times:
            # STEP到当前时间
            if current_time != time:
                lines.append(f"    nvboard_update();")
                lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL({time});")
                current_time = time
            
            # 添加该时间点的所有赋值
            for event in time_events[time]:

                lines.append(f"    VERILATOR_SWITCH_INPUT_TO({event['pin']}, {event['value']});")
    
    # 最后执行STEP到INITIAL_BLOCK_MAX_STIMULATE_TIME
    max_time = config.get('INITIAL_BLOCK_MAX_STIMULATE_TIME', '20')
    if 'current_time' in locals() and current_time != max_time:
        lines.append(f"    nvboard_update();")
        lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL(INITIAL_BLOCK_MAX_STIMULATE_TIME);")
    else:
        lines.append(f"    nvboard_update();")
        lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL(INITIAL_BLOCK_MAX_STIMULATE_TIME);")
    
    return lines

def generate_forever_block_code(events, config):
    """生成VERILATOR_MAIN_FOREVER_BLOCK宏的代码"""
    lines = []
    
    # 添加ENABLE_FOREVER_BLOCK检查
    lines.append("    if (!ENABLE_FOREVER_BLOCK)")
    lines.append("        break;")
    
    if not events:
        # 如果没有事件，直接STEP到周期时间
        lines.append("    VERILATOR_STEP_AND_EVAL_UNTIL(FOREVER_BLOCK_CYCLE + T_start);")
        return lines
    
    # 获取所有引脚
    pins = set()
    for event in events:
        pins.add(event['pin'])
    
    # t=0时的显式赋值
    zero_time_assignments = {}
    for event in events:
        if event['time'] == '0':
            zero_time_assignments[event['pin']] = event['value']
    
    # 为t=0时未显式赋值的引脚赋值为0
    for pin in pins:
        if pin not in zero_time_assignments:
            lines.append(f"    VERILATOR_SWITCH_INPUT_TO({pin}, 0);")
    
    # 添加t=0时的显式赋值
    for pin, value in zero_time_assignments.items():
        lines.append(f"    VERILATOR_SWITCH_INPUT_TO({pin}, {value});")
    
    # 按时间顺序处理事件（排除t=0）
    non_zero_events = [e for e in events if e['time'] != '0']
    
    if non_zero_events:
        # 按时间分组
        time_events = defaultdict(list)
        for event in non_zero_events:
            time_events[event['time']].append(event)
        
        # 获取所有时间并排序
        times = list(time_events.keys())
        try:
            times.sort(key=lambda x: int(x))
        except ValueError:
            times.sort()
        
        # 处理每个时间点的事件
        current_time = '0'
        for time in times:
            # STEP到当前时间
            if current_time != time:
                lines.append(f"    nvboard_update();")
                lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL({time} + T_start);")
                current_time = time
            
            # 添加该时间点的所有赋值
            for event in time_events[time]:
                
                lines.append(f"    VERILATOR_SWITCH_INPUT_TO({event['pin']}, {event['value']});")
    
    # 最后执行STEP到FOREVER_BLOCK_CYCLE
    max_time = config.get('FOREVER_BLOCK_CYCLE', '20')
    if 'current_time' in locals() and current_time != max_time:
        lines.append(f"    nvboard_update();")
        lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL(FOREVER_BLOCK_CYCLE + T_start);")
    else:
        lines.append(f"    nvboard_update();")
        lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL(FOREVER_BLOCK_CYCLE + T_start);")
    
    return lines

def generate_sim_config_h(config, initial_lines, forever_lines, output_path):
    """生成sim_config.h文件"""
    content = """#ifndef __SIM_CONFIG__
#define __SIM_CONFIG__
#include "sim_main.h"
#include "verilated.h"

"""

    
    # 添加配置宏（按特定顺序）
    preferred_order = [
        'ENABLE_LIMIT_TIME_STIMULATION',
        'MAX_TIME_SIM',
        'HALF_CLK_CYCLE',
        'ENABLE_CLK_INPUT',
        'CLK_PIN_NAME',
        'ENABLE_INITIAL_BLOCK',
        'INITIAL_BLOCK_MAX_STIMULATE_TIME',
        'ENABLE_FOREVER_BLOCK',
        'FOREVER_BLOCK_CYCLE'
    ]
    
    # 先添加优先顺序的宏
    for macro in preferred_order:
        if macro in config:
            value = config[macro]
            # 处理字符串值（添加引号）
            if macro == 'CLK_PIN_NAME' and not (value.startswith('"') or value.startswith("'")):
                content += f"#define {macro} {value}\n"
            else:
                content += f"#define {macro} {value}\n"

    # 添加其他宏（按字母顺序排序）
    other_macros = sorted([k for k in config.keys() if k not in preferred_order])
    for macro in other_macros:
        content += f"#define {macro} {config[macro]}\n"

    # 确保必要的宏存在
    required_macros = {
        'ENABLE_LIMIT_TIME_STIMULATION': '1',
        'MAX_TIME_SIM': '20',
        'HALF_CLK_CYCLE': '2',
        'ENABLE_CLK_INPUT': '0',
        'CLK_PIN_NAME': 'clk',
        'ENABLE_INITIAL_BLOCK': '1',
        'INITIAL_BLOCK_MAX_STIMULATE_TIME': '20',
        'ENABLE_FOREVER_BLOCK': '0',
        'FOREVER_BLOCK_CYCLE': '20'
    }

    for macro, default in required_macros.items():
        if macro not in config:
            content += f"#define {macro} {default}\n"

    # 添加INITIAL_BLOCK宏
    content += "\n#define VERILATOR_MAIN_INITIAL_BLOCK()                                   \\\n"
    content += "    do                                                                   \\\n"
    content += "    {                                                                    \\\n"
    
    if initial_lines:
        for i, line in enumerate(initial_lines):
            if i == len(initial_lines) :
                content += f"        {line}\n"
            else:
                content += f"        {line} \\\n"
    else:
        content += "        if (!ENABLE_INITIAL_BLOCK)                                       \\\n"
        content += "            break;                                                       \\\n"
        content += "        VERILATOR_STEP_AND_EVAL_UNTIL(INITIAL_BLOCK_MAX_STIMULATE_TIME); \\ \n"
    
    content += "    } while (0)\n"
    
    # 添加FOREVER_BLOCK宏
    content += "\n#define VERILATOR_MAIN_FOREVER_BLOCK()                               \\\n"
    content += "    vluint64_t T_start;                                              \\\n"
    content += "    do                                                               \\\n"
    content += "    {                                                                \\\n"
    content += "        T_start = T;                                                 \\\n"
    
    if forever_lines:
        for i, line in enumerate(forever_lines):
            if i == len(forever_lines) :
                content += f"        {line}\n"
            else:
                content += f"        {line} \\\n"
    else:
        content += "        if (!ENABLE_FOREVER_BLOCK)                                   \\\n"
        content += "            break;                                                   \\\n"
        content += "        VERILATOR_STEP_AND_EVAL_UNTIL(FOREVER_BLOCK_CYCLE + T_start) \\\n"
    
    content += "    } while (1)\n"
    
    content += "\n#endif //__SIM_CONFIG__\n"
    
    # 写入文件
    with open(output_path, 'w') as f:
        f.write(content)
    
    return content

def main():
    if len(sys.argv) < 2:
        print("用法: python csv2c.py testbench.csv [sim_config.h]")
        print("说明: 如果提供sim_config.h，将读取其中的配置，否则从CSV提取配置")
        print("      输出文件为sim_config.h")
        print("\n配置映射关系:")
        for csv_name, macro_name in CONFIG_MAPPING.items():
            print(f"  {csv_name} -> {macro_name}")
        sys.exit(1)

    
    csv_path =sys.argv[1]
    config_h_path =sys.argv[2] if len(sys.argv) > 2 else None
    output_path = config_h_path if config_h_path else "include/sim_config.h"
    
    try:
        # 解析CSV文件
        csv_config, initial_events, forever_events = parse_testbench_csv(csv_path)
        """
        print("从CSV文件解析到的配置:")
        for key, value in csv_config.items():
            print(f"  {key}: {value}")
        
        """
        
        # 解析现有配置（如果有）
        existing_config = parse_sim_config_h(config_h_path)
        if '__SIM_CONFIG__' in existing_config:
            del existing_config['__SIM_CONFIG__']
        # 合并配置（CSV中的配置优先级更高）
        config = {**existing_config, **csv_config}
        """
        print(config)
        
        print(f"\n从CSV文件解析到 {len(initial_events)} 个INITIAL事件:")
        for event in initial_events:
            print(f"  时间 {event['time']}: {event['pin']} = {event['value']}")
        
        print(f"\n从CSV文件解析到 {len(forever_events)} 个FOREVER事件:")
        for event in forever_events:
            print(f"  时间 {event['time']}: {event['pin']} = {event['value']}")
        
        if existing_config:
            print(f"\n从sim_config.h解析到 {len(existing_config)} 个配置项")
        
        """
        
        
        # 验证和排序INITIAL事件
        try:
            sorted_initial_events = validate_and_sort_events(
                initial_events, 
                'INITIAL_BLOCK_MAX_STIMULATE_TIME', 
                config, 
                'INITIAL'
            )
            print(f"\n验证后保留 {len(sorted_initial_events)} 个INITIAL事件")
        except ValueError as e:
            print(f"INITIAL事件验证错误: {e}")
            sys.exit(1)
        
        # 验证和排序FOREVER事件
        try:
            sorted_forever_events = validate_and_sort_events(
                forever_events, 
                'FOREVER_BLOCK_CYCLE', 
                config, 
                'FOREVER'
            )
            print(f"验证后保留 {len(sorted_forever_events)} 个FOREVER事件")
        except ValueError as e:
            print(f"FOREVER事件验证错误: {e}")
            sys.exit(1)
        
        # 生成INITIAL_BLOCK宏代码
        initial_lines = generate_initial_block_code(sorted_initial_events, config)
        
        # 生成FOREVER_BLOCK宏代码
        forever_lines = generate_forever_block_code(sorted_forever_events, config)
        
        # 生成sim_config.h文件
        output_content = generate_sim_config_h(config, initial_lines, forever_lines, output_path)
        """
        print(f"\n成功生成 {output_path}")
        print(f"INITIAL_BLOCK生成 {len(initial_lines)} 行代码")
        print(f"FOREVER_BLOCK生成 {len(forever_lines)} 行代码")
        
        # 打印生成的宏内容供检查
        print("\n生成的VERILATOR_MAIN_INITIAL_BLOCK宏内容预览:")
        print("#define VERILATOR_MAIN_INITIAL_BLOCK()                                   \\")
        for line in initial_lines:
            print(f"    {line}")
        
        print("\n生成的VERILATOR_MAIN_FOREVER_BLOCK宏内容预览:")
        print("#define VERILATOR_MAIN_FOREVER_BLOCK()                               \\")
        for line in forever_lines:
            print(f"    {line}")
        
        """
        
        
        # 如果输出目录不是当前目录，显示完整路径
        full_output_path = os.path.abspath(output_path)
        if full_output_path != os.path.abspath("."):
            print(f"\n输出文件位置: {full_output_path}")
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"验证错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
