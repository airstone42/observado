#include "mainwindow.h"
#include "mediawidget.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MainWindow w;
    MediaWidget m;
    w.setCentralWidget(&m);
    w.show();
    return a.exec();
}
