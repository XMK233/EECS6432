import datetime, time

now = datetime.datetime.now()
time.sleep(5)
next = datetime.datetime.now()
environment = datetime.timedelta(seconds=10)
print(next - now > environment)

t = 5640
t1 = 0
while (t >= 0):
    print(t, t1)
    t -= 240
    t1 += 120