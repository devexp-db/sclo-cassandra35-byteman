Name:             byteman
Version:          1.5.2
Release:          5%{?dist}
Summary:          Java agent-based bytecode injection tool
Group:            Development/Libraries
License:          LGPLv2+
URL:              http://www.jboss.org/byteman
# wget http://downloads.jboss.org/%{name}/%{version}/%{name}-%{version}-full-clean.zip
# unzip -q %{name}-%{version}-full-clean.zip -d %{name}-%{version}-full
# rm -rf %{name}-%{version}-full/ext/*
# tar -zcvf %{name}-%{version}-full-clean.tar.gz %{name}-%{version}-full
Source0:          %{name}-%{version}-full-clean.tar.gz
Patch0:           %{name}-%{version}-buildxml.patch

BuildArch:        noarch

BuildRequires:    jpackage-utils
BuildRequires:    java-devel
BuildRequires:    ant
BuildRequires:    java_cup
BuildRequires:    jarjar
BuildRequires:    objectweb-asm
BuildRequires:    junit4
BuildRequires:    testng

Requires:         java_cup
Requires:         objectweb-asm
Requires:         jpackage-utils
Requires:         java

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
%setup -q -n %{name}-%{version}-full
%patch0 -p1

find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

%build
OPT_JAR_LIST="jarjar junit4 testng objectweb-asm java_cup" ant install htdocs
ant -f build-release-pkgs.xml init mvn-repository

%install
# JAR
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}

install -pm 644 build/lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}.jar
install -pm 644 build/lib/%{name}-install.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}-install.jar
install -pm 644 build/lib/%{name}-submit.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}-submit.jar
install -pm 644 sample/build/lib/%{name}-sample.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}-sample.jar
install -pm 644 contrib/bmunit/build/lib/%{name}-bmunit.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}-bmunit.jar
install -pm 644 contrib/dtest/build/lib/%{name}-dtest.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/%{name}-dtest.jar

install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}

for m in bmunit dtest install sample submit; do
  # POM
  install -pm 644 workdir/pom-%{name}-${m}.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-%{name}-${m}.pom

  # DEPMAP
  %add_maven_depmap JPP.%{name}-%{name}-${m}.pom %{name}/%{name}-${m}.jar
done

# POM
install -pm 644 workdir/pom-%{name}.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-%{name}.pom

# DEPMAP
%add_maven_depmap JPP.%{name}-%{name}.pom %{name}/%{name}.jar

# APIDOCS
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -rp htdocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%files
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*
%{_javadir}/*
%doc README docs/ProgrammersGuide.pdf docs/copyright.txt

%files javadoc
%{_javadocdir}/%{name}
%doc docs/copyright.txt

%changelog
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

