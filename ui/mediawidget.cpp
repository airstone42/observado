#include "mediawidget.h"

#include <QDir>
#include <QFile>
#include <QFileDialog>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QProcess>
#include <QRegExp>
#include <QSlider>
#include <QStandardPaths>
#include <QStyle>
#include <QTableWidgetItem>
#include <QTime>
#include <QToolButton>
#include <QVBoxLayout>
#include <Qt>
#include <QtGlobal>

MediaWidget::MediaWidget(QWidget *parent)
    : QWidget(parent)
{
    connect(this, &MediaWidget::readResult, this, &MediaWidget::handleResult);

    fileLabel = new QLabel(parent);

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
    connect(mediaPlayer, &QMediaPlayer::stateChanged, this, &MediaWidget::setIcon);
    connect(mediaPlayer, &QMediaPlayer::durationChanged, this, &MediaWidget::updateDuration);
    connect(mediaPlayer, &QMediaPlayer::positionChanged, this, &MediaWidget::updatePosition);

    recordTable = new QTableWidget(parent);
    recordTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    recordTable->horizontalHeader()->setStretchLastSection(true);
    recordTable->verticalHeader()->setVisible(false);

    buttonLayout = new QHBoxLayout(parent);
    buttonLayout->addWidget(openButton);
    buttonLayout->addWidget(stopButton);
    buttonLayout->addWidget(playButton);

    barLayout = new QHBoxLayout(parent);
    barLayout->addWidget(positionLabel);
    barLayout->addWidget(positionSlider);
    barLayout->addWidget(durationLabel);

    tableLayout = new QVBoxLayout(parent);
    tableLayout->addWidget(recordTable);

    mainLayout = new QVBoxLayout(parent);
    mainLayout->addWidget(fileLabel, 0, Qt::AlignHCenter);
    mainLayout->addLayout(buttonLayout);
    mainLayout->addLayout(barLayout);
    mainLayout->addLayout(tableLayout);
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
    if (mediaPlayer->state() == QMediaPlayer::StoppedState)
        mediaPlayer->setPosition(0);
    else
        mediaPlayer->stop();
}

void MediaWidget::setPosition(qint64 position)
{
    if (qAbs(mediaPlayer->position() - position) > 99)
        mediaPlayer->setPosition(position);
}

void MediaWidget::handleResult(const QString &result)
{
    records.clear();
    clearTable();
    if (parse(result))
        setTable();
}

void MediaWidget::updateMedia(const QUrl &url)
{
    fileUrl = url;
    fileLabel->setText(fileUrl.fileName());
    playButton->setEnabled(true);
    stopButton->setEnabled(true);
    positionSlider->setEnabled(true);

    run();

    mediaPlayer->setMedia(url);
}

void MediaWidget::setIcon(QMediaPlayer::State previous)
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

    int index = search(position + 100);
    if (index < recordTable->rowCount())
        recordTable->selectRow(index);
}

void MediaWidget::updateDuration(qint64 duration)
{
    setDurationLabel(duration);
    positionSlider->setRange(0, duration);
    positionSlider->setEnabled(duration > 0);
    positionSlider->setPageStep(static_cast<int>(duration / 5));
}

void MediaWidget::setDurationLabel(qint64 duration)
{
    auto time = QTime(0, 0).addMSecs(duration);
    durationLabel->setText(time.toString("mm:ss"));
}

void MediaWidget::clearTable()
{
    recordTable->setRowCount(0);
}

void MediaWidget::setTable()
{
    if (records.empty()) {
        mediaPlayer->play();
        return;
    }

    recordTable->setColumnCount(3);
    recordTable->setHorizontalHeaderLabels({ "begin", "end", "chord" });
    for (const auto &item : records) {
        recordTable->insertRow(recordTable->rowCount());

        QStringList recordItems({ item.begin.toString("mm:ss.zzz"), item.end.toString("mm:ss.zzz"), item.chord });
        for (int i = 0; i < recordItems.size(); i++) {
            auto twi = new QTableWidgetItem(recordItems[i]);
            twi->setTextAlignment(Qt::AlignHCenter);
            recordTable->setItem(recordTable->rowCount() - 1, i, twi);
        }
    }
    mediaPlayer->play();
}

void MediaWidget::run()
{
    QStringList params;
#ifdef __FILE__
    QDir dir(__FILE__);
    if (dir.cdUp() && dir.cdUp()) {
        QFile script(dir.filePath("main.py"));
        if (script.exists())
            params << script.fileName();
    }
#endif
#ifdef WIN32
    QString python = "python";
    if (params.isEmpty())
        params << ".\\main.py";
#else
    QString python = "python3";
    if (params.isEmpty())
        params << "main.py";
#endif
    auto process = new QProcess(this);
    params << fileUrl.toLocalFile();

    auto slot = [=](int exitCode, QProcess::ExitStatus exitStatus) {
        auto result = QString(process->readAllStandardOutput());
        emit readResult(result);
    };
    connect(process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished), slot);
    process->start(python, params);
}

bool MediaWidget::parse(const QString &result)
{
    auto lines = result.split(QRegExp("[\r\n]"), QString::SkipEmptyParts);
    if (lines.isEmpty())
        return false;

    for (const auto &line : lines) {
        qDebug() << line;
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

int MediaWidget::search(qint64 position)
{
    auto comp = [&](const Record &r) {
        int begin = QTime(0, 0).msecsTo(r.begin);
        int end = QTime(0, 0).msecsTo(r.end);
        return position >= begin && position <= end;
    };
    auto iter = std::find_if(records.begin(), records.end(), comp);
    return iter - records.begin();
}

MediaWidget::~MediaWidget() = default;
