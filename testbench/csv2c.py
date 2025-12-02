import sys
import csv
import re
import os
from collections import defaultdict

# CSV中的配置名到宏定义名的映射
CONFIG_MAPPING = {
    'max stimulate time': 'MAX_TIME_SIM',
    'half clock cycle': 'HALF_CLK_CYCLE',
    'enable clock input': 'ENABLE_CLK_INPUT',
    'clock pin name': 'CLK_PIN_NAME'
}

def parse_testbench_csv(csv_path):
    """解析testbench.csv文件，返回配置和事件"""
    events = []
    config = {}
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        
        # 读取第一行（可能包含配置信息）
        try:
            header = next(reader)
        except StopIteration:
            return config, events
        
        # 解析配置信息（从第5列开始可能是配置）
        for i in range(4, len(header), 2):
            if i + 1 < len(header):
                config_name = header[i].strip().lower()  # 转换为小写以便匹配
                config_value = header[i + 1].strip()
                if config_name and config_value:
                    # 使用映射表转换为标准宏名
                    macro_name = CONFIG_MAPPING.get(config_name, config_name.upper().replace(' ', '_'))
                    config[macro_name] = config_value
        
        # 读取后续行
        for row in reader:
            if len(row) < 3:  # 至少需要时间、引脚、值三列
                continue
                
            time_ps = row[0].strip()
            pin = row[1].strip()
            value = row[2].strip()
            
            # 检查是否有配置信息在第5列之后
            for i in range(4, len(row), 2):
                if i + 1 < len(row):
                    config_name = row[i].strip().lower()  # 转换为小写以便匹配
                    config_value = row[i + 1].strip()
                    if config_name and config_value:
                        # 使用映射表转换为标准宏名
                        macro_name = CONFIG_MAPPING.get(config_name, config_name.upper().replace(' ', '_'))
                        config[macro_name] = config_value
            
            if time_ps and pin and value:
                # 处理Note列（第4列，索引3）
                note = row[3].strip() if len(row) > 3 else ""
                events.append({
                    'time': time_ps,
                    'pin': pin,
                    'value': value,
                    'note': note
                })
    
    return config, events

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

def validate_and_sort_events(events):
    """验证事件并排序，检查同时同引脚的赋值冲突"""
    if not events:
        return []
    
    # 按时间分组
    time_groups = defaultdict(list)
    
    for event in events:
        time = event['time']
        pin = event['pin']
        time_groups[time].append(event)
    
    # 检查冲突
    for time, time_events in time_groups.items():
        pins = {}
        for event in time_events:
            pin = event['pin']
            if pin in pins:
                raise ValueError(f"时间 {time} 时，引脚 {pin} 被多次赋值")
            pins[pin] = event['value']
    
    # 按时间排序（转为整数比较，但保持字符串格式）
    try:
        # 尝试转换为整数排序
        sorted_events = sorted(events, key=lambda x: int(x['time']))
    except ValueError:
        # 如果时间不是数字，按字符串排序
        sorted_events = sorted(events, key=lambda x: x['time'])
    
    return sorted_events

def get_unique_pins(events):
    """获取所有唯一的引脚"""
    pins = set()
    for event in events:
        pins.add(event['pin'])
    return pins

def generate_macro_code(config, events):
    """生成VERILATOR_MAIN_LOOP宏的代码"""
    lines = []
    
    # 获取所有引脚
    pins = get_unique_pins(events)
    
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
    
    if events:
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
                # 尝试转换为整数排序
                times.sort(key=lambda x: int(x))
            except ValueError:
                # 如果时间不是数字，按字符串排序
                times.sort()
            
            # 处理每个时间点的事件
            current_time = '0'
            for i, time in enumerate(times):
                # STEP到当前时间（如果是第一个非零时间）
                if current_time != time:
                    lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL({time});")
                    current_time = time
                
                # 添加该时间点的所有赋值
                for event in time_events[time]:
                    lines.append(f"    VERILATOR_SWITCH_INPUT_TO({event['pin']}, {event['value']});")
            
            # 如果最后有时间大于0的事件，更新current_time
            if times:
                current_time = times[-1]
    
    # 最后执行STEP到MAX_TIME_SIM
    max_time = config.get('MAX_TIME_SIM', '10')
    # 确保current_time不等于max_time，避免重复STEP
    if 'current_time' in locals() and current_time != max_time:
        lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL(MAX_TIME_SIM)")
    else:
        lines.append(f"    VERILATOR_STEP_AND_EVAL_UNTIL(MAX_TIME_SIM)")
    
    return lines

