Summary: Validating, recursive, and caching DNS(SEC) resolver
Name: unbound
Version: 1.1.0
Release: 1%{?dist}
License: BSD
Url: http://www.nlnetlabs.nl/unbound/
Source: http://www.unbound.net/downloads/%{name}-%{version}.tar.gz
Source1: unbound.init
Source2: unbound.conf
Source3: unbound.munin
Group: System Environment/Daemons
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: flex, openssl-devel, ldns-devel >= 1.4.0, libevent-devel
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
Requires: ldns >= 1.4.0
Requires(pre): shadow-utils
# Is this obsolete?
#Provides: caching-nameserver

%description
Unbound is a validating, recursive, and caching DNS(SEC) resolver.

The C implementation of Unbound is developed and maintained by NLnet
Labs. It is based on ideas and algorithms taken from a java prototype
developed by Verisign labs, Nominet, Kirei and ep.net.

Unbound is designed as a set of modular components, so that also
DNSSEC (secure DNS) validation and stub-resolvers (that do not run
as a server, but are linked into an application) are easily possible.

%package munin
Summary: Plugin for the munin / munin-node monitoring package
Group:     System Environment/Daemons
Requires: munin-node
Requires: %{name} = %{version}-%{release}

%description munin
Plugin for the munin / munin-node monitoring package

%package devel
Summary: Development package that includes the unbound header files
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}, openssl-devel, ldns-devel
Requires: libevent-devel

%description devel
The devel package contains the unbound library and the include files

%package libs
Summary: Libraries used by the unbound server and client applications
Group: Applications/System
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description libs
Contains libraries used by the unbound server and client applications

%prep
%setup -q 

%build
%configure  --with-ldns= --with-libevent --with-pthreads --with-ssl \
            --disable-rpath --enable-debug --disable-static \
            --with-run-dir=%{_localstatedir}/lib/%{name}\
            --with-conf-file=%{_localstatedir}/lib/%{name}/unbound.conf \
            --with-pidfile=%{_localstatedir}/run/%{name}/%{name}.pid
%{__make} CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE" QUIET=no %{?_smp_mflags}

%install
rm -rf %{buildroot}
%{__make} DESTDIR=%{buildroot} install
install -d 0755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d 0755 %{buildroot}%{_initrddir}
#install -m 0755 contrib/unbound.init %{buildroot}%{_initrddir}/unbound
install -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/unbound
#overwrite stock unbound.conf with our own
install -m 0755 %{SOURCE2} %{buildroot}%{_localstatedir}/lib/%{name}
install -d 0755 %{buildroot}%{_sysconfdir}/munin/plugin-conf.d
install -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/munin/plugin-conf.d/unbound
install -d 0755 %{buildroot}%{_datadir}/munin/plugins/
install -m 0755 contrib/unbound_munin_ %{buildroot}%{_datadir}/munin/plugins/unbound

# add symbolic link from /etc/unbound.conf -> /var/unbound/unbound.conf

( cd %{buildroot}%{_sysconfdir}/ ; ln -s ..%{_localstatedir}/lib/unbound/unbound.conf )
# remove static library from install (fedora packaging guidelines)
rm -rf %{buildroot}%{_libdir}/*.la

# The chroot needs /dev/log, /dev/random, /etc/resolv.conf and /etc/localtime
# but the init script uses mount --bind, so just create empty files
mkdir -p %{buildroot}%{_localstatedir}/lib/unbound/etc \
         %{buildroot}%{_localstatedir}/lib/unbound/dev 
echo "Used for mount --bind in initscript" >  %{buildroot}%{_localstatedir}/lib/unbound/etc/resolv.conf 
echo "Used for mount --bind in initscript" > %{buildroot}%{_localstatedir}/lib/unbound/etc/localtime
echo "Used for mount --bind in initscript" > %{buildroot}%{_localstatedir}/lib/unbound/dev/log 
echo "Used for mount --bind in initscript" > %{buildroot}%{_localstatedir}/lib/unbound/dev/random
mkdir -p %{buildroot}%{_localstatedir}/lib/unbound/var/run/unbound
mkdir -p %{buildroot}%{_localstatedir}/run/unbound

%clean
rm -rf ${RPM_BUILD_ROOT}

%files 
%defattr(-,root,root,-)
%doc doc/README doc/CREDITS doc/LICENSE doc/FEATURES
%attr(0755,root,root) %{_initrddir}/%{name}
# the chroot env
%attr(0755,root,root) %dir %{_localstatedir}/lib/%{name}
%attr(0755,unbound,unbound) %dir %{_localstatedir}/run/%{name}
%attr(0755,root,root) %dir %{_localstatedir}/lib/%{name}/dev
%attr(0755,root,root) %dir %{_localstatedir}/lib/%{name}/etc
%attr(0755,root,root) %dir %{_localstatedir}/lib/%{name}/var
%attr(0755,root,root) %dir %{_localstatedir}/lib/%{name}/var/run
%attr(0755,root,root) %dir %{_localstatedir}/lib/%{name}/var/run/unbound
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/unbound.conf
%attr(0644,root,root) %config(noreplace) %{_localstatedir}/lib/%{name}/unbound.conf
%attr(0644,root,root) %{_localstatedir}/lib/%{name}/dev/*
%attr(0644,root,root) %{_localstatedir}/lib/%{name}/etc/*
%{_sbindir}/*
%{_mandir}/*/*

