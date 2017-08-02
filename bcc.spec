Name:		bcc
Version:	0.3.0
Release:	4%{?dist}
Summary:	BPF Compiler Collection (BCC)
License:	ASL 2.0
URL:		https://github.com/iovisor/bcc
Source0:	%{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# Arches will be included as upstream support is added and dependencies are
# satisfied in the respective arches
ExclusiveArch:	x86_64

BuildRequires:	bison, cmake >= 2.8.7, flex, libxml2-devel
BuildRequires:	python3-devel
BuildRequires:	elfutils-libelf-devel-static
BuildRequires:	llvm-devel llvm-static clang-devel
BuildRequires:	ncurses-devel
BuildRequires:	pkgconfig(luajit)

Requires:	%{name}-tools = %{version}-%{release}

%description
BCC is a toolkit for creating efficient kernel tracing and manipulation
programs, and includes several useful tools and examples. It makes use of
extended BPF (Berkeley Packet Filters), formally known as eBPF, a new feature
that was first added to Linux 3.15. BCC makes BPF programs easier to write,
with kernel instrumentation in C (and includes a C wrapper around LLVM), and
front-ends in Python and lua. It is suited for many tasks, including
performance analysis and network traffic control.


%package devel
Summary:	Shared library for BPF Compiler Collection (BCC)
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for developing
application that use BPF Compiler Collection (BCC).


%package doc
Summary:	Examples for BPF Compiler Collection (BCC)
Requires:	python3-%{name} = %{version}-%{release}
Requires:	%{name}-lua = %{version}-%{release}
BuildArch:	noarch

%description doc
Examples for BPF Compiler Collection (BCC)


%package -n python3-%{name}
Summary:	Python3 bindings for BPF Compiler Collection (BCC)
Requires:	%{name}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{name}
Python3 bindings for BPF Compiler Collection (BCC)


%package lua
Summary:	Standalone tool to run BCC tracers written in Lua
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description lua
Standalone tool to run BCC tracers written in Lua


%package tools
Summary:	Command line tools for BPF Compiler Collection (BCC)
Requires:	python3-%{name} = %{version}-%{release}
Requires:	python3-netaddr
BuildArch:	noarch

%description tools
Command line tools for BPF Compiler Collection (BCC)


%prep
%autosetup -p1


%build
%cmake . -DREVISION_LAST=%{version} -DREVISION=%{version} -DPYTHON_CMD=python3 \
	-DLUAJIT_INCLUDE_DIR=`pkg-config --variable=includedir luajit` \
	-DLUAJIT_LIBRARIES=`pkg-config --variable=libdir luajit`/lib`pkg-config --variable=libname luajit`.so
%make_build


%install
%make_install

# Fix python shebangs
for i in `find %{buildroot}/usr/share/%{name}/tools/ -type f`; do
	sed -i 's/\/usr\/bin\/env python\>/\/usr\/bin\/python3/' $i
	sed -i 's/\/usr\/bin\/python\>/&3/' $i
done

# Examples in /usr/share shouldn't contain binaries according to FHS
rm -rf %{buildroot}/usr/share/%{name}/examples/cpp
for i in `find %{buildroot}/usr/share/%{name}/examples/ -type f`; do
	sed -i 's/\/usr\/bin\/env python\>/\/usr\/bin\/python3/' $i
	sed -i 's/\/usr\/bin\/python\>/&3/' $i
	sed -i 's/\/usr\/bin\/env bcc-lua\>/\/usr\/bin\/bcc-lua/' $i
	chmod -x $i
done

# Compress man pages
find %{buildroot}/usr/share/%{name}/man/man8/ -name "*.8" -exec gzip {} \;

# We cannot run the test suit since it requires root and it makes changes to
# the machine (e.g, IP address)
#%check

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc README.md
%license LICENSE.txt COPYRIGHT.txt
%{_libdir}/lib%{name}.so.*

%files devel
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/lib%{name}.pc
%{_includedir}/%{name}/

%files -n python3-%{name}
%{python3_sitelib}/%{name}*

%files doc
%dir %{_datadir}/%{name}
%doc %{_datadir}/%{name}/examples/
%exclude %{_datadir}/%{name}/examples/*.pyc
%exclude %{_datadir}/%{name}/examples/*.pyo
%exclude %{_datadir}/%{name}/examples/*/*.pyc
%exclude %{_datadir}/%{name}/examples/*/*.pyo
%exclude %{_datadir}/%{name}/examples/*/*/*.pyc
%exclude %{_datadir}/%{name}/examples/*/*/*.pyo

%files tools
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/tools
%{_datadir}/%{name}/tools/*
%exclude %{_datadir}/%{name}/tools/old/
%dir %{_datadir}/%{name}/man
%{_datadir}/%{name}/man/*

%files lua
%{_bindir}/bcc-lua


%changelog
* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.3.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.3.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Mar 30 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.3.0-2
- Rebuild for LLVM4
- Trivial fixes in spec

* Fri Mar 10 2017 Rafael Fonseca <rdossant@redhat.com> - 0.3.0-1
- Rebase to new release.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 10 2017 Rafael Fonseca <rdossant@redhat.com> - 0.2.0-2
- Fix typo

* Tue Nov 29 2016 Rafael Fonseca <rdossant@redhat.com> - 0.2.0-1
- Initial import
