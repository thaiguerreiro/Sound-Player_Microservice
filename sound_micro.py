from flask import Flask,request,jsonify
import pygame

VOLUME = 1

pygame.mixer.init()
app = Flask(__name__)

#using dictionary to pair sound name with file path
Sounds = {
    'Victory_sound':"WAV files/Victory_sound.wav",
    'Game_over':"WAV files/Game_over.wav",
    'Click':"WAV files/Click.wav",
    'Ding':"WAV files/Ding.mp3",
    'Error':"WAV files/Error.wav",
    'Success':"WAV files/Success.wav"
}


#actual microservice is here

# Plays sound based on key in Sounds disctonary
@app.route('/playSound/<sound_request>', methods=['GET'])
def playSound(sound_request):
    Valid_names = list(Sounds.keys())
    if sound_request not in Valid_names:
        return jsonify({'error': 'Invalid sound request!'}), 400
    else:
        sound_file = Sounds[sound_request]
        sound = pygame.mixer.Sound(sound_file)

        sound.set_volume(VOLUME)
        sound.play()
        return jsonify({'message': f'Sound {sound_request} at volume {VOLUME} played successfully!'}), 200


# Sets the volume for all future playSound calls
@app.route('/setVolume/<volume>', methods=['POST'])
def setVolume(volume):
    global VOLUME
    try:
        volume = float(volume)
    except ValueError:
        return jsonify({'error': 'Volume must be a number!'}), 400
    if volume < 0:
        return jsonify({'error': 'Volume too low, must be >= 0!'}), 400
    if volume > 1:
         return jsonify({'error': 'Volume too high, must be <= 1!'}), 400
    VOLUME = volume
    return jsonify({'message': f'Volume set to {VOLUME} successfully!'}), 200
    
