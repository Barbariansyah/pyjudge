def student_grade_5(a):
    if a < 0:
        return "INVALID"
    elif a > 100:
        return "INVALID"
    elif 80 <= a and a <= 100:
        return "A"
    elif 73 <= a and a <= 79:
        return "AB"
    elif 65 <= a and a <= 72:
        return "B"
    elif 57 <= a and a <= 64:
        return "BC"
    elif 50 <= a and a <= 56:
        return "C"
    else:
        return "D"