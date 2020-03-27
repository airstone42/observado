#include <QList>
#include <QString>
#include <QUrl>

#ifndef CORE_H
#define CORE_H

struct Record {
    QString begin;
    QString end;
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

    static QString pyModule;
    static QString pyFunction;

private:
    QUrl url;
    QList<Record> records;

    bool parse(const QString &pyResult);
};

#endif //CORE_H
