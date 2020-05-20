from obspy.clients.fdsn import Client


# These values are hardcoded from a csv file.
# In general, the depths are 0,50,100,150,200
# for the surface, and the following channels
# 1-4 respectfuly. (e.g. g##0=0, g##1=50,
# g##2=100, g##3=150, g##4=200 methers)
# However, the channels below do not follow
# the standard pattern, and are incorrectly
# set when using obspy fsdn access
def correct_station_depths(stations):

    depth_dict = {}

    depth_dict['G044'] = 185
    depth_dict['G054'] = 180
    depth_dict['G071'] = 30
    depth_dict['G072'] = 80
    depth_dict['G073'] = 130
    depth_dict['G074'] = 180
    depth_dict['G104'] = 197


    for channel_key in depth_dict:
        for s in stations:
            if s.code == channel_key:
                s.channels[0].depth = depth_dict[channel_key]
 
