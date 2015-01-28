## pyfetion

With pyfetion you can send sms to your fetion friends(include yourself) in an easy way.

All API refers to 

https://code.google.com/p/php-fetion/source/browse/trunk/lib/PHPFetion.php

### How to use

```
yourmob = "136XXXXXXXX"
password = '123456'

send_to = '138XXXXXXXX'
msg = 'SMS just for test!'

m = Fetion(yourmob, password)

# DEBUG

m = Fetion(yourmob, password, 1)

try:
    print m.send_msg(send_to, msg)
except FetionError, e:
    print e
```
