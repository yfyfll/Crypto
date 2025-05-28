# 浅谈AES加解密

## 介绍

和DES一样，AES全称为`Advanced Encryption Standard`
（高级加密标准）实际上是一种加密标准，它的出现是为了取代之前的标准即DES成为新的对称密码标准，最终在2000年选用了名为Rijndael对称密码，将其确认为AES。

其基本信息如下:

1. 输入：128 比特。
2. 输出：128 比特。
3. SPN 网络结构。

其迭代轮数与密钥长度有关系，如下:

| 密钥长度（比特） | 迭代轮数 |
| ---------------- | -------- |
| 128              | 10       |
| 192              | 12       |
| 256              | 14       |

其中除了每一块从DES的64位变成128位之外，最大的不同是AES采用SPN网络结构，在Feistel中，每轮只处理上一轮结果的一半，而SPN每次都加密整个块。Feilstel里面，F函数可以选可逆的，也可以选不可逆的，不影响加密解密（可以参考我们对DES解密的解释，我们实际上没有关注F函数内部是否可逆）。而SPN的解密必须是对加密的逆运算，所以SPN中必须每一步都可逆。





## 加密过程1（代码较简单）

![image-20250105174610153](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051746214.png)



### 密钥加法层

输入16字节的明文和子密钥，对这两个输入逐字节异或，并将异或结果输出

![image-20250105174902745](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051749798.png)

### 字节代换层

让输入的每一个字节通过S-Box代还(映射)到另外一个字节，此处的S-Box是可以根据某种方法计算出来的，也可以直接使用计算好的S-Box进行代换。

经过S盒替换后将原本的关系变为非线性的。

![image-20250105175116861](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051751917.png)



![image-20250105175255114](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051752182.png)



### 行移位（扩散原则）

对于4*4的字节矩阵，在做行移位时，第一行保持不变，第二行往左移动一格，第三行往左移动两格，第四行往左移动三格

![image-20250105175446530](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051754626.png)



### 列混淆（扩散原则）

将整个字节矩阵乘上一个列混淆矩阵(有限域上的矩阵运算)。行移位和列混淆操作是AES的混淆层目的是为了将单个字节上的变换扩散到整个状态。

![image-20250105175553832](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051755888.png)



![image-20250105175739389](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051757448.png)

### 密钥扩展

标准128位的AES密钥，对应共有11组子密钥，分别在一开始和每轮(共10轮)中参与轮密钥加法层的运算。
子密钥的生成是以列为单位的，一列是4字节，32比特，四列构成-组子密钥。子密钥由专门的密钥扩展算法计算得出，存储在w[0]w[1],… w[43]的子密钥数组中。

![image-20250105175930024](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051759077.png)



#### G函数

1.将输入的4个字节进行换位

2.逐字节经过S盒进行代换

3.用第一个字节和轮系数进行异或运算

G函数的目的有两个:
增加密钥扩展的非线性
消除AES中的对称性

![image-20250105180126463](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051801508.png)

![image-20250105180306018](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051803076.png)







## 加密过程2（代码较难）

### 1.字节代换（AddRoundKey）

设明文矩阵P，子密钥矩阵K
$$
P=
\left[
\begin{matrix}
p1&p2&p3&p4\\
p5&p6&p7&p8\\
p9&p10&p11&p12\\
p13&p14&p15&p16
\end{matrix}
\right]
$$

$$
K=
\left[
\begin{matrix}
k1&k2&k3&k4\\
k5&k6&k7&k8\\
k9&k10&k11&k12\\
k13&k14&k15&k16
\end{matrix}
\right]
$$

则轮加密的结果为
$$
P\bigoplus K=
\left[
\begin{matrix}
p1\bigoplus k1&p2\bigoplus k2&p3\bigoplus k3&p4\bigoplus k4\\
p5\bigoplus k5&p6\bigoplus k6&p7\bigoplus k7&p8\bigoplus k8\\
p9\bigoplus k9&p10\bigoplus k10&11\bigoplus k11&p12\bigoplus k12\\
p13\bigoplus k13&p14\bigoplus k14&p15\bigoplus k15&p16\bigoplus k16
\end{matrix}
\right]
$$
代码实现：

```python
def add_round_key(s, k):
    for i in range(4):
        for j in range(4):
            s[i][j] ^= k[i][j]
```







### 2.字节替换（SubBytes）

在这里，引入一个S盒（S box），也就是一个替换表，如下

```python
0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
```

替换方式：

```python
def sub_bytes(s):
    for i in range(4):
        for j in range(4):
            s[i][j] = s_box[s[i][j]]
```









### 3.行置换（ShiftRows）

