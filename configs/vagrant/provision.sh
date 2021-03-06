#!/bin/bash

# Arch Linux Development Environment
# This provisioning is designed for a virtualized development machine. The
# machine not only provides the development environment and services, but also
# the dev tools such as SQL editors and IDEs. Use the following variables to
# specify extra packages to install alongside those of this Vagrantfile's
# minimal configuration. AUR packages specified below will be downloaded into
# the default user's ~/src/abs directory, built, and installed. If AUR
# dependencies require user interaction beyond a simple confirmation of yes or
# no (such as the "java-runtime" virtual package), one may explcitly include
# them here.
extra_pkgs=( libmariadbclient python python-pip ttf-dejavu xorg-xauth )
aur_pkgs=()

# This script is executed on the guest machine via Vagrant's shell provisioner.
# Remember that the Vagrant shell provisioner transfers this file to the guest
# and executes it there as the root user, NOT vagrant. The initial PWD
# is the vagrant user's home directory, however. All commands in this file
# should be idempotent.
default_user='vagrant'
home_dir=/home/${default_user}
src_dir=/vagrant

echo 'TASK: Set timezone'
timedatectl set-timezone UTC

echo 'TASK: Full system upgrade'
pacman -Syu --noconfirm --quiet

# Install necessary packages.
# pacman will return exit status > 0 if one or more package in query was not found.
# As of 2016-03-11, Linux headers are necessary for virtualbox-guest-dkms package in order to build
# kernel modules for VirtualBox guest additions.
# See: https://www.archlinux.org/packages/community/x86_64/virtualbox-guest-dkms/
echo 'TASK: Installing explicit packages'
packages=( base-devel docker git linux-headers tree ${extra_pkgs[@]} )
pacman -Qiq ${packages[@]} 1> /dev/null || pacman -S ${packages[@]} --noconfirm --quiet --needed

# Configure git
su vagrant -c 'git config --global core.editor nano'

# Enable SSH X11 forwarding.
sed -i 's/#X11Forwarding no/X11Forwarding yes/' /etc/ssh/sshd_config

# Add default Vagrant user to docker group.
# Effectively NOOP if already in docker group.
echo 'TASK: Add vagrant user to docker group'
usermod -aG docker ${default_user}

# Effectively NOOP if already enabled.
echo 'TASK: Enable Docker Engine daemon at startup'
systemctl enable docker

echo 'TASK: Source .profile from .bash_profile'
source_profile='[[ -f ~/.profile ]] && source ~/.profile'
grep -Fxq "${source_profile}" .bash_profile || echo ${source_profile} >> .bash_profile

# Add alias to .bashrc. .bashrc is always present in base image so no need to check existence.
echo 'TASK: Add bash aliases'
alias_line_la="alias la='LC_COLLATE=C ls -Alh --color --group-directories-first'"
grep -q "${alias_line_la}" .bashrc || \
  sed -i "/alias ls='ls --color=auto'/a ${alias_line_la}" .bashrc

# Change to project directory on any new interactive terminal session.
echo 'TASK: Set PWD to project directory'
cd_cmd="cd ${src_dir}"
grep -Fxq "${cd_cmd}" .bashrc || echo ${cd_cmd} >> .bashrc

# Prepare to download and install AUR packages.
# Example: Import mysql-build@oss.oracle.com PGP key for JDBC driver.
# echo 'TASK: Prepare to download AUR packages'
#su ${default_user} -c 'gpg --keyserver pgp.mit.edu --recv 5072E1F5'

# Download AUR resources. Due to complexity of some manual installs, makepkg
# will not automatically be run. The user will need to install them after login.
# This is naive and brittle. Upgrade this to actual AUR helper tool.
# makepkg output is redirected to /dev/null since download progress cannot
# be silenced and it blasts display with disjointed characters under su.
echo 'TASK: Download AUR packages'
abs_dir=${home_dir}/src/abs
su ${default_user} -c 'mkdir -p '${abs_dir}
cd ${abs_dir}
for pkg in ${aur_pkgs[@]}; do
  if [[ -d ${pkg} ]]; then
    cd ${pkg}
    git pull --quiet origin #| sed 's/^/  /'
  else
    su ${default_user} -c 'git clone https://aur.archlinux.org/'${pkg}'.git'
    cd ${pkg}
  fi
  echo 'Running makepkg silently'
  su ${default_user} -c 'makepkg -crs --noconfirm --noprogressbar --needed > /dev/null 2>&1'
  pacman -U *.pkg.tar.xz --noconfirm --needed
  cd ${abs_dir}
done

# PROJECT-SPECIFIC TASKS
echo 'TASK: Install Python packages and modules.'
cd ${src_dir}
su ${default_user} -c 'make dependencies'

# Reboot system.
# Actual reboot removed for now since rebooting outside of Vagrant's control
# seems to prevent the working directory from being mounted to the guest's
# /vagrant path.
echo 'NOTICE: Optionally set git user.name and user.email.'
echo 'WARNING: "vagrant reload" may be required to apply software and configuration updates.'
