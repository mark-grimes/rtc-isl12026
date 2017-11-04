obj-m += rtc-isl12026.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

install:   # Not adding "all" as a dependency because "sudo make install" starts building loads of other stuff for some reason
	cp rtc-isl12026.ko /lib/modules/$(shell uname -r)/kernel/drivers/rtc/
	depmod -a
	dtc -I dts -O dtb -o /boot/overlays/i2c-rtc-isl12026.dtbo i2c-rtc-isl12026.dts
	@echo "\n\tThe kernel module has been installed to '/lib/modules/$(shell uname -r)/kernel/drivers/rtc'"
	@echo "\tTo enable it on boot you need to add the line \"dtoverlay=i2c-rtc-isl12026,isl12026\" to the '/boot/config.txt' file\n"
