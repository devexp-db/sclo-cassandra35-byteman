%{?scl:%scl_package byteman}
%{!?scl:%global pkg_name %{name}}

%global javacup_or_asm java_cup:java_cup|org.ow2.asm:asm-all
%global __requires_exclude ^.*mvn\\(%{javacup_or_asm}\\)$

%global homedir %{_datadir}/%{pkg_name}
%global bindir %{homedir}/bin

Name:		%{?scl_prefix}byteman
Version:	3.0.6
Release:	2%{?dist}
Summary:	Java agent-based bytecode injection tool
License:	LGPLv2+
URL:		http://www.jboss.org/byteman
# wget -O 3.0.6.tar.gz https://github.com/bytemanproject/byteman/archive/3.0.6.tar.gz
Source0:	https://github.com/%{pkg_name}project/%{pkg_name}/archive/%{version}.tar.gz

BuildArch:	noarch

BuildRequires:	%{?scl_prefix_maven}maven-local
BuildRequires:	%{?scl_prefix_maven}maven-shade-plugin
BuildRequires:	%{?scl_prefix_maven}maven-failsafe-plugin
BuildRequires:	%{?scl_prefix_maven}maven-jar-plugin
BuildRequires:	%{?scl_prefix_maven}maven-surefire-plugin
BuildRequires:	%{?scl_prefix_maven}maven-surefire-provider-testng
BuildRequires:	%{?scl_prefix_maven}maven-surefire-provider-junit
BuildRequires:	%{?scl_prefix_maven}maven-dependency-plugin
BuildRequires:	%{?scl_prefix_maven}maven-plugin-bundle
BuildRequires:	%{?scl_prefix_maven}maven-source-plugin
BuildRequires:	%{?scl_prefix_maven}maven-plugin-plugin
BuildRequires:	%{?scl_prefix_maven}testng
BuildRequires:	%{?scl_prefix_java_common}java_cup
BuildRequires:	%{?scl_prefix_java_common}junit
BuildRequires:	%{?scl_prefix}objectweb-asm
# missing dependencies in RHEL not needed in SCL package
%{!?scl:BuildRequires:	maven-verifier-plugin
# JBoss modules byteman plugin requires it
BuildRequires:	mvn(org.jboss.modules:jboss-modules)}
%{?scl:Requires: %scl_runtime}

Provides:       bundled(objectweb-asm) = 0:5.0.4-2
Provides:       bundled(java_cup) = 1:0.11b-3

%description
Byteman is a tool which simplifies tracing and testing of Java programs.
Byteman allows you to insert extra Java code into your application,
either as it is loaded during JVM startup or even after it has already
started running. The injected code is allowed to access any of your data
and call any application methods, including where they are private.
You can inject code almost anywhere you want and there is no need to
prepare the original source code in advance nor do you have to recompile,
repackage or redeploy your application. In fact you can remove injected
code and reinstall different code while the application continues to execute.

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%package rulecheck-maven-plugin
Summary:        Maven plugin for checking Byteman rules.

%description rulecheck-maven-plugin
This package contains the Byteman rule check maven plugin.

%prep
%setup -q -n %{pkg_name}-%{version}

# Fix the gid:aid for java_cup
sed -i "s|net.sf.squirrel-sql.thirdparty-non-maven|java_cup|" agent/pom.xml
sed -i "s|java-cup|java_cup|" agent/pom.xml

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
# Remove scope=system and systemPath for com.sun:tools
%pom_xpath_remove "pom:profiles/pom:profile/pom:dependencies/pom:dependency[pom:artifactId='tools']/pom:scope" install
%pom_xpath_remove "pom:profiles/pom:profile/pom:dependencies/pom:dependency[pom:artifactId='tools']/pom:systemPath" install
%pom_xpath_remove "pom:profiles/pom:profile/pom:dependencies/pom:dependency[pom:artifactId='tools']/pom:scope" contrib/bmunit
%pom_xpath_remove "pom:profiles/pom:profile/pom:dependencies/pom:dependency[pom:artifactId='tools']/pom:systemPath" contrib/bmunit

# Some tests fail intermittently during builds. Disable them.
%pom_disable_module tests contrib/jboss-modules-system
%pom_xpath_remove "pom:build/pom:plugins/pom:plugin[pom:artifactId='maven-surefire-plugin']/pom:executions" contrib/bmunit
%pom_xpath_set "pom:build/pom:plugins/pom:plugin[pom:artifactId='maven-surefire-plugin']/pom:configuration" '<skip>true</skip>' contrib/bmunit

# Don't build download, docs modules
%pom_disable_module download
%pom_disable_module docs

