#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os
import shutil


class PythonPopplerConan(ConanFile):
    name = "python-poppler"
    version = "0.25.1"
    description = "libpoppler binding for PyQt5"
    topics = "conan", "python", "binding", "sip", "poppler"
    url = "https://github.com/zehome/conan-python-poppler"
    homepage = "https://github.com/zehome/python-poppler-qt5"
    author = "Laurent Coustet <ed@zehome.com>"
    license = "GPL-3.0-only"
    generators = "txt"
    settings = "os", "compiler", "build_type", "arch"
    requires = (
        "poppler/0.72.0@clarisys/stable",
        "PyQt5/5.11.3@clarisys/stable",
    )
    _source_subfolder = "python-popppler-qt5"

    # LC: poppler-qt5
    default_options = "poppler:with_splash=True", "poppler:shared=True"

    def source(self):
        source_url = "https://github.com/zehome/python-poppler-qt5/archive/"
        tools.get("{0}/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = "python-poppler-qt5-{0}".format(self.version)
        if os.path.exists(self._source_subfolder):
            shutil.rmtree(self._source_subfolder)
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.os == "Windows":
            vcvars = tools.vcvars_command(self.settings)
        else:
            vcvars = None
        # python-poppler-qt5 sources are buggy, they import "qt5/qt5-poppler.h" and other
        # headers, but they are normally installed in poppler/qt5/qt5-poppler.h
        includedirs = self.deps_cpp_info.includedirs
        libdirs = self.deps_cpp_info.libdirs
        for incdir in self.deps_cpp_info["poppler"].include_paths:
            includedirs.append(os.path.join(incdir, "poppler"))
        with tools.chdir(self._source_subfolder):
            self.run("{vc}python setup.py build_ext --verbose "
                "--poppler-version=0.71.0 "
                "--pyqt-sip-dir={sipdir} "
                "--library-dirs={libdirs} "
                "--include-dirs={incdirs}".format(
                    vc="{0} && ".format(vcvars) if vcvars is not None else '',
                    sipdir=os.path.join(self.build_folder, "sip", "PyQt5"),
                    libdirs=";".join(self.deps_cpp_info.libdirs),
                    incdirs=";".join(includedirs),
                ),
                run_environment=True,
            )

    def package(self):
        self.copy("*popplerqt5*.pyd", dst="site-packages", keep_path=False)
        self.copy("*popplerqt5*.lib", dst="lib", keep_path=False)

    def imports(self):
        self.copy("*", src="sip", dst="sip", root_package="PyQt5")
