import streamlit as st
import pandas as pd
import numpy as np
import time

df1 = pd.DataFrame(np.random.randn(100, 10), columns=('col %d' % i for i in range(10)))
df1['index'] = np.arange(100)
df1.set_index('index', inplace=True)

add = st.button('Add')
chart = st.line_chart(df1)

start = time.time()
for i in range(30000):
    df1 = df1.iloc[1:]
    df2 = pd.DataFrame(np.random.randn(1, 10), columns=('col %d' % e for e in range(10)))
    df2['index'] = 100+i
    df2.set_index('index', inplace=True)
    df1 = pd.concat([df1,df2], )
    
    print(i)
    # Tried to create entirely new line chart every so often to help with performance.
    # Testing throws an error from time to time because the index i gets reset once in a while and it then seems to run two for loops in "parallel"
    if i%100 == 0:
        chart.empty()
        chart = st.line_chart(df1)
    else:
        chart.line_chart(df1)
    
    if i%1000 == 0 and i>0:
        stop = time.time()
        duration = stop - start
        print(f"{duration = }")
        start = stop
