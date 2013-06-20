cd ..
python print_stitch.py  fm/fmout.wav | perl fm/fmmapper.pl fm/map.dump  | csound -L stdin -o devaudio -+rtaudio=jack -dm6 ./fm/fm.orc ./fm/fmlive.sco
