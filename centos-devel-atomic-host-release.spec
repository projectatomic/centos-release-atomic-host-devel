%define debug_package %{nil}
%define product_family CentOSDev
%define variant_titlecase Atomic Host
%define variant_lowercase atomic-host
%define release_name Devel
%define base_release_version 7
%define full_release_version 7
%define dist_release_version 7
# Irritatingly systemd depends on system-release >= 7.2 so
# we need to synthesize that.
%define upstream_release_version 7.2
#define beta Beta
%define dist .el%{dist_release_version}.centos

Name:           centos-devel-atomic-host-release
Version:        %{base_release_version}
Release:        %{centos_rel}%{?dist}.2.10
Summary:        %{product_family} release file
Group:          System Environment/Base
License:        GPLv2
Provides:       centos-release = %{version}-%{release}
Provides:       redhat-release = %{upstream_release_version}
Provides:       system-release = %{upstream_release_version}
Provides:       system-release(releasever) = %{upstream_release_version}
Source0:        centos-devel-atomic-host-release-%{base_release_version}.tar.gz

%description
%{product_family} release files

%prep
%setup -q -n centos-release-%{base_release_version}

%build
echo OK

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
mkdir -p %{buildroot}/usr/lib/

# create /etc/system-release and /etc/redhat-release
echo "%{product_family} release %{full_release_version}.%{centos_rel} (%{release_name}) " > %{buildroot}/usr/lib/centos-release-devel
ln -s ../usr/lib/centos-release-devel %{buildroot}/etc/system-release
ln -s ../usr/lib/centos-release-devel %{buildroot}/etc/redhat-release

# create /etc/os-release
cat << EOF >>%{buildroot}/usr/lib/os-release
NAME="%{product_family}%{?variant_titlecase: %{variant_titlecase}}"
VERSION="%{full_release_version} (%{release_name})"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="%{full_release_version}"
PRETTY_NAME="%{product_family}%{?variant_titlecase: %{variant_titlecase}} %{full_release_version} (%{release_name})"
ANSI_COLOR="0;31"
HOME_URL="https://wiki.centos.org/SpecialInterestGroup/Atomic/Download/"
BUG_REPORT_URL="https://bugs.centos.org/"
VARIANT="Atomic Host"
VARIANT_ID=atomic.host
EOF
ln -s ../usr/lib/os-release %{buildroot}/etc/os-release

# create /etc/issue and /etc/issue.net
echo '\S' > %{buildroot}/etc/issue
echo 'Kernel \r on an \m' >> %{buildroot}/etc/issue
cp %{buildroot}/etc/issue %{buildroot}/etc/issue.net
echo >> %{buildroot}/etc/issue

# copy GPG keys
mkdir -p -m 755 %{buildroot}/etc/pki/rpm-gpg
for file in RPM-GPG-KEY* ; do
    install -m 644 $file %{buildroot}/etc/pki/rpm-gpg
done

# copy yum repos
mkdir -p -m 755 %{buildroot}/etc/yum.repos.d
for file in CentOS-*.repo; do
    install -m 644 $file %{buildroot}/etc/yum.repos.d
done

# add base centos remote
mkdir -p -m 755 %{buildroot}/etc/ostree/remotes.d
for f in centos-atomic-host.conf centos-atomic-continuous.conf; do \
    install -m 644 $f %{buildroot}/etc/ostree/remotes.d; \
done

# add centos atomic sig key
mkdir -p -m 700 %{buildroot}/usr/share/ostree/trusted.gpg.d
/usr/bin/gpg2 --homedir %{buildroot}/usr/share/ostree/trusted.gpg.d --import RPM-GPG-KEY-CentOS-SIG-Atomic

# use unbranded datadir
mkdir -p -m 755 %{buildroot}/%{_datadir}/centos-release
ln -s centos-release %{buildroot}/%{_datadir}/redhat-release
install -m 644 EULA %{buildroot}/%{_datadir}/centos-release

# use unbranded docdir
mkdir -p -m 755 %{buildroot}/%{_docdir}/centos-release
ln -s centos-release %{buildroot}/%{_docdir}/redhat-release
install -m 644 GPL %{buildroot}/%{_docdir}/centos-release
install -m 644 Contributors %{buildroot}/%{_docdir}/centos-release

# copy systemd presets
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -m 0644 85-display-manager.preset %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -m 0644 90-default.preset %{buildroot}%{_prefix}/lib/systemd/system-preset/


%files
%defattr(0644,root,root,0755)
/etc/redhat-release
/etc/system-release
/etc/os-release
%config(noreplace) /etc/issue
%config(noreplace) /etc/issue.net
/etc/pki/rpm-gpg/
%config(noreplace) /etc/yum.repos.d/*
/etc/ostree/remotes.d/
/usr/share/ostree/trusted.gpg.d/
%{_docdir}/redhat-release
%{_docdir}/centos-release/*
%{_datadir}/redhat-release
%{_datadir}/centos-release/*
%{_prefix}/lib/os-release
%{_prefix}/lib/centos-release-devel
%{_prefix}/lib/systemd/system-preset/*
