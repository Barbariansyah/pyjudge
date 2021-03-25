def loop_2(in1,in2):
    while in1 < in2:
        in1 = in1 + 1
        if in1 == 5:
            return in1 + in2
    if in1 - 2 == in2:
        return in1
    else:
        return in2
        
# def expected_result():
#     return [0,1,1]