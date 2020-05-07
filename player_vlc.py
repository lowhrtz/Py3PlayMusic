# PyPlayMusic
# Copyright (C) 2020 Giancarlo DiMino
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import vlc


class Player(object):
    def __init__(self):
        self.media_player = vlc.MediaPlayer()

    def load_url(self, url):
        self.media_player.set_mrl(url)

    def play(self):
        if self.media_player.play() == -1:
            return False
        return True

    def is_playing(self):
        state = self.media_player.get_state()
        #print state
        if state == vlc.State.Playing\
                or state == vlc.State.Opening\
                or state == vlc.State.Paused:
            return True
        return False

    def stop(self):
        self.media_player.stop()
        return True

    def pause(self):
        self.media_player.pause()
        return True

    def unpause(self):
        return self.pause()

    def get_duration(self):
        return self.media_player.get_length()

    def get_position(self):
        return self.media_player.get_time()

    def set_position(self, position):
        self.media_player.set_time(int(position))
        state = self.media_player.get_state()
        #print state
        if state == vlc.State.Ended\
                or state == vlc.State.Stopped\
                or state == vlc.State.Error:
            return False
        return True
