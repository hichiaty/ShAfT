import zlib
import base64

data = r'''(base) C:\Users\Hisham Abdel-Aty\Desktop\New folder\ShAT>dir
 Volume in drive C is Blade Stealth
 Volume Serial Number is 2E51-B6F3

 Directory of C:\Users\Hisham Abdel-Aty\Desktop\New folder\ShAT

10/08/2020  01:41    <DIR>          .
10/08/2020  01:41    <DIR>          ..
10/08/2020  01:40             1,075 client.py
10/08/2020  01:41                13 ctest.py
               2 File(s)          1,088 bytes
               2 Dir(s)  190,663,847,936 bytes free

(base) C:\Users\Hisham Abdel-Aty\Desktop\New folder\ShAT>'''

compressed_data = zlib.compress(data.encode('utf-8'), 9)
print(len(base64.b85encode(compressed_data)))