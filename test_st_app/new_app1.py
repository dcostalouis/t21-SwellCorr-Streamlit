
from multiapp import MultiApp
import streamlit as st

def foo():
    st.title("Hello Foo")



def bar():
    st.title("Hello Bar")



app = MultiApp()

app.add_app("Foo", foo)
hobby = st.selectbox("Hobbies: ",
                     ['Dancing', 'Reading', 'Sports'])

app.add_app("Bar", bar)
# print the selected hobby
st.write("Your hobby is: ", hobby)
    
app.run()