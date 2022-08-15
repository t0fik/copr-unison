
# These is the exact upstream version we are packaging
%global ver_maj 2
%global ver_min 52
%global ver_patch 1

# All Unison versions sharing ver_compat are compatible
# Examples are 2.13.15 and 2.13.16 -> ver_compat == 2.13
# In older versions, even patch levels were not compatible
# Examples are ver_compat==2.9.0 and ver_compat==2.9.1
%global ver_compat      %{ver_maj}.%{ver_min}
%global ver_compat_name %{ver_maj}%{ver_min}
%global ver_noncompat   .%{ver_patch}

# ver_priority is the first component of ver_compat, catenated with the second
# component of ver_compat zero-filled to 3 digits, catenated with a final
# zero-filled 3-digit field. The final field contains the 3rd component of
# ver_compat (if there is one), otherwise 0.
%global ver_priority %(printf %%d%%03d%%03d `echo %{ver_compat}|sed 's/\\./ /g'`)

# Is this package the unisonNNN package with the highest ${ver_compat}
# available in this Fedora branch/release? If so, we provide unison.
%global provide_unison 1

# Gtk2 build isn't working for el8
%global include_gtk 1
%global build_docs 1
# el8 and newer does not provide LaTeX
%if 0%{?el8}%{?el9}
%global include_gtk 0
%global build_docs 0
%endif


%global git_tag %{ver_maj}.%{ver_min}.%{ver_patch}

Name:      unison
Version:   %{ver_compat}%{ver_noncompat}
Release:   2%{?dist}

Summary:   Multi-master File synchronization tool

License:   GPLv3+
URL:       http://www.cis.upenn.edu/~bcpierce/unison
Source0:   https://github.com/bcpierce00/unison/archive/v%{git_tag}/unison-%{version}.tar.gz
Source1:  https://www.cis.upenn.edu/~bcpierce/unison/download/releases/unison-2.51.2/unison-2.51.2-manual.html

# can't make this noarch (rpmbuild fails about unpackaged debug files)
# BuildArch:     noarch
ExcludeArch:   sparc64 s390 s390x

BuildRequires: ocaml

%if %{build_docs}
BuildRequires: /usr/bin/latex
BuildRequires: /usr/bin/hevea
BuildRequires: /usr/bin/lynx
%endif

Requires:   %{name}-ui = %{version}-%{release}
Obsoletes: unison251 < 2.51.5

Requires(posttrans): %{_sbindir}/alternatives
Requires(postun):    %{_sbindir}/alternatives

%description
Unison is a multi-master file-synchronization tool. It allows two
replicas of a collection of files and directories to be stored on
different hosts (or different locations on the same host), modified
separately, and then brought up to date by propagating the changes
in each replica to the other.

Note that this package contains Unison version %{ver_compat}, and
will never be upgraded to a different major version. Other packages
exist if you require a different major version.


%if %{include_gtk}
%package gtk

Summary:   Multi-master File synchronization tool - gtk interface

BuildRequires: ocaml-lablgtk-devel
BuildRequires: gtk2-devel
BuildRequires: desktop-file-utils

Requires: %name = %{version}-%{release}
Obsoletes: unison251-gtk < 2.51.5
Recommends: %name-fsmonitor = %{version}-%{release}

Provides:   %{name}-ui = %{version}-%{release}


%description gtk
This package provides the graphical version of unison with gtk2 interface.
%endif

%package text

Summary:   Multi-master File synchronization tool - text interface

Requires: %name = %{version}-%{release}
Obsoletes: unison251-text < 2.51.5
Recommends: %name-fsmonitor = %{version}-%{release}

Provides:   %{name}-ui = %{version}-%{release}

%description text
This package provides the textual version of unison without graphical interface.

%package fsmonitor

Summary:   Multi-master File synchronization tool - fsmonitor

Requires: %name = %{version}-%{release}
Obsoletes: unison251-fsmonitor < 2.51.5

Provides:   %{name}-fsmonitor = %{version}-%{release}

%description fsmonitor
This package provides the fsmonitor functionality of unison.

%prep
%setup -q -n unison-%{git_tag}

