%define branch 3
%define with_selinux 1
%define pname radicale-auth-ldap
%define pname_und %( echo %{pname} | tr '-' '_' )

%define pyver python3
%if 0%{?centos}
%define pyver python36
%endif
Name:		radicale3-auth-ldap
Version:	0.3
Release:	1%{?dist}
Summary:	Ldap auth plugin for radicale3

License:	GPL 3.0
URL:		https://gitlab.com/bgstack15/radicale_auth_ldap
Source0:	%{url}/-/archive/%{branch}/radicale_auth_ldap-%{branch}.tar.gz
BuildArch: noarch

%if with_selinux
%package selinux
Summary: Selinux rules for radicale3-auth-ldap

%if 0%{?centos} == 7
BuildRequires:	policycoreutils-python
%endif
BuildRequires: policycoreutils
BuildRequires: checkpolicy
BuildRequires: selinux-policy-devel
Requires(post): selinux-policy-base
%endif
Requires:	%{pyver}-ldap3

%description
Provides ldap authentication support for radicale3,
including multi-server support and anonymous bind.

%if 0%{?with_selinux}
%description selinux
Includes selinux rule for radicale3 ldap auth plugin.
Tested with httpd.
%endif
%prep
%setup -n radicale_auth_ldap-%{branch}

%build
%py3_build
%if 0%{?with_selinux}
make -f /usr/share/selinux/devel/Makefile %{pname}.pp
%endif

%install
%py3_install
%if 0%{?with_selinux}
%{__install} -d %{buildroot}%{_datadir}/selinux/packages
%{__install} -m0644 %{pname}.pp %{buildroot}%{_datadir}/selinux/packages
find %{buildroot}%{_datadir}/selinux ! -type d -exec ls -altrdF {} +
%endif

%post selinux
#
# Install all modules in a single transaction
#
%_format MODULES %{_datadir}/selinux/packages/$x.pp
%{_sbindir}/semodule -n -s %{selinuxtype} -i $MODULES
if %{_sbindir}/selinuxenabled ; then
    %{_sbindir}/load_policy
    %relabel_files
fi

%postun selinux
if [ $1 -eq 0 ]; then
   %{_sbindir}/semodule -n -r %{modulenames} &> /dev/null || :
   if %{_sbindir}/selinuxenabled ; then
      %{_sbindir}/load_policy
      # no file contexts are defined in this policy.
      #%%relabel_files
   fi
fi

%files
%{python3_sitelib}/%{pname_und}
%{python3_sitelib}/%{pname_und}-*.egg-info
%if 0%{?with_selinux}
%files selinux
%{_datadir}/selinux/packages/*.pp
%endif

%doc

%changelog

