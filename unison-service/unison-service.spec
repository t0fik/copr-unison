Name: unison-service
Version: 0.2.2
Release: 1%{?dist}
License:   GPLv3+
URL: https://github.com/t0fik/copr-unison
Requires: %{_bindir}/unison
Requires: %{_bindir}/inotifywait
Summary: Service definition and required files for Unison
Source0: unison.service
Source1: stop-unison
Source2: sshcmd

BuildArch: noarch

BuildRequires: systemd-rpm-macros

%description
Systemd service files for Unison file-synchronization tool.

%install
install -D %{SOURCE0} %{buildroot}%{_userunitdir}/unison.service
install -m755 -D %{SOURCE1} %{buildroot}%{_libexecdir}/unison/stop-unison
install -m755 -D %{SOURCE2} %{buildroot}%{_libexecdir}/unison/sshcmd

%files
%{_userunitdir}/unison.service
%{_libexecdir}/unison/stop-unison
%{_libexecdir}/unison/sshcmd

%changelog
* Fri Jan 08 2021 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 0.2.2-1
- Added wrapper for ssh forcing closing stderr

* Sat Dec 05 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 0.2.1-1
- All options except -ui=text moved do environment variable
- Option -logfile set to /dev/null
- Added EnvironmentFile option to unit file
- Added ConditionPathIsDirectory to unit file

* Sat Dec 05 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 0.2.0-1
- Resolved problem with 'Main process exited, code=exited, status=2/INVALIDARGUMENT'
- stop-unison waits for child processes to exit

* Fri Dec 04 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 0.1.0-1
- Initial build

