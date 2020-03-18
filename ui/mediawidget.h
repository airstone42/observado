#ifndef MEDIAWIDGET_H
#define MEDIAWIDGET_H

#include <QMediaPlayer>
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

private:
    void updateMedia(const QUrl &url);
    void updateIcon(QMediaPlayer::State previous);

    QBoxLayout *layout = nullptr;
    QAbstractButton *openButton = nullptr;
    QAbstractButton *playButton = nullptr;
    QAbstractButton *stopButton = nullptr;

    QUrl fileUrl;
    QMediaPlayer *mediaPlayer = nullptr;
};

#endif // MEDIAWIDGET_H
