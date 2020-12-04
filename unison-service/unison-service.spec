Name: unison-service
Version: 0.1.0
Release: 1%{?dist}
License:   GPLv3+
URL: https://github.com/t0fik/copr-unison
Requires: %{_sbindir}/unison
Requires: %{_sbindir}/inotifywait
Summary: Service definition and required files for Unison
Source0: unison.service
Source1: stop-unison

%description
Systemd service files for Unison file-synchronization tool.

%install
install -D %{SOURCE0} %{buildroot}%{_userunitdir}/unison.service
install -m755 -D %{SOURCE1} %{buildroot}%{_libexecdir}/unison/stop-unison

%files
%{_userunitdir}/unison.service
%{_libexecdir}/unison/stop-unison

%changelog
* Fri Dec 04 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 0.1.0-1
- Initial build

