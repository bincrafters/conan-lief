from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import os_info, Version
import os

class LIEFConan(ConanFile):
    name = "lief"
    version = "0.9.0"
    description = "Library to Instrument Executable Formats"
    url = "https://github.com/bincrafters/conan-lief"
    homepage = "https://github.com/lief-project/LIEF"
    license = "MIT"

    exports = ["patches/*.patch"]

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared":       [True, False],
        "fPIC":         [True, False],
        "with_art":     [True, False],
        "with_c_api":   [True, False],
        "with_dex":     [True, False],
        "with_elf":     [True, False],
        "with_frozen":  [True, False],
        "with_json":    [True, False],
        "with_macho":   [True, False],
        "with_oat":     [True, False],
        "with_pe":      [True, False],
        "with_vdex":    [True, False],
    }
    default_options = {
        "shared":       False,
        "fPIC":         True,
        "with_art":     False,
        "with_c_api":   False,
        "with_dex":     False,
        "with_elf":     True,
        "with_frozen":  True,
        "with_json":    True,
        "with_macho":   True,
        "with_oat":     False,
        "with_pe":      True,
        "with_vdex":    False,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "rang/3.0.0@rang/stable",
        "mbedtls/2.16.3-apache",
    )

    def requirements(self):
        if self.options.with_json:
            self.requires("nlohmann_json/3.7.3")
        if not os_info.is_windows and self.options.with_frozen:
            self.requires("frozen/20181020@bincrafters/stable")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.with_frozen

    def source(self):
        source_url = "https://github.com/lief-project/lief"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = "LIEF-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        msg = "LIEF does not support "
        ver = Version(str(self.settings.compiler.version))
        if self.settings.compiler == "Visual Studio":
            if ver < Version("15"):
                raise ConanInvalidConfiguration(
                    msg + "Visual Studio versions older than 15.")
        elif self.settings.compiler == "gcc":
            if ver < Version("6"):
                raise ConanInvalidConfiguration(
                    msg + "gcc versions older than 6.")
        elif self.settings.compiler == "clang":
            if ver < Version("6"):
                raise ConanInvalidConfiguration(
                    msg + "clang versions older than 6.")

    def _configure_cmake(self):
        cmake = CMake(self)
        def on_if(val):
            return "ON" if val else "OFF"
        opt_flags = {
            "with_art":     "LIEF_ART",
            "with_c_api":   "LIEF_C_API",
            "with_dex":     "LIEF_DEX",
            "with_elf":     "LIEF_ELF",
            "with_json":    "LIEF_ENABLE_JSON",
            "with_macho":   "LIEF_MACHO",
            "with_oat":     "LIEF_OAT",
            "with_pe":      "LIEF_PE",
            "with_vdex":    "LIEF_VDEX",
        }
        for opt, flag in opt_flags.items():
            cmake.definitions[flag] = on_if(getattr(self.options, opt))

        major, minor, patch = self.version.split(".")
        cmake.definitions["LIEF_GIT_TAG"] = self.version
        cmake.definitions["LIEF_IS_TAGGED"] = "TRUE"
        cmake.definitions["LIEF_VERSION_MAJOR"] = major
        cmake.definitions["LIEF_VERSION_MINOR"] = minor
        cmake.definitions["LIEF_VERSION_PATCH"] = patch
        cmake.definitions["LIEF_PYTHON_API"] = "OFF"
        cmake.definitions["VERSION_STRING"] = self.version

        cmake.definitions["BUILD_SHARED_LIBS"] = on_if(self.options.shared)
        cmake.definitions["LIEF_SHARED_LIB"] = on_if(self.options.shared)

        off_vars = "LIEF_EXAMPLES", "LIEF_LOGGING", "LIEF_TESTS"

        for var in off_vars:
            cmake.definitions[var] = "OFF"

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        patches = os.listdir("patches")
        for patch_file in sorted(patches):
            self.output.info("Applying " + patch_file)
            tools.patch(self._source_subfolder, os.path.join("patches", patch_file))
        cmake = self._configure_cmake()
        lief_shared = "SHARED" if self.options.shared else "STATIC"
        lief_target = "LIB_LIEF_" + lief_shared
        cmake.build(target=lief_target)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.cxxflags += ["/FIiso646.h"]