cat > %{name}.desktop <<EOF
[Desktop Entry]
Type=Application
Exec=unison-gtk-%{ver_compat}
Name=Unison File Synchronizer (version %{ver_compat})
GenericName=File Synchronizer
Comment=Multi-master File synchronization tool
Terminal=false
Icon=%{name}
StartupNotify=true
Categories=Utility;
EOF

%build
# MAKEFLAGS=-j<N> breaks the build.
unset MAKEFLAGS
unset CFLAGS

%if %{include_gtk}
# we compile 2 versions: gtk2 ui and text ui
make NATIVE=true UISTYLE=gtk2 THREADS=true OCAMLOPT="ocamlopt -g" src
mv src/unison unison-gtk
%endif

make NATIVE=true UISTYLE=text THREADS=true OCAMLOPT="ocamlopt -g" src
mv src/unison unison-text
mv src/unison-fsmonitor unison-fsmonitor

%if %{build_docs}
make NATIVE=true docs
cp -f doc/unison-manual.html unison-manual.html
%else
cp -f %{SOURCE1} unison-manual.html
%endif

%install

%if %{include_gtk}
install -m 755 -D unison-gtk %{buildroot}%{_bindir}/unison-gtk-%{ver_compat}
# symlink for compatibility
ln -s unison-gtk-%{ver_compat} %{buildroot}%{_bindir}/unison-%{ver_compat}
install -D icons/U.svg %{buildroot}%{_datadir}/pixmaps/%{name}.svg

desktop-file-install --dir %{buildroot}%{_datadir}/applications \
    %{name}.desktop
%endif

install -m 755 -D unison-text %{buildroot}%{_bindir}/unison-text-%{ver_compat}
install -m 755 -D unison-fsmonitor %{buildroot}%{_bindir}/unison-fsmonitor-%{ver_compat}

# create/own alternatives target
touch %{buildroot}%{_bindir}/unison


%if %{include_gtk}
%posttrans gtk
alternatives \
  --install \
  %{_bindir}/unison \
  unison \
  %{_bindir}/unison-%{ver_compat} \
  %{ver_priority}

alternatives \
  --install \
  %{_bindir}/unison-fsmonitor \
  unison-fsmonitor \
  %{_bindir}/unison-fsmonitor-%{ver_compat} \
  %{ver_priority}

%postun gtk
if [ $1 -eq 0 ]; then
  alternatives --remove unison \
    %{_bindir}/unison-%{ver_compat}
  alternatives --remove unison-fsmonitor \
    %{_bindir}/unison-fsmonitor-%{ver_compat}  
fi
%endif

%posttrans text
alternatives \
  --install \
  %{_bindir}/unison \
  unison \
  %{_bindir}/unison-text-%{ver_compat} \
  %{ver_priority}

alternatives \
  --install \
  %{_bindir}/unison-text \
  unison-text \
  %{_bindir}/unison-text-%{ver_compat} \
  %{ver_priority}

alternatives \
  --install \
  %{_bindir}/unison-fsmonitor \
  unison-fsmonitor \
  %{_bindir}/unison-fsmonitor-%{ver_compat} \
  %{ver_priority}


%postun text
if [ $1 -eq 0 ]; then
  alternatives --remove unison \
    %{_bindir}/unison-text-%{ver_compat}
  alternatives --remove unison-text \
    %{_bindir}/unison-text-%{ver_compat}
  alternatives --remove unison-fsmonitor \
    %{_bindir}/unison-fsmonitor-%{ver_compat}  
fi


%posttrans fsmonitor
alternatives \
  --install \
  %{_bindir}/unison-fsmonitor \
  unison-fsmonitor \
  %{_bindir}/unison-fsmonitor-%{ver_compat} \
  %{ver_priority}


%postun fsmonitor
if [ $1 -eq 0 ]; then
  alternatives --remove unison-fsmonitor \
    %{_bindir}/unison-fsmonitor-%{ver_compat}
fi


%files
%doc src/COPYING src/README unison-manual.html
%license LICENSE

%if %{include_gtk}
%files gtk
%ghost %{_bindir}/unison
%{_bindir}/unison-gtk-%{ver_compat}
%{_bindir}/unison-%{ver_compat}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.svg
%endif

