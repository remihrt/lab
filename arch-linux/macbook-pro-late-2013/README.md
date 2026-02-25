## Create the bootable USB drive

##### Download the ISO

broadcom kernel module is need to be able to enable WiFi.

An ISO image with the necessary modules can be build using [this repo](https://github.com/SalDevX/archlinux-BCM4360_SUPPORT).

You can download a prebuilt ISO [here](https://drive.google.com/uc?export=download&id=1T7eOPBnpQysCpjo_9NMvmkim7hK84Oin).

##### Find the USB device

macOS:
```
diskutil list external
```

Linux:
```
fdisk -l
```

Copy the ISO on the USB (replace `sdX` with the USB device):
```
sudo dd if=archlinux-BCM4360_SUPPORT.iso of=/dev/sdX bs=1M status=progress && sync
```

## Boot the USB

Plug the USB drive into the MacBook, power it and hold alt/option key.  
Choose EFI (the icon that represent an external orange drive).

## Installation

##### Keyboard layout

U.S. English keyboard? Nothing to do.  
Otherwise, you may need to do the step 1.5 of the [installation guide](https://wiki.archlinux.org/title/Installation_guide).

##### Connect to internet

```
iwctl
```

List devices (should be wlan0):
```
device list
```

Search for networks:
```
station wlan0 scan
```

Find SSID name:
```
station wlan0 get-networks
```

Connect to the SSID:
```
station wlan0 connect SSID
```

##### Update the system clock

```
timedatectl
```

##### Partitioning the disk

I'm assuming that you only want Arch Linux.  
**This will wipe out the entire disk.**

Display devices:
```
fdisk -l
```

Normally it will be `sda`.

For security reason we wipe on the disk with zeros:
```
cryptsetup open --type plain --key-file /dev/urandom --sector-size 4096 /dev/sda to_be_wiped
```

```
dd if=/dev/zero of=/dev/mapper/to_be_wiped status=progress bs=1M
```

```
cryptsetup close to_be_wiped
```

First make sure to create a fresh GPT:
```
gdisk /dev/sda
```

o → create new GPT partition table  
n → new partition, 1 (sda1), default start (press enter), +1G, type EF00  
n → new partition, 2 (sda2), default start (press enter), rest of the disk space (press enter), type 8309 (Linux LUKS)  
w → write to disk, confirm with y

##### Format partitions

Format EFI:
```
mkfs.fat -F32 /dev/sda1
```

Set up LUKS on sda2:
```
cryptsetup luksFormat /dev/sda2
```
You will be asked to enter a passphrase to encrypt the disk.

Open the LUKS container with the passphrase:
```
cryptsetup open /dev/sda2 cryptlvm
```

Create physical volume:
```
pvcreate /dev/mapper/cryptlvm
```

Create volume group:
```
vgcreate vg0 /dev/mapper/cryptlvm
```

Create logical volumes:
```
lvcreate -L 4G vg0 -n swap
```

```
lvcreate -L 32G vg0 -n root
```

```
lvcreate -l 100%FREE vg0 -n home
```

Leave some free space in the volume group:
```
lvreduce -L -256M /dev/vg0/home
```

Then format them:
```
mkfs.ext4 /dev/vg0/root
```

```
mkfs.ext4 /dev/vg0/home
```

```
mkswap /dev/vg0/swap
```

Then mount:
```
mount /dev/vg0/root /mnt
```

```
mount --mkdir /dev/sda1 /mnt/boot
```

```
mount --mkdir /dev/vg0/home /mnt/home
```

```
swapon /dev/vg0/swap
```

##### Installing Arch Linux

```
pacstrap /mnt base linux linux-headers linux-firmware intel-ucode lvm2 broadcom-wl-dkms sudo vim iwd
```

Generate fstab file to mount volumes on boot:
```
genfstab -U /mnt >> /mnt/etc/fstab
```

```
cat /mnt/etc/fstab
```
You should see entries for `/`, `/boot`, `/home` and swap.

Enter in the new installed system:
```
arch-chroot /mnt
```

##### Time

```
ln -sf /usr/share/zoneinfo/<Area>/<Location> /etc/localtime
```

```
hwclock --systohc
```

##### Localization

```
vim /etc/locale.gen
```
Uncomment your locale, for example `en_US.UTF-8 UTF-8`.

Then generate it:
```
locale-gen
```

Then create `/etc/locale.conf`:
```
echo "LANG=en_US.UTF-8" > /etc/locale.conf
```

And set your hostname:
```
echo "yourhostname" > /etc/hostname
```

##### Networking

Edit network config:
```
vim /etc/systemd/network/25-wireless.network
```

Add this content:
```
[Match]
Name=wlan0

[Network]
DHCP=yes
IgnoreCarrierLoss=3s
```

Enable systemd-networkd:
```
systemctl enable systemd-networkd.service
```

Enable systemd-resolved:
```
systemctl enable systemd-resolved.service
```

Enable iwd:
```
systemctl enable iwd
```

##### Set bigger font for disk decryption passphrase

```
echo "FONT=latarcyrheb-sun32" > /etc/vconsole.conf
```

##### mkinitcpio

```
vim /etc/mkinitcpio.conf
```

Find the uncommented `HOOKS` line and make sure it looks like this:
```
HOOKS=(base systemd autodetect microcode modconf kms keyboard sd-vconsole block sd-encrypt lvm2 filesystems fsck)
```

Check that everything is good (might have some warnings):
```
mkinitcpio -P
```

##### Bootloader

Exit arch-chroot:
```
exit
```

```
bootctl --esp-path=/mnt/boot install
```

Re-enter in arch-chroot:
```
arch-chroot /mnt
```

```
bootctl install
```

```
vim /boot/loader/loader.conf
```

```
default arch.conf
timeout 3
console-mode max
```

Get /dev/sda2 UUID:
```
blkid -s UUID -o value /dev/sda2
```
*hint: you can also run this command directly in vim with* `:r!<command_above>`

```
vim /boot/loader/entries/arch.conf
```

```
title   Arch Linux
linux   /vmlinuz-linux
initrd  /intel-ucode.img
initrd  /initramfs-linux.img
options rd.luks.name=<uuid-of-sda2>=cryptlvm root=/dev/vg0/root resume=/dev/vg0/swap rw
```

##### Set up root password

```
passwd
```

##### REBOOT!!!

```
exit
```

```
reboot
```

Congratulations! You have completed the Arch Linux installation.  
Your old MacBook will have a second life.
