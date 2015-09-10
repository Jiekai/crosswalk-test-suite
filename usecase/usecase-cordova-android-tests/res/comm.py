#!/usr/bin/env python
import os
import commands
import sys
import json
import logging
import urllib2
import stat
import shutil
import subprocess
import time
import re
from bs4 import BeautifulSoup
from optparse import OptionParser
script_path = os.path.realpath(__file__)
const_path = os.path.dirname(script_path)
tool_path = const_path + "/../tools/"
plugin_tool = const_path + "/../tools/cordova-plugin-crosswalk-webview/"

def setUp():
    global CROSSWALK_VERSION
    global CROSSWALK_BRANCH
    global PACK_TYPE
    global LOG
    LOG = logging.getLogger("pack-tool")

    f_version = open(const_path + "/cordova-version", 'r')
    if f_version.read().strip("\n\t") != "3.6":
        CORDOVA_VERSION = "4.x"
    else:
        CORDOVA_VERSION = "3.6"
    f_version.close()

    if CORDOVA_VERSION == "4.x":
        f_pack_type = open(const_path + "/pack-type", 'r')
        pack_type_tmp = f_pack_type.read()
        if pack_type_tmp.strip("\n\t") == "local":
            PACK_TYPE = "local"
        elif pack_type_tmp.strip("\n\t") == "npm":
            PACK_TYPE = "npm"
        else:
            print (
                " get pack type error, the content of pack-type should be 'local' or 'npm'\n")
            sys.exit(1)
        f_pack_type.close()

        with open("../../tools/VERSION", "rt") as pkg_version_file:
            pkg_version_raw = pkg_version_file.read()
            pkg_version_file.close()
            pkg_version_json = json.loads(pkg_version_raw)
            CROSSWALK_VERSION = pkg_version_json["main-version"]
            CROSSWALK_BRANCH = pkg_version_json["crosswalk-branch"]

    


def installCrosswalk(pkgmode):
    version_parts = CROSSWALK_VERSION.split('.')
    if len(version_parts) < 4:
        print "The crosswalk version is not configured exactly!"
        sys.exit(1)
    versionType = version_parts[3]
    if versionType == '0':
        username = commands.getoutput("echo $USER")
        if pkgmode == "shared":
            repository_aar_path = "/home/%s/.m2/repository/org/xwalk/xwalk_shared_library/%s/" \
                "xwalk_shared_library-%s.aar" % \
                (username, CROSSWALK_VERSION, CROSSWALK_VERSION)
            repository_pom_path = "/home/%s/.m2/repository/org/xwalk/xwalk_shared_library/%s/" \
                "xwalk_shared_library-%s.pom" % \
                (username, CROSSWALK_VERSION, CROSSWALK_VERSION)
        else:
            repository_aar_path = "/home/%s/.m2/repository/org/xwalk/xwalk_core_library/%s/" \
                "xwalk_core_library-%s.aar" % \
            (username, CROSSWALK_VERSION, CROSSWALK_VERSION)
        repository_pom_path = "/home/%s/.m2/repository/org/xwalk/xwalk_core_library/%s/" \
            "xwalk_core_library-%s.pom" % \
            (username, CROSSWALK_VERSION, CROSSWALK_VERSION)

    if not os.path.exists(repository_aar_path) or not os.path.exists(repository_pom_path):
        if pkgmode == "shared":
            wget_cmd = "wget https://download.01.org/crosswalk/releases/crosswalk/" \
                "android/canary/%s/crosswalk-shared-%s.aar" % \
                (CROSSWALK_VERSION, CROSSWALK_VERSION)
            install_cmd = "mvn install:install-file -DgroupId=org.xwalk " \
                "-DartifactId=xwalk_shared_library -Dversion=%s -Dpackaging=aar " \
                "-Dfile=crosswalk-shared-%s.aar -DgeneratePom=true" % \
                (CROSSWALK_VERSION, CROSSWALK_VERSION)
        else:
            wget_cmd = "wget https://download.01.org/crosswalk/releases/crosswalk/" \
                "android/canary/%s/crosswalk-%s.aar" % \
                (CROSSWALK_VERSION, CROSSWALK_VERSION)
            install_cmd = "mvn install:install-file -DgroupId=org.xwalk " \
                "-DartifactId=xwalk_core_library -Dversion=%s -Dpackaging=aar " \
                "-Dfile=crosswalk-%s.aar -DgeneratePom=true" % \
                (CROSSWALK_VERSION, CROSSWALK_VERSION)

        os.system(wget_cmd)
        os.system(install_cmd)

def getLatestCrosswalkVersion(channel=None):
    version = ''
    crosswalk_url = ""
    if channel == "beta":
        crosswalk_url = 'https://download.01.org/crosswalk/releases/crosswalk/android/maven2/org/xwalk/' \
                'xwalk_core_library_beta/'
    elif channel == "stable":
        crosswalk_url = 'https://download.01.org/crosswalk/releases/crosswalk/android/maven2/org/xwalk/' \
                'xwalk_core_library/'
    else:
        LOG.error("getLatestCrosswalkVersion only support stable or beta")
        sys.exit(1)
    htmlDoc = urllib2.urlopen(crosswalk_url).read()
    soup = BeautifulSoup(htmlDoc)
    alist = soup.find_all('a')
    for index in range(-1, -len(alist)-1, -1):
        aEle = alist[index]
        version = aEle['href'].strip('/')
        if re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', version):
            break
    return version

def create(appname, pkgname, tmp_path):
    print "begin to create project:"
    os.chdir(tmp_path)
    if os.path.exists(appname):
        os.system("rm -rf %s" % appname)
    os.system("cordova create %s %s %s" % (appname, pkgname, appname))
    os.chdir("./%s" % appname)
    os.system('sed -i "s/<widget/<widget android-activityName=\\"%s\\"/g" config.xml' % appname)
    os.system('sed -i "s/<\/widget>/    <allow-navigation href=\\"*\\" \/>\\n<\/widget>/g" config.xml')
    os.system("cordova platform add android")

def build(xwalk_mode=None, xwalk_version=None):
    xwalk_mode_cmd = "--variable XWALK_MODE=\"%s\"" % xwalk_mode
    xwalk_version_cmd = ""
    if xwalk_version:
        xwalk_version_cmd = "--variable XWALK_VERSION=\"%s\"" % xwalk_version

    plugin_crosswalk_source = plugin_tool
    if PACK_TYPE == "npm":
        plugin_crosswalk_source = "cordova-plugin-crosswalk-webview"

    install_crosswalk_cmd = "cordova plugin add %s %s %s" % (plugin_crosswalk_source, xwalk_version_cmd, xwalk_mode_cmd)
    os.system(install_crosswalk_cmd)
    print install_crosswalk_cmd
    os.system("cordova build android")

