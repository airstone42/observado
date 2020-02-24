#include "mainwindow.h"
#include "mediawidget.h"

#include <QApplication>
#include <QtCore>

int main(int argc, char *argv[])
{
    QString file(argv[1]);
    if (!QFile::exists(file)) {
        qWarning() << "File not exists! Check argv[1].";
        return -1;
    }

    QApplication a(argc, argv);
    MainWindow w;
    auto m = new MediaWidget(QUrl::fromLocalFile(file));
    w.setCentralWidget(m);
    w.show();
    return a.exec();
}
