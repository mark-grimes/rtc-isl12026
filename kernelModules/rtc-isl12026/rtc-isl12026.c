/*
 * An I2C driver for the Intersil ISL 12026
 *
 * Author: Mark Grimes <mark.grimes@rymapt.com>
 *
 * Information for this was taken from the datasheet available at
 * https://www.intersil.com/content/dam/Intersil/documents/isl1/isl12026-a.pdf
 *
 * Based on the Intersil 12022 RTC by Roman Fietze
 * <roman.fietze@telemotive.de>, which was in turn based on the Philips
 * PCF8563 RTC by Alessandro Zummo <a.zummo@towertech.it>.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version
 * 2 as published by the Free Software Foundation.
 */

#include <linux/i2c.h>
#include <linux/bcd.h>
#include <linux/rtc.h>
#include <linux/slab.h>
#include <linux/module.h>
#include <linux/err.h>
#include <linux/of.h>
#include <linux/of_device.h>

/* ISL register offsets */
#define ISL12026_REG_SC		0x30
#define ISL12026_REG_MN		0x31
#define ISL12026_REG_HR		0x32
#define ISL12026_REG_DT		0x33
#define ISL12026_REG_MO		0x34
#define ISL12026_REG_YR		0x35
#define ISL12026_REG_DW		0x36
#define ISL12026_REG_Y2K	0x37

#define ISL12026_REG_SR		0x3f
#define ISL12026_REG_PWR	0x14

/* ISL register bits */
#define ISL12026_HR_MIL		(1 << 7)	/* military or 24 hour time */

#define ISL12026_SR_OSCF	(1 << 4)    /* oscillator failed */
#define ISL12026_SR_RWEL	(1 << 2)    /* indicate that the write is starting */
#define ISL12026_SR_WEL 	(1 << 1)    /* indicate that you want to start a write */
#define ISL12026_SR_RTCF	(1 << 0)    /* previous power failure */

#define ISL12026_PWR_SBIB	(1 << 7)    /* disables i2c when on battery backup */
#define ISL12026_PWR_BSW	(1 << 6)    /* determines when to switch to battery */


static struct i2c_driver isl12026_driver;

static int isl12026_read_regs(struct i2c_client *client, uint8_t reg,
			      uint8_t *data, size_t n)
{
	/* high byte of the 2 byte register address is never used */
	uint8_t registerAddress[2] = { 0x00, reg };

	struct i2c_msg msgs[] = {
		{
			.addr	= client->addr,
			.flags	= 0,
			.len	= 2,
			.buf	= registerAddress
		},		/* setup read ptr */
		{
			.addr	= client->addr,
			.flags	= I2C_M_RD,
			.len	= n,
			.buf	= data
		}
	};

	int ret;

	ret = i2c_transfer(client->adapter, msgs, ARRAY_SIZE(msgs));
	if (ret != ARRAY_SIZE(msgs)) {
		dev_err(&client->dev, "%s: read error, ret=%d\n",
			__func__, ret);
		return -EIO;
	}

	return 0;
}

/* Write to a Clock/Control Register (CCR). The ISL12026 requires a strict sequence of:
       1) Set the WEL bit in the status register
       2) Set the RWEL and WEL bits in the status register
       3) Write to the register you originally intended  */
static int isl12026_write_ccr_reg(struct i2c_client *client,
			      uint8_t reg, uint8_t val)
{
	/* register addresses are all 2 bytes, but the highest byte is never used */
	uint8_t WEL_bit[3] = { 0x00, ISL12026_REG_SR, ISL12026_SR_WEL };
	uint8_t WEL_and_RWEL_bits[3] = { 0x00, ISL12026_REG_SR, ISL12026_SR_RWEL | ISL12026_SR_WEL };
	uint8_t data[3] = { 0x00, reg, val };

	struct i2c_msg msgs[] = {
		{ /* Set WEL bit in the status register */
			.addr	= client->addr,
			.flags	= 0,
			.len	= sizeof(WEL_bit),
			.buf	= WEL_bit
		},
		{ /* Set WEL and RWEL bits in the status register */
			.addr	= client->addr,
			.flags	= 0,
			.len	= sizeof(WEL_and_RWEL_bits),
			.buf	= WEL_and_RWEL_bits
		}, /* Perform the write intended */
		{
			.addr	= client->addr,
			.flags	= 0,
			.len	= sizeof(data),
			.buf	= data
		}
	};

	int ret;

	ret = i2c_transfer(client->adapter, msgs, ARRAY_SIZE(msgs));
	if (ret != ARRAY_SIZE(msgs)) {
		dev_err(&client->dev, "%s: write error, ret=%d\n",
			__func__, ret);
		return -EIO;
	}

	return 0;
}

/* Write the bytes given without adding the register address before hand, assuming
   the caller has already done this themselves (saves copying into a new array).
   See isl12026_write_ccr_reg above for a description of the write sequence. */
