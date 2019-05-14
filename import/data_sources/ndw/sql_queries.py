# flake8: noqa

INSERT_TRAVELTIME = """
INSERT INTO importer_traveltime (
measurement_site_reference,
computational_method,
number_of_incomplete_input,
number_of_input_values_used,
standard_deviation,
supplier_calculated_data_quality,
duration,
data_error,
measurement_time,
geometrie,
length,
road_type,
stadsdeel,
buurt_code,
scraped_at
)
VALUES {}
"""

INSERT_TRAFFICSPEED = """
INSERT INTO importer_trafficspeed (
measurement_site_reference,
measurement_time,
type,
index,
data_error,
scraped_at,
flow,
speed,
number_of_input_values_used,
standard_deviation,
geometrie,
stadsdeel,
buurt_code
)
VALUES {}
"""

SELECT_STADSDEEL_28992 = "select code, ST_Transform(wkb_geometry, 28992) FROM stadsdeel"
SELECT_BUURT_CODE_28992 = "select code, ST_Transform(wkb_geometry, 28992) FROM buurt_simple"
SELECT_STADSDEEL_4326 = "select code, ST_Transform(wkb_geometry, 4326) FROM stadsdeel"
SELECT_BUURT_CODE_4326 = "select code, ST_Transform(wkb_geometry, 4326) FROM buurt_simple"


