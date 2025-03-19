import pandas as pd

REGISTER = {"A": "0", "X": "1", "L": "2", "B": "3", "S": "4", "T": "5", "F": "6"}

# Define global opcode table and directives based on the provided code
OPCODE_TABLE = {
    "STL": "14", "LDB": "68", "BASE": None, "COMP": "28", "JEQ": "30",
    "J": "3C", "JSUB": "48", "LDA": "00", "STA": "0C", "CLEAR": "B4",
    "LDT": "74", "TD": "E0", "RD": "D8", "COMPR": "A0", "STCH": "54",
    "TIXR": "B8", "LDCH": "50", "WD": "DC", "RSUB": "4C", "JLT": "38",
    "STX": "10", "LDT": "74"
}

DIRECTIVES = ["START",  "+", "BASE", "END", "BYTE", "RESW", "RESB"]

# Helper function for hexadecimal addition
def hex_add(hex1, hex2):
    return f"{int(hex1, 16) + int(hex2, 16):X}"

# Helper function to parse source code
def parse_line(line):
    # 如果該行是純註解（以 . 開頭），直接返回 None
    if line.strip().startswith("."):
        return None

    # 將註解部分移除（以 . 開頭的部分視為註解）
    line = line.split(".", 1)[0].strip()


    parts = line.split()
    if len(parts) == 3:
        return {"label": parts[0], "opcode": parts[1], "operand": parts[2]}
    elif len(parts) == 2:
        return {"label": None, "opcode": parts[0], "operand": parts[1]}
    elif len(parts) == 1:
        return {"label": None, "opcode": parts[0], "operand": None}
    return None

# Pass One: Build symbol table and intermediate representation
def pass_one(source_code):
    locctr = None
    symtab = {}
    intermediate = []
    base_address = None  # 用於記錄 BASE 指令的位址

    print('symbol table:')
    for line in source_code:
        line = line.strip()
        parsed = parse_line(line)

        if not parsed:
            continue
        
        label, opcode, operand = parsed["label"], parsed["opcode"], parsed["operand"]

        # Handle START directive
        if opcode == "START":
            locctr = operand
            intermediate.append({"loc": locctr, "line": line})
            print(f"{label}: {locctr}")
            symtab[label] = locctr
            continue



        # Record symbol in symbol table if it has a label
        if label:
            if label in OPCODE_TABLE or label in DIRECTIVES:
                raise ValueError(f"Label '{label}' cannot be an opcode or directive.")
            print(f"{label}: {locctr}")
            symtab[label] = locctr

        # Add current location and line to intermediate representation
        intermediate.append({"loc": locctr, "line": line})

        if opcode == "BASE":
            base_address = operand  # 取得 BASE 的位址
            continue

        if opcode == "END":
            break

        # Update LOCCTR based on instruction size
        if opcode[0] == "+":
            locctr = hex_add(locctr, "4")
        elif opcode in OPCODE_TABLE:
            if opcode == "CLEAR" or opcode == "COMPR" or opcode == "TIXR":
                locctr = hex_add(locctr, "2")
            else:
                locctr = hex_add(locctr, "3")
        elif opcode == "RESW":
            locctr = hex_add(locctr, f"{int(operand) * 3}")
        elif opcode == "RESB":
            locctr = hex_add(locctr, str(hex(int(operand))))
        elif opcode == "BYTE":
            if operand[0] == "C":
                locctr = hex_add(locctr, str(len(operand) - 3))  # Account for quotes
            else:
                locctr = hex_add(locctr, "1")
        else:
            raise ValueError(f"Unknown opcode: {opcode}")
        

    return symtab, intermediate, base_address


def format_object_code(opcode, operand, locctr, symtab, base):
    #deal with RSUB
    if opcode == "RSUB" or opcode == "+RSUB":
        op_bin = f"{int(OPCODE_TABLE[opcode], 16):06b}"
        ni_bin = "11"
        e = 0
        if opcode[0] == "+":
            e = 1
            xbpe_bin = f"{000}{e}"
            return f"{(int(op_bin,2) | int(ni_bin,2)):02X}{int(xbpe_bin, 2):01X}00000"
        xbpe_bin = f"{000}{e}"
        return f"{(int(op_bin,2) | int(ni_bin,2)):02X}{int(xbpe_bin, 2):01X}000"
    
    # deal with format 2    
    if opcode == "CLEAR" or opcode == "TIXR":
        return f"{OPCODE_TABLE[opcode]}{REGISTER[operand]}0"
    if opcode == "COMPR":
        reg1, reg2 = operand.split(',')
        return f"{OPCODE_TABLE[opcode]}{REGISTER[reg1]}{REGISTER[reg2]}"
    
    # Initialize flags
    n = i = x = b = p = e = 0
    disp = 0

    # Handle Format 4 (extended format)
    if opcode.startswith("+"):
        e = 1
        opcode = opcode[1:]  # Remove '+' for opcode lookup

    # Determine addressing mode (n, i)
    if operand:
        if operand.startswith("#"):  # Immediate addressing
            i = 1
            n = 0
            operand = operand[1:]
        elif operand.startswith("@"):  # Indirect addressing
            n = 1
            i = 0
            operand = operand[1:]
        else:  # Simple addressing (direct mode)
            n = i = 1

    # Check for indexed addressing (x)
    if operand and ",X" in operand:
        x = 1
        operand = operand.replace(",X", "")

    # Get target address
    if operand in symtab:
        target_address = int(symtab[operand], 16) #轉16進位
        # print(target_address)
    elif operand.isdigit():  # Immediate value
        target_address = int(operand)
        op_bin = f"{int(OPCODE_TABLE[opcode], 16):06b}"  # Get opcode binary
        ni_bin = f"{n}{i}"  # Combine n and i
        xbpe_bin = f"{x}{b}{p}{e}"
        if e == 1:
            return f"{(int(op_bin,2) | int(ni_bin,2)):02X}{int(xbpe_bin, 2):01X}{target_address:05X}"
        else:
            return f"{(int(op_bin,2) | int(ni_bin,2)):02X}{int(xbpe_bin, 2):01X}{target_address & 0xFFF:03X}"
    else:
        target_address = 0

    # Determine displacement (b, p)
    if e:  # Format 4 (no displacement, just target address)
        disp = target_address
    else:  # Format 3
        pc = int(locctr, 16) + 3  # PC is the next instruction
        disp = target_address - pc

        if -2048 <= disp <= 2047:  # PC-relative
            p = 1
        else:  # Try base-relative
            disp = target_address - int(base, 16)
            if 0 <= disp <= 4095:
                b = 1
            else:
                raise ValueError(f"Address out of range for PC or Base relative: {operand}")

    # Construct the object code
    op_bin = f"{int(OPCODE_TABLE[opcode], 16):06b}"  # Get opcode binary
    ni_bin = f"{n}{i}"  # Combine n and i
    xbpe_bin = f"{x}{b}{p}{e}"  # Combine x, b, p, e

    # Combine into final object code
    if e:  # Format 4
        return f"{(int(op_bin,2) | int(ni_bin,2)):02X}{int(xbpe_bin, 2):01X}{disp:05X}"
    else:  # Format 3
        return f"{(int(op_bin,2) | int(ni_bin,2)):02X}{int(xbpe_bin, 2):01X}{disp & 0xFFF:03X}"


