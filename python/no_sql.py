
import serial.tools.list_ports
import wave
#import pyaudio 
import os
import os.path
import codecs
import pandas
import jieba
import socket
import time
import numpy as np

from aip import AipSpeech
from threading import Thread

#cmds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#初始化

APP_ID = '15628658'
API_KEY = 'GAy9qAeG8BB5avZPWzeKzt5Y'
SECRET_KEY = '7B4gXiXLpfnHH4AXBUjiO04nphyEgGBp'

HOST_ADDR=''
DST=(HOST_ADDR,10101)
CMDDST=(HOST_ADDR,10102)

CMDDST=(HOST_ADDR,10102)
CMDDST=(HOST_ADDR,10102)


CMD_STOP=b'\x00\x00\x05\x00'
CMD_FFT=b'\x00\x00\x04\x00'
CMD_DM=b'\x00\x00\x03\x00'

SIG_FFTDATA_END=b'\x00\xba\xdc\xfe'
SIG_PIC_CLOSE=b'\xaa\xbb\xcc\xdd'
SIG_DM_SAVE=b'xxxxxx'


loc=[]
freq_list=np.array([88.5])
current_freq=88.5       #当前频点初始化
scan=0
n = 0
#================清空数据库===================================

#使用cursor()方法创建一个游标对象cursor

with open ("now_freq.txt",'w',encoding = 'utf-8') as now_freq_w:
    now_freq_w.truncate()       #清除now_freq.txt中的当前频点，即初始化为空
#语音识别
def reco(fname,client,c_freq):
    #====================连接数据库==============================

    #使用cursor()方法创建一个游标对象cursor

    #=========================================================
    with open(fname, 'rb') as fp:
        result=client.asr(fp.read(), 'wav', 16000, {'dev_pid': 1537,})
        print(result)
        if result.get('err_no')==0:
                print(result['result'][0])
                with open ("黑广播.txt",'w',encoding = 'utf-8') as hgb_wb:
                    hgb_wb.write(result['result'][0])
                with open ("黑广播.txt",'r',encoding = 'utf-8') as hgb_wb:
                    lines = hgb_wb.readlines()
                lines = ''.join(lines)
                #切割词组，并过滤停用词
                stoplist = codecs.open('stopwords.txt','r',encoding='utf8').readlines()
                stoplist = set(w.strip() for w in stoplist)#读取停用词表
                segment = []
                segs = jieba.cut(lines)
                segs = [word for word in list(segs) if word not in stoplist]
                for seg in segs:
                        segment.append(seg)
                segments = pandas.DataFrame({
                        '词组':segment
                        })
                c = segments.groupby(by = '词组')['词组'].agg(np.size)
                c = c.to_frame()
                c.columns = ['计数']
                c = c.sort_values(by = ["计数"],ascending = False)#对计数次数排序
                segStat = c.reset_index()#还原segStat矩阵索引
                #关键词提取
                f = open('keywords.txt','r',encoding='utf-8-sig')
                liness = f.readlines()#读取文本中全部行
                line_list = []
                for line in liness:
                        line_list.append(line.strip())#line_list为关键词库中关键词的数组集合
                f.close()
                keywords = segStat.iloc[:,0]
                l = len(keywords)
                ciku =[]
                i = 0
                while i<l:
                        if keywords[i] in line_list:
                                ciku.append(str(keywords[i]))
                        i +=1
        else:
                print(result.get('err_msg'))
def fftp():
    global loc
    global freq_list
    ydata = []
    FM_list = [ '88.5','89.7', '93.7', '97.5', '99.7',  '96.6', '102.4', '104.3', '105.8', '101.7', '95.8', '107.5', '98.9', '91.4', '106.9', '102','95.2','103.5','100.5','124.0']
    fts = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #建立一个基于TCP的Socket
    fts.bind((HOST_ADDR,10103))
    fts.listen(2)
    ft=fts.accept()[0]
    #ft.connect((HOST_ADDR,10103))
    print('fft connect successful')
    x=[]
    time1=0
    temp_list=[]
    final_list=np.array([])
    while 1:
        data=ft.recv(4)
        if data==SIG_FFTDATA_END:
            if(len(x)==8192):
                x=np.array(x)
                loc=np.where(x[:4096]>2e7)[0]          #loc为频谱数据x>2e7的位置
                loc=loc/8192*40+88
                loc=np.around(loc,1)
                loc=np.unique(loc)
                for i in range(len(loc)):
                    for j in freq_list:
                        if(abs(loc[i]-j)<0.4):
                            loc[i]=j
                final_list=np.append(final_list,loc)
                time1=time1+1
                if (time1>=20):
                    time1=0
                    temp_list=list(final_list)
                    final_list=np.unique(final_list)
                    for i in final_list:
                        if(temp_list.count(i)>10):
                            freq_list=np.append(freq_list,i)
                    freq_list=np.unique(freq_list)

                    for i in range(len(freq_list)):
                        if str(freq_list[i]) not in FM_list:                                  #判断是否在正常广播集合中

                            keyi_list = np.array([])
                            keyi_list = np.append(keyi_list, freq_list[i])
                            freq_list = np.delete(freq_list, i, axis = 0)
                            freq_list = np.insert(freq_list, 0 , keyi_list)

                ydata = x[0:4096:2]
                ydata = 10*np.log10(ydata)
                try:
                    freqplot_data_write = open("C:\\inetpub\\wwwroot\\Data\\data.txt",'w',encoding='utf-8')
                    for i in range(2048):
                        freqplot_data_write.writelines(str(round(ydata[i],2)))
                        freqplot_data_write.write(',')
                    freqplot_data_write.close()
                except:
                    print('频谱数据写入data.txt文件通道被占用')
            x=[]
        elif data==SIG_PIC_CLOSE:     #图片显示关闭
            #处理掉没处理的数据
            for i in range(1000):
                data=ft.recv(4)
            x=[]
        else:
            x.append(int.from_bytes(data,'little'))
    cur.close()
    db.close()  