%files text
%ghost %{_bindir}/unison
%{_bindir}/unison-text-%{ver_compat}

%files fsmonitor
%ghost %{_bindir}/unison-fsmonitor
%{_bindir}/unison-fsmonitor-%{ver_compat}

%changelog
* Mon Sep 15 2022 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.52.1-2
- EL9 package

* Wed Jul 20 2022 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.52.1-1
- Update to 2.52.1
- Package name change to unison, 2.52 got compability https://github.com/bcpierce00/unison/wiki/2.52-Migration-Guide

* Wed Jul 20 2022 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.5-1
- Update to 2.51.5

* Thu Aug 12 2021 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.4-1
- Update to 2.51.4

* Sat Jan 09 2021 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-10
- fsmonitor moved to seperate package
- disabled building Gtk2 package for EL8

* Fri Dec 04 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-9
- Service file moved to seperate package

* Tue Dec 01 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-8
- Added setting system limits in systemd unit
- Service KillMode set to process

* Sun Nov 29 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-7
- Added -ui argument to service command line

* Sun Nov 29 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-6
- Fixed enabling unison service
- Added restartig service on failure
- Added $DISPLAY variable unset in service

* Sun Nov 29 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-5
- Fixed running unison as systemd service

* Sat Nov 28 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-4
- Added unison.service file

* Sat Nov 28 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-3
- Added unison-fsmonitor to package

* Fri Nov 13 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-2
- Fixed GTK package

