Name:             byteman
Version:          2.0.4
Release:          1%{?dist}
Summary:          Java agent-based bytecode injection tool
Group:            Development/Libraries
License:          LGPLv2+
URL:              http://www.jboss.org/byteman

# git clone git://github.com/bytemanproject/byteman.git
# cd byteman/ && git archive --format=tar --prefix=byteman-2.0.4/ 2.0.4 | xz > byteman-2.0.4.tar.xz
Source0:          byteman-%{version}.tar.xz

BuildArch:        noarch

BuildRequires:    jpackage-utils
BuildRequires:    javapackages-tools
BuildRequires:    java-devel
BuildRequires:    maven-local
BuildRequires:    maven-shade-plugin
BuildRequires:    maven-failsafe-plugin
BuildRequires:    maven-jar-plugin
BuildRequires:    maven-surefire-plugin
BuildRequires:    maven-surefire-provider-testng
BuildRequires:    maven-surefire-provider-junit4
BuildRequires:    maven-verifier-plugin
BuildRequires:    java_cup
BuildRequires:    jarjar
BuildRequires:    objectweb-asm
BuildRequires:    junit4
BuildRequires:    testng

Requires:         jpackage-utils
Requires:         java

# Bundling
Provides:         bundled(java_cup) = 0.11a-12
Provides:         bundled(objectweb-asm) = 3.3.1-5

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
Summary:          Javadocs for %{name}
Group:            Documentation
Requires:         jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q

# Fix the gid:aid for java_cup
sed -i "s|net.sf.squirrel-sql.thirdparty-non-maven|java_cup|" agent/pom.xml
sed -i "s|java-cup|java_cup|" agent/pom.xml

%build
%mvn_build

%install
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}

for m in install sample submit; do
  # JAR
  install -pm 644 ${m}/target/%{name}-${m}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}-${m}.jar
  # POM
  install -pm 644 ${m}/pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-%{name}-${m}.pom
  # DEPMAP
  %add_maven_depmap JPP.%{name}-%{name}-${m}.pom %{name}/%{name}-${m}.jar
done

# Contrib
for m in bmunit dtest; do
  # JAR
  install -pm 644 contrib/${m}/target/%{name}-${m}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}-${m}.jar
  # POM
  install -pm 644 contrib/${m}/pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-%{name}-${m}.pom
  # DEPMAP
  %add_maven_depmap JPP.%{name}-%{name}-${m}.pom %{name}/%{name}-${m}.jar
done

# JAR
install -pm 644 agent/target/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}.jar
# POM
install -pm 644 agent/pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-%{name}.pom
# DEPMAP
%add_maven_depmap JPP.%{name}-%{name}.pom %{name}/%{name}.jar

# APIDOCS
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -rp target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%files
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*
%{_javadir}/*
%doc README docs/ProgrammersGuide.pdf docs/copyright.txt

%files javadoc
%{_javadocdir}/%{name}
%doc docs/copyright.txt

%changelog
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

