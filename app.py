from flask import Flask
from flask import request
from wtforms import SubmitField
from flask_wtf import Form
from flask import flash, render_template, request, redirect
app = Flask(__name__)
import copy
import sys
import numpy as np
from scipy import signal
import scipy.io.wavfile

import sklearn.decomposition
from scipy.io import wavfile
import os
import glob
import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


NAMES = {"a3":"arabic_numbers",
         "a6":"dutch_numbers",
         "a8":"english_numbers",
         "a1":"french_numbers",
         "a4":"hindi_numbers",
         "a7":"japanese_numbers",
         "a9":"russian_numbers",
         "a2":"spanish_numbers",
         "a5":"tamil_numbers"
         }



def getaudio(path):
    fs, data = wavfile.read(path)
    return fs, data

def load_audio(data):
    files = glob.glob('static/Data/Mixed/*')
    for f in files:
        os.remove(f)
    path = 'static/Data/Raw/'
    pathM = 'static/Data/Mixed'
    source_audios = []
    for i in data:
        p = path+i[0]+'.wav'
        audio = getaudio(p)[1]
        audio = audio[:,0]
        audio = (audio)/ float(2**15)
        source_audios.append(audio)
    sources = []
    np.random.seed(41)
    x = np.random.dirichlet(np.ones(len(data)),size=1)
    print (x)
    for i,j in enumerate(source_audios):
        d=0
        for k in range(len(data)):
            d+=source_audios[k]*x[0][-k+i]
        sources.append(d)
        d = np.int16(d*327*80)
        scipy.io.wavfile.write(pathM+'/mixed_{}.wav'.format(i),getaudio(path+data[0][0]+'.wav')[0],d)
        temp_path = pathM+'/mixed_{}.wav'.format(i)
        temp_path_1 = pathM+'/mixed_{}_simple.wav'.format(i)
        os.system("sox {} -b 16 {}".format(temp_path,temp_path_1))
        if(i==0):
            temp_path_1 = pathM+'/mixed_ghanta_simple.wav'
            os.system("sox {} -b 16 {}".format(temp_path,temp_path_1))
    return sources

def Fast_ICA(data,sources):
    files = glob.glob('static/Data/Separated/*')
    for f in files:
        os.remove(f)
    path = 'static/Data/Raw/'
    pathS = 'static/Data/Separated'
    fast_ica  = sklearn.decomposition.FastICA( n_components=len(sources[0]) )
    # separated = fast_ica.fit_transform( sources )
    # # Map the separated result into [-1, 1] range
    # max_source, min_source = 1.0, -1.0
    # max_result, min_result = max(separated.flatten()), min(separated.flatten())
    # separated = 2*((separated - np.ones(separated.shape)*min_result)/(max_result - min_result)) + np.ones(separated.shape)*(-1)

    
    # for i in range(len(sources[0])):
    #     scipy.io.wavfile.write( pathS+'/separated_{}.wav'.format(i), getaudio(path+data[0][0]+'.wav')[0], separated[:, i] )

    ica_result = fast_ica.fit_transform(sources)
    result_signal = []

    for i in range(len(sources[0])):
       result_signal.append(ica_result[:,i])
    result_signal_int = []

    for i in range(len(sources[0])):
       # Convert to int, map the appropriate range, and increase the volume a little bit
       result_signal_int.append(np.int16(result_signal[i]*32767*80))
       wavfile.write(pathS+'/separated_{}.wav'.format(i), getaudio(path+data[0][0]+'.wav')[0], result_signal_int[i])
       temp_path = pathS+'/separated_{}.wav'.format(i)
       temp_path_1 = pathS+'/separated_{}_simple.wav'.format(i)
       os.system("sox {} -b 16 {}".format(temp_path,temp_path_1))

@app.route('/', methods = ["GET", "POST"])
def home_form():
    return render_template("bg_new.html")
data_dic = {}
data = None
@app.route("/process", methods = ["GET", "POST"] )
def process_form():
    global data
    #try:
    #    if request.form['submit_button'] == 'Submit' and len(list(request.values.items()))!=0:
    #        return contact()
    #except:
    #    pass
    try:
        if request.form['separate'] == 'separate' and len(list(request.values.items()))!=0:
            
            return separated()
    except:
        pass
    try:
        if request.form['TryAgain'] == 'BACK' and len(list(request.values.items()))!=0:
            
            return home_form()
    except:
        pass
    formData = request.values if request.method == "GET" else request.values
    data = list(formData.items())
    print("Data", data)

    BOOL = {}
    for i in range(1, 10):
        BOOL[NAMES["a"+str(i)]] = 0
        data_dic[NAMES["a"+str(i)]] =0
    for tup in data:
        # print("this",tup[0])
        BOOL[tup[0]] = 1
        data_dic[tup[0]] = 1
    # print(BOOL)
      
    return render_template("bg_new.html",  bool1 = BOOL["french_numbers"], 
                                            bool2 = BOOL["spanish_numbers"],
                                            bool3 = BOOL["arabic_numbers"],
                                            bool4 = BOOL["hindi_numbers"],
                                            bool5 = BOOL["tamil_numbers"],
                                            bool6 = BOOL["dutch_numbers"],
                                            bool7 = BOOL["japanese_numbers"],
                                            bool8 = BOOL["english_numbers"],
                                            bool9 = BOOL["russian_numbers"], foo = 1)

@app.route('/results', methods=["GET", "POST"])
def contact():
    select = []
    for k in data_dic.keys():
        if data_dic[k] == 1:
            select.append(k)  
    sources = load_audio(data)
    d = sources[0]
    for i in sources[1:]:
        d = np.c_[d,i]
    # sources = np.c_[sources[0],sources[1],sources[2]]
    sources = d
    Fast_ICA(data,sources)
    num_mixed = len(sources[0])
    x = ["a1","a2","a3","a4","a5","a6","a7","a8","a9"]
    for j,i in enumerate(x):
        if(j<num_mixed):
            data_dic[NAMES[i]]=1
        else:
            data_dic[NAMES[i]]=0
    return render_template("bg_mixed.html", bool1 = data_dic[NAMES["a1"]], 
                                        bool2 = data_dic[NAMES["a2"]],
                                        bool3 = data_dic[NAMES["a3"]],
                                        bool4 = data_dic[NAMES["a4"]],
                                        bool5 = data_dic[NAMES["a5"]],
                                        bool6 = data_dic[NAMES["a6"]],
                                        bool7 = data_dic[NAMES["a7"]],
                                        bool8 = data_dic[NAMES["a8"]],
                                        bool9 = data_dic[NAMES["a9"]])

@app.route('/final',  methods=["GET", "POST"])
def separated(): 
    return render_template("bg_separated.html", bool1 = data_dic[NAMES["a1"]], 
                                        bool2 = data_dic[NAMES["a2"]],
                                        bool3 = data_dic[NAMES["a3"]],
                                        bool4 = data_dic[NAMES["a4"]],
                                        bool5 = data_dic[NAMES["a5"]],
                                        bool6 = data_dic[NAMES["a6"]],
                                        bool7 = data_dic[NAMES["a7"]],
                                        bool8 = data_dic[NAMES["a8"]],
                                        bool9 = data_dic[NAMES["a9"]])

@app.route('/startover',  methods=["GET", "POST"])
def FINALE(): 
    return render_template("bg_new.html")
if __name__ == '__main__':
    app.run(debug=True)



