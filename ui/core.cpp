#include "core.h"

#include <QDebug>
#include <utility>

#define PY_SSIZE_T_CLEAN
#ifdef slots
#undef slots
#include <Python.h>
#define slots Q_SLOTS
#endif

QString Core::pyModule = "main";
QString Core::pyFunction = "run";

Core::Core() = default;

Core::Core(QUrl url)
    : url(std::move(url))
{
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
        records.append(Record { words[0], words[1], words[2] });
    }
    return true;
}

bool Core::run()
{
    Py_Initialize();

    PyObject *module = nullptr, *function = nullptr, *result = nullptr;
    if (!(module = PyImport_ImportModule(pyModule.toStdString().c_str()))) {
        qDebug() << "Loading module failed!";
        Py_Finalize();
        return false;
    }
    if (!(function = PyObject_GetAttrString(module, pyFunction.toStdString().c_str()))) {
        qDebug() << "Loading function failed!";
        Py_Finalize();
        return false;
    }
    if (!(result = PyObject_CallFunction(function, "s", url.toLocalFile().toStdString().c_str()))) {
        qDebug() << "Calling function failed!";
        Py_Finalize();
        return false;
    }
    auto s = QString(PyUnicode_AsUTF8(result));
    if (!parse(s)) {
        qDebug() << "Parsing result failed!";
        Py_Finalize();
        return false;
    }

    Py_Finalize();
    return true;
}

Core::~Core() = default;
