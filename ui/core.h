#include <QList>
#include <QString>
#include <QStringList>
#include <QTime>
#include <QUrl>

#define PY_SSIZE_T_CLEAN
#ifdef slots
#undef slots
#include <Python.h>
#define slots Q_SLOTS
#endif

#ifndef CORE_H
#define CORE_H

struct Record {
    QTime begin;
    QTime end;
    QString chord;
};

class Core {
public:
    Core();
    explicit Core(QUrl url);
    Core(const Core &) = delete;
    Core &operator=(const Core &) = delete;
    Core(const Core &&) = delete;
    Core &operator=(const Core &&) = delete;
    ~Core();

    bool run();
    void setUrl(const QUrl &url);
    QList<QStringList> recordItems();

    static QString PY_MODULE;
    static QString PY_FUNCTION;

private:
    PyObject *pyModule = nullptr, *pyFunction = nullptr;

    bool available;
    QUrl url;
    QList<Record> records;

    bool parse(const QString &pyResult);
};

#endif //CORE_H