%files munin
%defattr(-,root,root,-)
%{_sysconfdir}/munin/plugin-conf.d/unbound
%{_datadir}/munin/plugins/unbound

%files devel
%defattr(-,root,root,-)
%{_libdir}/libunbound.so
%{_includedir}/unbound.h
%doc README

%files libs
%defattr(-,root,root,-)
%{_libdir}/libunbound.so.*
%doc doc/README doc/LICENSE

%pre
getent group unbound >/dev/null || groupadd -r unbound
getent passwd unbound >/dev/null || \
useradd -r -g unbound -d %{_localstatedir}/lib/%{name} -s /sbin/nologin \
-c "Unbound DNS resolver" unbound
exit 0

%post 
/sbin/chkconfig --add %{name}

%post libs -p /sbin/ldconfig


%preun
if [ $1 -eq 0 ]; then
        /sbin/service %{name} stop >/dev/null 2>&1
        /sbin/chkconfig --del %{name} 
fi

%postun 
if [ "$1" -ge "1" ]; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%postun libs -p /sbin/ldconfig

%changelog
* Fri Nov 14 2008 Paul Wouters <paul@xelerance.com> - 1.1.0-1
- Updated to version 1.1.0
- Updated unbound.conf's statistics options and remote-control
  to work properly for munin
- Added unbound-munin package
- Generate unbound remote-control  key/certs on first startup
- Required ldns is now 1.4.0

* Wed Oct 22 2008 Paul Wouters <paul@xelerance.com> - 1.0.2-5
- Only call ldconfig in -libs package
- Move configure into build section
- devel subpackage should only depend on libs subpackage

* Tue Oct 21 2008 Paul Wouters <paul@xelerance.com> - 1.0.2-4
- Fix CFLAGS getting lost in build
- Don't enable interface-automatic:yes because that
  causes unbound to listen on 0.0.0.0 instead of 127.0.0.1

* Sun Oct 19 2008 Paul Wouters <paul@xelerance.com> - 1.0.2-3
- Split off unbound-libs, make build verbose 

* Thu Oct  9 2008 Paul Wouters <paul@xelerance.com> - 1.0.2-2
- FSB compliance, chroot fixes, initscript fixes

* Thu Sep 11 2008 Paul Wouters <paul@xelerance.com> - 1.0.2-1
- Upgraded to 1.0.2

* Wed Jul 16 2008 Paul Wouters <paul@xelerance.com> - 1.0.1-1
- upgraded to new release

* Wed May 21 2008 Paul Wouters <paul@xelerance.com> - 1.0.0-2
- Build against ldns-1.3.0

* Wed May 21 2008 Paul Wouters <paul@xelerance.com> - 1.0.0-1
- Split of -devel package, fixed dependancies, make rpmlint happy

* Thu Apr 25 2008 Wouter Wijngaards <wouter@nlnetlabs.nl> - 0.12
- Using parts from ports collection entry by Jaap Akkerhuis.
- Using Fedoraproject wiki guidelines.

* Wed Apr 23 2008 Wouter Wijngaards <wouter@nlnetlabs.nl> - 0.11
- Initial version.



