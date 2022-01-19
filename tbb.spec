Name:           tbb
Version:        2021.4.0
Release:        1
Summary:        Threading Building Blocks lets you easily write parallel C++ programs
License:        ASL 2.0
URL:            http://threadingbuildingblocks.org/

Source0:        https://github.com/intel/tbb/archive/v%{version}/%{name}-%{version}.tar.gz
Source6:        tbb.pc
Source7:        tbbmalloc.pc
Source8:        tbbmalloc_proxy.pc
Patch9000:      bugfix-tbb-fix-__TBB_machine_fetchadd4-was-not-declared-on-.patch
Patch9001:      specify-the-python-interpreter.patch

BuildRequires:  gcc-c++ doxygen swig python3-devel cmake make

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

sed -i 's,env python,python3,' python/TBB.py python/tbb/__*.py
sed -i '/^#!/d' python/tbb/{pool,test}.py

%build
%cmake \
    -DTBB_TEST:BOOL=OFF \
    -DTBB4PY_BUILD:BOOL=ON

%make_build tbb_build_prefix=obj stdver=c++14 \
	CXXFLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD -fstack-protector-strong" \
	LDFLAGS="$RPM_LD_FLAGS -lpthread -fstack-protector-strong"
%define pcsource {%{SOURCE6} %{SOURCE7} %{SOURCE8}}
for pcfile in %{pcsource}; do
    base=$(basename ${pcfile})
    sed 's/_openEuler_VERSION/%{version}/' ${pcfile} > ${base}
    touch -r ${pcfile} ${base}
done

.  */vars.sh
pushd python
%make_build -C rml stdver=c++14 \
  CPLUS_FLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD -fstack-protector-strong" \
  %ifarch riscv64
  LDFLAGS="$RPM_LD_FLAGS -lpthread -fstack-protector-strong -latomic"
  %else
  LDFLAGS="$RPM_LD_FLAGS -lpthread -fstack-protector-strong"
  %endif
%py3_build
popd


%check
make test %{?_smp_mflags} tbb_build_prefix=obj stdver=c++14 CXXFLAGS="$RPM_OPT_FLAGS"

%install
mkdir -p build/python/build
%make_install

mkdir -p %{buildroot}/%{_libdir}
mkdir -p %{buildroot}/%{_includedir}

pushd include
    find tbb -type f ! -name \*.htm\* -exec install -p -D -m 644 {} \
        %{buildroot}/%{_includedir}/{} \;
popd

%define pcsource {%{SOURCE6} %{SOURCE7} %{SOURCE8}}
for file in %{pcsource}; do
    install -p -D -m 644 $(basename ${file}) \
        %{buildroot}/%{_libdir}/pkgconfig/$(basename ${file})
done

.  */vars.sh
pushd python
%py3_install
chmod a+x %{buildroot}%{python3_sitearch}/TBB.py
chmod a+x %{buildroot}%{python3_sitearch}/tbb/__*.py
popd

mkdir -p %{buildroot}%{_libdir}/cmake
cp -a cmake %{buildroot}%{_libdir}/cmake/tbb

%ldconfig_scriptlets libs

%files
%defattr(-,root,root)
%license LICENSE.txt
%doc %{_docdir}/TBB/README.md
%{_prefix}/lib.*/*
%{_prefix}/temp.*/*
%{_libdir}/libirml.so.1
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/*.pc
%{_includedir}/tbb
%{_includedir}/oneapi/
%{_libdir}/cmake/
%{_libdir}/*.so

%files help
%defattr(-,root,root)
%doc README.md

%files -n python3-tbb
%{python3_sitearch}/TBB*
%{python3_sitearch}/tbb/
%{python3_sitearch}/__pycache__/TBB*

%changelog
* Wed Jan 19 2022 wulei <wulei80@huawei.com> - 2021.4.0-1
- Package update

* Fri Jul 2 2021 Hugel <genqihu1@huawei.com> - 2020.3-4
- Add multiple threads to make test

* Wed  Apr 14 2021 yangyanchao <yangyanchao6@huawei.com> - 2020.3-3
- Link to libatomic in riscv

* Sat Mar 20 2021 shenyangyang <shenyangyang4@huawei.com> - 2020.3-2
- Add -fstack-protector-strong for so file

* Fri Jul 24 2020 shixuantong <shixuantong@huawei.com> - 2020.3-1
- update to 2020.3-1

* Fri Feb 14 2020 lingsheng <lingsheng@huawei.com> - 2018.5-4
- Package init