LATEST_TRAVELTIME_WITH_SPEED = """
create view latest_traveltime_with_speed as
select id, measurement_site_reference, length, duration, measurement_time, scraped_at, geometrie, road_type, stadsdeel, buurt_code, (length/duration)*3.6 as velocity
from
    importer_traveltime
where
    data_error=false
    and duration >=0
    and scraped_at = (select scraped_at from importer_traveltime order by scraped_at desc limit 1)
    and ("measurement_site_reference" ilike 'GAD03_%_' and "measurement_site_reference" not ilike '%MOA%'and "measurement_site_reference" not ilike '%GAD03_S%'
    or measurement_site_reference in ('RWS01_MONIBAS_0101hrr0032ra0', 'GAD03_MOA_Route102', 'RWS01_MONIBAS_0011hrl0106ra1', 'RWS01_MONIBAS_0021hrr0359ra0', 'RWS01_MONIBAS_0101hrr0312ra0', 'GAD03_MOA_Route109', 'RWS01_MONIBAS_0100vwn0300ra0', 'RWS01_MONIBAS_0021hrl0333ra0', 'RWS01_MONIBAS_0021hrr0348ra0', 'ABM01_ZA_krLeijenb-Boele_krEblvrd-Boele', 'RWS01_MONIBAS_0091hrr0296ra0', 'RWS01_MONIBAS_0091hrl0274ra0', 'RWS01_MONIBAS_0091hrl0103ra0', 'RWS01_MONIBAS_0021hrr0369ra0', 'ABM01_S106_LiafrS106_krS106-S108', 'RWS01_MONIBAS_0021hrr0313ra0', 'RWS09_051', 'RWS01_MONIBAS_0041hrl0011ra0', 'RWS01_MONIBAS_0090vwr0212ra0', 'RWS01_MONIBAS_0021hrr0335ra0', 'RWS01_MONIBAS_0091hrr0324ra0', 'RWS01_MONIBAS_0101hrl0147ra0', 'RWS01_MONIBAS_0101hrr0127ra0', 'RWS01_MONIBAS_0091hrl0320rb0', 'RWS01_MONIBAS_0101hrl0135ra0', 'ABM01_AV_N522_S109_A9Li', 'RWS09_136', 'RWS01_MONIBAS_0021hrr0323ra0', 'RWS09_134', 'PNH03_N522L_11.68-11.57', 'RWS09_135', 'RWS01_MONIBAS_0020vwn0348ra0', 'RWS01_MONIBAS_0100vwp0294ra0', 'RWS01_MONIBAS_0091hrr0084ra0', 'RWS09_065', 'RWS01_MONIBAS_0101hrl0239ra0', 'RWS01_MONIBAS_0091hrl0079ra0', 'RWS01_MONIBAS_0011hrr0046ra0', 'RWS01_MONIBAS_0011hrr0080ra0', 'RWS01_MONIBAS_0021hrl0363rb0', 'ABM01_S103_toeA10Li_LitoeS103', 'RWS01_MONIBAS_0091hrl0332ra0', 'ABM01_AV_N522_S109_oost_S109_west', 'RWS01_MONIBAS_0011hrr0070ra0', 'RWS01_MONIBAS_0021hrl0363ra0', 'RWS01_MONIBAS_0101hrr0144ra0', 'RWS01_MONIBAS_0101hrl0074ra0', 'RWS09_141', 'RWS01_MONIBAS_0101hrr0330ra0', 'RWS01_MONIBAS_0101hrl0109ra0', 'ABM01_S109_krAmstelv-Nijerodew_krBuitenv-Nijerodew', 'ABM01__A10_LiafrS112_S112NZ_ZO', 'RWS09_035', 'RWS09_036', 'RWS09_033', 'RWS09_034', 'RWS01_MONIBAS_0101hrr0317ra0', 'RWS09_031', 'RWS01_MONIBAS_0101hrl0050ra0', 'RWS01_MONIBAS_0091hrl0281ra0', 'RWS01_MONIBAS_0101hrl0247ra0', 'RWS01_MONIBAS_0101hrr0305ra0', 'RWS01_MONIBAS_0101hrl0271ra0', 'RWS01_MONIBAS_0091hrl0213ra0', 'RWS01_MONIBAS_0011hrl0101ra0', 'RWS01_MONIBAS_0091hrr0047ra0', 'RWS01_MONIBAS_0101hrl0062ra0', 'RWS01_MONIBAS_0091hrl0062ra1', 'RWS01_MONIBAS_0091hrl0062ra0', 'RWS01_MONIBAS_0051hrr0121ra0', 'RWS01_MONIBAS_0091hrl0329ra0', 'RWS01_MONIBAS_0091hrl0307ra0', 'RWS01_MONIBAS_0021hrr0326ra0', 'RWS01_MONIBAS_0091hrl0098ra0', 'RWS01_MONIBAS_0091hrr0114ra0', 'RWS01_MONIBAS_0011hrr0061ra0', 'ABM01_S109_krBuitenv-Nijerodew_K-burgZN', 'RWS01_MONIBAS_0021hrl0348ra0', 'RWS01_MONIBAS_0091hrr0320ra0', 'RWS01_MONIBAS_0011hrr0095ra0', 'RWS01_MONIBAS_0010vwn0106ra0', 'RWS01_MONIBAS_0051hrr0157ra0', 'PNH03_N522R_11.68-12.53', 'RWS01_MONIBAS_0101hrl0140ra0', 'RWS09_049', 'RWS01_MONIBAS_0011hrr0086ra0', 'RWS01_MONIBAS_0100vwp0312ra0', 'RWS01_MONIBAS_0091hrr0332ra0', 'RWS01_MONIBAS_0091hrl0052ra0', 'RWS01_MONIBAS_0091hrr0307ra0', 'LRA01_RWS_A10Re31.9b_A10Re32.1b', 'RWS01_MONIBAS_0011hrr0075ra0', 'LRA01_RWS_A10Li7.4_A10Li7.0c', 'RWS01_MONIBAS_0021hrl0336ra0', 'RWS09_127', 'RWS01_MONIBAS_0020vwn0352ra0', 'RWS09_126', 'RWS01_MONIBAS_0021hrl0379ra0', 'RWS01_MONIBAS_0091hrr0312ra0', 'RWS01_MONIBAS_0091hrl0089ra0', 'RWS01_MONIBAS_0101hrl0160ra0', 'RWS01_MONIBAS_0011hrl0070ra0', 'RWS09_121', 'RWS01_MONIBAS_0100vwp0290ra0', 'ABM01_afrit_A10re_S103', 'RWS09_122', 'RWS09_120', 'RWS01_MONIBAS_0101hrl0304ra0', 'RWS01_MONIBAS_0011hrr0099ra0', 'RWS01_MONIBAS_0011hrl0080ra0', 'PNH03_N522L_11.35-11.00', 'RWS01_MONIBAS_0011hrl0057ra0', 'RWS01_MONIBAS_0021hrr0375ra0', 'RWS01_MONIBAS_0041hrr0023ra0', 'LRA01_RWS_A10Li2.0_A10Li1.8c', 'RWS01_MONIBAS_0021hrl0355ra0', 'RWS01_MONIBAS_0091hrl0066ra0', 'RWS04_BHD_30', 'RWS01_MONIBAS_0101hrl0181ra0', 'RWS09_178', 'RWS04_BHD_31', 'RWS01_MONIBAS_0101hrl0056ra0', 'RWS01_MONIBAS_0101hrr0290ra0', 'RWS01_MONIBAS_0100vwp0285ra0', 'RWS04_BHD_33', 'ABM01_S102_Toerit_A10re', 'RWS01_MONIBAS_0101hrl0261ra0', 'RWS01_MONIBAS_0101hrl0225ra1', 'RWS01_MONIBAS_0011hrl0037ra0', 'PNH03_N236L_6.01-5.29', 'RWS01_MONIBAS_0100vwt0113ra0', 'RWS01_MONIBAS_0101hrr0209ra1', 'RWS01_MONIBAS_0051hrl0167ra0', 'ABM01_A9_ReafrS108_Stadshart', 'RWS01_MONIBAS_0100vws0322ra0', 'PNH03_N522L_10.37-10.12', 'RWS01_MONIBAS_0091hrl0056rb0', 'ABM01_AV_B.Rijnderslaan_S109_S108', 'ABM01_S106_pc1065_S106WO', 'RWS01_MONIBAS_0101hrl0297ra0', 'RWS01_MONIBAS_0011hrl0047ra0', 'ABM01_S103_A10re_Kimpoweg', 'RWS01_MONIBAS_0101hrl0212ra0', 'RWS01_MONIBAS_0101hrl0170ra0', 'RWS01_MONIBAS_0051hrr0105ra0', 'RWS01_MONIBAS_0101hrr0244ra0', 'RWS01_MONIBAS_0091hrr0266ra0', 'RWS01_MONIBAS_0091hrl0285ra0', 'RWS09_154', 'GAD03_MOA_Route131_R', 'RWS09_155', 'PNH03_N522R_11.35-11.57', 'RWS01_MONIBAS_0101hrr0281ra0', 'RWS01_MONIBAS_0101hrl0120ra0', 'RWS09_152', 'RWS01_MONIBAS_0051hrr0129ra0', 'RWS09_153', 'RWS01_MONIBAS_0100vwp0298ra0', 'RWS01_MONIBAS_0101hrl0281ra0', 'RWS09_151', 'RWS01_MONIBAS_0020vwf0352ra0', 'RWS01_MONIBAS_0091hrl0261ra0', 'RWS01_MONIBAS_0091hrr0291ra0', 'RWS01_MONIBAS_0101hrr0271ra1', 'RWS01_MONIBAS_0101hrl0293ra0', 'RWS01_MONIBAS_0091hrl0291ra0', 'RWS01_MONIBAS_0051hrr0116ra0', 'RWS09_165', 'RWS01_MONIBAS_0040vwh0003ra0', 'RWS09_166', 'RWS09_164', 'RWS01_MONIBAS_0101hrr0258ra0', 'RWS01_MONIBAS_0021hrl0328ra0', 'RWS01_MONIBAS_0021hrr0340ra0', 'LRA01_RWS_A10Re32.1b_A10Re32.5', 'RWS01_MONIBAS_0101hrl0144ra0', 'RWS01_MONIBAS_0021hrr0340ra1', 'RWS01_MONIBAS_0041hrl0030ra0', 'LRA01_RWS_A10Li4.8_A10Li4.2c', 'RWS01_MONIBAS_0101hrl0308ra0', 'RWS01_MONIBAS_0051hrl0143ra0', 'ABM01_AV_N522_A9Li_S109', 'RWS01_MONIBAS_0051hrr0110ra0', 'RWS01_MONIBAS_0091hrr0068ra0', 'RWS01_MONIBAS_0101hrr0261ra0', 'RWS01_MONIBAS_0080vwf0016ra0', 'RWS01_MONIBAS_0081hrl0021rb0', 'ABM01_AV_N522_A9Re_S109', 'RWS01_MONIBAS_0100vwn0297ra0', 'RWS01_MONIBAS_0041hrl0040ra0', 'RWS01_MONIBAS_0080vwf0016ra1', 'PNH03_N236R_5.29-6.01', 'RWS04_BHD_27', 'RWS01_MONIBAS_0091hrl0224ra0', 'RWS01_MONIBAS_0101hrr0285ra0', 'RWS01_MONIBAS_0020vwf0309ra0', 'RWS01_MONIBAS_0100vwt0119ra0', 'RWS01_MONIBAS_0020vwh0314ra1', 'ABM01_AV_Rembrandtweg_S108_S109', 'RWS01_MONIBAS_0020vwh0314ra0', 'RWS01_MONIBAS_0091hrl0106ra0', 'RWS01_MONIBAS_0091hrr0044ra0', 'RWS01_MONIBAS_0100vwp0281ra0', 'RWS01_MONIBAS_0091hrr0056ra0', 'RWS01_MONIBAS_0091hrl0256ra0', 'RWS01_MONIBAS_0081hrl0021ra0', 'RWS01_MONIBAS_0041hrl0027ra0', 'PNH03_N236L_6.85-6.01', 'RWS01_MONIBAS_0051hrl0116ra0', 'RWS01_MONIBAS_0021hrl0322ra0', 'RWS01_MONIBAS_0021hrl0322ra1', 'RWS01_MONIBAS_0041hrl0036ra0', 'RWS01_MONIBAS_0041hrl0024ra0', 'RWS01_MONIBAS_0010vwf0047ra0', 'RWS01_MONIBAS_0041hrl0015ra0', 'RWS01_MONIBAS_0091hrl0266ra0', 'RWS01_MONIBAS_0041hrl0004ra0', 'RWS01_MONIBAS_0100vwn0293ra0', 'RWS01_MONIBAS_0101hrl0080ra0', 'RWS01_MONIBAS_0100vws0166ra0', 'RWS01_MONIBAS_0081hrr0013ra0', 'RWS01_MONIBAS_0101hrr0149ra0', 'RWS01_MONIBAS_0021hrr0352ra0', 'RWS01_MONIBAS_0091hrr0119ra0', 'RWS01_MONIBAS_0090vwr0215ra0', 'RWS01_MONIBAS_0090vwr0215ra1', 'RWS01_MONIBAS_0101hrl0067ra0', 'RWS01_MONIBAS_0101hrl0257ra0', 'RWS01_MONIBAS_0091hrl0324ra1', 'RWS01_MONIBAS_0101hrr0113ra0', 'RWS09_103', 'RWS01_MONIBAS_0101hrr0163ra0', 'ABM01_AV_N522_A9Li_A9Re', 'RWS09_104', 'RWS01_MONIBAS_0051hrr0140ra0', 'RWS01_MONIBAS_0101hrr0103ra0', 'RWS09_102', 'RWS01_MONIBAS_0091hrl0229ra0', 'RWS01_MONIBAS_0101hrr0175ra0', 'RWS01_MONIBAS_0101hrr0219ra0', 'LRA01_RWS_A10Li1.9d_A10Li1.8d', 'RWS01_MONIBAS_0091hrl0312ra0', 'RWS01_MONIBAS_0091hrr0075ra0', 'RWS01_MONIBAS_0101hrr0253ra0', 'RWS01_MONIBAS_0020vwm0355ra1', 'ABM01_AV_N522_S109_west_S109_oost', 'RWS01_MONIBAS_0011hrr0078ra0', 'RWS01_MONIBAS_0100vwt0155ra0', 'RWS01_MONIBAS_0101hrl0191ra0', 'RWS01_MONIBAS_0101hrl0233ra0', 'RWS01_MONIBAS_0041hrr0030ra0', 'RWS01_MONIBAS_0101hrr0197ra0', 'RWS01_MONIBAS_0021hrl0319ra0', 'RWS01_MONIBAS_0011hrr0090ra0', 'RWS01_MONIBAS_0101hrr0069ra0', 'RWS01_MONIBAS_0101hrr0185ra0', 'RWS01_MONIBAS_0101hrl0166ra0', 'RWS01_MONIBAS_0010vwq0071ra0', 'RWS01_MONIBAS_0100vwp0307ra0', 'RWS01_MONIBAS_0101hrr0323ra0', 'LRA01_RWS_A10Re31.3_A10Re31.7a', 'ABM01_AV_N522_A9Re_A9Li', 'RWS01_MONIBAS_0051hrl0157ra0', 'RWS01_MONIBAS_0041hrr0020ra0', 'RWS01_MONIBAS_0010vwn0102rb0', 'ABM01_S109_O-baanZN_K-burgZN', 'RWS01_MONIBAS_0041hrr0038ra0', 'LRA01_RWS_A10Li32.5s_A10Re32.0p', 'RWS01_MONIBAS_0101hrr0118ra0', 'LRA01_RWS_A10Re3.5_A10Re4.1a', 'ABM01_S109_K-burgZN_O-baanZN', 'RWS01_MONIBAS_0101hrl0199ra0', 'LRA01_RWS_A10Re6.5_A10Re6.9a', 'RWS01_MONIBAS_0091hrl0316ra0', 'PNH03_N522R_11.00-11.35', 'RWS01_MONIBAS_0091hrl0084ra0', 'RWS01_MONIBAS_0020vwm0359ra0', 'PNH03_N522L_12.53-11.68', 'RWS01_MONIBAS_0101hrl0319ra0', 'LRA01_RWS_A8Li0.7_A10Re32.0', 'RWS01_MONIBAS_0051hrl0121ra0', 'RWS01_MONIBAS_0021hrl0373ra0', 'LRA01_RWS_A1Li5.2_A10Li11.0', 'RWS01_MONIBAS_0101hrr0109ra0', 'RWS01_MONIBAS_0021hrl0373ra1', 'RWS01_MONIBAS_0091hrl0094ra0', 'RWS01_MONIBAS_0020vwn0356ra0', 'ABM01_AV_Rembrandtweg_S109_S108', 'RWS01_MONIBAS_0020vwn0356ra1', 'RWS01_MONIBAS_0021hrr0331ra0', 'PNH03_N522L_14.21-13.84', 'ABM01_S109_krBuitenv-Nijerodew_krAmstelv-Nijerodew', 'RWS01_MONIBAS_0101hrl0155ra0', 'RWS01_MONIBAS_0101hrr0249ra0', 'RWS01_MONIBAS_0021hrl0359ra0', 'RWS01_MONIBAS_0101hrl0094ra0', 'RWS01_MONIBAS_0091hrr0241ra0', 'RWS01_MONIBAS_0101hrr0042ra0', 'GAD01_MOA_Route023', 'ABM01_AV_GroenvPlaan_S108_S109', 'RWS01_MONIBAS_0011hrl0066ra0', 'RWS01_MONIBAS_0101hrl0267ra0', 'GAD01_MOA_Route033', 'GAD01_MOA_Route115', 'RWS01_MONIBAS_0021hrr0318ra0', 'GAD01_MOA_Route116', 'GAD01_MOA_Route133_R', 'RWS01_MONIBAS_0100vwq0290ra1', 'GAD01_MOA_Route133_L', 'RWS01_MONIBAS_0091hrr0253ra0', 'RWS01_MONIBAS_0101hrr0294ra0', 'GAD01_MOA_Route118_L', 'RWS01_MONIBAS_0091hrr0103ra0', 'RWS09_215', 'RWS01_MONIBAS_0101hrr0180ra0', 'RWS09_216', 'GAD01_MOA_Route005', 'PNH03_N522L_13.84-12.53', 'RWS01_MONIBAS_0101hrr0057ra0', 'RWS09_213', 'RWS09_214', 'RWS09_211', 'RWS09_212', 'GAD01_MOA_Route12B', 'RWS09_210', 'RWS01_MONIBAS_0011hrl0054ra1', 'ABM01_afrit_A10Li_s102', 'LRA01_RWS_A10Li10.0_A10Li9.6c', 'RWS01_MONIBAS_0021hrl0368ra0', 'RWS09_217', 'RWS01_MONIBAS_0101hrr0045ra0', 'RWS01_MONIBAS_0101hrl0242ra0', 'RWS09_218', 'LRA01_RWS_A10Re1.7b_A10Re1.9b', 'RWS01_MONIBAS_0021hrr0355ra0', 'RWS01_MONIBAS_0091hrr0229ra0', 'RWS01_MONIBAS_0101hrl0326ra0', 'RWS01_MONIBAS_0101hrr0088ra0', 'RWS01_MONIBAS_0091hrr0261ra0', 'RWS01_MONIBAS_0101hrl0326rb0', 'RWS01_MONIBAS_0041hrr0002ra0', 'RWS01_MONIBAS_0100vwq0276ra0', 'RWS01_MONIBAS_0100vws0319ra0', 'RWS01_MONIBAS_0091hrr0219ra0', 'ABM01_N247_LiS116_RetoeS116', 'PNH03_N236R_6.01-6.85', 'ABM01_A9_LiafrOudek_Amstelland', 'RWS01_MONIBAS_0020vwe0359ra0', 'RWS01_MONIBAS_0021hrl0344ra0', 'RWS01_MONIBAS_0101hrl0033ra0', 'RWS01_MONIBAS_0101hrl0090ra0', 'GAD01_MOA_Route098', 'RWS01_MONIBAS_0081hrl0013ra0', 'ABM01_A10_LitoeS109_knpAmstel', 'GAD01_MOA_Route061', 'RWS01_MONIBAS_0101hrl0314ra0', 'RWS01_MONIBAS_0051hrl0178ra0', 'RWS01_MONIBAS_0101hrr0233ra0', 'RWS01_MONIBAS_0100vwp0317ra0', 'LRA01_RWS_A10Re7.3b_A10Re7.5', 'RWS01_MONIBAS_0091hrr0302ra0', 'PNH03_N522L_11.00-10.37', 'RWS01_MONIBAS_0020vwh0319ra0', 'RWS01_MONIBAS_0091hrr0062ra0', 'RWS01_MONIBAS_0081hrr0008ra0', 'RWS01_MONIBAS_0091hrl0204ra0', 'LRA01_RWS_A10Li1.8d_A10Li1.5', 'RWS01_MONIBAS_0020vwm0350ra0', 'ABM01_N247_A10_litoeS116', 'PNH03_N522R_12.53-13.84', 'RWS01_MONIBAS_0021hrl0339ra0', 'LRA01_RWS_A10Li9.8d_A10Li9.5', 'LRA01_RWS_A10Re7.2b_A10Re7.3b', 'RWS01_MONIBAS_0091hrl0216ra0', 'RWS01_MONIBAS_0091hrr0329ra0', 'RWS01_MONIBAS_0101hrl0042ra0', 'RWS01_MONIBAS_0021hrl0352ra0', 'RWS01_MONIBAS_0101hrr0267ra0', 'RWS01_MONIBAS_0090vwu0053ra0', 'RWS01_MONIBAS_0101hrl0097ra0', 'ABM01_ZA_krEblvrd-Boele_krLeijenb-Boele', 'RWS01_MONIBAS_0040vwm0038ra0', 'RWS01_MONIBAS_0040vwm0038ra1', 'LRA01_RWS_A10Li9.9d_A10Li9.8d', 'RWS01_MONIBAS_0091hrl0071ra0', 'RWS01_MONIBAS_0091hrr0094ra0', 'RWS09_209', 'RWS01_MONIBAS_0041hrl0020ra0', 'RWS01_MONIBAS_0091hrr0071ra0', 'RWS01_MONIBAS_0101hrl0085ra0', 'ABM01_AV_GroenvPlaan_S109_S108', 'RWS01_MONIBAS_0051hrr0099ra0', 'LRA01_RWS_A10Re1.9b_A10Re2.0', 'GAD03_MOA_Route142_R', 'RWS01_MONIBAS_0091hrl0235ra0', 'RWS01_MONIBAS_0021hrr0308ra0', 'RWS01_MONIBAS_0101hrr0225ra0', 'RWS01_MONIBAS_0101hrl0290ra0', 'RWS01_MONIBAS_0101hrl0290ra1', 'RWS01_MONIBAS_0101hrl0017ra0', 'RWS01_MONIBAS_0091hrl0247ra0', 'RWS01_MONIBAS_0051hrl0184ra0', 'RWS01_MONIBAS_0091hrr0316ra0', 'RWS01_MONIBAS_0010vwn0097ra0', 'RWS08_01', 'RWS01_MONIBAS_0101hrl0151ra0', 'RWS01_MONIBAS_0041hrr0010ra0', 'RWS01_MONIBAS_0051hrl0152ra0', 'RWS01_MONIBAS_0011hrr0052ra0', 'ABM01_A2_LIafrN522_Entree', 'ABM01_S109_K-burgZN_krBuitenv-Nijerodew', 'RWS01_MONIBAS_0101hrl0175ra0', 'ABM01_AV_Oranjebaan_S109_N522', 'ABM01_A9_LIafrS108_Stadshart', 'RWS01_MONIBAS_0020vwm0362ra0', 'RWS01_MONIBAS_0101hrr0301ra0', 'RWS01_MONIBAS_0051hrl0147ra0', 'RWS01_MONIBAS_0040vwm0041ra0', 'RWS01_MONIBAS_0100vwp0303ra0', 'RWS01_MONIBAS_0041hrr0032ra0', 'RWS01_MONIBAS_0090vwu0057ra0', 'RWS01_MONIBAS_0101hrl0253ra0', 'RWS01_MONIBAS_0091hrl0296ra0', 'RWS01_MONIBAS_0041hrr0032rb0', 'RWS01_MONIBAS_0091hrl0253ra0', 'RWS01_MONIBAS_0100vwn0308ra0', 'RWS01_MONIBAS_0020vwe0368ra0', 'RWS01_MONIBAS_0020vwh0307ra0', 'RWS01_MONIBAS_0091hrr0098ra0', 'RWS01_MONIBAS_0091hrl0241ra0', 'RWS01_MONIBAS_0101hrl0112ra0', 'RWS01_MONIBAS_0021hrr0344ra0', 'RWS01_MONIBAS_0101hrl0277ra0', 'RWS01_MONIBAS_0101hrl0124ra0', 'RWS01_MONIBAS_0051hrr0162ra0', 'RWS01_MONIBAS_0011hrl0061ra0', 'RWS01_MONIBAS_0101hrr0085ra0', 'LRA01_RWS_A10Re9.5_A10Re10.1a', 'RWS01_MONIBAS_0101hrr0097ra0', 'RWS01_MONIBAS_0100vwn0290ra0', 'RWS01_MONIBAS_0091hrr0247ra0', 'RWS01_MONIBAS_0101hrl0101ra0', 'RWS01_MONIBAS_0041hrr0015ra0', 'RWS01_MONIBAS_0101hrr0037ra0', 'RWS01_MONIBAS_0091hrr0281ra0', 'LRA01_RWS_A10Re9.5b_A10Re9.8b', 'LRA01_RWS_A10Li7.0d_A10Li6.8d', 'RWS01_MONIBAS_0011hrl0041rb0', 'RWS01_MONIBAS_0101hrr0308rb0', 'RWS01_MONIBAS_0101hrr0025ra0', 'RWS01_MONIBAS_0101hrl0027ra0', 'RWS01_MONIBAS_0100vwt0158ra0', 'RWS01_MONIBAS_0101hrr0189ra0', 'RWS01_MONIBAS_0101hrr0074ra0', 'GAD03_MOA_Route140_R', 'RWS01_MONIBAS_0090vwb0109ra1', 'RWS01_MONIBAS_0091hrr0105ra0', 'ABM01_A10_RetoeS108_knpNM', 'RWS01_MONIBAS_0101hrr0063ra0', 'RWS01_MONIBAS_0090vwt0114ra0', 'RWS01_MONIBAS_0080vwf0010ra0', 'RWS01_MONIBAS_0011hrl0075ra0', 'RWS01_MONIBAS_0101hrl0228ra0', 'ABM01_S109_krEblvrd-Nijerodew_krEblvrd-Boele', 'RWS01_MONIBAS_0101hrr0093ra0', 'RWS01_MONIBAS_0101hrr0051ra0', 'RWS01_MONIBAS_0101hrl0205ra0', 'RWS01_MONIBAS_0101hrr0308ra0', 'RWS01_MONIBAS_0101hrr0153rb0', 'RWS01_MONIBAS_0011hrl0090ra0', 'ABM01_S109_krEblvrd-Nijerodew_krBuitenv-Nijerodew', 'RWS01_MONIBAS_0011hrl0085ra0', 'RWS01_MONIBAS_0091hrr0235ra0', 'RWS01_MONIBAS_0101hrr0153ra0', 'RWS01_MONIBAS_0011hrl0051rb0', 'RWS01_MONIBAS_0020vwe0363ra0', 'PNH03_N522R_10.37-11.00', 'GAD03_MOA_Route14B', 'RWS01_MONIBAS_0101hrr0157ra0', 'RWS01_MONIBAS_0091hrr0256ra0', 'RWS01_MONIBAS_0101hrl0105ra0', 'RWS01_MONIBAS_0020vwg0348ra0', 'RWS01_MONIBAS_0051hrl0105ra0', 'RWS01_MONIBAS_0020vwn0344ra0', 'RWS01_MONIBAS_0090vws0215ra0', 'RWS01_MONIBAS_0040vwh0007ra0', 'ABM01_A10_S106WO_LitoeS106', 'RWS01_MONIBAS_0101hrr0169ra0', 'RWS01_MONIBAS_0051hrl0162ra0', 'RWS01_MONIBAS_0101hrr0019ra0', 'RWS01_MONIBAS_0091hrl0337ra0', 'PNH03_N522L_11.57-11.35', 'LRA01_RWS_A10Li32.3s_A10Li31.9s', 'RWS01_MONIBAS_0101hrr0203ra0', 'RWS01_MONIBAS_0101hrr0133ra0', 'RWS09_027', 'RWS01_MONIBAS_0091hrr0276ra0', 'RWS01_MONIBAS_0091hrl0075ra0', 'RWS01_MONIBAS_0091hrr0080ra0', 'RWS01_MONIBAS_0101hrl0129ra0', 'RWS01_MONIBAS_0101hrr0215ra0', 'RWS01_MONIBAS_0101hrl0071ra0', 'RWS01_MONIBAS_0051hrl0129ra0', 'RWS01_MONIBAS_0091hrl0221ra0', 'RWS01_MONIBAS_0091hrl0221ra1', 'RWS01_MONIBAS_0101hrr0080ra0', 'ABM01_AV_Oranjebaan_N522_S109', 'RWS01_MONIBAS_0091hrr0089ra0', 'RWS01_MONIBAS_0091hrr0287ra0', 'RWS01_MONIBAS_0101hrr0123ra0', 'RWS01_MONIBAS_0020vwm0344ra1', 'RWS01_MONIBAS_0091hrr0111ra0', 'RWS01_MONIBAS_0020vwm0344ra0', 'RWS01_MONIBAS_0101hrr0239ra0', 'LRA01_RWS_A10Re9.8b_A10Re10.0', 'RWS01_MONIBAS_0101hrl0022ra0', 'RWS01_MONIBAS_0101hrl0287ra1', 'RWS01_MONIBAS_0101hrl0287ra0', 'RWS01_MONIBAS_0091hrr0065ra0', 'RWS01_MONIBAS_0101hrl0186ra0', 'RWS01_MONIBAS_0091hrr0272ra0', 'RWS01_MONIBAS_0091hrl0301ra0', 'RWS01_MONIBAS_0101hrr0229ra0', 'LRA01_RWS_A10Re1.7_A10Re2.1a', 'RWS01_MONIBAS_0101hrr0138ra0', 'RWS01_MONIBAS_0101hrr0194ra0', 'RWS01_MONIBAS_0051hrl0110ra0', 'RWS01_MONIBAS_0041hrl0011rb0', 'RWS01_MONIBAS_0051hrl0137ra0', 'RWS01_MONIBAS_0091hrr0053ra0', 'RWS01_MONIBAS_0101hrr0276ra0')
    )
"""

