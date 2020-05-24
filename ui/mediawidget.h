#include <QAbstractButton>
#include <QAbstractSlider>
#include <QBoxLayout>
#include <QLabel>
#include <QList>
#include <QMediaPlayer>
#include <QString>
#include <QTableWidget>
#include <QTime>
#include <QUrl>
#include <QtGlobal>
#include <QtWidgets>

#ifndef MEDIAWIDGET_H
#define MEDIAWIDGET_H

struct Record {
    QTime begin;
    QTime end;
    QString chord;
};

class MediaWidget : public QWidget {
    Q_OBJECT
public:
    explicit MediaWidget(QWidget *parent = nullptr);

    ~MediaWidget() override;

public slots:
    void toggleOpen();
    void togglePlay();
    void toggleStop();
    void setPosition(qint64 position);
    void handleResult(const QString &result);

signals:
    void readResult(const QString &result);

private:
    void updateMedia(const QUrl &url);
    void setIcon(QMediaPlayer::State previous);
    void updatePosition(qint64 position);
    void updateDuration(qint64 duration);
    void setDurationLabel(qint64 duration);
    void clearTable();
    void setTable();

    void run();
    bool parse(const QString &pyResult);
    int search(qint64 position);

    static const char *CHORD_STYLE;
    static const char *NOTE_SPECIAL_STYLE;
    static const char *NOTE_NORMAL_STYLE;

    QList<Record> records;
    QString currentChord;
    QList<QLabel *> noteList;

    QBoxLayout *buttonLayout = nullptr;
    QBoxLayout *chordLayout = nullptr;
    QBoxLayout *barLayout = nullptr;
    QBoxLayout *tableLayout = nullptr;
    QBoxLayout *mainLayout = nullptr;

    QLabel *fileLabel = nullptr;
    QAbstractButton *openButton = nullptr;
    QAbstractButton *playButton = nullptr;
    QAbstractButton *stopButton = nullptr;
    QAbstractSlider *positionSlider = nullptr;
    QLabel *chordLabel = nullptr;
    QLabel *positionLabel = nullptr;
    QLabel *durationLabel = nullptr;
    QTableWidget *recordTable = nullptr;

    QUrl fileUrl;
    QMediaPlayer *mediaPlayer = nullptr;
};

#endif // MEDIAWIDGET_H
