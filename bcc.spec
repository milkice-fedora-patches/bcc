# luajit is not available for some architectures
%ifarch ppc64 ppc64le s390x
%bcond_with lua
%else
%bcond_without lua
%endif

%bcond_without llvm_static

Name:           bcc
Version:        0.10.0
Release:        2%{?dist}
Summary:        BPF Compiler Collection (BCC)
License:        ASL 2.0
URL:            https://github.com/iovisor/bcc
# Generate source tarball until upstream bug is fixed
# See https://github.com/iovisor/bcc/issues/2261
# To generate the tarball, use the following commands
# git clone -b "v0.10.0" --single-branch --depth 1 url bcc-0.10.0
# pushd bcc-0.10.0
# git submodule update --init
# popd
# tar zcvf bcc-0.10.0.tar.gz bcc-0.10.0/
#Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz

# Arches will be included as upstream support is added and dependencies are
# satisfied in the respective arches
ExclusiveArch:  x86_64 %{power64} aarch64 s390x

BuildRequires:  bison
BuildRequires:  cmake >= 2.8.7
BuildRequires:  flex
BuildRequires:  libxml2-devel
BuildRequires:  python3-devel
BuildRequires:  elfutils-libelf-devel
BuildRequires:  llvm-devel
BuildRequires:  clang-devel
%if %{with llvm_static}
BuildRequires:  llvm-static
%endif
BuildRequires:  ncurses-devel
%if %{with lua}
BuildRequires:  pkgconfig(luajit)
%endif

Requires:       %{name}-tools = %{version}-%{release}

%description
BCC is a toolkit for creating efficient kernel tracing and manipulation
programs, and includes several useful tools and examples. It makes use of
extended BPF (Berkeley Packet Filters), formally known as eBPF, a new feature
that was first added to Linux 3.15. BCC makes BPF programs easier to write,
with kernel instrumentation in C (and includes a C wrapper around LLVM), and
front-ends in Python and lua. It is suited for many tasks, including
performance analysis and network traffic control.


%package devel
Summary:        Shared library for BPF Compiler Collection (BCC)
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for developing
application that use BPF Compiler Collection (BCC).


%package doc
Summary:        Examples for BPF Compiler Collection (BCC)
Recommends:     python3-%{name} = %{version}-%{release}
Recommends:     %{name}-lua = %{version}-%{release}
BuildArch:      noarch

%description doc
Examples for BPF Compiler Collection (BCC)


%package -n python3-%{name}
Summary:        Python3 bindings for BPF Compiler Collection (BCC)
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{name}
Python3 bindings for BPF Compiler Collection (BCC)


%if %{with lua}
%package lua
Summary:        Standalone tool to run BCC tracers written in Lua
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description lua
Standalone tool to run BCC tracers written in Lua
%endif


%package tools
Summary:        Command line tools for BPF Compiler Collection (BCC)
Requires:       python3-%{name} = %{version}-%{release}
Requires:       python3-netaddr
Requires:       kernel-devel

%description tools
Command line tools for BPF Compiler Collection (BCC)


%prep
%autosetup -p1


%build
%cmake . \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DREVISION_LAST=%{version} -DREVISION=%{version} -DPYTHON_CMD=python3 \
        %{?with_llvm_shared:-DENABLE_LLVM_SHARED=1}
%make_build


%install
%make_install

# Fix python shebangs
find %{buildroot}%{_datadir}/%{name}/{tools,examples} -type f -exec \
  sed -i -e '1s=^#!/usr/bin/python\([0-9.]\+\)\?$=#!%{__python3}=' \
         -e '1s=^#!/usr/bin/env python\([0-9.]\+\)\?$=#!%{__python3}=' \
         -e '1s=^#!/usr/bin/env bcc-lua$=#!/usr/bin/bcc-lua=' {} \;