# disable jboss-modules-plugin module in SCL package due to missing dependency
%{?scl:%pom_disable_module contrib/jboss-modules-system}

# disable maven-verifier-pugin for SCL package due to missing dependency
%{?scl:%pom_remove_plugin -r :maven-verifier-plugin}

# Put maven plugin into a separate package
%mvn_package ":%{pkg_name}-rulecheck-maven-plugin" rulecheck-maven-plugin
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_build
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

install -d -m 755 %{buildroot}%{_bindir}

install -d -m 755 %{buildroot}%{homedir}
install -d -m 755 %{buildroot}%{homedir}/lib
install -d -m 755 %{buildroot}%{bindir}

install -m 755 bin/bmsubmit.sh %{buildroot}%{bindir}/bmsubmit
install -m 755 bin/bminstall.sh  %{buildroot}%{bindir}/bminstall
install -m 755 bin/bmjava.sh  %{buildroot}%{bindir}/bmjava
install -m 755 bin/bmcheck.sh  %{buildroot}%{bindir}/bmcheck

for f in bmsubmit bmjava bminstall bmcheck; do
cat > %{buildroot}%{_bindir}/${f} << EOF
#!/bin/sh

export BYTEMAN_HOME=/usr/share/byteman
export JAVA_HOME=/usr/lib/jvm/java

\$BYTEMAN_HOME/bin/${f} \$*
EOF
done

chmod 755 %{buildroot}%{_bindir}/*

for m in bmunit dtest install sample submit; do
  ln -s %{_javadir}/byteman/byteman-${m}.jar %{buildroot}%{homedir}/lib/byteman-${m}.jar
done

ln -s %{_javadir}/byteman/byteman.jar %{buildroot}%{homedir}/lib/byteman.jar

%files -f .mfiles
%{homedir}/*
%{_bindir}/*
%doc README docs/ProgrammersGuide.pdf
%license docs/copyright.txt

%files javadoc -f .mfiles-javadoc
%license docs/copyright.txt

%files rulecheck-maven-plugin -f .mfiles-rulecheck-maven-plugin
%license docs/copyright.txt

%changelog
* Tue Nov 08 2016 Tomas Repik <trepik@redhat.com> - 3.0.6-2
- scl conversion

* Mon Jun 13 2016 Severin Gehwolf <sgehwolf@redhat.com> - 3.0.6-1
- Update to latest upstream release.

* Mon Mar 14 2016 Severin Gehwolf <sgehwolf@redhat.com> - 3.0.4-2
- Enable some tests during build
- Fix generated requires by filtering requires for bundled libs.
- Split maven plugin into separate package.

* Thu Feb 18 2016 Severin Gehwolf <sgehwolf@redhat.com> - 3.0.4-1
- Update to latest upstream 3.0.4 release.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.4.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Aug 06 2015 gil cattaneo <puntogil@libero.it> 2.1.4.1-7
- Fix FTBFS rhbz#1239392
- Remove duplicate files
- Introduce license macro

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.4.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Feb 27 2015 Michal Srb <msrb@redhat.com> - 2.1.4.1-5
- Fix FTBFS
- Rebuild to generate new metadata

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.4.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 18 2014 Marek Goldmann <mgoldman@redhat.com> - 2.1.4.1-3
- Rebuilding for objectweb-asm update, RHBZ#1083570

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 2.1.4.1-2
- Use Requires: java-headless rebuild (#1067528)

* Fri Feb 14 2014 Marek Goldmann <mgoldman@redhat.com> - 2.1.4.1-1
- Upstream release 2.1.4.1

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jul 04 2013 Marek Goldmann <mgoldman@redhat.com> - 2.1.2-1
- Upstream release 2.1.2

* Wed Jun  5 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.0.4-5
- Remove tools.jar from dependencyManagement

* Wed May 29 2013 Marek Goldmann <mgoldman@redhat.com> - 2.0.4-4
- New guidelines

* Thu Apr 25 2013 Marek Goldmann <mgoldman@redhat.com> - 2.0.4-3
- Fixes to the launch scripts

* Wed Apr 24 2013 Marek Goldmann <mgoldman@redhat.com> - 2.0.4-2
- Added bmsubmit, bminstall and bmjava scripts, RHBZ#951560

* Thu Feb 21 2013 Marek Goldmann <mgoldman@redhat.com> - 2.0.4-1
- Upstream release 2.0.4
- Switched to Maven
- Bundling java_cup and objectweb-asm (fpc#226)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Sep 20 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.2-3
- Removed binary files from src.rpm

* Mon Sep 19 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.2-2
- Cleaned spec file

* Wed Jul 27 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.2-1
- Upstream release: 1.5.2

* Thu Jul 21 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.1-1
- Initial packaging

