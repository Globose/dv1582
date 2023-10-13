list1 = []
list2 = []

for i in range(10000000):
    list1.append(i)
    list2.append(i)

for i in range(len(list1)):
    list1[i] = i+1

for i in range(len(list2)):
    list2[i] = i+1

# list1.extend(list2)
# for i in range(len(list1)):
#     list1[i] = i+1


# print (list1[123])