static int isl12026_write_ccr_bytes(struct i2c_client *client, uint8_t *data, size_t n)
{
	/* register addresses are all 2 bytes, but the highest byte is never used */
	uint8_t WEL_bit[3] = { 0x00, ISL12026_REG_SR, ISL12026_SR_WEL };
	uint8_t WEL_and_RWEL_bits[3] = { 0x00, ISL12026_REG_SR, ISL12026_SR_RWEL | ISL12026_SR_WEL };

	struct i2c_msg msgs[] = {
		{ /* Set WEL bit in the status register */
			.addr	= client->addr,
			.flags	= 0,
			.len	= sizeof(WEL_bit),
			.buf	= WEL_bit
		},
		{ /* Set WEL and RWEL bits in the status register */
			.addr	= client->addr,
			.flags	= 0,
			.len	= sizeof(WEL_and_RWEL_bits),
			.buf	= WEL_and_RWEL_bits
		}, /* Perform the write intended */
		{
			.addr	= client->addr,
			.flags	= 0,
			.len	= n,
			.buf	= data
		}
	};

	int ret;

	ret = i2c_transfer(client->adapter, msgs, ARRAY_SIZE(msgs));
	if (ret != ARRAY_SIZE(msgs)) {
		dev_err(&client->dev, "%s: write error, ret=%d\n",
			__func__, ret);
		return -EIO;
	}

	return 0;
}

/*
 * In the routines that deal directly with the isl12026 hardware, we use
 * rtc_time -- month 0-11, hour 0-23, yr = calendar year-epoch.
 */
static int isl12026_get_datetime(struct i2c_client *client, struct rtc_time *tm)
{
	uint8_t buf[ISL12026_REG_Y2K - ISL12026_REG_SC + 1];
	uint8_t status;
	int ret;

	ret = isl12026_read_regs(client, ISL12026_REG_SC, buf, sizeof(buf));
	if (ret)
		return ret;

	/* Status register is not contiguous with the time registers, so need a separate read */
	ret = isl12026_read_regs(client, ISL12026_REG_SR, &status, 1);
	if (ret)
		return ret;

	if (status & ISL12026_SR_OSCF) {
		dev_warn(&client->dev,"The Real Time Clock is reporting that the oscillator is not operating");
	}

	if (status & ISL12026_SR_RTCF) {
		dev_warn(&client->dev,"The power to the Real Time Clock was interrupted. You must write the time to the clock before it will function.");
	}

	dev_dbg(&client->dev,
		"%s: raw data is sec=%02x, min=%02x, hr=%02x, "
		"mday=%02x, mon=%02x, year=%02x, wday=%02x, y2k=%02x, "
		"sr=%02x",
		__func__,
		buf[ISL12026_REG_SC-ISL12026_REG_SC],
		buf[ISL12026_REG_MN-ISL12026_REG_SC],
		buf[ISL12026_REG_HR-ISL12026_REG_SC],
		buf[ISL12026_REG_DT-ISL12026_REG_SC],
		buf[ISL12026_REG_MO-ISL12026_REG_SC],
		buf[ISL12026_REG_YR-ISL12026_REG_SC],
		buf[ISL12026_REG_DW-ISL12026_REG_SC],
		buf[ISL12026_REG_Y2K-ISL12026_REG_SC],
		status);

	tm->tm_sec = bcd2bin(buf[ISL12026_REG_SC-ISL12026_REG_SC] & 0x7F);
	tm->tm_min = bcd2bin(buf[ISL12026_REG_MN-ISL12026_REG_SC] & 0x7F);
	tm->tm_hour = bcd2bin(buf[ISL12026_REG_HR-ISL12026_REG_SC] & 0x3F);
	if( buf[ISL12026_REG_HR-ISL12026_REG_SC] & ISL12026_HR_MIL ) {
		/* Hour is in 24 hour format */
		tm->tm_hour = bcd2bin(buf[ISL12026_REG_HR-ISL12026_REG_SC] & 0x3F);
	}
	else {
		/* Hour is in 12 hour format with the 6th bit indicating AM/PM.
		   Note this driver won't set the time in this format, but just in
		   case the chip was set in some other way */
		tm->tm_hour = bcd2bin(buf[ISL12026_REG_HR-ISL12026_REG_SC] & 0x1F);
		if( buf[ISL12026_REG_HR-ISL12026_REG_SC] & (1 << 5) ) {
			tm->tm_hour += 12;
		}
	}
	tm->tm_mday = bcd2bin(buf[ISL12026_REG_DT-ISL12026_REG_SC] & 0x3F);
	tm->tm_wday = buf[ISL12026_REG_DW-ISL12026_REG_SC] & 0x07;
	tm->tm_mon = bcd2bin(buf[ISL12026_REG_MO-ISL12026_REG_SC] & 0x1F) - 1;
	tm->tm_year = bcd2bin(buf[ISL12026_REG_YR-ISL12026_REG_SC])
			+ ((bcd2bin(buf[ISL12026_REG_Y2K-ISL12026_REG_SC]) - 19) * 100);

	dev_dbg(&client->dev, "%s: secs=%d, mins=%d, hours=%d, "
		"mday=%d, mon=%d, year=%d, wday=%d\n",
		__func__,
		tm->tm_sec, tm->tm_min, tm->tm_hour,
		tm->tm_mday, tm->tm_mon, tm->tm_year, tm->tm_wday);

	return rtc_valid_tm(tm);
}

