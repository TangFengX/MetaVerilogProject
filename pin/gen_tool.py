import re
import sys
import os

class NXDCConverter:
    def __init__(self, pins_db_path):
        # 自动生成引脚数据库文件（如果不存在）
        self.ensure_pins_db(pins_db_path)
        self.valid_pins = self.load_pins(pins_db_path)
        self.summary = []

    def ensure_pins_db(self, path):
        """如果pins文件不存在，则创建它"""
        if not os.path.exists(path):
            pins_data = """
            BTNC BTNU BTND BTNL BTNR
            SW0 SW1 SW2 SW3 SW4 SW5 SW6 SW7 SW8 SW9 SW10 SW11 SW12 SW13 SW14 SW15
            LD0 LD1 LD2 LD3 LD4 LD5 LD6 LD7 LD8 LD9 LD10 LD11 LD12 LD13 LD14 LD15
            R16 G16 B16 R17 G17 B17
            SEG0A SEG0B SEG0C SEG0D SEG0E SEG0F SEG0G DEC0P
            SEG1A SEG1B SEG1C SEG1D SEG1E SEG1F SEG1G DEC1P
            SEG2A SEG2B SEG2C SEG2D SEG2E SEG2F SEG2G DEC2P
            SEG3A SEG3B SEG3C SEG3D SEG3E SEG3F SEG3G DEC3P
            SEG4A SEG4B SEG4C SEG4D SEG4E SEG4F SEG4G DEC4P
            SEG5A SEG5B SEG5C SEG5D SEG5E SEG5F SEG5G DEC5P
            SEG6A SEG6B SEG6C SEG6D SEG6E SEG6F SEG6G DEC6P
            SEG7A SEG7B SEG7C SEG7D SEG7E SEG7F SEG7G DEC7P
            VGA_VSYNC VGA_HSYNC VGA_BLANK_N
            VGA_R0 VGA_R1 VGA_R2 VGA_R3 VGA_R4 VGA_R5 VGA_R6 VGA_R7
            VGA_G0 VGA_G1 VGA_G2 VGA_G3 VGA_G4 VGA_G5 VGA_G6 VGA_G7
            VGA_B0 VGA_B1 VGA_B2 VGA_B3 VGA_B4 VGA_B5 VGA_B6 VGA_B7
            UART_TX UART_RX PS2_CLK PS2_DAT
            """.strip()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(pins_data)
            print(f"Created pins database: {path}")

    def load_pins(self, path):
        with open(path, 'r') as f:
            return set(f.read().split())

    def expand_range(self, prefix, start, end):
        res = []
        prefix = prefix or ""
        if start.isdigit() and end.isdigit():
            s, e = int(start), int(end)
            step = -1 if s > e else 1
            for i in range(s, e + step, step):
                res.append(f"{prefix}{i}")
        elif len(start) == 1 and len(end) == 1:
            s, e = ord(start), ord(end)
            step = -1 if s > e else 1
            for i in range(s, e + step, step):
                res.append(f"{prefix}{chr(i)}")
        return res

    def expand_curly(self, prefix, content):
        res = []
        prefix = prefix or ""
        if ' ' in content.strip():
            items = content.strip().split()
            for item in items:
                if not item.isdigit() and len(item) > 1:
                    for char in item: res.append(f"{prefix}{char}")
                else:
                    res.append(f"{prefix}{item}")
        else:
            for char in content:
                res.append(f"{prefix}{char}")
        return res

    def process_description(self, description):
        # 1. 处理大括号扩展 prefix{...}
        def curly_repl(m):
            return " " + " ".join(self.expand_curly(m.group(1), m.group(2))) + " "
        description = re.sub(r"([A-Za-z0-9_]*)\{([^}]*)\}", curly_repl, description)

        # 2. 处理范围扩展 (修复的关键：移除 \b 并区分数字和字母)
        # 匹配数字范围 (如 SW7-0, LD15-0)
        def num_range_repl(m):
            return " " + " ".join(self.expand_range(m.group(1), m.group(2), m.group(3))) + " "
        description = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)?(\d+)-(\d+)", num_range_repl, description)

        # 匹配字母范围 (如 A-G)
        def alpha_range_repl(m):
            return " " + " ".join(self.expand_range(m.group(1), m.group(2), m.group(3))) + " "
        description = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)?([A-Z])-([A-Z])", alpha_range_repl, description)

        return [p for p in re.split(r"[\s,]+", description.strip()) if p]

    def process_line(self, line):
        line = line.strip()
        if not line or '=' in line: return line

        match = re.match(r"(\w+)\s*\((.*)\)", line)
        if not match: return line

        module_pin_name, description = match.groups()
        expanded_pins = self.process_description(description)

        for p in expanded_pins:
            if p not in self.valid_pins:
                print(f"\033[31mSyntax Error: Invalid pin '{p}' in line: {line}\033[0m")
                sys.exit(1)

        self.summary.append(f"{module_pin_name} [{len(expanded_pins)-1}:0]")
        return f"{module_pin_name} ({', '.join(expanded_pins)})"

    def convert(self, input_path, output_path):
        if not os.path.exists(input_path):
            print(f"Error: {input_path} not found.")
            return

        with open(input_path, 'r') as f:
            lines = f.readlines()

        final_lines = []
        for line in lines:
            line = line.strip()
            if not line: continue

            # ... (前面的代码保持不变) ...

            if line.startswith('@'):
                # 1. 解析循环范围 @0-7
                loop_match = re.match(r"@(\d+|[A-Z])-(\d+|[A-Z])\s+(.*)", line)
                if loop_match:
                    start, end, body = loop_match.groups()
                    s_val = int(start) if start.isdigit() else ord(start)
                    e_val = int(end) if end.isdigit() else ord(end)
                    step = -1 if s_val > e_val else 1
                    
                    for i in range(s_val, e_val + step, step):
                        current_val = str(i) if start.isdigit() else chr(i)
                        current_line = body
                        
                        # 2. 核心修复：支持 [@ 后面跟任意数学运算 ]
                        # 匹配 [@ ... ] 结构，内部允许包含 + - * / % ( ) 和数字
                        # 使用非贪婪匹配 [^\]]+ 确保匹配到最近的 ]
                        exprs = re.findall(r"\[@([^\]]+)\]", current_line)
                        for expr_content in exprs:
                            # 构造完整的 Python 表达式，例如将 "@*3+1" 变成 "1*3+1"
                            full_expr = f"{i}{expr_content}"
                            try:
                                # 执行计算并强制转为整数
                                res_val = int(eval(full_expr))
                                # 将原文本 [@*3+1] 替换为计算结果
                                current_line = current_line.replace(f"[@{expr_content}]", str(res_val))
                            except Exception as e:
                                print(f"\033[31m[Calc Error] Failed to eval '[@{expr_content}]': {e}\033[0m")
                                sys.exit(1)
                        
                        # 3. 替换剩余的孤立 @ 变量
                        current_line = current_line.replace('@', current_val)
                        final_lines.append(self.process_line(current_line))
                else:
                    print(f"Loop Error: {line}"); sys.exit(1)
            else:
                final_lines.append(self.process_line(line))

        with open(output_path, 'w') as f:
            f.write('\n'.join(final_lines) + '\n')

        print("\n\033[32m=== Pin Mapping Summary ===\033[0m")
        for s in self.summary: print(f"  {s}")
        print("\033[32m===========================\033[0m\n")



if __name__ == "__main__":
    pwd=os.path.dirname(os.path.abspath(__file__))+"/"
    conv = NXDCConverter(pwd+"pins")
    conv.convert(pwd+"top.nxdclite", pwd+"top.nxdc")
    print("Success: top.nxdc has been generated.")