fopen=open('help.csv', 'r')
fcheck=open('sub_class.csv', 'r')
fcheck.readline()
sub_class=[]
for line in fcheck:
    line.strip().split(',')
    sub_class.append(line[0])
fopen.readline()
name=[]
for line in fopen:
    line=line.strip().split(',')
    name.append(line[1])