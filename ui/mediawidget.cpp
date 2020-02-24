#include "mediawidget.h"

MediaWidget::MediaWidget(QUrl &&fileUrl, QWidget *parent)
    : QWidget(parent)
    , fileUrl(fileUrl)
{
    playButton = new QToolButton(parent);
    playButton->setIcon(style()->standardIcon(QStyle::SP_MediaPlay));
    connect(playButton, &QAbstractButton::clicked, this, &MediaWidget::togglePlay);
    stopButton = new QToolButton(parent);
    stopButton->setIcon(style()->standardIcon(QStyle::SP_MediaStop));
    connect(stopButton, &QAbstractButton::clicked, this, &MediaWidget::toggleStop);

    mediaPlayer = new QMediaPlayer();
    mediaPlayer->setMedia(fileUrl);
    mediaPlayer->setVolume(50);
    connect(mediaPlayer, &QMediaPlayer::stateChanged, this, &MediaWidget::updateIcon);

    layout = new QHBoxLayout(parent);
    layout->addWidget(stopButton);
    layout->addWidget(playButton);
    this->setLayout(layout);
}

void MediaWidget::togglePlay()
{
    if (mediaPlayer->state() == QMediaPlayer::PlayingState)
        mediaPlayer->pause();
    else
        mediaPlayer->play();
}

void MediaWidget::toggleStop()
{
    mediaPlayer->stop();
}

void MediaWidget::updateIcon(QMediaPlayer::State previous)
{
    if (previous == QMediaPlayer::PlayingState)
        playButton->setIcon(style()->standardIcon(QStyle::SP_MediaPause));
    else
        playButton->setIcon(style()->standardIcon(QStyle::SP_MediaPlay));
}

MediaWidget::~MediaWidget() = default;