这也是一次扩散处理，达到雪崩效应（雪崩效应是指当输入发生最微小的改变（例如，反转一个二进制位）时，也会导致输出的不可区分性改变，即扩大错误防止攻击者找到不同明密文之间的关系）。

第一行不变，第二行左移1，第三行左移2，第四行左移3。即矩阵P变成：
$$
P\rightarrow
\left[
\begin{matrix}
p1&p2&p3&p4\\
p6&p7&p8&p5\\
p11&p12&9&p10\\
p16&p13&p14&p15
\end{matrix}
\right]
$$

```python
def shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]
```

不过注意上面的代码，你会发现行列反了，这是因为为了方便后面的操作，我们改变了编写手法，一般我们使用：

```python
s = [[1, 2, 3],
     [2, 2, 2]]
```

代表一个`2x3`的矩阵，但是这里我们用:

```python
s = [[1, 2],
     [2, 2],
     [3, 2]]
```

来代表这个`2x3`矩阵，这样的好处是我们可以直接通过`s[i]`来获取`s`中的某一列。(注意 后续的代码相同)







### 4.列混淆（MixColumn）

同样也是扩散操作

将给定矩阵和P在GF($2^8$)做乘法。(GF代表伽罗瓦域，这里我们可以不用关系这是什么，我们只需要知道所有的运算结果需要%256即可)
$$
\left[
\begin{matrix}
2&3&1&1\\
1&2&3&1\\
1&1&2&3\\
3&1&1&2
\end{matrix}
\right]
 \bigoplus P
$$

```python
xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)#例：a = 0xFF 左移一位，得到 0x1FE，然后丢弃第九位（超出 8 位的部分），最终结果是 0xFE，执行 (a << 1) ^ 0x1B 后，结果是 0xE5。
#为什么是0x1B:因为AES 使用的 模多项式 是：x**8+x**4+x**3+x+1即10011011（二进制）
#lambda a: 定义了一个函数(xtime)，接收一个参数 a，并执行特定的逻辑（有限域上的乘法）
#a & 0x80:& 是 按位与运算符，用于在二进制级别比较两个数的每一位。
#0x80:二进制10000000   128  验算最高位是否为1
#0x1B:二进制00011011   27   
#0xFF:二进制11111111   255
#上述代码等效于：
#def xtime(a):
#    if a & 0x80:  #最高位是1，进行与运算：如果结果是非零（即                          0x80），则字节的最高位为 1，否则...。
#        return ((a << 1) ^ 0x1B) & 0xFF
#    else:  #最高位是0
#        return a << 1
def mix_single_column(a):
    # see Sec 4.1.2 in The Design of Rijndael
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)

def mix_columns(s):
    for i in range(4):
        mix_single_column(s[i])
```







### 5.子密钥生成

下一轮的子密钥是按列生成的，我们现在将K1设为：
$$
K_1=K_{11}K_{12}K_{13}K_{14}
$$
其中$K_{1j}$代表第j列

则下一轮子密钥$K_{2j}$满足
$$
K_{21}=K_{11}\bigoplus SubBytes(Shift(K_{14}))\bigoplus S_1\\
K_{22}=K_{21}\bigoplus K_{12}\\
K_{23}=K_{22}\bigoplus K_{13}\\
K_{24}=K_{23}\bigoplus K_{14}\\
$$
其中`Shift`代表位移，`SubBytes`代表子节替换函数，`S_{i}`代表上图下方处的异或表，不同轮次将会异或不同列。

而对于192或是256位密钥会稍微又些不一样，但大致流程相同，这里我们以128位的密钥为例：

```python
r_con = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,0x80, 0x1B, 0x36)#轮常数 r_con 是一个固定的常数序列

def xor_bytes(a, b):
    return bytes(i^j for i, j in zip(a, b))

def _expand_key(s):
    for i in range(10):
        word = list(s[-1])  # 取得最后一列
        word.append(word.pop(0)) # 将首位移动到最后
        word = [s_box[b] for b in word]  # SubBytes操作
        word[0] ^= r_con[i]  # 和异或表内数据异或

        s.append(xor_bytes(word, s[-4]))  # 得到新的子密钥
        s.append(xor_bytes(s[-1], s[-4]))  # 因为直接在s中添加，所以本该和上一轮第二列异或的位置还是-4
        s.append(xor_bytes(s[-1], s[-4]))
        s.append(xor_bytes(s[-1], s[-4]))

    return [s[4*i : 4*(i+1)] for i in range(len(s) // 4)]
```

在配合迭代流程，我们就可以完成AES的python代码实现了，当然我们也可以直接使用Python包来完成，例如：

