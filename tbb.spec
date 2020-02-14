Name:           tbb
Version:        2018.5
Release:        4
Summary:        Threading Building Blocks lets you easily write parallel C++ programs
License:        ASL 2.0
URL:            http://threadingbuildingblocks.org/

Source0:        https://github.com/01org/tbb/archive/2018_U5.tar.gz
Source6:        tbb.pc
Source7:        tbbmalloc.pc
Source8:        tbbmalloc_proxy.pc
Patch1:         tbb-4.4-cxxflags.patch
Patch2:         tbb-4.0-mfence.patch
Patch3:         tbb-2018U5-dont-snip-Wall.patch

BuildRequires:  gcc-c++ swig python2-devel python3-devel

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

%package -n python2-tbb
Summary: TBB module of Python 2
%{?python_provide:%python_provide python2-tbb}

%description -n python2-tbb
TBB module of Python 2


%package -n python3-tbb
Summary: TBB module of Python 3
%{?python_provide:%python_provide python3-tbb}

%description -n python3-tbb
TBB module of Python 3

%prep
%autosetup -n tbb-2018_U5 -p1

sed -i 's/"`hostname -s`" ("`uname -m`"/openEulerbuild (%{_arch}/' \
    build/version_info_linux.sh
sed -i 's/-mrtm//' build/linux.gcc.inc
sed -i 's,env python,python2,' python/TBB.py python/tbb/__*.py
sed -i '/^#!/d' python/tbb/{pool,test}.py

if [ "%{_libdir}" != "%{_prefix}/lib" ]; then
  sed -i.orig 's/"lib"/"%{_lib}"/' cmake/TBBMakeConfig.cmake
  touch -r cmake/TBBMakeConfig.cmake.orig cmake/TBBMakeConfig.cmake
  rm cmake/TBBMakeConfig.cmake.orig
fi

cp -a python python3
sed -i 's,python,python3,g' python3/Makefile python3/rml/Makefile
sed -i 's,python2,python3,' python3/TBB.py python3/tbb/__*.py

%build
%ifarch %{ix86}
cp -a build build.orig
make %{?_smp_mflags} tbb_build_prefix=obj stdver=c++14 \
    CXXFLAGS="$RPM_OPT_FLAGS -march=pentium4 -msse2" \
    LDFLAGS="-Wl,--as-needed $RPM_LD_FLAGS"
mv build build.sse2
mv build.orig build
%endif

%make_build tbb_build_prefix=obj stdver=c++14 \
    CXXFLAGS="$RPM_OPT_FLAGS" \
    LDFLAGS="-Wl,--as-needed $RPM_LD_FLAGS"

%define pcsource {%{SOURCE6} %{SOURCE7} %{SOURCE8}}
for pcfile in %{pcsource}; do
    base=$(basename ${pcfile})
    sed 's/_openEuler_VERSION/%{version}/' ${pcfile} > ${base}
    touch -r ${pcfile} ${base}
done

. build/obj_release/tbbvars.sh
pushd python
%make_build -C rml stdver=c++14 \
  CPLUS_FLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD" \
  PIC_KEY="-fPIC -Wl,--as-needed" LDFLAGS="$RPM_LD_FLAGS"
cp -p rml/libirml.so* .
%py2_build
popd

pushd python3
%make_build -C rml stdver=c++14 \
  CPLUS_FLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD" \
  PIC_KEY="-fPIC -Wl,--as-needed" LDFLAGS="$RPM_LD_FLAGS"
cp -p rml/libirml.so* .
%py3_build
popd

%check
make test tbb_build_prefix=obj stdver=c++14 CXXFLAGS="$RPM_OPT_FLAGS"

%install
mkdir -p %{buildroot}/%{_libdir}
mkdir -p %{buildroot}/%{_includedir}

%ifarch %{ix86}
mkdir -p %{buildroot}/%{_libdir}/sse2
pushd build.sse2/obj_release
    for file in libtbb{,malloc{,_proxy}}; do
        install -p -D -m 755 ${file}.so.2 %{buildroot}/%{_libdir}/sse2
    done
popd
%endif

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
%py2_install
chmod a+x %{buildroot}%{python2_sitearch}/TBB.py
chmod a+x %{buildroot}%{python2_sitearch}/tbb/__*.py
cp -p libirml.so.1 %{buildroot}%{_libdir}
ln -s libirml.so.1 %{buildroot}%{_libdir}/libirml.so
popd

pushd python3
%py3_install
chmod a+x %{buildroot}%{python3_sitearch}/TBB.py
chmod a+x %{buildroot}%{python3_sitearch}/tbb/__*.py
cp -p libirml.so.1 %{buildroot}%{_libdir}
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
%ifarch %{ix86}
%{_libdir}/sse2/*.so.2
%endif

%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/*.pc
%{_includedir}/tbb
%{_includedir}/rml
%{_libdir}/cmake/
%{_libdir}/*.so

%files help
%defattr(-,root,root)
%doc doc/Release_Notes.txt doc/html README README.md cmake/README.rst CHANGES

%files -n python2-tbb
%doc python/index.html
%{python2_sitearch}/TBB*
%{python2_sitearch}/tbb/

%files -n python3-tbb
%doc python3/index.html
%{python3_sitearch}/TBB*
%{python3_sitearch}/tbb/
%{python3_sitearch}/__pycache__/TBB*

%changelog
* Fri Feb 14 2020 lingsheng <lingsheng@huawei.com> - 2018.5-4
- Package init
