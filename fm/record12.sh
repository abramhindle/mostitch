#ffmpeg -f jack -i SuperCollider:out_1  -acodec copy -f x11grab -r 24 -s 1900x1080 -i :0.0 -aspect 16:9 -vcodec libx264 -vpre lossless_ultrafast -threads 8 -y output.mov
rm output.mkv
## ffmpeg -f jack -i SuperCollider:out_1  -acodec vorbis -f x11grab -r 24 -s 1900x1080 -i :0.0 -aspect 16:9 -vcodec libx264 -vpre lossless_ultrafast -threads 8 -y output.mkv
# ffmpeg -f jack -i system:playback_1  -acodec vorbis -f x11grab -r 24 -s 1900x1080 -i :0.0 -aspect 16:9 -vcodec libx264 -vpre lossless_ultrafast -threads 8 -y output.mkv
#mplayer -ao jack output.mkv
(sleep 2; jack_connect csound5:output1 ffmpeg:input_1) &
#(sleep 2; jack_connect csound5:output1 ffmpeg:input_2) &
#ffmpeg -f jack -ac 2 -i ffmpeg -f x11grab -r 30 -s 1920x1080 -i :0.0 -acodec pcm_s16le -vcodec libx264 -vpre lossless_ultrafast -threads 0 -y output.mkv
ffmpeg -f jack -ac 1 -i ffmpeg -f x11grab -r 30 -s 512x360 -i :0.0+0,64 -acodec pcm_s16le -vcodec libx264 -vpre faster -threads 0 -y output.mkv
