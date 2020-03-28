#include "core.h"

#include <QAbstractButton>
#include <QAbstractSlider>
#include <QBoxLayout>
#include <QLabel>
#include <QMediaPlayer>
#include <QTableWidget>
#include <QUrl>
#include <QtGlobal>
#include <QtWidgets>

#ifndef MEDIAWIDGET_H
#define MEDIAWIDGET_H

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

private:
    void updateMedia(const QUrl &url);
    void setIcon(QMediaPlayer::State previous);
    void updatePosition(qint64 position);
    void updateDuration(qint64 duration);
    void setDurationLabel(qint64 duration);
    void setTable(bool available);

    Core core;

    QBoxLayout *buttonLayout = nullptr;
    QBoxLayout *barLayout = nullptr;
    QBoxLayout *mainLayout = nullptr;

    QLabel *fileLabel = nullptr;
    QAbstractButton *openButton = nullptr;
    QAbstractButton *playButton = nullptr;
    QAbstractButton *stopButton = nullptr;
    QAbstractSlider *positionSlider = nullptr;
    QLabel *positionLabel = nullptr;
    QLabel *durationLabel = nullptr;
    QTableWidget *recordTable = nullptr;

    QUrl fileUrl;
    QMediaPlayer *mediaPlayer = nullptr;
};

#endif // MEDIAWIDGET_H
