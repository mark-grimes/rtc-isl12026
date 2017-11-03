# Kernel module driver for the Intersil 12026 Real Time Clock

To build this you need to first get the source code for the kernel you are running. [This stackoverflow answer](https://stackoverflow.com/a/23685353) gives details of how to do it on a Raspberry Pi. Basically:

```
sudo rpi-update
sudo wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /usr/bin/rpi-source
sudo chmod +x /usr/bin/rpi-source
/usr/bin/rpi-source -q --tag-update
rpi-source
```

Then you can change to this directory, and:

```
make
sudo insmod rtc-isl12026.ko
echo isl12026 0x6f | sudo tee /sys/class/i2c-adapter/i2c-1/new_device
```

The `echo isl12026 ...` is tell the kernel the i2c address of the device. You can then use `sudo hwclock -r` to read from the clock, although if the clock loses power it shuts down until the current date is written to it. E.g.:

```
pi@ethoscope:~/rtc-isl12026 $ sudo hwclock -r
hwclock: ioctl(RTC_RD_TIME) to /dev/rtc to read the time failed: Invalid argument
pi@ethoscope:~/rtc-isl12026 $ tail /var/log/syslog
<snip>
Nov  3 11:32:01 ethoscope kernel: [  169.999579] rtc-isl12026 1-006f: The power to the Real Time Clock was interrupted. You must write the time to the clock before it will function.
<snip>
pi@ethoscope:~/rtc-isl12026 $ sudo hwclock --systohc -D --noadjfile --utc
<snip>
ioctl(RTC_SET_TIME) was successful.
pi@ethoscope:~/rtc-isl12026 $ sudo hwclock -r
Fri 03 Nov 2017 11:32:57 UTC  -0.894538 seconds
```

If you use the battery for backup power you should not see this after the first time.
