import spotipy

class Feature:

    def __init__(self, sp):
        self.features = []
        self.sp = sp

    def getFeatures(self):
        return self.features

    def addFeatures(self, playlist, target, weight):
        w = weight
        tracks = playlist["tracks"]
        songs = tracks["items"]
        j = 0
        ids = self.getIDs(tracks, songs)
        for i in range(0, len(ids), 50):
            audio_features = self.sp.audio_features(ids[i:i+50])
            for track in audio_features:
                popularity = songs[j]['track']['popularity']
                artistPopularity = self.sp.artist(songs[j]['track']['artists'][0]['id'])['popularity']
                #while w > 0:
                self.features.append(track)
                self.features[-1]['trackPopularity'] = popularity
                self.features[-1]['artistPopularity'] = artistPopularity
                self.features[-1]['target'] = target

                j = j + 1


    def getIDs(self, tracks, songs):
        while tracks['next']:
            tracks = self.sp.next(tracks)
            for item in tracks["items"]:
                songs.append(item)
        ids = []
        for i in range(len(songs)):
            ids.append(songs[i]['track']['id'])
        return ids
