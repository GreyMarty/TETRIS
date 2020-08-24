class SoundManager:
    def __init__(self):
        self.playing = None

    def play(self, effect):
        if self.playing == effect:
            self.playing.stop()
        effect.play()
        self.playing = effect
