# build ids are not currently generated:
# https://code.google.com/p/go/issues/detail?id=5238
#
# also, debuginfo extraction currently fails with
# "Failed to write file: invalid section alignment"
%global debug_package %{nil}

Name:		golang
Version:	1.1
Release:	1%{?dist}
Summary:	The Go Programming Language

License:	BSD
URL:		http://golang.org/
Source0:	https://go.googlecode.com/files/go%{version}.src.tar.gz

BuildRequires:	/bin/hostname
BuildRequires:	emacs xemacs xemacs-packages-extra

Patch0:		golang-1.1-verbose-build.patch

%description
%{summary}.


%package godoc
Summary: The Go documentation tool
Requires:    %{name}%{?_isa} = %{version}-%{release}
Requires:    %{name}-docs = %{version}-%{release}

%description godoc
%{summary}.


%package docs
Summary: Go sources and documentation
BuildArch:  noarch

%description docs
%{summary}.


%package vim
Summary: Vim plugins for Go
Requires:    vim-filesystem
BuildArch:   noarch

%description vim
%{summary}.


%package -n emacs-%{name}
Summary: Emacs add-on package for Go
Requires:      emacs(bin) >= %{_emacs_version}
BuildArch:     noarch

%description -n emacs-%{name}
%{summary}.


%package -n xemacs-%{name}
Summary: XEmacs add-on package for Go
Requires:	xemacs(bin) >= %{_xemacs_version}
Requires:	xemacs-packages-extra
BuildArch:	noarch

%description -n xemacs-%{name}
%{summary}.


%prep
%setup -q -n go

# increase verbosity of build
%patch0 -p1


%build
# create a gcc wrapper to allow us to build with our own flags
mkdir zz
cd zz
echo -e "#!/bin/sh\n/usr/bin/gcc $RPM_OPT_FLAGS $RPM_LD_FLAGS \"\$@\"" > mygcc
chmod +x mygcc
export CC="$(pwd -P)/mygcc"
cd ..

# set up final install location
export GOROOT_FINAL=%{_libdir}/%{name}

# TODO use the system linker to get the system link flags and build-id
# when https://code.google.com/p/go/issues/detail?id=5221 is solved
#export GO_LDFLAGS="-linkmode external -extldflags $RPM_LD_FLAGS"

# build
cd src
./make.bash
cd ..

# build static version of documentation
export GOROOT=$(pwd -P)
export PATH="$PATH":"$GOROOT"/bin
cd doc
make
cd ..

# compile for emacs and xemacs
cd misc
mv emacs/go-mode-load.el emacs/%{name}-init.el
cp -av emacs xemacs
%{_emacs_bytecompile} emacs/go-mode.el
%{_xemacs_bytecompile} xemacs/go-mode.el
cd ..


%check
export GOROOT=$(pwd -P)
export PATH="$PATH":"$GOROOT"/bin
cd src
./run.bash --no-rebuild
cd ..


%install
rm -rf $RPM_BUILD_ROOT

# create the top level directories
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_libdir}/%{name}
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}

# install binaries and runtime files into libdir
cp -av bin pkg $RPM_BUILD_ROOT%{_libdir}/%{name}

# install sources and other data in datadir
cp -av api doc include lib favicon.ico robots.txt $RPM_BUILD_ROOT%{_datadir}/%{name}

# remove the unnecessary zoneinfo file (Go will always use the system one first)
rm -rfv $RPM_BUILD_ROOT%{_datadir}/%{name}/lib/time

# remove the doc Makefile
rm -rfv $RPM_BUILD_ROOT%{_datadir}/%{name}/doc/Makefile

# install all sources, used by godoc
mkdir $RPM_BUILD_ROOT%{_datadir}/%{name}/src
cp -av src/pkg $RPM_BUILD_ROOT%{_datadir}/%{name}/src

# remove testdata, tests, and non-go files: this is all we need for godoc
pushd $RPM_BUILD_ROOT%{_datadir}/%{name}/src/pkg
find \( -name testdata -type d -o -name '*_test.go' -type f \) -print0 | xargs -0 rm -rfv
find -type f \! -name '*.go' -print0 | xargs -0 rm -rfv
popd

# restore the gdb debugging script, needed at runtime by gdb
cp -av src/pkg/runtime/runtime-gdb.py $RPM_BUILD_ROOT%{_datadir}/%{name}/src/pkg/runtime