```python
from Crypto.Cipher import AES
aes = AES.new(b'1234567812345678', AES.MODE_ECB)
print(aes.encrypt(b'1234567812345678'))  # b'm\xac\x1cV\xe7G\xfa\xe0:\xcf\x8ch\x91\xe4(\xe0'
```

关于其中的`AES.MODE_ECB`指代使用ECB模式，关于不同加密模式的介绍则会在分组加密中进行介绍，此处我们暂不关心。

你也可以对比你的AES实现是否和标准库加密得到的内容相同









### 完整加密代码

```python
r_con = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,0x80, 0x1B, 0x36)
s_box = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

def xor_bytes(a, b):
    return bytes(i^j for i, j in zip(a, b))

def add_round_key(s, k):
    for i in range(4):
        for j in range(4):
            s[i][j] ^= k[i][j]

def sub_bytes(s):
    for i in range(4):
        for j in range(4):
            s[i][j] = s_box[s[i][j]]

def shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]

# 参考 http://cs.ucsb.edu/~koc/cs178/projects/JT/aes.c
xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)

def mix_single_column(a):
    # see Sec 4.1.2 in The Design of Rijndael
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)

def mix_columns(s):
    for i in range(4):
        mix_single_column(s[i])

def _expand_key(s):
    for i in range(10):
        word = list(s[-1])  # 取得最后一列
        word.append(word.pop(0)) # 将首位移动到最后
        word = [s_box[b] for b in word]  # SubBytes操作
        word[0] ^= r_con[i]  # 和异或表内数据异或

        s.append(xor_bytes(word, s[-4]))  # 得到新的子密钥
        s.append(xor_bytes(s[-1], s[-4]))  # 因为直接在s中添加，所以本该和上一轮第二列异或的位置还是-4
        s.append(xor_bytes(s[-1], s[-4]))
        s.append(xor_bytes(s[-1], s[-4]))

    return [s[4*i : 4*(i+1)] for i in range(len(s) // 4)]

def bytes2matrix(text):
    """ Converts a 16-byte array into a 4x4 matrix.  """
    return [list(text[i:i+4]) for i in range(0, len(text), 4)]

key = b'1234567812345678'
plain = b'1234567812345678'
skeys = _expand_key(bytes2matrix(key))
plain = bytes2matrix(plain)

add_round_key(plain, skeys[0])

for i in range(1, 10):
    sub_bytes(plain)
    shift_rows(plain)
    mix_columns(plain)
    add_round_key(plain, skeys[i])

sub_bytes(plain)
shift_rows(plain)
add_round_key(plain, skeys[-1])

enc = bytes(plain[0]+plain[1]+plain[2]+plain[3])
print(enc)  # b'm\xac\x1cV\xe7G\xfa\xe0:\xcf\x8ch\x91\xe4(\xe0'
```

 

## Python调库

调用Python的Crypto库进行AES算法加解密：
![image-20250105180405714](https://raw.githubusercontent.com/yfyfll/typora/main/img202501051804771.png)













## 解密

和DES并不相同，在DES中我们介绍了其前后是互逆的，并且中间函数内部无需关系，而对于AES来说，每个函数都是独立的加密函数，我们必须一一找到这些函数的逆函数才可以解密

### 1.轮密钥加（AddRoundKey）

显然我们只需要生成子密钥后再异或一次即可解密





### 2.字节替换（SubByte）

通过逆替换表替换回来即可:

```python
def inv_sub_bytes(s):
    for i in range(4):
        for j in range(4):
            s[i][j] = inv_s_box[s[i][j]]
```







### 3.行置换（ShiftRows）

将左移的位置移动回来即可:

```python
def inv_shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]
```





### 4.列混淆（MixColumn）

这一步乘的矩阵是存在逆矩阵的，我们可以恢复这个函数

其逆矩阵为:

```python
0x0e, 0x0b, 0x0d, 0x09 
0x09, 0x0e, 0x0b, 0x0d 
0x0d, 0x09, 0x0e, 0x0b 
0x0b, 0x0d, 0x09, 0x0e
```

```python
def inv_mix_columns(s):
    # see Sec 4.1.3 in The Design of Rijndael
    for i in range(4):
        u = xtime(xtime(s[i][0] ^ s[i][2]))
        v = xtime(xtime(s[i][1] ^ s[i][3]))
        s[i][0] ^= u
        s[i][1] ^= v
        s[i][2] ^= u
        s[i][3] ^= v

    mix_columns(s)
```

可发现我们这里并不是乘上了上述逆矩阵，实际上AES比DES更好的还有一个原因就是其性能很高，加密过程中的函数经过优化有可以合并或是变成等价代换.

