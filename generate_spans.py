import numpy as np
import re

def CSS():

    with open("ROOS/sample-span.txt", "r") as f:
        text = f.read()

    num_spans = 100
    span_list = [text] * num_spans
    tops = np.random.randint(91, size=num_spans)
    for i in range(len(tops)):
        # while tops[i] >= 36 and tops[i] <= 56:
            tops[i] = np.random.randint(99, size=1)[0]
    delay = np.random.randint(0, 1000, size=num_spans) / 100
    duration = np.random.randint(low = 1500, high = 3200, size=num_spans) / 100

    for i in range(num_spans):
        span_list[i] = (re.sub("#span_num#", str(i+1), span_list[i]))
        span_list[i] = (re.sub("#top_num#", str(tops[i]), span_list[i]))
        span_list[i] = (re.sub("#delay_num#", str(delay[i]), span_list[i]))
        span_list[i] = (re.sub("#duration_num#", str(duration[i]), span_list[i]))


    with open("ROOS/output-spans.txt", "w") as f:
        for i in span_list:
            f.write(i+"\n")

def Section():

    num_spans = 100

    with open("ROOS/section-spans.txt", "w") as f:
        for i in range(num_spans):
            text = "        <span id=\"spann{}\"></span>".format(i+1)
            f.write(text+"\n")

CSS()
Section()