import hashlib
import sys
filePath1 = sys.argv[1]  # 文件1
filePath2 = sys.argv[2]  # 文件2

'''
@description: 计算md5码
@param {*} src
@return {*}
'''


def out_md5(src):
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