# add symlinks for things in datadir
for z in $RPM_BUILD_ROOT%{_datadir}/%{name}/*
  do ln -s ../../share/%{name}/$(basename "$z") $RPM_BUILD_ROOT%{_libdir}/%{name}
done

# add symlinks for binaries
pushd $RPM_BUILD_ROOT%{_bindir}
for z in $RPM_BUILD_ROOT%{_libdir}/%{name}/bin/*
  do ln -s %{_libdir}/%{name}/bin/$(basename $z)
done
popd

# misc/bash
mkdir -p $RPM_BUILD_ROOT%{_datadir}/bash-completion/completions
cp -av misc/bash/go $RPM_BUILD_ROOT%{_datadir}/bash-completion/completions
for z in 8l 6l 5l 8g 6g 5g gofmt gccgo
  do ln -s go $RPM_BUILD_ROOT%{_datadir}/bash-completion/completions/$z
done

# misc/emacs
mkdir -p $RPM_BUILD_ROOT%{_emacs_sitelispdir}/%{name}
mkdir -p $RPM_BUILD_ROOT%{_emacs_sitestartdir}
cp -av misc/emacs/go-mode.* $RPM_BUILD_ROOT%{_emacs_sitelispdir}/%{name}
cp -av misc/emacs/%{name}-init.el $RPM_BUILD_ROOT%{_emacs_sitestartdir}

# misc/xemacs
mkdir -p $RPM_BUILD_ROOT%{_xemacs_sitelispdir}/%{name}
mkdir -p $RPM_BUILD_ROOT%{_xemacs_sitestartdir}
cp -av misc/xemacs/go-mode.* $RPM_BUILD_ROOT%{_xemacs_sitelispdir}/%{name}
cp -av misc/xemacs/%{name}-init.el $RPM_BUILD_ROOT%{_xemacs_sitestartdir}

# misc/vim
mkdir -p $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles
cp -av misc/vim/* $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles
rm $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/readme.txt

# misc/zsh
mkdir -p $RPM_BUILD_ROOT%{_datadir}/zsh/site-functions
cp -av misc/zsh/go $RPM_BUILD_ROOT%{_datadir}/zsh/site-functions


%files
%doc AUTHORS CONTRIBUTORS LICENSE PATENTS VERSION

# binaries
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/bin
%{_libdir}/%{name}/bin/go
%{_libdir}/%{name}/bin/gofmt
%{_libdir}/%{name}/pkg

# data
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/api
%{_datadir}/%{name}/include

# symlinks (lib -> share)
%{_bindir}/go
%{_bindir}/gofmt
%{_libdir}/%{name}/api
%{_libdir}/%{name}/include
%{_libdir}/%{name}/src

# GDB script
%dir %{_datadir}/%{name}/src
%dir %{_datadir}/%{name}/src/pkg
%dir %{_datadir}/%{name}/src/pkg/runtime
%{_datadir}/%{name}/src/pkg/runtime/runtime-gdb.*

# bash completion
%{_datadir}/bash-completion

# zsh
%{_datadir}/zsh


%files godoc
# binaries
%{_libdir}/%{name}/bin/godoc

# symlinks
%{_bindir}/godoc
%{_libdir}/%{name}/doc
%{_libdir}/%{name}/favicon.ico
%{_libdir}/%{name}/lib
%{_libdir}/%{name}/robots.txt


%files docs
%doc AUTHORS CONTRIBUTORS LICENSE PATENTS VERSION

# data
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/doc
%{_datadir}/%{name}/favicon.ico
%{_datadir}/%{name}/robots.txt
%{_datadir}/%{name}/lib
%{_datadir}/%{name}/src

# exclude the GDB script
%exclude %{_datadir}/%{name}/src/pkg/runtime/runtime-gdb.*


%files vim
%doc AUTHORS CONTRIBUTORS LICENSE PATENTS
%{_datadir}/vim/vimfiles/*


%files -n emacs-%{name}
%doc AUTHORS CONTRIBUTORS LICENSE PATENTS
%{_emacs_sitelispdir}/%{name}
%{_emacs_sitestartdir}/*.el


%files -n xemacs-%{name}
%doc AUTHORS CONTRIBUTORS LICENSE PATENTS
%{_xemacs_sitelispdir}/%{name}
%{_xemacs_sitestartdir}/*.el


%changelog
* Fri May 24 2013 Adam Goode <adam@spicenitz.org> - 1.1-1
- Initial Fedora release.
- Update to 1.1

* Thu May  9 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.3.rc3
- Update to rc3

* Thu Apr 11 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.2.beta2
- Update to beta2

* Tue Apr  9 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.1.beta1
- Initial packaging.
