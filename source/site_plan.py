"""Draw a clearly qualified parcel concept from listing reference and modeled footprint."""
import sys,json,random,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from house_spec import ROOT,FOOTPRINT
from site_spec import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch,Circle
from shapely.geometry import Polygon,Point
random.seed(72)
parcel=Polygon(PARCEL);house=Polygon([to_site(p) for p in FOOTPRINT])
assert parcel.contains(house),'Proposed footprint must fit inside illustrative parcel outline.'
fig=plt.figure(figsize=(16,11),facecolor='#f4f1e8')
ax=fig.add_axes([.035,.13,.62,.76]);ax.set_aspect('equal');ax.set_xlim(-27,157);ax.set_ylim(-12,166);ax.axis('off')
ax.add_patch(Patch(PARCEL,fc='#d9dfc7',ec='#737c56',lw=1.7,ls=(0,(5,3))))
# Concept planting pattern, deliberately schematic.
for i in range(125):
    x=random.uniform(0,130);y=random.uniform(7,147)
    if not parcel.buffer(-5).contains(Point(x,y)) or Point(x,y).distance(house)<9:continue
    ax.add_patch(Circle((x,y),random.uniform(2.3,4),fc='#aab790',ec='#93a479',lw=.35,alpha=.7))
# Highway follows the eastern / northeastern edge in the marketing aerial.
road=[(137,-2),(137,96),(85,151)]
ax.plot(*zip(*road),lw=12,color='#c4c0b4',solid_capstyle='round');ax.plot(*zip(*road),lw=1,color='#faf6e9',ls='--')
ax.text(148,62,'HIGHWAY 49',rotation=90,fontsize=10,color='#66695f',ha='center')
ax.text(101,123,'Woodland context',rotation=-43,fontsize=8,color='#566845')
ax.plot([-23,-8,0],[3,15,19],lw=8,color='#c4c0b4',solid_capstyle='round')
ax.text(-24,-2,'LAKOTAH LANE SIDE',fontsize=8,color='#66695f')
ax.plot(*zip(*DRIVE),color='#9b8360',lw=4,ls=(0,(3,2)),solid_capstyle='round')
ax.annotate('Proposed approach\nroute / grade unverified',xy=(31,25),xytext=(8,2),fontsize=8,color='#705d43',arrowprops=dict(arrowstyle='-',lw=.8,color='#9b8360'))
terrace=[to_site(p) for p in [(8,-2),(30,-2),(30,1),(20.5,1),(20.5,8),(8,8)]]
ax.add_patch(Patch(terrace,fc='#d7b98d',ec='#b0956f',lw=.8))
ax.add_patch(Patch(list(house.exterior.coords),fc='#71664e',ec='#403f32',lw=1.2))
court=to_site((14.5,3));ax.annotate('COURTYARD\nproposed NE outlook',xy=court,xytext=(91,42),fontsize=8,ha='center',color='#795c39',arrowprops=dict(arrowstyle='-',lw=.8,color='#795c39'))
ax.annotate('Single-level house\n3,503 sq ft',xy=to_site((13,12)),xytext=(20,79),fontsize=9,color='#3c4738',arrowprops=dict(arrowstyle='-',lw=.8,color='#3c4738'))
ax.annotate('Illustrative downslope\ndirection',xy=(95,94),xytext=(68,77),ha='center',fontsize=8,color='#657957',arrowprops=dict(arrowstyle='->',lw=1.1,color='#657957'))
ax.text(38,115,'OAK WOODLAND',fontsize=10,color='#566845',rotation=62)
ax.annotate('N*',xy=(-13,150),xytext=(-13,136),ha='center',fontsize=11,color='#3f5a4a',arrowprops=dict(arrowstyle='-|>',lw=1.2,color='#3f5a4a'))
ax.plot([0,30],[158,158],color='#3f5a4a',lw=2);ax.plot([0,0],[156.5,159.5],color='#3f5a4a');ax.plot([30,30],[156.5,159.5],color='#3f5a4a')
ax.text(15,161,'30 m · approximate',ha='center',fontsize=8,color='#3f5a4a')
fig.text(.055,.945,'LAKOTAH HOUSE',fontsize=26,color='#343d36',weight='light')
fig.text(.055,.911,'SCHEMATIC SITE STUDY  /  SIERRA FOOTHILLS',fontsize=10,color='#826b4a')
fig.text(.69,.88,'5725 LAKOTAH LANE',fontsize=15,color='#343d36')
fig.text(.69,.85,'Placerville, California',fontsize=11,color='#737263')
blocks=[('LISTING BASIS','3 acres · APN 006-480-028-000\nDownslope parcel with oak woodland\nLakotah Lane and Highway 49 context\nNo utilities listed'),('DESIGN RESPONSE','Low roof planes and deep overhangs\nStone plinth beneath one living level\nThree bedrooms, three baths and office\nGlazed courtyard with reflecting pool\nWalnut kitchen and long island'),('PROPOSED, NOT VERIFIED','House position and orientation\nApproach route and tree locations\nTerrain shape and grading\nNo surveyed contours or setbacks'),('OUTLINE METHOD','Marketing aerial traced and scaled to\nthe advertised 3-acre area. Boundary\nshape and north arrow are approximate.\nThis is not a cadastral or grading plan.')]
y=.79
for title,body in blocks:
    fig.text(.69,y,title,fontsize=10,color='#816a48',weight='medium')
    fig.text(.69,y-.035,body,fontsize=10,color='#4b5546',va='top',linespacing=1.6)
    y-=.175
fig.text(.055,.075,'Concept placement only. Survey, access rights, utilities, geotechnical conditions and local requirements remain unverified.',fontsize=9,color='#6c715f')
fig.text(.055,.043,'Source: owner-supplied Zillow listing / MetroList MLS 226056226. Reference links and assumptions are included in START_HERE.md.',fontsize=8,color='#838577')
for suffix in ['png','svg']:fig.savefig(ROOT/'drawings'/('LAKOTAH_site_study.'+suffix),dpi=170,facecolor=fig.get_facecolor())
(ROOT/'checks'/'site_checks.json').write_text(json.dumps({'address':ADDRESS,'apn':APN,'illustrative_parcel_area_m2':parcel.area,'footprint_inside_illustrative_outline':parcel.contains(house),'survey_verified':False,'assumptions':ASSUMPTIONS,'sources':[LISTING_URL,MLS_URL,OUTLINE_IMAGE]},indent=2))
print('Schematic site plan exported; proposed footprint lies within approximate outline.')
