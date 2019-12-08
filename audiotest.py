import simpleaudio as sa
import wave
a3 = wave.open("sound/A3.wav")
c4 = wave.open("sound/C4.wav")
wave_a3 = sa.WaveObject.from_wave_read(a3)
wave_c4 = sa.WaveObject.from_wave_read(c4)
play_a3 = wave_a3.play()
play_c4 = wave_c4.play()
play_c4.wait_done()
#play_c42 = wave_c4.play()
#play_c42.wait_done()
