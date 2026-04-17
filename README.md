# houston

Exploit for Exynos devices to gain ACE in BootROM context.

>[!CAUTION]
> The code for this exploit was previously stolen and used in an AI vibecoded tool made by [Creeeeger](https://github.com/Creeeeger).
> Be extremely careful when using his stuff, it might be broken and cause harm to your device.

## How does this even work

A length parameter left unchecked in the USB Control Request code allows iRAM to be dumped, modified and resent
to the device, allowing for code execution.

## Known vulnerable SoCs

>[!CAUTION]
> An SoC being vulnerable does not mean payloads and support are available for it.

- Exynos9810
- Exynos9820
- Exynos9830
- Exynos8825
- Exynos9925

There probably are many more.

## Notice for non Exynos990 users

There is another [tool](https://github.com/VDavid003/exynos-usbdl) made by a great friend [VDavid003](https://github.com/VDavid003), which supports more platforms.

## Usage

```
usage: houston.py [-h] [-e] [-p PAYLOAD] [-d] [-o OUTPUT] [-c] files [files ...]

Exploit for Exynos devices to gain ACE in BootROM context.

positional arguments:
  files                 Files to send to the device post exploit (seperated by a space)

options:
  -h, --help            show this help message and exit
  -e, --exploit         Run the exploit before sending files
  -p, --payload PAYLOAD
                        Path to the payload to launch
  -d, --debug           Debug Mode
  -o, --output OUTPUT   Path to a folder where to save payload output to
  -c, --console-output  Show output to console
```

## Credits

Thanks to these teams and people we have houston!
- [Chimera Tool](https://chimeratool.com) ```First discovery of the exploit circa 2021-2022. They provide the most advanced Exynos servicing capabilities in the market to a broad amount of devices, and that is thanks to this specific exploit, and many more.```
- [CVE-2024-56426](https://semiconductor.samsung.com/support/quality-support/product-security-updates/cve-2024-56426/) ```This is the CVE houston is based off as we know.```
- Christopher Wade ```Reported CVE-2024-56426 to Samsung```
- [kethily-daniel](https://github.com/kethily-daniel) ```Gave me access to the tool for USB packet tracing to extract samples.```
- [BotchedRPR](https://github.com/BotchedRPR) ```Helped with the initial research and creation of carte2.```
- [VDavid003](https://github.com/VDavid003) ```Helped me reverse engineer the PoC via the packet dumps and personally tested on his devices.```
- [halal-beef](https://github.com/halal-beef) ```Initial USB packet dumps and analysis of the PoC during the research lifecycle.```
- [R0rt1z2](https://github.com/R0rt1z2) ```Huge help, even in payload creation, some stuff was based off his project, kaeru.```
- [AntiEngineer](https://github.com/AntiEngineer) ```Huge help, gave knowledge and hints about ARM and is all around a great friend.```
- AA ```Vulnerability inspiration, first use outside of Chimera. Someone I knew who conducted research on this exploit.```