TRAVELTIME_WITH_SPEED = """
create view traveltime_with_speed as
select id, measurement_site_reference, length, duration, measurement_time, scraped_at, geometrie, road_type, stadsdeel, buurt_code, (length/duration)*3.6 as velocity
from
    importer_traveltime
where
    data_error=false
    and duration >=0
    and ("measurement_site_reference" ilike 'GAD03_%_'
        and "measurement_site_reference" not ilike '%MOA%'
        and "measurement_site_reference" not ilike '%GAD03_S%'
        or measurement_site_reference in ('RWS01_MONIBAS_0101hrr0032ra0', 'GAD03_MOA_Route102', 'RWS01_MONIBAS_0011hrl0106ra1', 'RWS01_MONIBAS_0021hrr0359ra0', 'RWS01_MONIBAS_0101hrr0312ra0', 'GAD03_MOA_Route109', 'RWS01_MONIBAS_0100vwn0300ra0', 'RWS01_MONIBAS_0021hrl0333ra0', 'RWS01_MONIBAS_0021hrr0348ra0', 'ABM01_ZA_krLeijenb-Boele_krEblvrd-Boele', 'RWS01_MONIBAS_0091hrr0296ra0', 'RWS01_MONIBAS_0091hrl0274ra0', 'RWS01_MONIBAS_0091hrl0103ra0', 'RWS01_MONIBAS_0021hrr0369ra0', 'ABM01_S106_LiafrS106_krS106-S108', 'RWS01_MONIBAS_0021hrr0313ra0', 'RWS09_051', 'RWS01_MONIBAS_0041hrl0011ra0', 'RWS01_MONIBAS_0090vwr0212ra0', 'RWS01_MONIBAS_0021hrr0335ra0', 'RWS01_MONIBAS_0091hrr0324ra0', 'RWS01_MONIBAS_0101hrl0147ra0', 'RWS01_MONIBAS_0101hrr0127ra0', 'RWS01_MONIBAS_0091hrl0320rb0', 'RWS01_MONIBAS_0101hrl0135ra0', 'ABM01_AV_N522_S109_A9Li', 'RWS09_136', 'RWS01_MONIBAS_0021hrr0323ra0', 'RWS09_134', 'PNH03_N522L_11.68-11.57', 'RWS09_135', 'RWS01_MONIBAS_0020vwn0348ra0', 'RWS01_MONIBAS_0100vwp0294ra0', 'RWS01_MONIBAS_0091hrr0084ra0', 'RWS09_065', 'RWS01_MONIBAS_0101hrl0239ra0', 'RWS01_MONIBAS_0091hrl0079ra0', 'RWS01_MONIBAS_0011hrr0046ra0', 'RWS01_MONIBAS_0011hrr0080ra0', 'RWS01_MONIBAS_0021hrl0363rb0', 'ABM01_S103_toeA10Li_LitoeS103', 'RWS01_MONIBAS_0091hrl0332ra0', 'ABM01_AV_N522_S109_oost_S109_west', 'RWS01_MONIBAS_0011hrr0070ra0', 'RWS01_MONIBAS_0021hrl0363ra0', 'RWS01_MONIBAS_0101hrr0144ra0', 'RWS01_MONIBAS_0101hrl0074ra0', 'RWS09_141', 'RWS01_MONIBAS_0101hrr0330ra0', 'RWS01_MONIBAS_0101hrl0109ra0', 'ABM01_S109_krAmstelv-Nijerodew_krBuitenv-Nijerodew', 'ABM01__A10_LiafrS112_S112NZ_ZO', 'RWS09_035', 'RWS09_036', 'RWS09_033', 'RWS09_034', 'RWS01_MONIBAS_0101hrr0317ra0', 'RWS09_031', 'RWS01_MONIBAS_0101hrl0050ra0', 'RWS01_MONIBAS_0091hrl0281ra0', 'RWS01_MONIBAS_0101hrl0247ra0', 'RWS01_MONIBAS_0101hrr0305ra0', 'RWS01_MONIBAS_0101hrl0271ra0', 'RWS01_MONIBAS_0091hrl0213ra0', 'RWS01_MONIBAS_0011hrl0101ra0', 'RWS01_MONIBAS_0091hrr0047ra0', 'RWS01_MONIBAS_0101hrl0062ra0', 'RWS01_MONIBAS_0091hrl0062ra1', 'RWS01_MONIBAS_0091hrl0062ra0', 'RWS01_MONIBAS_0051hrr0121ra0', 'RWS01_MONIBAS_0091hrl0329ra0', 'RWS01_MONIBAS_0091hrl0307ra0', 'RWS01_MONIBAS_0021hrr0326ra0', 'RWS01_MONIBAS_0091hrl0098ra0', 'RWS01_MONIBAS_0091hrr0114ra0', 'RWS01_MONIBAS_0011hrr0061ra0', 'ABM01_S109_krBuitenv-Nijerodew_K-burgZN', 'RWS01_MONIBAS_0021hrl0348ra0', 'RWS01_MONIBAS_0091hrr0320ra0', 'RWS01_MONIBAS_0011hrr0095ra0', 'RWS01_MONIBAS_0010vwn0106ra0', 'RWS01_MONIBAS_0051hrr0157ra0', 'PNH03_N522R_11.68-12.53', 'RWS01_MONIBAS_0101hrl0140ra0', 'RWS09_049', 'RWS01_MONIBAS_0011hrr0086ra0', 'RWS01_MONIBAS_0100vwp0312ra0', 'RWS01_MONIBAS_0091hrr0332ra0', 'RWS01_MONIBAS_0091hrl0052ra0', 'RWS01_MONIBAS_0091hrr0307ra0', 'LRA01_RWS_A10Re31.9b_A10Re32.1b', 'RWS01_MONIBAS_0011hrr0075ra0', 'LRA01_RWS_A10Li7.4_A10Li7.0c', 'RWS01_MONIBAS_0021hrl0336ra0', 'RWS09_127', 'RWS01_MONIBAS_0020vwn0352ra0', 'RWS09_126', 'RWS01_MONIBAS_0021hrl0379ra0', 'RWS01_MONIBAS_0091hrr0312ra0', 'RWS01_MONIBAS_0091hrl0089ra0', 'RWS01_MONIBAS_0101hrl0160ra0', 'RWS01_MONIBAS_0011hrl0070ra0', 'RWS09_121', 'RWS01_MONIBAS_0100vwp0290ra0', 'ABM01_afrit_A10re_S103', 'RWS09_122', 'RWS09_120', 'RWS01_MONIBAS_0101hrl0304ra0', 'RWS01_MONIBAS_0011hrr0099ra0', 'RWS01_MONIBAS_0011hrl0080ra0', 'PNH03_N522L_11.35-11.00', 'RWS01_MONIBAS_0011hrl0057ra0', 'RWS01_MONIBAS_0021hrr0375ra0', 'RWS01_MONIBAS_0041hrr0023ra0', 'LRA01_RWS_A10Li2.0_A10Li1.8c', 'RWS01_MONIBAS_0021hrl0355ra0', 'RWS01_MONIBAS_0091hrl0066ra0', 'RWS04_BHD_30', 'RWS01_MONIBAS_0101hrl0181ra0', 'RWS09_178', 'RWS04_BHD_31', 'RWS01_MONIBAS_0101hrl0056ra0', 'RWS01_MONIBAS_0101hrr0290ra0', 'RWS01_MONIBAS_0100vwp0285ra0', 'RWS04_BHD_33', 'ABM01_S102_Toerit_A10re', 'RWS01_MONIBAS_0101hrl0261ra0', 'RWS01_MONIBAS_0101hrl0225ra1', 'RWS01_MONIBAS_0011hrl0037ra0', 'PNH03_N236L_6.01-5.29', 'RWS01_MONIBAS_0100vwt0113ra0', 'RWS01_MONIBAS_0101hrr0209ra1', 'RWS01_MONIBAS_0051hrl0167ra0', 'ABM01_A9_ReafrS108_Stadshart', 'RWS01_MONIBAS_0100vws0322ra0', 'PNH03_N522L_10.37-10.12', 'RWS01_MONIBAS_0091hrl0056rb0', 'ABM01_AV_B.Rijnderslaan_S109_S108', 'ABM01_S106_pc1065_S106WO', 'RWS01_MONIBAS_0101hrl0297ra0', 'RWS01_MONIBAS_0011hrl0047ra0', 'ABM01_S103_A10re_Kimpoweg', 'RWS01_MONIBAS_0101hrl0212ra0', 'RWS01_MONIBAS_0101hrl0170ra0', 'RWS01_MONIBAS_0051hrr0105ra0', 'RWS01_MONIBAS_0101hrr0244ra0', 'RWS01_MONIBAS_0091hrr0266ra0', 'RWS01_MONIBAS_0091hrl0285ra0', 'RWS09_154', 'GAD03_MOA_Route131_R', 'RWS09_155', 'PNH03_N522R_11.35-11.57', 'RWS01_MONIBAS_0101hrr0281ra0', 'RWS01_MONIBAS_0101hrl0120ra0', 'RWS09_152', 'RWS01_MONIBAS_0051hrr0129ra0', 'RWS09_153', 'RWS01_MONIBAS_0100vwp0298ra0', 'RWS01_MONIBAS_0101hrl0281ra0', 'RWS09_151', 'RWS01_MONIBAS_0020vwf0352ra0', 'RWS01_MONIBAS_0091hrl0261ra0', 'RWS01_MONIBAS_0091hrr0291ra0', 'RWS01_MONIBAS_0101hrr0271ra1', 'RWS01_MONIBAS_0101hrl0293ra0', 'RWS01_MONIBAS_0091hrl0291ra0', 'RWS01_MONIBAS_0051hrr0116ra0', 'RWS09_165', 'RWS01_MONIBAS_0040vwh0003ra0', 'RWS09_166', 'RWS09_164', 'RWS01_MONIBAS_0101hrr0258ra0', 'RWS01_MONIBAS_0021hrl0328ra0', 'RWS01_MONIBAS_0021hrr0340ra0', 'LRA01_RWS_A10Re32.1b_A10Re32.5', 'RWS01_MONIBAS_0101hrl0144ra0', 'RWS01_MONIBAS_0021hrr0340ra1', 'RWS01_MONIBAS_0041hrl0030ra0', 'LRA01_RWS_A10Li4.8_A10Li4.2c', 'RWS01_MONIBAS_0101hrl0308ra0', 'RWS01_MONIBAS_0051hrl0143ra0', 'ABM01_AV_N522_A9Li_S109', 'RWS01_MONIBAS_0051hrr0110ra0', 'RWS01_MONIBAS_0091hrr0068ra0', 'RWS01_MONIBAS_0101hrr0261ra0', 'RWS01_MONIBAS_0080vwf0016ra0', 'RWS01_MONIBAS_0081hrl0021rb0', 'ABM01_AV_N522_A9Re_S109', 'RWS01_MONIBAS_0100vwn0297ra0', 'RWS01_MONIBAS_0041hrl0040ra0', 'RWS01_MONIBAS_0080vwf0016ra1', 'PNH03_N236R_5.29-6.01', 'RWS04_BHD_27', 'RWS01_MONIBAS_0091hrl0224ra0', 'RWS01_MONIBAS_0101hrr0285ra0', 'RWS01_MONIBAS_0020vwf0309ra0', 'RWS01_MONIBAS_0100vwt0119ra0', 'RWS01_MONIBAS_0020vwh0314ra1', 'ABM01_AV_Rembrandtweg_S108_S109', 'RWS01_MONIBAS_0020vwh0314ra0', 'RWS01_MONIBAS_0091hrl0106ra0', 'RWS01_MONIBAS_0091hrr0044ra0', 'RWS01_MONIBAS_0100vwp0281ra0', 'RWS01_MONIBAS_0091hrr0056ra0', 'RWS01_MONIBAS_0091hrl0256ra0', 'RWS01_MONIBAS_0081hrl0021ra0', 'RWS01_MONIBAS_0041hrl0027ra0', 'PNH03_N236L_6.85-6.01', 'RWS01_MONIBAS_0051hrl0116ra0', 'RWS01_MONIBAS_0021hrl0322ra0', 'RWS01_MONIBAS_0021hrl0322ra1', 'RWS01_MONIBAS_0041hrl0036ra0', 'RWS01_MONIBAS_0041hrl0024ra0', 'RWS01_MONIBAS_0010vwf0047ra0', 'RWS01_MONIBAS_0041hrl0015ra0', 'RWS01_MONIBAS_0091hrl0266ra0', 'RWS01_MONIBAS_0041hrl0004ra0', 'RWS01_MONIBAS_0100vwn0293ra0', 'RWS01_MONIBAS_0101hrl0080ra0', 'RWS01_MONIBAS_0100vws0166ra0', 'RWS01_MONIBAS_0081hrr0013ra0', 'RWS01_MONIBAS_0101hrr0149ra0', 'RWS01_MONIBAS_0021hrr0352ra0', 'RWS01_MONIBAS_0091hrr0119ra0', 'RWS01_MONIBAS_0090vwr0215ra0', 'RWS01_MONIBAS_0090vwr0215ra1', 'RWS01_MONIBAS_0101hrl0067ra0', 'RWS01_MONIBAS_0101hrl0257ra0', 'RWS01_MONIBAS_0091hrl0324ra1', 'RWS01_MONIBAS_0101hrr0113ra0', 'RWS09_103', 'RWS01_MONIBAS_0101hrr0163ra0', 'ABM01_AV_N522_A9Li_A9Re', 'RWS09_104', 'RWS01_MONIBAS_0051hrr0140ra0', 'RWS01_MONIBAS_0101hrr0103ra0', 'RWS09_102', 'RWS01_MONIBAS_0091hrl0229ra0', 'RWS01_MONIBAS_0101hrr0175ra0', 'RWS01_MONIBAS_0101hrr0219ra0', 'LRA01_RWS_A10Li1.9d_A10Li1.8d', 'RWS01_MONIBAS_0091hrl0312ra0', 'RWS01_MONIBAS_0091hrr0075ra0', 'RWS01_MONIBAS_0101hrr0253ra0', 'RWS01_MONIBAS_0020vwm0355ra1', 'ABM01_AV_N522_S109_west_S109_oost', 'RWS01_MONIBAS_0011hrr0078ra0', 'RWS01_MONIBAS_0100vwt0155ra0', 'RWS01_MONIBAS_0101hrl0191ra0', 'RWS01_MONIBAS_0101hrl0233ra0', 'RWS01_MONIBAS_0041hrr0030ra0', 'RWS01_MONIBAS_0101hrr0197ra0', 'RWS01_MONIBAS_0021hrl0319ra0', 'RWS01_MONIBAS_0011hrr0090ra0', 'RWS01_MONIBAS_0101hrr0069ra0', 'RWS01_MONIBAS_0101hrr0185ra0', 'RWS01_MONIBAS_0101hrl0166ra0', 'RWS01_MONIBAS_0010vwq0071ra0', 'RWS01_MONIBAS_0100vwp0307ra0', 'RWS01_MONIBAS_0101hrr0323ra0', 'LRA01_RWS_A10Re31.3_A10Re31.7a', 'ABM01_AV_N522_A9Re_A9Li', 'RWS01_MONIBAS_0051hrl0157ra0', 'RWS01_MONIBAS_0041hrr0020ra0', 'RWS01_MONIBAS_0010vwn0102rb0', 'ABM01_S109_O-baanZN_K-burgZN', 'RWS01_MONIBAS_0041hrr0038ra0', 'LRA01_RWS_A10Li32.5s_A10Re32.0p', 'RWS01_MONIBAS_0101hrr0118ra0', 'LRA01_RWS_A10Re3.5_A10Re4.1a', 'ABM01_S109_K-burgZN_O-baanZN', 'RWS01_MONIBAS_0101hrl0199ra0', 'LRA01_RWS_A10Re6.5_A10Re6.9a', 'RWS01_MONIBAS_0091hrl0316ra0', 'PNH03_N522R_11.00-11.35', 'RWS01_MONIBAS_0091hrl0084ra0', 'RWS01_MONIBAS_0020vwm0359ra0', 'PNH03_N522L_12.53-11.68', 'RWS01_MONIBAS_0101hrl0319ra0', 'LRA01_RWS_A8Li0.7_A10Re32.0', 'RWS01_MONIBAS_0051hrl0121ra0', 'RWS01_MONIBAS_0021hrl0373ra0', 'LRA01_RWS_A1Li5.2_A10Li11.0', 'RWS01_MONIBAS_0101hrr0109ra0', 'RWS01_MONIBAS_0021hrl0373ra1', 'RWS01_MONIBAS_0091hrl0094ra0', 'RWS01_MONIBAS_0020vwn0356ra0', 'ABM01_AV_Rembrandtweg_S109_S108', 'RWS01_MONIBAS_0020vwn0356ra1', 'RWS01_MONIBAS_0021hrr0331ra0', 'PNH03_N522L_14.21-13.84', 'ABM01_S109_krBuitenv-Nijerodew_krAmstelv-Nijerodew', 'RWS01_MONIBAS_0101hrl0155ra0', 'RWS01_MONIBAS_0101hrr0249ra0', 'RWS01_MONIBAS_0021hrl0359ra0', 'RWS01_MONIBAS_0101hrl0094ra0', 'RWS01_MONIBAS_0091hrr0241ra0', 'RWS01_MONIBAS_0101hrr0042ra0', 'GAD01_MOA_Route023', 'ABM01_AV_GroenvPlaan_S108_S109', 'RWS01_MONIBAS_0011hrl0066ra0', 'RWS01_MONIBAS_0101hrl0267ra0', 'GAD01_MOA_Route033', 'GAD01_MOA_Route115', 'RWS01_MONIBAS_0021hrr0318ra0', 'GAD01_MOA_Route116', 'GAD01_MOA_Route133_R', 'RWS01_MONIBAS_0100vwq0290ra1', 'GAD01_MOA_Route133_L', 'RWS01_MONIBAS_0091hrr0253ra0', 'RWS01_MONIBAS_0101hrr0294ra0', 'GAD01_MOA_Route118_L', 'RWS01_MONIBAS_0091hrr0103ra0', 'RWS09_215', 'RWS01_MONIBAS_0101hrr0180ra0', 'RWS09_216', 'GAD01_MOA_Route005', 'PNH03_N522L_13.84-12.53', 'RWS01_MONIBAS_0101hrr0057ra0', 'RWS09_213', 'RWS09_214', 'RWS09_211', 'RWS09_212', 'GAD01_MOA_Route12B', 'RWS09_210', 'RWS01_MONIBAS_0011hrl0054ra1', 'ABM01_afrit_A10Li_s102', 'LRA01_RWS_A10Li10.0_A10Li9.6c', 'RWS01_MONIBAS_0021hrl0368ra0', 'RWS09_217', 'RWS01_MONIBAS_0101hrr0045ra0', 'RWS01_MONIBAS_0101hrl0242ra0', 'RWS09_218', 'LRA01_RWS_A10Re1.7b_A10Re1.9b', 'RWS01_MONIBAS_0021hrr0355ra0', 'RWS01_MONIBAS_0091hrr0229ra0', 'RWS01_MONIBAS_0101hrl0326ra0', 'RWS01_MONIBAS_0101hrr0088ra0', 'RWS01_MONIBAS_0091hrr0261ra0', 'RWS01_MONIBAS_0101hrl0326rb0', 'RWS01_MONIBAS_0041hrr0002ra0', 'RWS01_MONIBAS_0100vwq0276ra0', 'RWS01_MONIBAS_0100vws0319ra0', 'RWS01_MONIBAS_0091hrr0219ra0', 'ABM01_N247_LiS116_RetoeS116', 'PNH03_N236R_6.01-6.85', 'ABM01_A9_LiafrOudek_Amstelland', 'RWS01_MONIBAS_0020vwe0359ra0', 'RWS01_MONIBAS_0021hrl0344ra0', 'RWS01_MONIBAS_0101hrl0033ra0', 'RWS01_MONIBAS_0101hrl0090ra0', 'GAD01_MOA_Route098', 'RWS01_MONIBAS_0081hrl0013ra0', 'ABM01_A10_LitoeS109_knpAmstel', 'GAD01_MOA_Route061', 'RWS01_MONIBAS_0101hrl0314ra0', 'RWS01_MONIBAS_0051hrl0178ra0', 'RWS01_MONIBAS_0101hrr0233ra0', 'RWS01_MONIBAS_0100vwp0317ra0', 'LRA01_RWS_A10Re7.3b_A10Re7.5', 'RWS01_MONIBAS_0091hrr0302ra0', 'PNH03_N522L_11.00-10.37', 'RWS01_MONIBAS_0020vwh0319ra0', 'RWS01_MONIBAS_0091hrr0062ra0', 'RWS01_MONIBAS_0081hrr0008ra0', 'RWS01_MONIBAS_0091hrl0204ra0', 'LRA01_RWS_A10Li1.8d_A10Li1.5', 'RWS01_MONIBAS_0020vwm0350ra0', 'ABM01_N247_A10_litoeS116', 'PNH03_N522R_12.53-13.84', 'RWS01_MONIBAS_0021hrl0339ra0', 'LRA01_RWS_A10Li9.8d_A10Li9.5', 'LRA01_RWS_A10Re7.2b_A10Re7.3b', 'RWS01_MONIBAS_0091hrl0216ra0', 'RWS01_MONIBAS_0091hrr0329ra0', 'RWS01_MONIBAS_0101hrl0042ra0', 'RWS01_MONIBAS_0021hrl0352ra0', 'RWS01_MONIBAS_0101hrr0267ra0', 'RWS01_MONIBAS_0090vwu0053ra0', 'RWS01_MONIBAS_0101hrl0097ra0', 'ABM01_ZA_krEblvrd-Boele_krLeijenb-Boele', 'RWS01_MONIBAS_0040vwm0038ra0', 'RWS01_MONIBAS_0040vwm0038ra1', 'LRA01_RWS_A10Li9.9d_A10Li9.8d', 'RWS01_MONIBAS_0091hrl0071ra0', 'RWS01_MONIBAS_0091hrr0094ra0', 'RWS09_209', 'RWS01_MONIBAS_0041hrl0020ra0', 'RWS01_MONIBAS_0091hrr0071ra0', 'RWS01_MONIBAS_0101hrl0085ra0', 'ABM01_AV_GroenvPlaan_S109_S108', 'RWS01_MONIBAS_0051hrr0099ra0', 'LRA01_RWS_A10Re1.9b_A10Re2.0', 'GAD03_MOA_Route142_R', 'RWS01_MONIBAS_0091hrl0235ra0', 'RWS01_MONIBAS_0021hrr0308ra0', 'RWS01_MONIBAS_0101hrr0225ra0', 'RWS01_MONIBAS_0101hrl0290ra0', 'RWS01_MONIBAS_0101hrl0290ra1', 'RWS01_MONIBAS_0101hrl0017ra0', 'RWS01_MONIBAS_0091hrl0247ra0', 'RWS01_MONIBAS_0051hrl0184ra0', 'RWS01_MONIBAS_0091hrr0316ra0', 'RWS01_MONIBAS_0010vwn0097ra0', 'RWS08_01', 'RWS01_MONIBAS_0101hrl0151ra0', 'RWS01_MONIBAS_0041hrr0010ra0', 'RWS01_MONIBAS_0051hrl0152ra0', 'RWS01_MONIBAS_0011hrr0052ra0', 'ABM01_A2_LIafrN522_Entree', 'ABM01_S109_K-burgZN_krBuitenv-Nijerodew', 'RWS01_MONIBAS_0101hrl0175ra0', 'ABM01_AV_Oranjebaan_S109_N522', 'ABM01_A9_LIafrS108_Stadshart', 'RWS01_MONIBAS_0020vwm0362ra0', 'RWS01_MONIBAS_0101hrr0301ra0', 'RWS01_MONIBAS_0051hrl0147ra0', 'RWS01_MONIBAS_0040vwm0041ra0', 'RWS01_MONIBAS_0100vwp0303ra0', 'RWS01_MONIBAS_0041hrr0032ra0', 'RWS01_MONIBAS_0090vwu0057ra0', 'RWS01_MONIBAS_0101hrl0253ra0', 'RWS01_MONIBAS_0091hrl0296ra0', 'RWS01_MONIBAS_0041hrr0032rb0', 'RWS01_MONIBAS_0091hrl0253ra0', 'RWS01_MONIBAS_0100vwn0308ra0', 'RWS01_MONIBAS_0020vwe0368ra0', 'RWS01_MONIBAS_0020vwh0307ra0', 'RWS01_MONIBAS_0091hrr0098ra0', 'RWS01_MONIBAS_0091hrl0241ra0', 'RWS01_MONIBAS_0101hrl0112ra0', 'RWS01_MONIBAS_0021hrr0344ra0', 'RWS01_MONIBAS_0101hrl0277ra0', 'RWS01_MONIBAS_0101hrl0124ra0', 'RWS01_MONIBAS_0051hrr0162ra0', 'RWS01_MONIBAS_0011hrl0061ra0', 'RWS01_MONIBAS_0101hrr0085ra0', 'LRA01_RWS_A10Re9.5_A10Re10.1a', 'RWS01_MONIBAS_0101hrr0097ra0', 'RWS01_MONIBAS_0100vwn0290ra0', 'RWS01_MONIBAS_0091hrr0247ra0', 'RWS01_MONIBAS_0101hrl0101ra0', 'RWS01_MONIBAS_0041hrr0015ra0', 'RWS01_MONIBAS_0101hrr0037ra0', 'RWS01_MONIBAS_0091hrr0281ra0', 'LRA01_RWS_A10Re9.5b_A10Re9.8b', 'LRA01_RWS_A10Li7.0d_A10Li6.8d', 'RWS01_MONIBAS_0011hrl0041rb0', 'RWS01_MONIBAS_0101hrr0308rb0', 'RWS01_MONIBAS_0101hrr0025ra0', 'RWS01_MONIBAS_0101hrl0027ra0', 'RWS01_MONIBAS_0100vwt0158ra0', 'RWS01_MONIBAS_0101hrr0189ra0', 'RWS01_MONIBAS_0101hrr0074ra0', 'GAD03_MOA_Route140_R', 'RWS01_MONIBAS_0090vwb0109ra1', 'RWS01_MONIBAS_0091hrr0105ra0', 'ABM01_A10_RetoeS108_knpNM', 'RWS01_MONIBAS_0101hrr0063ra0', 'RWS01_MONIBAS_0090vwt0114ra0', 'RWS01_MONIBAS_0080vwf0010ra0', 'RWS01_MONIBAS_0011hrl0075ra0', 'RWS01_MONIBAS_0101hrl0228ra0', 'ABM01_S109_krEblvrd-Nijerodew_krEblvrd-Boele', 'RWS01_MONIBAS_0101hrr0093ra0', 'RWS01_MONIBAS_0101hrr0051ra0', 'RWS01_MONIBAS_0101hrl0205ra0', 'RWS01_MONIBAS_0101hrr0308ra0', 'RWS01_MONIBAS_0101hrr0153rb0', 'RWS01_MONIBAS_0011hrl0090ra0', 'ABM01_S109_krEblvrd-Nijerodew_krBuitenv-Nijerodew', 'RWS01_MONIBAS_0011hrl0085ra0', 'RWS01_MONIBAS_0091hrr0235ra0', 'RWS01_MONIBAS_0101hrr0153ra0', 'RWS01_MONIBAS_0011hrl0051rb0', 'RWS01_MONIBAS_0020vwe0363ra0', 'PNH03_N522R_10.37-11.00', 'GAD03_MOA_Route14B', 'RWS01_MONIBAS_0101hrr0157ra0', 'RWS01_MONIBAS_0091hrr0256ra0', 'RWS01_MONIBAS_0101hrl0105ra0', 'RWS01_MONIBAS_0020vwg0348ra0', 'RWS01_MONIBAS_0051hrl0105ra0', 'RWS01_MONIBAS_0020vwn0344ra0', 'RWS01_MONIBAS_0090vws0215ra0', 'RWS01_MONIBAS_0040vwh0007ra0', 'ABM01_A10_S106WO_LitoeS106', 'RWS01_MONIBAS_0101hrr0169ra0', 'RWS01_MONIBAS_0051hrl0162ra0', 'RWS01_MONIBAS_0101hrr0019ra0', 'RWS01_MONIBAS_0091hrl0337ra0', 'PNH03_N522L_11.57-11.35', 'LRA01_RWS_A10Li32.3s_A10Li31.9s', 'RWS01_MONIBAS_0101hrr0203ra0', 'RWS01_MONIBAS_0101hrr0133ra0', 'RWS09_027', 'RWS01_MONIBAS_0091hrr0276ra0', 'RWS01_MONIBAS_0091hrl0075ra0', 'RWS01_MONIBAS_0091hrr0080ra0', 'RWS01_MONIBAS_0101hrl0129ra0', 'RWS01_MONIBAS_0101hrr0215ra0', 'RWS01_MONIBAS_0101hrl0071ra0', 'RWS01_MONIBAS_0051hrl0129ra0', 'RWS01_MONIBAS_0091hrl0221ra0', 'RWS01_MONIBAS_0091hrl0221ra1', 'RWS01_MONIBAS_0101hrr0080ra0', 'ABM01_AV_Oranjebaan_N522_S109', 'RWS01_MONIBAS_0091hrr0089ra0', 'RWS01_MONIBAS_0091hrr0287ra0', 'RWS01_MONIBAS_0101hrr0123ra0', 'RWS01_MONIBAS_0020vwm0344ra1', 'RWS01_MONIBAS_0091hrr0111ra0', 'RWS01_MONIBAS_0020vwm0344ra0', 'RWS01_MONIBAS_0101hrr0239ra0', 'LRA01_RWS_A10Re9.8b_A10Re10.0', 'RWS01_MONIBAS_0101hrl0022ra0', 'RWS01_MONIBAS_0101hrl0287ra1', 'RWS01_MONIBAS_0101hrl0287ra0', 'RWS01_MONIBAS_0091hrr0065ra0', 'RWS01_MONIBAS_0101hrl0186ra0', 'RWS01_MONIBAS_0091hrr0272ra0', 'RWS01_MONIBAS_0091hrl0301ra0', 'RWS01_MONIBAS_0101hrr0229ra0', 'LRA01_RWS_A10Re1.7_A10Re2.1a', 'RWS01_MONIBAS_0101hrr0138ra0', 'RWS01_MONIBAS_0101hrr0194ra0', 'RWS01_MONIBAS_0051hrl0110ra0', 'RWS01_MONIBAS_0041hrl0011rb0', 'RWS01_MONIBAS_0051hrl0137ra0', 'RWS01_MONIBAS_0091hrr0053ra0', 'RWS01_MONIBAS_0101hrr0276ra0')
        )
"""
