%global underscore() %(echo %1 | sed 's/-/_/g')

%global python3_pkgversion_311 3.11
%global python3_pkgversion_312 3.12

%global sum A simple python library for interacting with the ARGO HANDLE.net service
%global desc A simple python library for interacting with the ARGO HANDLE.net service


Name:           pyhandle-newgen
Summary:        %{sum}
Version:        0.1.0
Release:        1%{?dist}

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://github.com/ARGOeu/pyhandle-newgen
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch


%description
%{desc}

%if 0%{?el8}
%package -n python%{python3_pkgversion_311}-%{name}
Summary: %{sum}
BuildRequires: python%{python3_pkgversion_311}-devel    python%{python3_pkgversion_311}-setuptools
Requires:      python(abi) = %{python3_pkgversion_311}    python%{python3_pkgversion_311}-requests
AutoReq: no
%description -n python%{python3_pkgversion_311}-%{name}
%{desc}
%{?python_provide:%python_provide python%{python3_pkgversion_311}-%{name}}

%package -n python%{python3_pkgversion_312}-%{name}
Summary: %{sum}
BuildRequires: python%{python3_pkgversion_312}-devel    python%{python3_pkgversion_312}-setuptools
Requires:      python(abi) = %{python3_pkgversion_312}    python%{python3_pkgversion_312}-requests
AutoReq: no
%description -n python%{python3_pkgversion_312}-%{name}
%{desc}
%{?python_provide:%python_provide python%{python3_pkgversion_312}-%{name}}

%prep
%setup -q

%build
python%{python3_pkgversion_311} setup.py build
python%{python3_pkgversion_312} setup.py build

%install
rm -rf %{buildroot}
python%{python3_pkgversion_311} setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_311
python%{python3_pkgversion_312} setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_312

%files -n python%{python3_pkgversion_311}-%{name} -f INSTALLED_FILES_PY3_311
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python%{python3_pkgversion_311}/site-packages/*
%doc examples/ README.md

%files -n python%{python3_pkgversion_312}-%{name} -f INSTALLED_FILES_PY3_312
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python%{python3_pkgversion_312}/site-packages/*
%doc examples/ README.md
%endif

%if 0%{?el9}
%package -n python%{python3_pkgversion}-%{name}
Summary: %{sum}
BuildRequires: python3-devel    python3-setuptools
Requires:      python(abi) = 3.9    python3-requests    python3-typing-extensions
AutoReq: no
%description -n python%{python3_pkgversion}-%{name}
%{desc}
%{?python_provide:%python_provide python3-%{name}}

%package -n python%{python3_pkgversion_311}-%{name}
Summary: %{sum}
BuildRequires: python%{python3_pkgversion_311}-devel    python%{python3_pkgversion_311}-setuptools
Requires:      python(abi) = %{python3_pkgversion_311}    python%{python3_pkgversion_311}-requests
AutoReq: no
%description -n python%{python3_pkgversion_311}-%{name}
%{desc}
%{?python_provide:%python_provide python%{python3_pkgversion_311}-%{name}}

%package -n python%{python3_pkgversion_312}-%{name}
Summary: %{sum}
BuildRequires: python%{python3_pkgversion_312}-devel    python%{python3_pkgversion_312}-setuptools
Requires:      python(abi) = %{python3_pkgversion_312}    python%{python3_pkgversion_312}-requests
AutoReq: no
%description -n python%{python3_pkgversion_312}-%{name}
%{desc}
%{?python_provide:%python_provide python%{python3_pkgversion_312}-%{name}}

%prep
%setup -q

%build
%{py3_build}
python%{python3_pkgversion_311} setup.py build
python%{python3_pkgversion_312} setup.py build

%install
rm -rf %{buildroot}
%{py3_install "--record=INSTALLED_FILES_PY3" }
python%{python3_pkgversion_311} setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_311
python%{python3_pkgversion_312} setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_312

%files -n python%{python3_pkgversion}-%{name} -f INSTALLED_FILES_PY3
%doc examples/ README.md
%defattr(-,root,root,-)
%{python3_sitelib}/*
%doc examples/ README.md

%files -n python%{python3_pkgversion_311}-%{name} -f INSTALLED_FILES_PY3_311
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python%{python3_pkgversion_311}/site-packages/*
%doc examples/ README.md

%files -n python%{python3_pkgversion_312}-%{name} -f INSTALLED_FILES_PY3_312
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python%{python3_pkgversion_312}/site-packages/*
%doc examples/ README.md
%endif

%changelog
* Thu Jan 15 2026 William V. Karageorgos <wvkarageorgos@admin.grnet.gr> - 0.1.0-1%{?dist}
- Initial version
