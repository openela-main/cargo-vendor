# Only x86_64 and i686 are Tier 1 platforms at this time.
# https://forge.rust-lang.org/platform-support.html
#global rust_arches x86_64 i686 armv7hl aarch64 ppc64 ppc64le s390x
%global rust_arches x86_64 i686 aarch64 ppc64 ppc64le s390x

# libgit2-sys expects to use its bundled library, which is sometimes just a
# snapshot of libgit2's master branch.  This can mean the FFI declarations
# won't match our released libgit2.so, e.g. having changed struct fields.
# So, tread carefully if you toggle this...
%bcond_without bundled_libgit2

%if 0%{?rhel}
%bcond_without bundled_libssh2
%else
%bcond_with bundled_libssh2
%endif

Name:           cargo-vendor
Version:        0.1.23
Release:        2%{?dist}
Summary:        Cargo subcommand to vendor crates.io dependencies
License:        ASL 2.0 or MIT
URL:            https://github.com/alexcrichton/cargo-vendor
ExclusiveArch:  %{rust_arches}

Source0:        https://crates.io/api/v1/crates/%{name}/%{version}/download#/%{name}-%{version}.crate

# Use vendored crate dependencies so we can build offline.
# Created using cargo-vendor itself!
# It's so big because some of the -sys crates include the C library source they
# want to link to.  With our -devel buildreqs in place, they'll be used instead.
# FIXME: These should all eventually be packaged on their own!
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  rust-toolset >= 1.30

# Indirect dependencies for vendored -sys crates above
BuildRequires:  make
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  libcurl-devel
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
BuildRequires:  pkgconfig

%if %with bundled_libgit2
Provides:       bundled(libgit2) = 0.27.0
%else
BuildRequires:  libgit2-devel >= 0.24
%endif

%if %with bundled_libssh2
Provides:       bundled(libssh2) = 1.8.1~dev
%else
# needs libssh2_userauth_publickey_frommemory
BuildRequires:  libssh2-devel >= 1.6.0
%endif

# It only supports being called as a subcommand, "cargo vendor"
Requires:       cargo

%description
This is a Cargo subcommand which vendors all crates.io dependencies into a
local directory using Cargo's support for source replacement.


%prep
%setup -q -n %{name}-%{version}

# Source1 is vendored dependencies
%cargo_prep -V 1


%build

%if %without bundled_libgit2
# convince libgit2-sys to use the distro libgit2
export LIBGIT2_SYS_USE_PKG_CONFIG=1
%endif

%if %without bundled_libssh2
# convince libssh2-sys to use the distro libssh2
export LIBSSH2_SYS_USE_PKG_CONFIG=1
%endif

# cargo-vendor doesn't use a configure script, but we still want to use
# CFLAGS in case of the odd C file in vendored dependencies.
%{?__global_cflags:export CFLAGS="%{__global_cflags}"}
%{!?__global_cflags:%{?optflags:export CFLAGS="%{optflags}"}}
%{?__global_ldflags:export LDFLAGS="%{__global_ldflags}"}

%cargo_build


%install
%cargo_install


#check
# the tests don't work offline


%files
%license LICENSE-APACHE LICENSE-MIT
%doc README.md
%{_bindir}/cargo-vendor


%changelog
* Fri May 24 2019 Josh Stone <jistone@redhat.com> - 0.1.23-2
- Rebuild with Rust 1.35

* Tue Apr 09 2019 Josh Stone <jistone@redhat.com> - 0.1.23-1
- Update to 0.1.23

* Thu Dec 13 2018 Josh Stone <jistone@redhat.com> - 0.1.22-1
- Update to 0.1.22

* Thu Oct 04 2018 Josh Stone <jistone@redhat.com> - 0.1.15-3
- Rebuild without SCL packaging. (rhbz1635067)

* Tue Jul 31 2018 Josh Stone <jistone@redhat.com> - 0.1.15-2
- Rebuild for the rust-toolset-1.26 module.
- Update vendored dependencies.

* Fri May 18 2018 Josh Stone <jistone@redhat.com> - 0.1.15-1
- Update to 0.1.15.

* Wed Dec 13 2017 Josh Stone <jistone@redhat.com> - 0.1.13-1
- Update to 0.1.13.

* Mon Sep 11 2017 Josh Stone <jistone@redhat.com> - 0.1.12-1
- Update to 0.1.12.

* Mon Jul 24 2017 Josh Stone <jistone@redhat.com> - 0.1.11-1
- Update to 0.1.11.

* Thu Jun 15 2017 Josh Stone <jistone@redhat.com> - 0.1.7-1
- Initial packaging.
