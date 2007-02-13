#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)
#
%define		rel	0.1
Summary:	Prism54 kernel drivers
Summary(es.UTF-8):	Driveres del núcleo de Prism54
Summary(pl.UTF-8):	Sterowniki Prism54 dla jądra Linuksa
Name:		kernel-net-prism54
Version:	1.3
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://prism54.org/pub/linux/snapshot/tars/prism54-svn-latest.tar.bz2
# Source0-md5:	6c5ffe1f32db577ffd2083cbc3622eb6
URL:		http://prism54.org/
BuildRequires:	%{kgcc_package}
%if %{with dist_kernel}
BuildRequires:	kernel-module-build >= 3:2.6.7
%requires_releq_kernel_up
%endif
BuildRequires:	rpmbuild(macros) >= 1.153
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Prism54 kernel drivers.

%description -l es.UTF-8
Módulos de núcleo para Prism54.

%description -l pl.UTF-8
Sterowniki Prism54 dla jądra Linuksa.

%package -n kernel-smp-net-prism54
Summary:	Prism54 SMP kernel drivers
Summary(pl.UTF-8):	Sterowniki Prism54 dla jądra Linuksa SMP
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-net-prism54
Prism54 kernel drivers. SMP version.

%description -n kernel-smp-net-prism54 -l es.UTF-8
Módulos de núcleo para Prism54. Versión SMP.

%description -n kernel-smp-net-prism54 -l pl.UTF-8
Sterowniki Prism54 dla jądra Linuksa SMP.

%prep
%setup -q -n prism54-svn-latest

%build
cd ksrc
mv Makefile.k26 Makefile
rm -rf built
mkdir -p built/{nondist,smp,up}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	cp %{_kernelsrcdir}/config-$cfg .config
	cp %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv *.ko built/$cfg
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/net/wireless

cd ksrc/built
install %{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/prism54.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless
%if %{with smp} && %{with dist_kernel}
install smp/prism54.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wireless
%endif

%post
%depmod %{_kernel_ver}

%preun
%depmod %{_kernel_ver}

%post -n kernel-smp-net-prism54
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-prism54
%depmod %{_kernel_ver}smp

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-prism54
%defattr(644,root,root,755)
%doc README
/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wireless/*.ko*
%endif
