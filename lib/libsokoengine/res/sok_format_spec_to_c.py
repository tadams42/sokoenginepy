import binascii

with open('SOK_format_specification.md', 'r') as f:
    content = f.read()

content = binascii.hexlify(content.encode()).decode()

def slices_per(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]

with open('SOK_format_specification.h', 'w') as f:
    f.write('const unsigned char SOK_format_specification_res[] = {\n')

    groups = (
        '  ' + ', '.join(('0x' + str for str in group))
        for group in
        slices_per(slices_per(content, 2), 12)
    )

    f.writelines(',\n'.join(groups))

    f.write('\n};\n')
