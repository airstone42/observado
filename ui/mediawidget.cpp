#include "mediawidget.h"

#include <QFileDialog>
#include <QHBoxLayout>
#include <QSlider>
#include <QStandardPaths>
#include <QStyle>
#include <QTime>
#include <QToolButton>
#include <QVBoxLayout>

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

    positionSlider = new QSlider(Qt::Horizontal, parent);
    positionSlider->setDisabled(true);
    connect(positionSlider, &QAbstractSlider::valueChanged, this, &MediaWidget::setPosition);

    positionLabel = new QLabel(tr("--:--"), this);
    durationLabel = new QLabel(tr("--:--"), this);

    mediaPlayer = new QMediaPlayer(parent);
    mediaPlayer->setVolume(50);
    connect(mediaPlayer, &QMediaPlayer::stateChanged, this, &MediaWidget::updateIcon);
    connect(mediaPlayer, &QMediaPlayer::durationChanged, this, &MediaWidget::updateDuration);
    connect(mediaPlayer, &QMediaPlayer::positionChanged, this, &MediaWidget::updatePosition);

    buttonLayout = new QHBoxLayout(parent);
    buttonLayout->addWidget(openButton);
    buttonLayout->addWidget(stopButton);
    buttonLayout->addWidget(playButton);

    barLayout = new QHBoxLayout(parent);
    barLayout->addWidget(positionLabel);
    barLayout->addWidget(positionSlider);
    barLayout->addWidget(durationLabel);

    mainLayout = new QVBoxLayout(parent);
    mainLayout->addLayout(buttonLayout);
    mainLayout->addLayout(barLayout);
    this->setLayout(mainLayout);
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

void MediaWidget::setPosition(qint64 position)
{
    if (qAbs(mediaPlayer->position() - position) > 99)
        mediaPlayer->setPosition(position);
}

void MediaWidget::updateMedia(const QUrl &url)
{
    fileUrl = url;
    playButton->setEnabled(true);
    stopButton->setEnabled(true);
    positionSlider->setEnabled(true);

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

void MediaWidget::updatePosition(qint64 position)
{
    positionSlider->setValue(position);
    auto time = QTime(0, 0).addMSecs(position);
    positionLabel->setText(time.toString("mm:ss"));
}

void MediaWidget::updateDuration(qint64 duration)
{
    setDurationLabel(duration);
    positionSlider->setRange(0, duration);
    positionSlider->setEnabled(duration > 0);
    positionSlider->setPageStep(static_cast<int>(duration / 10));
}

void MediaWidget::setDurationLabel(qint64 duration)
{
    auto time = QTime(0, 0).addMSecs(duration);
    durationLabel->setText(time.toString("mm:ss"));
}

MediaWidget::~MediaWidget() = default;
