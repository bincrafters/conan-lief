cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# This makes LIEF skip its own dependency management.
set(__add_lief_dependencies TRUE CACHE INTERNAL "" FORCE)

# This is patched out completely because git is required:
# outside the LIEFGit.cmake file: https://github.com/lief-project/LIEF/issues/224
# The version and tag variables are pass from the conanfile.
# set(__add_lief_git TRUE CACHE INTERNAL "" FORCE)

# The following targets bridge the gap between LIEF's internal
# dependency handling (based on ExternalProject_Add targets)
# and conan.

# Json
# ----
if(TARGET CONAN_PKG::jsonformoderncpp)
  add_custom_target(lief_libjson ALL DEPENDS CONAN_PKG::jsonformoderncpp)
  set(LIBJSON_SOURCE_DIR ${CONAN_INCLUDE_DIRS_JSONFORMODERNCPP} CACHE INTERNAL "" FORCE)
  message(STATUS "Enable JSON support")
  set(ENABLE_JSON_SUPPORT 1 CACHE INTERNAL "" FORCE)
else()
  message(STATUS "Disable JSON support")
  set(ENABLE_JSON_SUPPORT 0 CACHE INTERNAL "" FORCE)
endif()

# Rang
# ----
add_custom_target(lief_rang_cpp_color ALL DEPENDS CONAN_PKG::rang)
set(LIBRANG_SOURCE_DIR ${CONAN_INCLUDE_DIRS_RANG}/.. CACHE INTERNAL "" FORCE)

# mbed TLS
# --------
add_custom_target(lief_mbed_tls ALL DEPENDS CONAN_PKG::mbedtls)
set(MBEDTLS_INCLUDE_DIRS ${CONAN_INCLUDE_DIRS_MBEDTLS} CACHE INTERNAL "" FORCE)

# Frozen
# ------
if(TARGET CONAN_PKG::frozen)
  message(STATUS "Enable Frozen (C++14 support)")
  set(LIEF_FROZEN_ENABLED 1 CACHE INTERNAL "" FORCE)
  add_custom_target(lief_frozen ALL DEPENDS CONAN_PKG::frozen)
  set(FROZEN_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_FROZEN} CACHE INTERNAL "" FORCE)
else()
  set(LIEF_FROZEN_ENABLED 0 CACHE INTERNAL "" FORCE)
endif()

include_directories(${CMAKE_CURRENT_BINARY_DIR}/source_subfolder)

add_subdirectory("source_subfolder")
