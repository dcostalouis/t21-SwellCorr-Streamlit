import pickle
l = [1,2,3,4]
with open("test.txt", "wb") as fp:   #Pickling
    pickle.dump(l, fp)

with open("test.txt", "rb") as fp:   # Unpickling
    b = pickle.load(fp)

print(b)
