#include "core.h"

#include <stdexcept>
#include <utility>

#include <QDebug>
#include <QtGlobal>

QString Core::PY_MODULE = "main";
QString Core::PY_FUNCTION = "run";

Core::Core()
{
    Py_Initialize();
    try {
        PyObject *sys = PyImport_ImportModule("sys");
        PyObject *path = PyObject_GetAttrString(sys, "path");
        if (!sys || !path)
            throw std::runtime_error("Loading sys failed!");
        PyList_Append(path, PyUnicode_FromString("."));
        if (!(pyModule = PyImport_ImportModule(PY_MODULE.toStdString().c_str())))
            throw std::runtime_error("Loading module failed!");
        if (!(pyFunction = PyObject_GetAttrString(pyModule, PY_FUNCTION.toStdString().c_str())))
            throw std::runtime_error("Loading function failed!");
        available = true;
    } catch (const std::runtime_error &e) {
        available = false;
        qWarning() << e.what();
    }
}

Core::Core(QUrl url)
    : Core()
{
    this->url = std::move(url);
}

bool Core::parse(const QString &pyResult)
{
    auto lines = pyResult.split('\n');
    if (lines.isEmpty())
        return false;
    for (const auto &line : lines) {
        auto words = line.split(' ');
        if (words.size() != 3) {
            records.clear();
            return false;
        }
        auto begin = QTime(0, 0).addMSecs(static_cast<int>(words[0].toDouble() * 1000));
        auto end = QTime(0, 0).addMSecs(static_cast<int>(words[1].toDouble() * 1000));
        records.append(Record { begin, end, words[2] });
    }
    return true;
}

bool Core::run()
{
    if (!available || url.isEmpty())
        return false;
    records.clear();

    PyObject *result = nullptr;
    try {
        if (!(result = PyObject_CallFunction(pyFunction, "s", url.toLocalFile().toStdString().c_str())))
            throw std::runtime_error("Calling function failed!");
        auto s = QString(PyUnicode_AsUTF8(result));
        if (!parse(s))
            throw std::runtime_error("Parsing result failed!");
    } catch (const std::runtime_error &e) {
        qWarning() << e.what();
        return false;
    }
    return true;
}

void Core::setUrl(const QUrl &url)
{
    this->url = url;
}

QList<QStringList> Core::recordItems()
{
    QList<QStringList> items;
    if (available)
        for (const auto &record : records)
            items.append({ record.begin.toString("mm:ss.zzz"), record.end.toString("mm:ss.zzz"), record.chord });
    return items;
}

Core::~Core()
{
    Py_Finalize();
}
