

# ===================================================================
# インクルードパスの設定
# ===================================================================
include_directories (
  ${PROJECT_SOURCE_DIR}/ym-base/cython-src
  ${PROJECT_SOURCE_DIR}/ym-sat/cython-src
  )


# ===================================================================
#  マクロの定義
# ===================================================================


# ===================================================================
# サブディレクトリの設定
# ===================================================================


# ===================================================================
#  cython 用のソースファイルの設定
# ===================================================================

set ( CYTHON_SOURCES
  pym_sat.pyx
  )

set_source_files_properties (
  ${CYTHON_SOURCES}
  PROPERTIES CYTHON_IS_CXX TRUE
  )


# ===================================================================
#  module ターゲットの設定
# ===================================================================

cython_add_module ( pym_sat
  ${CYTHON_SOURCES}
  $<TARGET_OBJECTS:ym_sat>
  $<TARGET_OBJECTS:ym_base>
  )

target_compile_options ( pym_sat
  PRIVATE "-O3"
  )

target_compile_definitions ( pym_sat
  PRIVATE "-DNDEBUG"
  )

target_link_libraries ( pym_sat
  ${YM_LIB_DEPENDS}
  )

#add_custom_command (
#  TARGET pym_sat
#  POST_BUILD
#  COMMAND ${CMAKE_COMMAND}
#  ARGS -E copy ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py ${CMAKE_CURRENT_BINARY_DIR}/
#  )


# ===================================================================
# テストターゲット
# ===================================================================


# ===================================================================
# インストールターゲット
# ===================================================================

#install (TARGETS
#  pym_sat
#  DESTINATION ${MATOTH_PYTHON_LIBDIR}
#  )
