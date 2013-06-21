cd fm
cd ..
cat fm/fmlive.sco > fm/bs.sco
#echo "i 555 0 -1" >> fm/bs.sco
python print_stitch.py --input bs.wav  fm/fmout.wav | perl fm/fmmapper.pl fm/map.dump >> fm/bs.sco
rm bs-fm.wav
csound -dm6 -o fm/bs-fm.wav fm/fm.orc fm/bs.sco


python print_stitch.py --input bs-1.wav  fm/fmout.wav | perl fm/fmmapper.pl fm/map.dump > fm/bs-1.1.sco
python print_stitch.py --input bs-2.wav  fm/fmout.wav | perl fm/fmmapper.pl fm/map.dump > fm/bs-2.1.sco
python print_stitch.py --input bs-3.wav  fm/fmout.wav | perl fm/fmmapper.pl fm/map.dump > fm/bs-3.1.sco

cat fm/fmlive.sco fm/bs-1.1.sco > fm/bs-1.sco
cat fm/fmlive.sco fm/bs-2.1.sco > fm/bs-2.sco
cat fm/fmlive.sco fm/bs-3.1.sco > fm/bs-3.sco

csound -dm6 -o fm/bs-1-fm.wav fm/fm.orc fm/bs-1.sco
csound -dm6 -o fm/bs-2-fm.wav fm/fm.orc fm/bs-2.sco
csound -dm6 -o fm/bs-3-fm.wav fm/fm.orc fm/bs-3.sco

#cat fm/fmlive.sco > fm/bs-all.sco
#echo "i 555 0 -1" >> fm/bs-all.sco
#cat fm/bs-1.sco fm/bs-2.sco fm/bs-3.sco >> fm/bs-all.sco
#csound -dm6 -o fm/bs-all-fm.wav fm/fm.orc fm/bs-all.sco