# Move man pages to the right location
mkdir -p %{buildroot}%{_mandir}
mv %{buildroot}%{_datadir}/%{name}/man/* %{buildroot}%{_mandir}/
# Avoid conflict with other manpages
# https://bugzilla.redhat.com/show_bug.cgi?id=1517408
for i in `find %{buildroot}%{_mandir} -name "*.gz"`; do
  tname=$(basename $i)
  rename $tname %{name}-$tname $i
done
mkdir -p %{buildroot}%{_docdir}/%{name}
mv %{buildroot}%{_datadir}/%{name}/examples %{buildroot}%{_docdir}/%{name}/

# Delete old tools we don't want to ship
rm -rf %{buildroot}%{_datadir}/%{name}/tools/old/

# We cannot run the test suit since it requires root and it makes changes to
# the machine (e.g, IP address)
#%check

%ldconfig_scriptlets

%files
%doc README.md
%license LICENSE.txt
%{_libdir}/lib%{name}.so.*
%{_libdir}/libbcc_bpf.so.*

%files devel
%{_libdir}/lib%{name}.so
%{_libdir}/libbcc_bpf.so
%{_libdir}/pkgconfig/lib%{name}.pc
%{_includedir}/%{name}/

%files -n python3-%{name}
%{python3_sitelib}/%{name}*

%files doc
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/examples/

%files tools
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/tools/
%{_datadir}/%{name}/introspection/
%{_mandir}/man8/*

%if %{with lua}
%files lua
%{_bindir}/bcc-lua
%endif


%changelog
* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed May 29 2019 Rafael dos Santos <rdossant@redhat.com> - 0.10.0-1
- Rebase to latest upstream version (#1714902)

* Thu Apr 25 2019 Rafael dos Santos <rdossant@redhat.com> - 0.9.0-1
- Rebase to latest upstream version (#1686626)
- Rename libbpf header to libbcc_bpf

* Mon Apr 22 2019 Neal Gompa <ngompa@datto.com> - 0.8.0-5
- Make the Python 3 bindings package noarch
- Small cleanups to the spec

* Tue Mar 19 2019 Rafael dos Santos <rdossant@redhat.com> - 0.8.0-4
- Add s390x support (#1679310)

* Wed Feb 20 2019 Rafael dos Santos <rdossant@redhat.com> - 0.8.0-3
- Add aarch64 support (#1679310)

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jan 17 2019 Rafael dos Santos <rdossant@redhat.com> - 0.8.0-1
- Rebase to new released version

* Thu Nov 01 2018 Rafael dos Santos <rdossant@redhat.com> - 0.7.0-4
- Fix attaching to usdt probes (#1634684)

* Mon Oct 22 2018 Rafael dos Santos <rdossant@redhat.com> - 0.7.0-3
- Fix encoding of non-utf8 characters (#1516678)
- Fix str-bytes conversion in killsnoop (#1637515)

* Sat Oct 06 2018 Rafael dos Santos <rdossant@redhat.com> - 0.7.0-2
- Fix str/bytes conversion in uflow (#1636293)

* Tue Sep 25 2018 Rafael Fonseca <r4f4rfs@gmail.com> - 0.7.0-1
- Rebase to new released version

* Wed Aug 22 2018 Rafael Fonseca <r4f4rfs@gmail.com> - 0.6.1-2
- Fix typo when mangling shebangs.

* Thu Aug 16 2018 Rafael Fonseca <r4f4rfs@gmail.com> - 0.6.1-1
- Rebase to new released version (#1609485)

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.6.0-2
- Rebuilt for Python 3.7

* Mon Jun 18 2018 Rafael dos Santos <rdossant@redhat.com> - 0.6.0-1
- Rebase to new released version (#1591989)

* Thu Apr 05 2018 Rafael Santos <rdossant@redhat.com> - 0.5.0-4
- Resolves #1555627 - fix compilation error with latest llvm/clang

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Feb 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.5.0-2
- Switch to %%ldconfig_scriptlets

* Wed Jan 03 2018 Rafael Santos <rdossant@redhat.com> - 0.5.0-1
- Rebase to new released version

* Thu Nov 16 2017 Rafael Santos <rdossant@redhat.com> - 0.4.0-4
- Resolves #1517408 - avoid conflict with other manpages

* Thu Nov 02 2017 Rafael Santos <rdossant@redhat.com> - 0.4.0-3
- Use weak deps to not require lua subpkg on ppc64(le)

* Wed Nov 01 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.4.0-2
- Rebuild for LLVM5

* Wed Nov 01 2017 Rafael Fonseca <rdossant@redhat.com> - 0.4.0-1
- Resolves #1460482 - rebase to new release
- Resolves #1505506 - add support for LLVM 5.0
- Resolves #1460482 - BPF module compilation issue
- Partially address #1479990 - location of man pages
- Enable ppc64(le) support without lua
- Soname versioning for libbpf by ignatenkobrain

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