static int isl12026_set_datetime(struct i2c_client *client, struct rtc_time *tm)
{
	int ret;
	/* extra +2 to put 2 byte register address in the first position */
	uint8_t buf[ISL12026_REG_Y2K-ISL12026_REG_SC + 1 + 2];

	dev_dbg(&client->dev, "%s: secs=%d, mins=%d, hours=%d, "
		"mday=%d, mon=%d, year=%d, wday=%d\n",
		__func__,
		tm->tm_sec, tm->tm_min, tm->tm_hour,
		tm->tm_mday, tm->tm_mon, tm->tm_year, tm->tm_wday);

	/* put the register to write to as the first piece of data */
	buf[0] = 0x00; /* register address is 2 bytes, but we never need this byte */
	buf[1] = ISL12026_REG_SC;

	/* hours, minutes and seconds */
	buf[ISL12026_REG_SC-ISL12026_REG_SC+2] = bin2bcd(tm->tm_sec);
	buf[ISL12026_REG_MN-ISL12026_REG_SC+2] = bin2bcd(tm->tm_min);
	buf[ISL12026_REG_HR-ISL12026_REG_SC+2] = bin2bcd(tm->tm_hour) | ISL12026_HR_MIL;

	buf[ISL12026_REG_DT-ISL12026_REG_SC+2] = bin2bcd(tm->tm_mday);

	/* month, 1 - 12 */
	buf[ISL12026_REG_MO-ISL12026_REG_SC+2] = bin2bcd(tm->tm_mon + 1);

	/* year and century */
	buf[ISL12026_REG_YR-ISL12026_REG_SC+2] = bin2bcd(tm->tm_year % 100);
	/* set the Y2K register to either 19 or 20 for the century */
	buf[ISL12026_REG_Y2K-ISL12026_REG_SC+2] = bin2bcd(tm->tm_year/100 + 19);

	buf[ISL12026_REG_DW-ISL12026_REG_SC+2] = tm->tm_wday & 0x07;

	ret = isl12026_write_ccr_bytes(client, buf, sizeof(buf));
	if (ret) return -EIO;

	return 0;
}

static int isl12026_rtc_read_time(struct device *dev, struct rtc_time *tm)
{
	return isl12026_get_datetime(to_i2c_client(dev), tm);
}

static int isl12026_rtc_set_time(struct device *dev, struct rtc_time *tm)
{
	return isl12026_set_datetime(to_i2c_client(dev), tm);
}

static const struct rtc_class_ops isl12026_rtc_ops = {
	.read_time	= isl12026_rtc_read_time,
	.set_time	= isl12026_rtc_set_time,
};

static int isl12026_probe(struct i2c_client *client,
			  const struct i2c_device_id *id)
{
	struct rtc_device *rtc;
	int result;

	if (!i2c_check_functionality(client->adapter, I2C_FUNC_I2C))
		return -ENODEV;

	rtc = devm_rtc_device_register(&client->dev,
					isl12026_driver.driver.name,
					&isl12026_rtc_ops, THIS_MODULE);
	result = PTR_ERR_OR_ZERO(rtc);

	/* Disable the i2c bus when on battery backup. This minimises drain on the
	   battery, and it's not like we're going to use the bus when there's no power. */
	if( result==0 ) {
		result = isl12026_write_ccr_reg(client, ISL12026_REG_PWR, ISL12026_PWR_SBIB | ISL12026_PWR_BSW);
		if (result)
			dev_warn(&client->dev,"Unable to disable i2c bus during battery power option");
		result = 0; /* reset to the result from PTR_ERR_OR_ZERO(rtc) */
	}

	return result;
}

#ifdef CONFIG_OF
static const struct of_device_id isl12026_dt_match[] = {
	{ .compatible = "isl,isl12026" }, /* for backward compat., don't use */
	{ .compatible = "isil,isl12026" },
	{ },
};
MODULE_DEVICE_TABLE(of, isl12026_dt_match);
#endif

static const struct i2c_device_id isl12026_id[] = {
	{ "isl12026", 0 },
	{ }
};
MODULE_DEVICE_TABLE(i2c, isl12026_id);

static struct i2c_driver isl12026_driver = {
	.driver		= {
		.name	= "rtc-isl12026",
#ifdef CONFIG_OF
		.of_match_table = of_match_ptr(isl12026_dt_match),
#endif
	},
	.probe		= isl12026_probe,
	.id_table	= isl12026_id,
};

module_i2c_driver(isl12026_driver);

MODULE_AUTHOR("mark.grimes@rymapt.com");
MODULE_DESCRIPTION("ISL 12026 RTC driver");
MODULE_LICENSE("GPL");
