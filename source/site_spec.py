"""Illustrative site placement; marketing outline is not a boundary survey."""
import math
ADDRESS='5725 Lakotah Lane, Placerville, CA 95667'
APN='006-480-028-000'
LISTING_URL='https://www.zillow.com/homedetails/5725-Lakotah-Ln-Placerville-CA-95667/195361834_zpid/'
MLS_URL='https://www.metrolistpro.com/homes/2/6/5725-LAKOTAH-LANE-PLACERVILLE-CA-95667/226056226'
OUTLINE_IMAGE='https://photos.zillowstatic.com/fp/bfbafa200d5d39fbcba719e11042d7dd-cc_ft_576.jpg'
# Traced from listing aerial; normalized to advertised 3 acres, NOT cadastral coordinates.
SCALE=.38252079526944477
PIXELS=[(68,401),(403,382),(400,152),(271,24),(248,16),(84,351),(62,352)]
PARCEL=[((x-68)*SCALE,(401-y)*SCALE) for x,y in PIXELS]
ANGLE=math.radians(135)
CENTER=(53,53)
def to_site(p):
    x,y=p[0]-14.5,p[1]-7.9
    return (CENTER[0]+math.cos(ANGLE)*x-math.sin(ANGLE)*y,CENTER[1]+math.sin(ANGLE)*x+math.cos(ANGLE)*y)
DRIVE=[(0,19),(20,22),(41,27),(56,36),(62,42)]
ASSUMPTIONS=[
 'North is interpreted from the listing aerial; verify against a survey.',
 'House location, 135-degree rotation and northeast-facing courtyard are proposed.',
 'Local +Y is treated as uphill. No slope bearing, contour or elevation survey was supplied.',
 'Approach from the Lakotah Lane side is indicative; route, easements and grades are unverified.',
 'Trees in the model indicate woodland character, not an existing-tree inventory.',
 'No utility layout, driveway engineering, setbacks or construction feasibility are established.'
]
