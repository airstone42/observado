#include "mediawidget.h"

MediaWidget::MediaWidget(QWidget *parent)
    : QWidget(parent)
{
    openButton = new QToolButton(parent);
    openButton->setIcon(style()->standardIcon(QStyle::SP_DirOpenIcon));
    connect(openButton, &QAbstractButton::clicked, this, &MediaWidget::toggleOpen);

    playButton = new QToolButton(parent);
    playButton->setIcon(style()->standardIcon(QStyle::SP_MediaPlay));
    playButton->setDisabled(true);
    connect(playButton, &QAbstractButton::clicked, this, &MediaWidget::togglePlay);

    stopButton = new QToolButton(parent);
    stopButton->setIcon(style()->standardIcon(QStyle::SP_MediaStop));
    stopButton->setDisabled(true);
    connect(stopButton, &QAbstractButton::clicked, this, &MediaWidget::toggleStop);

    mediaPlayer = new QMediaPlayer(parent);
    mediaPlayer->setVolume(50);
    connect(mediaPlayer, &QMediaPlayer::stateChanged, this, &MediaWidget::updateIcon);

    layout = new QHBoxLayout(parent);
    layout->addWidget(openButton);
    layout->addWidget(stopButton);
    layout->addWidget(playButton);
    this->setLayout(layout);
}

void MediaWidget::toggleOpen()
{
    QFileDialog dialog(this);
    dialog.setAcceptMode(QFileDialog::AcceptOpen);
    dialog.setMimeTypeFilters(QMediaPlayer::supportedMimeTypes());
    dialog.setDirectory(QStandardPaths::standardLocations(QStandardPaths::MusicLocation).constLast());
    dialog.setViewMode(QFileDialog::Detail);
    if (dialog.exec())
        updateMedia(dialog.selectedUrls().constLast());
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

void MediaWidget::updateMedia(const QUrl &url)
{
    fileUrl = url;
    playButton->setEnabled(true);
    stopButton->setEnabled(true);

    mediaPlayer->setMedia(url);
    mediaPlayer->play();
}

void MediaWidget::updateIcon(QMediaPlayer::State previous)
{
    if (previous == QMediaPlayer::PlayingState)
        playButton->setIcon(style()->standardIcon(QStyle::SP_MediaPause));
    else
        playButton->setIcon(style()->standardIcon(QStyle::SP_MediaPlay));
}

MediaWidget::~MediaWidget() = default;
