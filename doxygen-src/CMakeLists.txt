
# ===================================================================
# doxygen 起動用のコマンド
# ===================================================================

# doxygen の対象となるヘッダファイル(のパタン)を YM_DOXY_SRCS に入れる．
set ( YM_DOXY_SRCS )
foreach (dir
    "${CMAKE_CURRENT_SOURCE_DIR}"
    )
  list ( APPEND YM_DOXY_SRCS ${dir} )
endforeach()
foreach ( dir
    "ym-base"
    "ym-common"
    "ym-sat"
    )
  list ( APPEND YM_DOXY_SRCS "${PROJECT_SOURCE_DIR}/${dir}/include" )
endforeach ()
#list ( APPEND YM_DOXY_SRCS "${PROJECT_SOURCE_DIR}/gui-pyqt5" )

# YM_DOXY_SRCS を Doxyfile の INPUT 用に変換する．
string ( REPLACE ";" " " YM_DOXY_INPUT "${YM_DOXY_SRCS}" )

# プロジェクト名の設定
set ( YM_DOXY_PROJECT_NAME "nl3d-2017" )

# Doxyfile の生成
configure_file (
  "${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in"
  "Doxyfile"
  )

# doxygen 用ターゲット
add_custom_target(dox ALL
  DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/docs/html/index.html"
  )

# doxygen 起動ルール
add_custom_command(
  COMMAND "${DOXYGEN_EXECUTABLE}" ">" "doxygen.log"
  DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/Doxyfile" ${YM_DOXY_SRCS}
  OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/docs/html/index.html"
  COMMENT "generating doxygen documents"
  )

# 生成物のインストールルール
install (DIRECTORY
  "${CMAKE_CURRENT_BINARY_DIR}/docs"
  DESTINATION share/satpg-${SATPG_VERSION}/
  )