def pass_two(intermediate_rep, symtab, base_address):
    object_program = []  # Stores all object program records
    text_records = []  # Holds individual T records
    modification_records = []  # Holds M records

    # Initialize header record
    start_address = intermediate_rep[0]['loc']
    program_name = intermediate_rep[0]['line'].split()[0]
    program_length = hex(int(intermediate_rep[-1]['loc'], 16) - int(start_address, 16))[2:].zfill(6).upper()
    object_program.append(f"H^{program_name:<6}^{start_address.zfill(6)}^{program_length}")
    

    # text record
    current_text_start = None
    current_text_length = 0
    current_text = ""

    print('object code:')
    for entry in intermediate_rep:
        loc = entry["loc"]
        line = entry["line"]
        parsed = parse_line(line)
        opcode = parsed["opcode"]
        operand = parsed["operand"]

        # Skip directives not generating object code
        if opcode in ["START", "END", "BASE", "RESW", "RESB"]:
            if current_text:
                object_program.append(
                    f"T^{current_text_start.zfill(6)}^{current_text_length:02X}^{current_text}"
                )
                current_text, current_text_start, current_text_length = "", None, 0
            continue

        # Generate object code
        if opcode.startswith("+"): #format 4
            obj_code = format_object_code(opcode, operand, loc, symtab, base_address)
            print(obj_code)
            if operand[0] != "#":
                modification_loc = str(hex(int(loc, 16)+1)[2:])
                modification_records.append(f"M^{modification_loc.zfill(6)}^05")
        elif opcode in OPCODE_TABLE: #format 3 or format 2
            obj_code = format_object_code(opcode, operand, loc, symtab, base_address)
            print(obj_code)
        elif opcode == "BYTE":  # Handle BYTE
            if operand.startswith("C'"):
                obj_code = ''.join(f"{ord(c):X}" for c in operand[2:-1])
                print(obj_code)
            elif operand.startswith("X'"):
                obj_code = operand[2:-1]
                print(obj_code)
        else:
            raise ValueError(f"Unhandled opcode: {opcode}")
        
        # Append object code to current text record
        if not current_text_start:
            current_text_start = loc
        
        if current_text_length + len(obj_code) // 2 > 30:
            object_program.append(
                f"T^{current_text_start.zfill(6)}^{current_text_length:02X}^{current_text}"
            )
            current_text, current_text_start, current_text_length = "", loc, 0
        
        current_text += obj_code
        current_text_length += len(obj_code) // 2
        

    # Flush last text record
    if current_text:
        object_program.append(
            f"T^{current_text_start.zfill(6)}^{current_text_length:02X}^{current_text}"
        )

    # Modification Records
    object_program.extend(modification_records)

    # End Record
    end_label = intermediate_rep[-1]['line'].split()[1]
    end_address = symbol_table[end_label]
    end = f"E^{end_address.zfill(6)}"
    object_program.append(end)

    return object_program


# main function
symbol_table = {}
intermediate_rep = []
base_address = ""

filename = input("Please enter the name of code file: ")

with open(filename, "r", encoding = "utf-8") as file:
    # Perform Pass One
    symbol_table, intermediate_rep, base_address = pass_one(file)
    if base_address != None:
        base_address = symbol_table[base_address]
    print('-------------------------------------')
    # Output results
    print("SYMTAB:")
    # 將 dictionary 轉為 DataFrame
    data_dict = {
        "Label": list(symbol_table.keys()),
        "Address": list(symbol_table.values())
    }

    df = pd.DataFrame(data_dict)

    # 輸出表格
    print(df)
    print('-------------------------------------')

    """
    # 確認intermediate representation
    for i in intermediate_rep:
        print(i)
    print('-------------------------------------')
    """
    
object_program = pass_two(intermediate_rep, symbol_table, base_address)

print('-------------------------------------')
print('Object program:')
for i in object_program:
    print(i)
