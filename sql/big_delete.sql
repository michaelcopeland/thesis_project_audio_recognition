

fdgfd  #intentional error
# BE SUPER CAREFUL

#dete from songs
#delete from audioextraction.fingerprints where (id > 3540795)
delete from audioextraction.fingerprints where song_name in ('Cans and Small Containers - Processed (Tape) Junk, Metal, Aluminum Cans, Rustle, Long Tail 01.wav',
'MR - Large Metal Air Drum C, Dark Resonance, Creaking, Metal [192 kHz].wav',
'MR - Medium Long Metal Square B, Bright Harsh Squeaking, Tonal Feedback, Ringing [96 kHz].wav',
'MR - Metal Shelf D, Bright Tonal Creak, Harsh, Friction, Crackling [96 kHz].wav',
'MR - Small Metal Box, Bright Creaking, Tonal, Dragging [96 kHz].wav',
'SHARDS [LD Mono] 02 - Impact, Glass, Shatter, Small.wav',
'SHARDS [LD Mono] 16 - Drop, Glass, Small Shards.wav',
'SHARDS [LD Mono] 24 - Trickle, Glass, Metal, Debree.wav',
'SHARDS [MS Stereo] 19 - Drop, Glass, Table, Metal, Debree.wav',
'TAJ - Jas Gripen Repeated Flyover [XY Stereo]-005.wav',
'TAJ - Tank Battle Cannon Fire [XY Stereo]-001.wav',
'TAJ - Tank Battle Machine Guns (7.62 & 50 cal), Walkie Talkie Chatter [XY Stereo].wav',
'TAJ - Tank Driving and Stopping, Revving, Close To Far [MS Stereo].wav',
'Anarchy,motorcycle,FatBoy,100year,straightpipes,tunedengine,parked,far,revdown,throttling,sporadic,cutengine.wav',
'BigBlock,Corvette,1967,exterior,driverpipe,engine,crank,idle,cut,windowsdown,hooddown,gutteral,rumble,soft,alt.wav',
'Gravitas,bridge,stomp,average,arched,wood,metal,lightiron,gully,stream,forest,strong,rattle,hum,XY.wav',
'Gravitas,bridge,stomp,large,arched,wood,metal,heavyiron,deepstream,greenway,strong,resonant,loose,XY.wav',
'Meridian,ASMR,loop,pageturning,book,standardweight,paper,medium,stiff,crispy,peeling,sliding,flip,mono.wav',
'Meridian,ASMR,loop,scratching,matches,wood,flint,flicks,scrapes,snap,ignite,burn,brief,sudden,mono.wav');

delete from audioextraction.songs where song_name in ('Cans and Small Containers - Processed (Tape) Junk, Metal, Aluminum Cans, Rustle, Long Tail 01.wav',
'MR - Large Metal Air Drum C, Dark Resonance, Creaking, Metal [192 kHz].wav',
'MR - Medium Long Metal Square B, Bright Harsh Squeaking, Tonal Feedback, Ringing [96 kHz].wav',
'MR - Metal Shelf D, Bright Tonal Creak, Harsh, Friction, Crackling [96 kHz].wav',
'MR - Small Metal Box, Bright Creaking, Tonal, Dragging [96 kHz].wav',
'SHARDS [LD Mono] 02 - Impact, Glass, Shatter, Small.wav',
'SHARDS [LD Mono] 16 - Drop, Glass, Small Shards.wav',
'SHARDS [LD Mono] 24 - Trickle, Glass, Metal, Debree.wav',
'SHARDS [MS Stereo] 19 - Drop, Glass, Table, Metal, Debree.wav',
'TAJ - Jas Gripen Repeated Flyover [XY Stereo]-005.wav',
'TAJ - Tank Battle Cannon Fire [XY Stereo]-001.wav',
'TAJ - Tank Battle Machine Guns (7.62 & 50 cal), Walkie Talkie Chatter [XY Stereo].wav',
'TAJ - Tank Driving and Stopping, Revving, Close To Far [MS Stereo].wav',
'Anarchy,motorcycle,FatBoy,100year,straightpipes,tunedengine,parked,far,revdown,throttling,sporadic,cutengine.wav',
'BigBlock,Corvette,1967,exterior,driverpipe,engine,crank,idle,cut,windowsdown,hooddown,gutteral,rumble,soft,alt.wav',
'Gravitas,bridge,stomp,average,arched,wood,metal,lightiron,gully,stream,forest,strong,rattle,hum,XY.wav',
'Gravitas,bridge,stomp,large,arched,wood,metal,heavyiron,deepstream,greenway,strong,resonant,loose,XY.wav',
'Meridian,ASMR,loop,pageturning,book,standardweight,paper,medium,stiff,crispy,peeling,sliding,flip,mono.wav',
'Meridian,ASMR,loop,scratching,matches,wood,flint,flicks,scrapes,snap,ignite,burn,brief,sudden,mono.wav');