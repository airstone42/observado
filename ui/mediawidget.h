#ifndef MEDIAWIDGET_H
#define MEDIAWIDGET_H

#include <QAbstractButton>
#include <QAbstractSlider>
#include <QBoxLayout>
#include <QLabel>
#include <QMediaPlayer>
#include <QUrl>
#include <QtGlobal>
#include <QtWidgets>

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
    void updateIcon(QMediaPlayer::State previous);
    void updatePosition(qint64 position);
    void updateDuration(qint64 duration);
    void setDurationLabel(qint64 duration);

    QBoxLayout *layout = nullptr;
    QAbstractButton *openButton = nullptr;
    QAbstractButton *playButton = nullptr;
    QAbstractButton *stopButton = nullptr;
    QAbstractSlider *positionSlider = nullptr;
    QLabel *nowLabel = nullptr;
    QLabel *durationLabel = nullptr;

    QUrl fileUrl;
    QMediaPlayer *mediaPlayer = nullptr;
};

#endif // MEDIAWIDGET_H
