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
import json
import os
import tkinter.filedialog as tkFileDialog
import tkinter as Tkinter
from tkinter import ttk
from urllib.request import urlopen
from datetime import datetime as dt

from eyed3.id3.frames import ImageFrame
from eyed3.mp3 import Mp3AudioFile
from gmusicapi import Mobileclient
import shared


def filename_template(track):
    """
    Formats template for naming a downloaded file
    :param track: dict containing track info
    :return: filename string
    """
    if 'trackNumber' in track:
        date_or_tracknumber = str(track['trackNumber'])
    else:
        date_or_tracknumber = dt.fromtimestamp(int(track['publicationTimestampMillis'])/1000).strftime('%Y_%m_%d')
    track_title = track['title'].replace('/', '_').replace('=', '_')
    track_album = track['album'].replace('/', '_').replace('=', '_')
    track_artist = track['artist'].replace('/', '_').replace('=', '_')

    return date_or_tracknumber + "-" + track_title + "-" + track_album + "-" + track_artist + ".mp3"


def get_image_tuple_from_url(url):
    """
    Gets an album or artist image from the given url.
    :param url: URL of the album/artist image
    :return: tuple containing mime-type and image data
    """
    response = urlopen(url)
    #print(response.getheaders())
    mime_type = response.getheader('Content-Type')
    image_bytes = response.read()
    return mime_type, image_bytes


def download_track(track, path='', mobile_client=None, device_id=None):
    """
    Downloads the mp3 file of the given track
    :param track: Track dict
    :param path: Path to download to. If omitted, then will download to current working directory.
    :return: None
    """
    if 'id' in track:
        track_id = track['id']
    elif 'storeId' in track:
        track_id = track['storeId']
    elif 'episodeId' in track:
        track_id = track['episodeId']
    else:
        print('Problem with track info...')
        print(track)
        return
    try:
        if 'episodeId' in track:
            stream_url = mobile_client.get_podcast_episode_stream_url(track_id, device_id)
        else:
            stream_url = mobile_client.get_stream_url(track_id, device_id)
        song_bytes = urlopen(stream_url).read()
    except Exception as e:
        print("Error retrieving track: " + track['title'])
        print("Error: ", e)
        return

    output_file = open(os.path.join(path, filename_template(track)), "wb")
    output_file.write(song_bytes)
    output_file.close()
    id3 = Mp3AudioFile(output_file.name)
    id3.initTag()
    id3.tag.title = track['title']
    id3.tag.artist = track['artist']
    id3.tag.album = track['album']
    id3.tag.album_artist = track['albumArtist']
    if 'genre' in track:
        genre = track['genre']
    else:
        genre = u'Podcast'
    id3.tag.genre = genre
    if 'year' in track:
        year_int = int(track['year'])
    else:
        year_int = 0
    if year_int != 0:
        id3.tag.release_date = year_int
        id3.tag.original_release_date = year_int
        id3.tag.recording_date = year_int
    if 'trackNumber' in track:
        track_number = track['trackNumber']
    else:
        track_number = 0
    id3.tag.track_num = track_number
    if 'discNumber' in track:
        disc_number = track['discNumber']
    else:
        disc_number = 1
    id3.tag.disc_num = disc_number
    if 'albumArtRef' in track:
        art_url = track['albumArtRef'][0]['url']
    elif 'artistArtRef' in track:
        art_url = track['artistArtRef'][0]['url']
    elif 'art' in track:
        art_url = track['art'][0]['url']
    else:
        art_url = None
    if art_url:
        mime_type, image_data = get_image_tuple_from_url(art_url)
        id3.tag.images.set(ImageFrame.FRONT_COVER, image_data, mime_type)

    id3.tag.save()


