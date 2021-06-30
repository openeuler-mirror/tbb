Name:           tbb
Version:        2020.3
Release:        3
Summary:        Threading Building Blocks lets you easily write parallel C++ programs
License:        ASL 2.0
URL:            http://threadingbuildingblocks.org/

Source0:        https://github.com/intel/tbb/archive/v%{version}/%{name}-%{version}.tar.gz
Source6:        tbb.pc
Source7:        tbbmalloc.pc
Source8:        tbbmalloc_proxy.pc
Patch9000:      bugfix-tbb-fix-__TBB_machine_fetchadd4-was-not-declared-on-.patch

BuildRequires:  gcc-c++ doxygen swig python3-devel

%description
Threading Building Blocks (TBB) lets you easily write parallel C++ programs that 
take full advantage of multicore performance, that are portable, composable and 
have future-proof scalability.

%package devel
Summary:        C++ headers and shared development libraries of TBB
Requires:       tbb%{?_isa} = %{version}-%{release}

%description devel
The Threading Building Blocks (TBB) C++ libraries including Header files and 
shared object symlinks.

%package help
Summary:        Documents for tbb
Buildarch:      noarch
Requires:       man info
Provides:       bundled(jquery) tbb-doc = %{version}-%{release}
Obsoletes:      tbb-doc < %{version}-%{release}

%description help
Man pages and other related documents for tbb.

%package -n python3-tbb
Summary: TBB module of Python 3
%{?python_provide:%python_provide python3-tbb}

%description -n python3-tbb
TBB module of Python 3

%prep
%autosetup -n oneTBB-%{version} -p1

sed -i 's/"`hostname -s`" ("`uname -m`"/openEulerbuild (%{_arch}/' \
    build/version_info_linux.sh
sed -i 's/-mrtm//' build/linux.gcc.inc
sed -i 's,env python,python3,' python/TBB.py python/tbb/__*.py
sed -i '/^#!/d' python/tbb/{pool,test}.py

%build
%make_build tbb_build_prefix=obj stdver=c++14 \
	CXXFLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD -fstack-protector-strong" \
	LDFLAGS="$RPM_LD_FLAGS -lpthread -fstack-protector-strong"
%define pcsource {%{SOURCE6} %{SOURCE7} %{SOURCE8}}
for pcfile in %{pcsource}; do
    base=$(basename ${pcfile})
    sed 's/_openEuler_VERSION/%{version}/' ${pcfile} > ${base}
    touch -r ${pcfile} ${base}
done

. build/obj_release/tbbvars.sh
pushd python
%make_build -C rml stdver=c++14 \
  CPLUS_FLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD -fstack-protector-strong" \
  %ifarch riscv64
  LDFLAGS="$RPM_LD_FLAGS -lpthread -fstack-protector-strong -latomic"
  %else
  LDFLAGS="$RPM_LD_FLAGS -lpthread -fstack-protector-strong"
  %endif
cp -p rml/libirml.so* .
%py3_build
popd

make doxygen

%check
make test tbb_build_prefix=obj stdver=c++14 CXXFLAGS="$RPM_OPT_FLAGS"

%install
mkdir -p %{buildroot}/%{_libdir}
mkdir -p %{buildroot}/%{_includedir}

pushd build/obj_release
    for file in libtbb{,malloc{,_proxy}}; do
        install -p -D -m 755 ${file}.so.2 %{buildroot}/%{_libdir}
        ln -s $file.so.2 %{buildroot}/%{_libdir}/$file.so
    done
popd

pushd include
    find tbb -type f ! -name \*.htm\* -exec install -p -D -m 644 {} \
        %{buildroot}/%{_includedir}/{} \;
popd

%define pcsource {%{SOURCE6} %{SOURCE7} %{SOURCE8}}
for file in %{pcsource}; do
    install -p -D -m 644 $(basename ${file}) \
        %{buildroot}/%{_libdir}/pkgconfig/$(basename ${file})
done

# Install the rml headers
mkdir -p %{buildroot}%{_includedir}/rml
cp -p src/rml/include/*.h %{buildroot}%{_includedir}/rml

. build/obj_release/tbbvars.sh
pushd python
%py3_install
chmod a+x %{buildroot}%{python3_sitearch}/TBB.py
chmod a+x %{buildroot}%{python3_sitearch}/tbb/__*.py
cp -p libirml.so.1 %{buildroot}%{_libdir}
ln -s libirml.so.1 $RPM_BUILD_ROOT%{_libdir}/libirml.so
popd

mkdir -p %{buildroot}%{_libdir}/cmake
cp -a cmake %{buildroot}%{_libdir}/cmake/tbb
rm %{buildroot}%{_libdir}/cmake/tbb/README.rst

%ldconfig_scriptlets libs

%files
%defattr(-,root,root)
%license LICENSE
%{_libdir}/libirml.so.1
%{_libdir}/*.so.2

%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/*.pc
%{_includedir}/tbb
%{_includedir}/rml
%{_libdir}/cmake/
%{_libdir}/*.so

%files help
%defattr(-,root,root)
%doc doc/Release_Notes.txt html README README.md cmake/README.rst CHANGES

%files -n python3-tbb
%doc python/index.html
%{python3_sitearch}/TBB*
%{python3_sitearch}/tbb/
%{python3_sitearch}/__pycache__/TBB*

%changelog
* Wed  Apr 14 2021 yangyanchao <yangyanchao6@huawei.com> - 2020.3-3
- Link to libatomic in riscv

* Sat Mar 20 2021 shenyangyang <shenyangyang4@huawei.com> - 2020.3-2
- Add -fstack-protector-strong for so file

* Fri Jul 24 2020 shixuantong <shixuantong@huawei.com> - 2020.3-1
- update to 2020.3-1

* Fri Feb 14 2020 lingsheng <lingsheng@huawei.com> - 2018.5-4
- Package init
