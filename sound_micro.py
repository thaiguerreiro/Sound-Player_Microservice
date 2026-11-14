from flask import Flask,request,jsonify
import winsound
import time

app = Flask(__name__)

#using dictionary to pair sound name with file path
Sounds = {
    'Victory_sound':"WAV files/Victory.wav",
    'Game_over':"WAV files/Game_over.wav",
    'Click':"WAV files/Click.wav",
    'Ding':"WAV files/Ding.wav",
    'Error':"WAV files/Error.wav",
    'Success':"WAV files/Success.wav"
}


#actual microservice is here
@app.route('/sound', methods=['POST'])
def sound():
    Valid_names = list(Sounds.keys())
    sound_request = request.args.get('sound_request')

    if sound_request not in Valid_names:
        return jsonify({'error': 'Invalid sound request!'}), 400
    else:
        sound_file = Sounds[sound_request]
        winsound.PlaySound(sound_file, winsound.SND_FILENAME)
        time.sleep(1)
        return jsonify({'message': f'Sound {sound_request} played successfully!'}), 200