class MainWindow(shared.Centerable, Tkinter.Tk):
    """
    Main GUI window for the application.
    """
    #def __init__(self, parent, mobile_client):
    def __init__(self, parent=None):
        """
        MainWindow __init__ function
        :param parent: Tk parent. Fine to be None.
        :return: None
        """
        Tkinter.Tk.__init__(self)
        self.parent = parent
        self.resizable(0, 0)
        #self.mobile_client = mobile_client
        self.device_id = None
        self.library = mobile_client.get_all_songs()

        # Initializes the gui widgets. Should only be called from the __init__function.
        self.grid()

        # Set up widgets
        tracklist_frame = Tkinter.Frame(self)
        tracklist_scrollbar = Tkinter.Scrollbar(self)
        self.tree = tree = ttk.Treeview(self, height=30, yscrollcommand=tracklist_scrollbar.set)
        tree.column("#0", width=750)
        tracklist_scrollbar.config(command=tree.yview)
        download_button = Tkinter.Button(self, text="Download", state="normal", command=self.on_download_press)

        # place widgets on grid
        tracklist_frame.grid(column=0, row=0, rowspan=1, sticky='NS')
        self.tree.grid(in_=tracklist_frame, column=0, row=0, sticky='NS')
        tracklist_scrollbar.grid(in_=tracklist_frame, column=1, row=0, sticky='NS')
        download_button.grid(column=0, row=1, sticky='EW')

        self.fill_tree(self.library)
        self.center()
        splash.master.destroy()
        #self.device_chooser = shared.ChooseDevice(self, mobile_client)

    def fill_tree(self, tracks):
        """

        """
        tracks.sort(key=lambda trk: trk['title'])
        tracks.sort(key=lambda trk: trk['trackNumber'])
        tracks.sort(key=lambda trk: trk['discNumber'])
        tracks.sort(key=lambda trk: trk['album'])
        tracks.sort(key=lambda trk: trk['albumArtist'])
        #print(tracks[0])
        for track in tracks:
            #print(track['title'])
            if track['albumArtist'] == '':
                artist_label = ''
            else:
                artist_label = 'ar:$:' + track['albumArtist'].strip()

            if track['album'] == '':
                album_label = ''
            else:
                album_label = 'al:$:' + track['album'].strip()

            try:
                if artist_label != '':
                    self.tree.insert('', 'end', artist_label, text='Artist: ' + track['albumArtist'],
                                     values=('artist:' + track['albumArtist'],))
            except Tkinter.TclError:
                pass
            try:
                if album_label != '':
                    self.tree.insert(artist_label, 'end', album_label + artist_label, text='Album: ' + track['album'],
                                     values=('album:' + track['album'],))
            except Tkinter.TclError:
                pass
            self.tree.insert(album_label + artist_label, 'end', track['title'] + track['id'], text=track['title'],
                             values=(json.dumps(track),))


    def on_download_press(self):
        """
        Callback for pressing the download button. This will create a folder
        structure and download tracks based on what is selected in the tree.
        :return: None
        """
        #if self.device_id is None:
        #    shared.ChooseDevice(self, mobile_client)
        #    # print(self.device_id)
        #    return
        base_dir = tkFileDialog.askdirectory(master=self)
        if not base_dir:
            return
        steps_number = self.count_steps()
        progress = ProgressWindow(self, 0, steps_number)
        progress.set_message('Downloading...')
        progress.center()
        for selected_item in self.tree.selection():
            values = self.tree.item(selected_item)['values']
            data = values[0]
            if data.startswith('artist:'):
                progress.steps_complete(1)
                artist_name = data.split(':', 1)[1].replace('/', '_').replace('=', '_')
                progress.set_message('Retreiving: ' + artist_name)
                albums = self.tree.get_children(selected_item)
                for album in albums:
                    album_item = self.tree.item(album)
                    #print(album_item)
                    album_name = album_item['values'][0].split(':', 1)[1].replace('/', '_').replace('=', '_')
                    progress.set_message('Retrieving: ' + album_name)
                    try:
                        os.makedirs(os.path.join(base_dir, artist_name, album_name))
                    except OSError:
                        print("Directory already exists. Skipping directory creation.\n" + album_name)
                    progress.steps_complete(1)
                    tracks = self.tree.get_children(album)
                    for track_child in tracks:
                        track_item = self.tree.item(track_child)
                        track_data = track_item['values'][0]
                        track = json.loads(track_data)
                        progress.set_message('Retrieving: ' + track['title'])
                        download_track(track, os.path.join(base_dir, artist_name, album_name),
                                       mobile_client=mobile_client, device_id=self.device_id)
                        progress.steps_complete(1)
            elif data.startswith('album:'):
                progress.steps_complete(1)
                album_name = data.split(':', 1)[1].replace('/', '_').replace('=', '_')
                progress.set_message('Retreiving: ' + album_name)
                try:
                    os.makedirs(os.path.join(base_dir, album_name))
                except OSError:
                    print("Directory already exists. Skipping directory creation.\n" + album_name)
                progress.steps_complete(1)
                tracks = self.tree.get_children(selected_item)
                for track_child in tracks:
                    track_item = self.tree.item(track_child)
                    track_data = track_item['values'][0]
                    track = json.loads(track_data)
                    progress.set_message('Retreiving: ' + track['title'])
                    #self.download_track(track, os.path.join(base_dir, album_name))
                    download_track(track, os.path.join(base_dir, album_name), mobile_client=mobile_client,
                                   device_id=self.device_id)
                    progress.steps_complete(1)
            else:
                track = json.loads(data)
                #print track['title']
                progress.set_message('Retreiving: ' + track['title'])
                #self.download_track(track, base_dir)
                download_track(track, base_dir, mobile_client=mobile_client, device_id=self.device_id)
                progress.steps_complete(1)
        progress.destroy()

    def count_steps(self):
        """

        """
        count = 0
        selection = self.tree.selection()
        for selected_item in selection:
            count += 1
            for child in self.tree.get_children(selected_item):
                count += 1
                for grandchild in self.tree.get_children(child):
                    count += 1
        return count


class ProgressWindow(Tkinter.Toplevel):
    """
    Progress window for downloading.
    """
    def __init__(self, parent, minimum, maximum):
        Tkinter.Toplevel.__init__(self, parent) 
        self.parent = parent
        self.overrideredirect(1)
        self.message = Tkinter.Label(self)
        self.message.pack()

        self.bar = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.bar['value'] = minimum
        self.bar['maximum'] = maximum
        self.bar.pack(padx=10, pady=10)

        #self.grab_set()

    def center(self):
        self.update_idletasks()
        parent_x, parent_y = (int(_) for _ in self.parent.geometry().split('+', 1)[1].split('+'))
        parent_w, parent_h = (int(_) for _ in self.parent.geometry().split('+', 1)[0].split('x'))
        w, h = (int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = parent_x + parent_w/2 - w/2
        y = parent_y + parent_h/2 - h/2
        self.geometry("+%d+%d" % (x, y))

    def steps_complete(self, number_of_steps):
        self.bar['value'] += number_of_steps
        self.parent.update_idletasks()
        self.update_idletasks()
        #print(self.bar['value'])

    def set_message(self, message_text):
        self.message.config(text=message_text)
        self.update_idletasks()


if __name__ == "__main__":
    #mobile_client = Mobileclient(debug_logging=True)
    mobile_client = Mobileclient(debug_logging=False)
    if not mobile_client.oauth_login(Mobileclient.FROM_MAC_ADDRESS):
        mobile_client.perform_oauth(open_browser=True)
        mobile_client.oauth_login(Mobileclient.FROM_MAC_ADDRESS)

    splash = shared.Splash('GMusicDownloader\nis loading...')
    app = MainWindow()
    app.title('GMusic Downloader')
    app.mainloop()