def change_freq():
    cmd.send(CMD_STOP)#
    time.sleep(2)
    cmd.send(CMD_FFT)#
    time.sleep(5)
    cmd.send(CMD_STOP)#
    time.sleep(3)
    cmd.send(CMD_DM)#

def fmdm():
    global scan
    global freq_list,now
    global current_freq
    global scan_time
    #网络socket初始化
    sts = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #建立一个基于TCP的Socket
    sts.bind((HOST_ADDR,10101))
    sts.listen(2)
    st=sts.accept()[0]
    #st.connect((HOST_ADDR,10101))
    print('fmdm connect successful')
    count=0
    state=0
    now = 0
    #缓存文件初始化
    rec=wave.open('fm0.wav','wb')
    rec.setnchannels(1)
    rec.setsampwidth(2)
    rec.setframerate(16000)
    #线程字典及初始化
    thd={} 
    tt=0
    for i in range(0,11):
        thd[i]=Thread()
    while 1:
        data=st.recv(6)
        current2_freq = current_freq
        if(data==SIG_DM_SAVE):
            count=0
            rec.close()
            rec=wave.open('fm'+str(state)+'.wav','wb')
            rec.setnchannels(1)
            rec.setsampwidth(2)
            rec.setframerate(16000)
            continue
        dataa=np.array(bytearray(data))
        dataa.dtype='int16'
        datab=dataa[0:len(dataa):3]
        count=count+len(datab)
        #写缓存文件
        rec.writeframes(bytes(datab))
        if(count>160000):
            count=0
            rec.close()
            dem_time=int(scan_time/10-1)
            if (state>=dem_time):
                if(thd[state].isAlive()):
                    thd[state].join()
                thd[state]=Thread(target=reco,args=('fm'+str(state)+'.wav',AipSpeech(APP_ID, API_KEY, SECRET_KEY),current2_freq,))
                thd[state].start()
                 #xiugaide==================================================
                if(1==scan):
                    now += 1
                    with open ("黑广播.txt",'w',encoding = 'utf-8') as hgb_wb:
                        hgb_wb.truncate()
                    if(now>=freq_list.size):
                        now=0
                        for sd in thd:
                            if(thd[sd].isAlive()):
                                thd[sd].join()
                        freq_list=np.array([88.5])                    
                        cg=Thread(target=change_freq,)
                        cg.start()
                        while(cg.isAlive()):
                            data=st.recv(6)
                    cmd.sendto((int(freq_list[now]*10)-880).to_bytes(2,'little')+b'\x01\x00',CMDDST)
                    current_freq=freq_list[now]
                    with open("C:\\inetpub\\wwwroot\\Data\\now_freq.txt",'w',encoding='utf-8') as now_freq_write:
                        now_freq_write.write(str(current_freq))
                    while count<16000:
                        data=st.recv(6)
                        count +=1
                    count=0
                rec=wave.open('fm0.wav','wb')
                rec.setnchannels(1)
                rec.setsampwidth(2)
                rec.setframerate(16000)
                state=0
            else:
                thd[state]=Thread(target=reco,args=('fm'+str(state)+'.wav',AipSpeech(APP_ID, API_KEY, SECRET_KEY),current2_freq,))
                thd[state].start()
                
                if(thd[state+1].isAlive()):
                    thd[state+1].join()
                state += 1
                rec=wave.open('fm'+str(state)+'.wav','wb')
                rec.setnchannels(1)
                rec.setsampwidth(2)
                rec.setframerate(16000)

#========查询数据库scan和 scan_time的值，判断是否执行扫描,及查询扫描时间============
def scan_sql():
    global scan                  #scan扫描指令，1扫描；0停止扫描
    global scan_time        #scan_time为扫描停留时间：0（初始值）;扫描时可选10s:80s:10s
    global current_freq
    scan_time = 0
    while 1:                        #循环查询数据库中 scan 和 scan_time的值

        scan = 98

        scan_time = 30
        lines=''
        try:
            with open("C:\\inetpub\\wwwroot\\Data\\now_freq.txt",'r',encoding='utf-8') as now_freq_read:
                lines=now_freq_read.readlines()
                current_freq=float(lines[0])
        except:
            print('get current_freq fail')


def cmd_loop():
    global cmds
    cmd_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #建立一个基于UDP的Socket
    cmd_in.bind(('',10104))
    cmds = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #建立一个基于UDP的Socket
    cmds.bind(('',10102))
    cmds.listen(2)
    cmd=cmds.accept()[0]
    print('cmd connect successful')
    while 1:
        data,addr=cmd_in.recvfrom(4)
        print(data)
        cmd.send(data)
#=================================================================
cmdid=Thread(target=cmd_loop)
cmdid.start()
fmid=Thread(target=fmdm)
fmid.start()
fftid=Thread(target=fftp)
fftid.start()
scan_sqls = Thread(target=scan_sql)
scan_sqls.start()
fmid.join()
fftid.join()
cmdid.join()
cmd.send(CMD_STOP)