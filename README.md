# Linux kernel module driver for the Intersil 12026 Real Time Clock

I intend to try and get this into the Linux kernel, but I want to test for a bit first. In the meantime...

## To compile yourself

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

### Installing the driver

The compiled driver (`rtc-isl12026.ko` file) should be copied to the `/lib/modules/$(uname -r)/kernel/drivers/rtc/` directory and then `depmod` used to tell the system about it. I.e.:

```
sudo cp rtc-isl12026.ko /lib/modules/$(uname -r)/kernel/drivers/rtc/
sudo depmod -a
```

The driver should then be available without having to reference the compiled file directly. I assume that **if you upgrade your kernel, you will lose the driver**, since it's tied to a specific kernel directory. I don't know if copying the file to another directory other than the kernel it was compiled against works.

### Getting the driver to load at each boot

Raspberry Pi now uses device trees to manage everything, which is not something I know much about. You need to compile an overlay with settings for e.g. the I2C address to be available at boot, and tell the kernel to load it. I've cobbled together the `i2c-rtc-isl12026.dts` overlay and it seems to work. First compile it to the binary format and stick it in the boot volume:

```
sudo dtc -I dts -O dtb -o /boot/overlays/i2c-rtc-isl12026.dtbo <this repo>/kernelModules/rtc-isl12026/i2c-rtc-isl12026.dts
```

(I get some warning about "has a unit name, but no reg property" but it doesn't seem to matter) Then add this line to the bottom of `/boot/config.txt`:

```
dtoverlay=i2c-rtc-isl12026,isl12026
```

### Remove the fake hwclock

You'll get conflicts if you leave the fake-hwclock module running. I don't know of a way to only disable the fake-hwclock if a real one is not present.

```
sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
```
