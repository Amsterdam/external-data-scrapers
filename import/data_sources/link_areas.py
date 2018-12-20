UPDATE_STADSDEEL = """
UPDATE {target_table} tt
SET stadsdeel = s.code
FROM (SELECT * from stadsdeel) as s
WHERE ST_DWithin(s.wkb_geometry, tt.geometrie, 0)
AND stadsdeel IS NULL
AND tt.geometrie IS NOT NULL
"""

UPDATE_BUURT = """
UPDATE {target_table} tt
SET buurt_code = b.vollcode
FROM (SELECT * from buurt_simple) as b
WHERE ST_DWithin(b.wkb_geometry, tt.geometrie, 0)
AND buurt_code is null
AND tt.geometrie IS NOT NULL
"""


def link_areas(session, target_table):
    session.execute(UPDATE_STADSDEEL.format(target_table=target_table))
    session.commit()

    session.execute(UPDATE_BUURT.format(target_table=target_table))
    session.commit()
