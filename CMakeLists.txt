cmake_minimum_required(VERSION 3.15)
project(Observado)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt5 COMPONENTS Core Multimedia Widgets REQUIRED)

add_executable(Observado
        ui/main.cpp
        ui/mainwindow.cpp
        ui/mediawidget.cpp
        )

target_link_libraries(Observado PRIVATE Qt5::Core Qt5::Multimedia Qt5::Widgets)
