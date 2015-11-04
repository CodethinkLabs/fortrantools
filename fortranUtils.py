def split_fortran_line_at_72(line):
    # Commented lines won't be split
    if line[0].lower() == 'c':
        return [line]
    lines = [line]
    remain = line[72:]
    while len(remain)>66:
        lines.append("     +" + remain[:66] +"\n")
        remain = remain[66:]
    if len(remain)>0:
        lines.append("     +" + remain)
    return lines
