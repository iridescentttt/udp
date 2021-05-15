import hashlib
import sys
filePath1=sys.argv[1]
filePath2=sys.argv[2]
def out_md5(src):
    # 简单封装
    m = hashlib.md5()
    m.update(src)
    return m.hexdigest()


with open(filePath1, 'rb') as f:
    src = f.read()
    m1 = out_md5(src)
    print("文件"+str(filePath1)+"的md5码为"+":"+str(m1))

with open(filePath2, 'rb') as f:
    src = f.read()
    m2 = out_md5(src)
    print("文件"+str(filePath2)+"的md5码为"+":"+str(m2))

if m1 == m2:
    print(True)
else:
    print(False)
