import sys


tokens = ['+', '-']

def parse_line(line):
    res = None
    prev_token = ''
    curr = 0
    for value in line:
        if value not in tokens:
            if value == ' ':
                pass
            else:
                curr = curr * 10 + int(value)
        else:
            if res is None:
                res = curr if prev_token != '-' else -curr
            elif prev_token == '-':
                res -= curr
            elif prev_token == '+':
                res += curr
            else:
                print('ERROR, invalid string:', line)
                break
            curr = 0
            prev_token = value
    return (res + curr) if prev_token == '+' else (res - curr)


if __name__ == '__main__':
    fname = str(sys.argv[1])
    with open(fname, 'r') as fin:
        for i in range(5):
            line = fin.readline().strip()
            print('{}={}'.format(line, parse_line(line)))