def generate_sim_config_h(config, macro_lines, output_path):
    """生成sim_config.h文件"""
    content = """#ifndef __SIM_CONFIG__
#define __SIM_CONFIG__
#include "sim_main.h"

"""

    # 添加配置宏（按特定顺序）
    preferred_order = ['MAX_TIME_SIM', 'HALF_CLK_CYCLE', 'ENABLE_CLK_INPUT', 'CLK_PIN_NAME']
    
    # 先添加优先顺序的宏
    for macro in preferred_order:
        if macro in config:
            content += f"#define {macro} {config[macro]}\n"
    
    # 添加其他宏（按字母顺序排序）
    other_macros = sorted([k for k in config.keys() if k not in preferred_order])
    for macro in other_macros:
        content += f"#define {macro} {config[macro]}\n"
    
    # 确保必要的宏存在
    required_macros = {
        'MAX_TIME_SIM': '10',
        'HALF_CLK_CYCLE': '2',
        'ENABLE_CLK_INPUT': '1',
        'CLK_PIN_NAME': 'clk'
    }
    
    for macro, default in required_macros.items():
        if macro not in config:
            content += f"#define {macro} {default}\n"
    
    content += "\n#define VERILATOR_MAIN_LOOP()          \\\n"
    
    # 添加宏内容
    if macro_lines:
        for i, line in enumerate(macro_lines):
            if i == len(macro_lines) - 1:
                content += line + "\n"
            else:
                content += line + " \\\n"
    else:
        # 如果没有事件，生成一个基本宏
        content += "    VERILATOR_STEP_AND_EVAL_UNTIL(MAX_TIME_SIM)\n"
    
    content += "\n#endif\n"
    
    # 写入文件
    with open(output_path, 'w') as f:
        f.write(content)
    
    return content

def main():
    if len(sys.argv) < 2:
        print("用法: python generate_config.py testbench.csv [sim_config.h]")
        print("说明: 如果提供sim_config.h，将读取其中的配置，否则从CSV提取配置")
        print("      输出文件为sim_config.h")
        print("\n配置映射关系:")
        for csv_name, macro_name in CONFIG_MAPPING.items():
            print(f"  {csv_name} -> {macro_name}")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    config_h_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = config_h_path
    
    try:
        # 解析CSV文件
        csv_config, events = parse_testbench_csv(csv_path)
        
        print("从CSV文件解析到的配置:")
        for key, value in csv_config.items():
            print(f"  {key}: {value}")
        
        # 解析现有配置（如果有）
        existing_config = parse_sim_config_h(config_h_path)
        
        # 合并配置（CSV中的配置优先级更高）
        config = {**existing_config, **csv_config}
        
        # 验证和排序事件
        sorted_events = validate_and_sort_events(events)
        
        print(f"\n从CSV文件解析到 {len(sorted_events)} 个事件:")
        for event in sorted_events:
            print(f"  时间 {event['time']}: {event['pin']} = {event['value']}")
        
        if existing_config:
            print(f"\n从sim_config.h解析到 {len(existing_config)} 个配置项")
        
        # 生成宏代码
        macro_lines = generate_macro_code(config, sorted_events)
        
        # 生成sim_config.h文件
        output_content = generate_sim_config_h(config, macro_lines, output_path)
        
        print(f"\n成功生成 {output_path}")
        print(f"共生成 {len(macro_lines)} 行宏代码")
        
        # 打印生成的宏内容供检查
        print("\n生成的VERILATOR_MAIN_LOOP宏内容预览:")
        print("#define VERILATOR_MAIN_LOOP()          \\")
        for line in macro_lines:
            print(f"    {line}")
        
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