* Fri Nov 13 2020 Jerzy Drozdz <jerzy.drozdz@jdsieci.pl> - 2.51.3-1
- Rebuild for OCaml 4.11

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu May 31 2018 Richard W.M. Jones <rjones@redhat.com> - 2.40.128-11
- Use unsafe-string with OCaml 4.06.
- Add small hack to keep it working with new lablgtk.
- Enable debugging.

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Feb 14 2017 Richard W.M. Jones <rjones@redhat.com> - 2.40.128-7
- Small fix for compiling against OCaml 4.04 (RHBZ#1392152).

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Nov 05 2016 Richard W.M. Jones <rjones@redhat.com> - 2.40.128-5
- Rebuild for OCaml 4.04.0.

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.40.128-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 05 2016 Richard Jones <rjones@redhat.com> - 2.40.128-3
- Use global instead of define.

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.40.128-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jan 19 2015 Richard W.M. Jones <rjones@redhat.com> - 2.40.128-1
- New upstream version 2.40.128 (RHBZ#1178444).
- Remove missing documentation patch, now included upstream.

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.40.102-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.40.102-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jan 01 2014 Rex Dieter <rdieter@fedoraproject.org> - 2.40.102-6
- own alternatives target

* Mon Sep 09 2013 Gregor Tätzner <brummbq@fedoraproject.org> - 2.40.102-5
- ship 2 versions of unison: text only and gtk2 user interface
- move binaries into subpackages
- enable dependency generator

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.40.102-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.40.102-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Dec 14 2012 Richard W.M. Jones <rjones@redhat.com> - 2.40.102-2
- Rebuild for OCaml 4.00.1.

* Thu Nov 15 2012 Gregor Tätzner <brummbq@fedoraproject.org> - 2.40.102-1
- 2.40.102
- fixes incompatibility between unison ocaml3 and ocaml4 builds

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.40.63-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jan 22 2012 Gregor Tätzner <brummbq@fedoraproject.com> - 2.40.63-6
- Patch built-in documentation.

* Sat Jan 21 2012 Gregor Tätzner <brummbq@fedoraproject.org> - 2.40.63-5
- Add unison-manual.html.

* Fri Jan 13 2012 Gregor Tätzner <brummbq@fedoraproject.org> - 2.40.63-4
- Remove ocaml minimum version.
- Add Requires and provides scripts.

* Tue Sep 27 2011 Gregor Tätzner <brummbq@fedoraproject.org> - 2.40.63-3
- Remove vendor tag.

* Sun Sep 04 2011 Gregor Tätzner <brummbq@fedoraproject.org> - 2.40.63-2
- Remove xorg-x11-font-utils Requirement.
- Enable THREADS=true.

* Tue Aug 30 2011 Gregor Tätzner <brummbq@fedoraproject.org> - 2.40.63-1
- Version bump.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.57-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Apr 16 2009 S390x secondary arch maintainer <fedora-s390x@lists.fedoraproject.org>
- ExcludeArch sparc64, s390, s390x as we don't have OCaml on those archs
  (added sparc64 per request from the sparc maintainer)

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.57-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 8 2009 Stephen Warren <s-t-rhbugzilla@wwwdotorg.org> - 2.27.57-11
- Add Requires: xorg-x11-fonts-misc

* Wed Nov 26 2008 Richard W.M. Jones <rjones@redhat.com> - 2.27.57-10
- Rebuild for OCaml 3.11.0+rc1.

* Sat May 24 2008 Richard W.M. Jones <rjones@redhat.com> - 2.27.57-9
- Rebuild with OCaml 3.10.2-2 (fixes bz 441685, 445545).

* Sun Mar 30 2008 Stephen Warren <s-t-rhbugzilla@wwwdotorg.org> - 2.27.57-8
- Don't use alternatives for desktop and icon files, to avoid duplicate
  menu entries.

* Wed Mar 19 2008 Stephen Warren <s-t-rhbugzilla@wwwdotorg.org> - 2.27.57-7
- Fix license to match correct interpretation of source & GPL
- Remove Excludes for ppc64, since ocaml is available there now, in devel

* Sat Mar 15 2008 Stephen Warren <s-t-rhbugzilla@wwwdotorg.org> - 2.27.57-6
- Rename package unison2.27 -> unison227 to match Fedora naming rules
- Automatically calculate ver_priority using the shell; easier maintenance

* Sat Mar 1 2008 Stephen Warren <s-t-rhbugzilla@wwwdotorg.org> - 2.27.57-5
- Use Provides/Obsoletes to provide upgrade path, per:
  http://fedoraproject.org/wiki/Packaging/NamingGuidelines

* Thu Feb 28 2008 Stephen Warren <s-t-rhbugzilla@wwwdotorg.org> - 2.27.57-4
- Explicitly conflict with existing unison package

* Fri Feb 22 2008 Stephen Warren <s-t-rhbugzilla@wwwdotorg.org> - 2.27.57-3
- Derived unison2.27 package from unison2.13 package

* Mon Feb  4 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.27.57-2
- exclude arch ppc64

* Mon Feb  4 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.27.57-1
- new release 2.27.57

* Tue Aug 29 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.13.16-3
- Rebuild for FE6

* Tue Feb 28 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.13.16-2
- Rebuild for Fedora Extras 5

* Thu Sep  1 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.13.16-1
- New Version 2.13.16

* Sun Jul 31 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.12.0-0
- New Version 2.12.0

* Fri May 27 2005 Toshio Kuratomi <toshio-tiki-lounge.com> - 2.10.2-7
- Bump and rebuild with new ocaml and new lablgtk

* Sun May 22 2005 Jeremy Katz <katzj@redhat.com> - 2.10.2-6
- rebuild on all arches

* Mon May 16 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.10.2-5
- Patch: http://groups.yahoo.com/group/unison-users/message/3200

* Thu Apr 7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Thu Feb 24 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 0:2.10.2-2
- BR gtk2-devel
- Added NEWS and README docs

* Sat Feb 12 2005 Gerard Milmeister <gemi@bluewin.ch> - 0:2.10.2-1
- New Version 2.10.2

* Wed Apr 28 2004 Gerard Milmeister <gemi@bluewin.ch> - 0:2.9.74-0.fdr.1
- New Version 2.9.74
- Added icon

* Tue Jan 13 2004 Gerard Milmeister <gemi@bluewin.ch> - 0:2.9.72-0.fdr.1
- New Version 2.9.72

* Tue Dec  9 2003 Gerard Milmeister <gemi@bluewin.ch> - 0:2.9.70-0.fdr.2
- Changed Summary
- Added .desktop file

* Fri Oct 31 2003 Gerard Milmeister <gemi@bluewin.ch> - 0:2.9.70-0.fdr.1
- First Fedora release

