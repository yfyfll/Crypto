memory_size = 8192
memory = [0] * memory_size
ptr = 0

ip = 0
ins = open('C:/Users/liyunfei/Desktop/CodeC.txt', 'rt').read().strip()

while True:
    if ip >= len(ins):
        break
    if ip < 0:
        break

    opcode = ins[ip]
    if opcode == '+':
        memory[ptr] += 1
    elif opcode == '-':
        memory[ptr] -= 1
    elif opcode == '>':
        ptr += 1
    elif opcode == '<':
        ptr -= 1
    elif opcode == '.':
        print(memory[ptr], end=' ')
    elif opcode == '[':
        if memory[ptr] == 0:
            while ins[ip] != ']':
                ip += 1
    elif opcode == ']':
        if memory[ptr] != 0:
            while ins[ip] != '[':
                ip -= 1

    ip += 1