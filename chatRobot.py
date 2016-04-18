# -*- coding: utf-8 -*-
import pyaudio
import wave
import sys
import base64
import urllib2,urllib,json,time
import mp3play
reload(sys)
sys.setdefaultencoding('utf8')

appid='XXXX'
apiKey='XXXX'
securetKey='XXXX'

url='http://vop.baidu.com/server_api'
urlOfToken='https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=pRM4Y0Z32GI3gmOetPg2qChE&client_secret=af97dd5f362e4ff06d006323a7c35318&'

filecount=1000
#获取密钥  这是必须的一步
req=urllib2.Request(urlOfToken)
recv=urllib2.urlopen(req).read()
recvJson=json.loads(recv)
acessToken=recvJson['access_token']
#采样率8000hz  采样位数16位  单声道
#r'y:\\Coding\\python\\blocking.wav'
def getAnswer(filename):
	source=open(filename,'rb').read()
	lenOfSource=len(source)
	content=base64.b64encode(source)
	content=base64.b64encode(source).decode('utf-8')
	formats='wav'
	rate=8000
	channel=1
	cuid='AB:CC:DE:F3:2A:44:51:90'
	token=acessToken
	speech=content
	lens=lenOfSource
	jsonStr={
		'format':formats,
		'rate':rate,
		'channel':channel,
		'cuid':cuid,
		'token':token,
		'speech':content,
		'len':lens
	}
	jsonStr=json.dumps(jsonStr)
	req2=urllib2.Request(url,jsonStr)
	req2.add_header("Content-Type", "application/json")
	resp=urllib2.urlopen(req2).read()

	recvJson2=json.loads(resp)
	if recvJson2['err_msg'] == 'success.':
		words=recvJson2['result'][0]
		print words
		return ('success',words)
	else:
		
		return ('error',recvJson2['err_msg'])

class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile
rec = Recorder(channels=1,rate=8000)

inputStr2='s'

while (inputStr2!=';'):
	inputStr2=raw_input('Press key to continue or end.')
	if(inputStr2==';'):
		break
	print 
	with rec.open('sample.wav', 'wb') as recfile:
		print 'Please say something...'
		recfile.record(duration=4)
	#print '[+]'
	pp=getAnswer('sample.wav')
	if (pp[0]=='success'):
		pass#print pp[1]
	else:
		print 'Can`t recognize...'

	keyTuring='a22493d86308355fc5ee110953a9ecc7'
	paramsTuring={
		'key':keyTuring,
		'info':''
	}
	urlTuring=r'http://www.tuling123.com/openapi/api'
	enterWord=pp[1]
	#time.sleep(1)
	#enterWord='你好'
	#print enterWord
	paramsTuring['info']=enterWord
	params2=urllib.urlencode(paramsTuring)

	target=urllib.urlopen(urlTuring,params2).read()
	decode=json.loads(target)
	print decode['text']

	urlTsn='http://tsn.baidu.com/text2audio'
	
	
	textToSpeak=decode['text']
	jsonStrTsn={
		'tex':textToSpeak,
		'lan':'zh',
		'tok':acessToken,
		'ctp':1,
		'cuid':'AB:CC:DE:F3:2A:44:51:90'
	}
	encodeDataTsn=urllib.urlencode(jsonStrTsn)
	targetTsn=urllib.urlopen(urlTsn,encodeDataTsn).read()
	voicefilename=str(filecount)+'.mp3'
	filecount=filecount+1
	if (len(targetTsn)<100):
		print targetTsn
	try:
		filemp3=open(voicefilename,'wb')
		filemp3.write(targetTsn)
		filemp3.close()
	except:
		time.sleep(1)
		print 'Little error ,try again'
		filemp3=open(voicefilename,'wb')
		filemp3.write(targetTsn)
		filemp3.close()
	#print 'ok'
	replay=mp3play.load(voicefilename)
	replay.play()
	time.sleep(len(textToSpeak)*0.3)
	replay.stop()
	#print 'done'
