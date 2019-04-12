import wave
import numpy as np
from scipy.fftpack import fft,ifft
from scipy import signal

input_file='fm3.wav'
output_file='fm31.wav'

rec=wave.open(input_file,'rb')
recs=wave.open(output_file,'wb')

recs.setnchannels(1)
recs.setsampwidth(2)
recs.setframerate(16000)

dataa=rec.readframes(160000)
dataa=np.array(bytearray(dataa))
dataa.dtype='int16'

b, a = signal.butter(8, 2*6000/16000, 'highpass')
filtedData = signal.filtfilt(b, a, dataa)#data为要过滤的信号
datas=filtedData.astype(int)
datas.dtype='int16'
datas=datas[::2]
recs.writeframes(bytes(datas))

recs.close()
