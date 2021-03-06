#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QDebug>
#define printf qDebug
//#define saddr "134.175.99.84"
#define ports 10102
#define saddr "192.168.3.120"
MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_pushButton_4_clicked()
{
    this->dat.resize(4);
    //cmd
    this->dat[2]=0x01;
    this->dat[3]=0x00;
    //data
    int freq;
    freq=ui->spinBox->value()-880;
    printf("%d",freq);
    this->dat[0]=(char)(freq&0xff);
    this->dat[1]=(char)(freq>>8&0xff);
    printf("%d,%d\n",(char)dat[0],(char)dat[1]);
    this->cmd.writeDatagram(dat, QHostAddress(saddr), ports);



}

void MainWindow::on_pushButton_clicked()//RESTART
{
    this->dat.resize(4);
    //cmd
    this->dat[0]=0x00;
    this->dat[1]=0x00;
    this->dat[2]=0x07;
    this->dat[3]=0x00;
    this->cmd.writeDatagram(dat, QHostAddress(saddr), ports);
}

void MainWindow::on_pushButton_2_clicked()//fm
{
    MainWindow::on_pushButton_5_clicked();
    this->dat.resize(4);
    //cmd
    this->dat[0]=0x00;
    this->dat[1]=0x00;
    this->dat[2]=0x03;
    this->dat[3]=0x00;
    this->cmd.writeDatagram(dat, QHostAddress(saddr), ports);

}

void MainWindow::on_pushButton_3_clicked()//fft
{
    MainWindow::on_pushButton_5_clicked();
    this->dat.resize(4);
    //cmd
    this->dat[0]=0x00;
    this->dat[1]=0x00;
    this->dat[2]=0x04;
    this->dat[3]=0x00;
    this->cmd.writeDatagram(dat, QHostAddress(saddr), ports);
}

void MainWindow::on_pushButton_5_clicked()//stop
{
    this->dat.resize(4);
    //cmd
    this->dat[0]=0x00;
    this->dat[1]=0x00;
    this->dat[2]=0x05;
    this->dat[3]=0x00;
    this->cmd.writeDatagram(dat, QHostAddress(saddr), ports);
}

void MainWindow::on_spinBox_valueChanged(int arg1)
{
    this->dat.resize(4);
    //cmd
    this->dat[2]=0x01;
    this->dat[3]=0x00;
    //data
    int freq;
    freq=ui->spinBox->value()-880;
    printf("%d",freq);
    this->dat[0]=(char)(freq&0xff);
    this->dat[1]=(char)(freq>>8&0xff);
    this->cmd.writeDatagram(dat, QHostAddress(saddr), ports);
}


void MainWindow::on_KILL_clicked()
{
    this->dat.resize(4);
    //cmd
    this->dat[0]=0x00;
    this->dat[1]=0x00;
    this->dat[2]=0x06;
    this->dat[3]=0x00;
    this->cmd.writeDatagram(dat, QHostAddress(saddr), ports);
}
