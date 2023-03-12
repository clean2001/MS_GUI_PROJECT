import numpy as np

# ms 데이터의 일부 (피크 7개)
sample_data = np.array([
    [110.698067, 3592.378418],
    [111.152618, 2282.734131],
    [113.980606, 2600.364502],
    [127.085716, 2481.166748],
    [129.102295, 30748.218750],
    [130.085617, 26399.017578],
    [147.113022, 41320.484375],
    [157.096283, 7622.079102],
    [159.075760, 9155.642578],

])

string_of_spectrum = '''110.698067 3592.378418
111.152618 2282.734131
113.980606 2600.364502
127.085716 2481.166748
129.102295 30748.218750
130.085617 26399.017578
147.113022 41320.484375
157.096283 7622.079102
159.075760 9155.642578
169.133514 537017.687500
170.136749 33989.105469
171.112091 7468.723145
175.107742 32592.103516
181.096405 7816.973633
181.131409 3072.664063
183.112457 8144.851563
185.092148 141607.437500
187.142685 3920.287109
189.444168 3101.858643
190.167007 3043.598145
194.956345 2949.762939
197.128464 541842.625000
198.131790 45429.792969
199.107849 54009.406250
199.143784 8114.201660
200.102905 16853.195313
201.107117 2798.193604
201.122726 35560.621094
203.102951 34856.031250
209.092026 4277.992188
215.137848 14248.956055
225.158234 4401.718262
227.082153 5047.862793
227.102478 100234.218750
231.005859 3105.219482
236.138855 4383.278320
238.119370 4575.733398
240.133041 3559.099609
241.000076 4036.506836
244.127853 5869.320801
245.112808 3474.475098
253.152969 7856.599609
254.149246 65177.066406
256.128082 6104.215820
258.143066 8625.438477
259.090454 8613.974609
262.139374 34924.500000
266.112793 3162.593018
266.150024 4350.103027
268.164307 6636.666992
272.160095 4705.229980
280.165527 208741.468750
281.166138 23623.898438
282.143555 21946.712891
283.141052 5380.131836
284.160919 30023.765625
287.098083 7250.873535
294.142487 22197.398438
294.178314 5505.906738
296.100189 3586.360107
298.176025 435215.625000
299.177979 62775.937500
300.152313 5409.872559
302.169678 18254.849609
307.235352 3244.671631
308.158356 5171.458984
310.139557 7380.414551
310.172821 13865.414063
311.169312 9586.355469
312.153656 17192.300781
313.188751 5225.591309
314.171936 3399.074463
319.161072 121294.953125
320.162659 15753.929688
327.201324 17469.583984
328.149536 33468.242188
336.189148 7730.822266
337.186890 68732.156250
337.222412 9859.020508
353.218353 39701.230469
354.203522 66709.242188
355.198029 156618.750000
356.144989 255893.406250
356.195190 21726.425781
357.147186 39280.269531
358.140808 5720.843262
363.159241 7119.957031
363.202423 170667.937500
364.205109 27951.562500
365.178467 4692.286133
367.234161 6793.661133
370.207153 9330.914063
371.228851 74484.070313
372.178833 6015.645996
372.229706 7285.549805
373.171417 6221.175293
381.213074 498060.093750
382.215973 88087.812500
393.176422 4092.804199
398.162598 5533.181641
399.223633 464696.343750
400.226196 96203.476563
408.221283 5361.387207
412.255737 6303.998047
416.177368 29648.421875
423.225830 7686.605469
425.201477 7039.854004
426.231293 4057.844971
427.176178 6292.833984
428.137360 9608.041016
429.196045 15164.671875
433.203705 181482.765625
434.202606 29530.251953
441.236298 46019.156250
442.230591 8335.029297
445.166901 24869.443359
451.214508 4993.581543
452.247192 18230.632813
453.244385 19275.072266
457.193604 45507.246094
458.197144 8706.108398
460.250854 7660.343750
468.281372 5882.677246
469.229523 171971.671875
470.229065 32182.658203
471.255157 7170.226074
478.265991 19137.103516
487.212616 17827.218750
492.246765 4952.917969
495.294708 7251.893555
496.206207 6268.476563
496.277832 23284.783203
504.241302 175098.937500
505.248657 28735.101563
506.258148 4664.774902
512.270691 21795.601563
522.213440 6155.193848
523.210266 6643.568359
524.273376 6374.583984
526.249634 5850.263672
540.269226 87438.187500
541.273682 25183.384766
542.281311 9434.035156
549.298767 5325.431641
552.266968 45539.984375
553.269897 7310.873047
556.232666 9055.207031
557.289673 23851.445313
558.234070 34465.527344
559.242493 5782.805176
566.327515 38232.453125
567.332092 5731.723145
570.277832 47568.796875
571.273682 22160.990234
573.261963 21320.835938
574.249390 58066.878906
584.335632 17834.041016
589.295837 8507.599609
591.273254 666845.000000
592.276489 148667.234375
593.278625 16393.955078
594.313843 6215.703125
597.311401 6146.593750
607.303650 24992.664063
609.289429 20476.242188
623.299805 12808.063477
625.320862 70362.648438
626.315735 17432.349609
632.322632 4670.307129
635.298645 32082.111328
636.300781 7569.779785
637.299622 5478.503418
640.335449 4736.562988
641.317383 31692.539063
651.301575 5683.455566
653.309875 32878.960938
654.311829 19721.832031
659.306702 8979.773438
665.348572 15021.873047
668.325562 111113.531250
669.329102 35310.039063
671.329102 29724.562500
679.409851 6453.237793
686.344543 5917.309082
687.331726 8674.754883
691.341858 5636.554688
692.327637 21273.880859
704.356506 186631.359375
705.362915 51484.726563
706.346375 21659.673828
707.340576 7144.451172
710.342163 8896.585938
718.343262 43439.296875
719.341187 7154.846191
724.351563 26416.929688
725.359375 9657.574219
726.363647 25518.378906
727.374268 8367.170898
734.363647 5906.176270
736.346558 65163.062500
737.354797 24941.519531
739.389221 9037.745117
740.385742 8613.931641
741.393677 5045.340820
742.367920 19931.101563
743.378906 5142.256348
749.377625 18151.908203
750.372070 17858.498047
751.376587 6916.350586
753.374268 5056.642578
754.362122 157299.703125
755.367249 48839.277344
756.362244 6606.297852
767.393127 127863.296875
768.394836 39458.542969
769.378235 25502.708984
770.372314 8253.693359
787.395813 18891.404297
788.383362 18918.550781
805.404602 371631.375000
806.408813 102218.523438
807.407104 28412.542969
812.906982 7129.378906
813.398193 17905.617188
813.907654 6868.637207
820.424683 5918.154785
821.247192 5368.273438
821.400635 13158.403320
821.918091 64978.441406
822.418579 83551.531250
822.915894 17463.714844
823.426331 27752.708984
824.424683 6302.995605
825.411804 6265.781250
831.418945 22517.451172
832.417358 7165.052734
834.395630 5487.604980
835.407532 5514.044922
838.429016 56816.394531
839.443298 38230.261719
840.440125 19245.630859
849.437439 54206.019531
850.443359 36181.117188
851.430725 15307.275391
852.408752 7640.038574
858.439819 27670.726563
859.427002 30265.882813
863.921570 6192.566895
867.446167 141417.484375
868.444397 86840.406250
869.449707 9003.286133
870.422302 25311.980469
871.412048 7022.530762
872.442627 18411.332031
872.934387 20401.490234
876.441956 633412.625000
877.445190 236232.734375
878.453003 33491.007813
892.446106 6989.064453
894.460022 17743.439453
902.458191 20241.890625
904.953674 7756.769531
907.457520 5822.669434
910.485840 5578.186523
920.474060 40731.683594
921.467346 86271.031250
922.473633 37594.148438
923.470642 6147.288574
933.463562 6073.943848
938.482971 67560.476563
939.479126 84553.851563
940.480164 29898.550781
951.484314 7849.491211
952.459412 7782.603027
955.491272 28509.164063
956.499939 7737.015625
957.494568 22998.449219
958.487610 17070.394531
959.495911 5405.663086
963.506836 5632.319336
964.517761 5495.852539
965.499207 5102.748535
969.485229 30449.064453
970.498962 17035.712891
975.510742 362637.031250
976.510742 142920.562500
977.511902 18676.511719
990.007507 5394.656250
990.509705 5579.281250
994.508423 7293.807617
1003.013000 25931.541016
1003.512634 40370.386719
1004.019409 7214.198242
1004.498047 17161.277344
1012.018799 25171.843750
1012.525574 56047.089844
1013.011963 21913.236328
1020.552490 27489.626953
1021.027344 158033.640625
1021.528503 197751.843750
1022.025818 77066.617188
1022.514465 20485.123047
1023.516602 7122.844727
1024.561035 7491.586426
1034.552979 90699.757813
1035.553833 45186.773438
1040.522827 18809.214844
1041.521606 6759.189941
1048.535034 26192.013672
1049.524414 8528.160156
1052.561768 28476.740234
1053.553101 6925.270020
1066.541260 84316.039063
1067.547729 44330.804688
1068.548706 18680.279297
1085.555786 21541.931641
1086.542603 95043.023438
1087.545410 41868.902344
1088.540649 7206.011719
1103.569946 301301.562500
1104.571289 140016.250000
1105.564941 29494.869141
1121.583252 19013.283203
1122.582153 9116.107422
1123.571533 14820.175781
1135.596680 17239.607422
1139.579224 27422.005859
1140.588623 16606.384766
1141.579224 6189.714844
1147.597534 17283.925781
1148.596802 8477.249023
1156.595947 21911.292969
1157.583008 47504.316406
1158.597412 19131.744141
1165.614502 101049.164063
1166.611816 59326.058594
1167.612915 9450.950195
1174.606689 646866.000000
1175.609375 348605.125000
1176.606689 62214.796875
1218.647339 9346.020508
1219.637695 15961.251953
1236.641968 64344.945313
1237.646606 27344.738281
1238.654053 5934.461914
1270.671143 19305.515625
1271.679077 6184.874512
1287.692383 231662.546875
1288.690552 148046.640625
1289.690552 34841.902344
1319.691284 49370.652344
1320.690918 22715.958984
1337.694702 21953.230469
1338.706787 7064.275391
1381.722778 7539.288086
1398.717407 17588.062500
1399.730469 19468.767578
1416.734741 139839.031250
1417.739624 90090.101563
1418.740234 30628.621094
1432.785034 32195.703125
1433.766235 31800.835938
1434.760620 7212.983887
1451.799561 6377.242188
1496.704346 14803.560547
1497.739136 16309.605469
1527.776855 6820.373535
1528.745483 18004.925781
1545.771851 76918.140625
1546.779053 53149.988281
1547.792236 14999.369141
1607.822754 8477.251953
1624.811646 48814.183594
1625.819336 95025.585938
1626.796143 56093.160156
1627.802979 7703.729492
1642.831177 1068107.500000
1643.829102 842800.375000
1644.819092 236038.296875
1699.838379 9371.269531
1743.878906 114963.250000
1744.870972 88008.429688
1745.868530 30633.593750
1827.959106 6247.979492
1844.929199 119669.632813
1845.926514 114916.679688
1846.915527 39619.050781
1943.991821 6846.456543
'''

rslt = string_of_spectrum.splitlines()
# print(rslt)
# print(len(rslt))
title = 'b1906_293T_proteinID_01A_QE3_122212.56082'
pep_mass = 1021.0269
pep_seq = 'PVTTPEEIAQVATISANGDK'

string_of_spectrum2 = '''114.617485 9781.066406
115.086624 5880.285156
115.206055 3139.882568
120.081009 88952.578125
129.102341 367150.656250
130.050339 4212.109863
130.078537 2610.970703
130.086624 26653.794922
130.105881 12896.693359
131.081619 21027.130859
132.078430 2997.281982
136.075775 6393.521973
141.066101 12841.688477
141.102661 8873.853516
143.081909 6675.307129
147.112686 110294.226563
152.586227 3845.483643
157.060547 5990.867676
157.097214 35108.539063
158.092453 27516.019531
159.065781 4147.689453
159.075958 43281.644531
167.082703 4335.408203
169.060608 8669.788086
169.097244 21924.669922
170.044754 4943.368652
173.092484 4496.451172
174.087357 9665.976563
183.112900 23263.445313
183.148880 22890.935547
184.071686 30248.658203
185.056625 4855.277832
185.077911 4048.438232
185.092209 30762.005859
185.165207 31920.941406
186.087234 84244.679688
186.124084 5271.318359
186.169174 4615.034180
187.071304 73426.906250
187.086945 7342.270996
196.071213 4019.000000
198.087646 6246.000977
199.107330 52067.117188
199.181030 13073.910156
200.139908 20413.496094
201.123154 9995.136719
202.082184 133639.421875
203.085373 7402.092285
203.102463 7115.775879
209.091492 6513.123535
211.108398 6679.153320
211.143967 24150.054688
212.103134 24788.058594
212.138794 35415.574219
213.159622 48185.515625
214.118393 29377.599609
214.163544 4625.718262
216.097977 11506.295898
226.117676 12168.700195
227.101288 144152.859375
227.134552 4107.428223
227.175659 40871.179688
228.101288 11183.442383
228.109726 9617.317383
228.133759 105555.710938
228.176178 3815.127930
229.118011 26476.607422
229.138031 7304.250977
230.077026 5594.704590
230.113724 28794.738281
230.149673 57567.921875
231.097672 5211.894043
235.107574 7052.508789
238.082764 5120.755371
239.065765 4914.235840
240.096756 6744.722168
240.133316 39136.132813
242.113510 6085.539063
245.113358 23245.142578
249.158417 8294.722656
255.109055 77989.968750
256.092102 21258.390625
257.123993 81905.992188
258.146027 57209.410156
260.123169 6469.284180
268.129517 10649.229492
268.165253 4958.394043
269.160248 53982.292969
270.143433 8828.173828
272.125793 6729.602051
273.119080 109321.125000
274.122986 9751.143555
276.155029 64873.503906
277.155640 24915.324219
280.129242 8820.205078
283.107758 7082.128418
283.139740 29492.611328
285.157227 5939.073242
286.139679 92778.187500
287.142120 9498.726563
287.171143 56148.222656
294.179657 4685.027344
297.122253 5296.604492
297.156006 144207.265625
297.189423 8031.106934
298.159210 6903.158203
299.134705 34448.312500
301.115417 6491.285645
309.119904 21558.060547
313.152496 7050.350586
314.135010 10440.358398
314.178314 6086.764160
315.132629 7490.654785
315.165863 215474.265625
316.167389 26657.759766
323.170685 6700.884277
326.145416 65000.019531
326.181976 99037.914063
327.128479 44523.285156
327.204834 44101.234375
328.160614 45987.957031
328.193420 4369.039551
332.192627 8701.614258
334.139801 48167.703125
335.139313 7449.056641
337.187012 25976.076172
340.191284 21313.847656
341.181702 36398.414063
343.162262 12475.745117
344.155762 138165.625000
344.193390 40883.859375
345.159698 12135.333008
350.181915 9009.039063
351.165863 8009.494141
352.160461 33978.492188
354.139465 7177.729004
354.177002 8474.628906
354.214966 6369.532715
355.159637 8538.697266
355.197357 82456.023438
356.200043 10993.504883
357.175964 9060.601563
366.356628 5398.638672
368.194214 43285.234375
369.174469 15166.041016
370.173645 9106.831055
372.187378 6684.209961
373.207855 1445618.625000
374.162628 8791.000977
374.211029 268800.250000
375.214203 43128.941406
376.219604 6081.026855
377.143829 6321.164551
380.155640 37561.394531
381.173096 5647.304199
382.167847 6022.654297
386.202393 26080.312500
388.179108 4924.770020
396.227692 12217.166992
397.179718 45091.191406
398.166779 132447.078125
399.169281 25079.796875
399.226471 13086.596680
405.215942 7755.353027
407.241119 8780.257813
409.172455 5004.708496
411.240601 6299.507813
412.221680 5439.021973
413.176514 6042.325195
414.236816 18985.486328
415.192993 128367.765625
416.196869 10335.910156
423.227600 4927.099121
424.145569 7558.980957
425.251312 96818.171875
426.201172 12652.036133
426.251923 26121.500000
427.195557 7600.667969
429.195709 5799.309082
433.200958 35457.613281
434.212067 5813.188965
437.183411 5460.817871
437.238953 42329.726563
438.242645 6550.650879
441.171417 26543.701172
443.205017 8975.772461
443.262207 190343.031250
444.208740 7165.548828
444.264496 34778.574219
445.207581 8302.357422
445.263916 5231.504395
449.170563 22683.421875
451.196259 5227.139648
455.250885 8015.856445
457.240967 24019.494141
458.198273 24951.671875
466.201599 6779.562012
467.187469 10752.770508
467.259460 7372.565918
468.207916 9553.284180
469.209045 6602.356934
477.177063 6194.860352
477.250885 5560.638672
480.229340 4901.419434
481.202820 7736.605957
484.216095 7124.124512
485.197174 6682.574707
485.269867 9316.559570
486.220947 19561.654297
486.291687 68608.414063
487.293243 11281.437500
494.113861 4694.559570
494.189606 5367.723633
494.268951 7635.781738
495.181946 10372.665039
495.257111 6142.303223
497.238647 7606.505371
498.232849 9220.866211
499.217529 6995.536133
502.227661 6956.613770
506.258392 6320.038574
510.235352 11837.370117
511.226898 22775.376953
512.214111 40633.980469
512.279968 37376.980469
513.207886 6111.325195
513.279114 9030.631836
514.296509 26294.009766
516.242004 7273.797363
517.239014 25069.972656
522.748108 6528.316895
526.268250 19274.132813
528.240173 11411.335938
529.236328 77727.796875
530.241394 33888.339844
537.236084 12964.440430
538.233093 20830.841797
539.288940 8237.243164
540.311646 7891.881836
545.241028 49993.128906
553.286682 9274.175781
554.260132 24679.560547
555.238342 38260.285156
556.238708 21476.400391
563.211731 26842.582031
565.336121 29088.023438
569.309265 20625.226563
569.763733 6910.819824
571.286133 28036.830078
572.286682 9816.687500
573.279846 62425.484375
573.784485 9179.667969
574.270752 22151.130859
578.276306 46118.730469
578.778015 24175.457031
583.345093 1172306.750000
584.253845 11721.065430
584.347961 348859.562500
585.353577 71480.507813
587.280396 164300.531250
587.782898 77279.500000
588.282288 34866.703125
591.267639 9242.708008
593.346313 6945.025879
599.260437 6226.454590
600.285339 28085.875000
600.791260 6263.767090
601.300537 7044.514160
602.257751 26058.455078
603.259094 6872.096680
605.255798 20365.441406
607.303772 9624.283203
608.274353 9904.420898
611.265625 7640.826660
611.356262 92127.648438
612.355713 22951.642578
613.367249 7970.670410
613.815308 7259.421875
614.305237 10667.121094
616.262146 7948.180664
619.283508 21743.453125
622.814209 39881.355469
623.313110 34777.156250
625.296265 38583.144531
626.309570 12351.814453
627.810608 32402.126953
628.313477 33533.515625
629.298584 7452.985352
636.815186 64638.667969
637.313354 51146.441406
637.817322 10872.135742
641.316284 8672.624023
642.318054 43983.847656
643.320435 47311.140625
643.826843 22707.462891
644.301392 23937.292969
649.824768 11558.243164
658.316101 7504.168945
660.336792 9048.118164
661.335083 8530.537109
662.271790 47627.714844
666.316040 7555.322754
668.375732 45829.488281
669.380432 10124.974609
670.283142 9309.530273
671.337158 9297.419922
672.342896 8436.625977
673.330566 27370.634766
674.319519 10506.254883
678.336182 6576.070801
679.338501 8319.866211
680.340881 9139.381836
684.338745 29437.251953
685.333008 10190.883789
688.311829 22372.511719
692.333008 9190.571289
693.353027 24174.507813
693.854675 26744.142578
694.379089 115304.296875
695.384277 55973.656250
696.369507 20741.423828
697.362427 11281.811523
699.358398 7679.460938
700.338623 7425.432129
701.334717 12555.729492
703.308594 30630.044922
704.311401 8125.793457
707.342957 7114.031738
712.390991 164577.812500
713.301208 15486.345703
713.397949 65924.765625
714.374573 26560.867188
715.365417 9629.188477
718.335938 6810.187988
719.344666 7302.085449
723.330811 11692.460938
725.395935 41601.765625
726.392273 9652.844727
728.371155 6651.278809
729.349792 12741.618164
730.353210 36726.597656
731.296875 151595.484375
732.298950 69993.695313
733.306580 11331.967773
734.351379 28115.773438
735.357483 21998.355469
736.362244 8819.443359
737.359619 7290.196777
740.325012 9874.292969
741.371521 54886.191406
741.866882 10785.424805
742.366394 39525.574219
744.356506 6634.970703
748.345886 11438.875977
748.859863 7724.479492
750.377136 41264.531250
750.879333 28290.574219
751.382874 24428.636719
757.351868 9956.802734
758.346741 12427.612305
759.343262 11456.316406
763.378601 11485.231445
763.883484 6625.661133
764.378357 9117.684570
765.370544 25221.205078
771.360107 23570.734375
771.880249 9718.934570
775.361877 29853.787109
775.885437 20918.287109
776.367432 35380.082031
779.883545 9023.529297
780.382568 8189.061035
783.378906 39412.210938
784.374329 24776.011719
784.892700 53086.566406
785.385559 60099.187500
785.883606 33566.949219
786.396057 28312.386719
793.895325 53963.906250
794.396606 70104.609375
794.894348 35535.906250
795.412598 7933.244629
796.429382 8632.808594
798.398010 24933.662109
801.395508 43244.523438
802.384094 37184.867188
803.393494 21925.189453
806.397522 12936.103516
806.898438 36172.554688
807.400330 26410.867188
807.907837 7588.911133
811.393982 24742.742188
811.898315 20667.148438
812.358826 36656.023438
813.439148 256983.531250
814.438904 110039.578125
815.424866 29359.894531
820.405090 28114.531250
820.908325 25593.955078
821.404663 21750.662109
821.908142 9140.359375
822.404053 10047.992188
829.390869 27730.335938
829.915222 11734.672852
830.367615 199723.640625
831.372437 103845.203125
832.384705 26035.730469
833.401855 12314.036133
835.412109 12418.872070
836.408020 6879.221191
840.420959 201689.468750
841.421936 86840.546875
842.417175 28378.677734
842.908875 23377.845703
843.423584 9163.382813
847.398376 31913.691406
854.410156 6698.305664
855.398560 8551.064453
856.405945 24000.626953
857.425476 12172.226563
859.395203 47211.003906
860.406189 27450.693359
864.930847 23127.449219
865.437439 28062.283203
865.933228 9013.428711
866.437012 12307.900391
870.420532 26284.310547
871.415588 7408.417480
872.419922 37195.527344
873.412659 7299.929199
883.420105 8644.929688
884.424255 9837.666016
888.419556 53783.414063
889.422974 33154.445313
890.425476 27973.468750
896.468994 10404.033203
898.411133 11689.027344
899.436035 31409.402344
899.943542 10253.849609
900.422913 9950.683594
901.424438 7613.105957
904.437561 9208.833984
904.939087 9562.536133
908.455994 9968.003906
913.444397 29934.193359
914.482788 347111.343750
915.485413 173119.890625
916.494446 51891.742188
921.954590 29180.076172
922.462036 38675.699219
922.957947 10828.340820
925.438965 22837.964844
926.444458 11669.483398
927.446716 27958.214844
928.458557 9708.202148
929.448059 22145.490234
930.448303 10089.587891
940.459351 29064.328125
940.956726 11771.876953
941.463745 10528.831055
943.452332 100834.710938
944.452393 52503.941406
945.447510 53945.367188
946.442200 10297.729492
948.464722 30937.078125
948.958679 51843.968750
949.466064 45100.042969
949.959900 21910.113281
950.461121 21300.693359
951.459106 9628.478516
952.450317 9518.092773
953.493103 9068.875977
954.470276 7782.401855
957.469482 151562.500000
957.972473 161788.796875
958.466736 126846.320313
958.965881 22374.625000
959.475525 44845.484375
960.457764 34128.691406
969.470215 38694.070313
970.463074 26810.457031
971.487793 10186.124023
978.467896 8938.918945
986.475159 31234.261719
987.489136 154246.281250
988.498596 69458.054688
989.488403 33348.125000
991.486328 8306.510742
992.482727 36004.992188
992.978455 27725.548828
997.516052 40726.253906
998.522034 20136.634766
1001.487305 23412.753906
1005.464050 11455.525391
1008.504761 9448.024414
1013.499573 21015.013672
1014.514404 9905.223633
1015.530640 604323.062500
1016.534058 339954.781250
1017.535645 102672.890625
1018.166443 11847.820313
1018.497620 40803.082031
1019.483398 12778.421875
1024.176025 10810.394531
1024.516602 10125.229492
1026.500977 25100.744141
1027.486450 30864.527344
1028.501709 24421.949219
1029.506958 42122.253906
1030.489746 19699.564453
1039.480469 11792.472656
1040.478882 31270.826172
1041.494019 24441.048828
1042.518921 27343.367188
1043.523315 22400.435547
1044.505005 102852.242188
1045.502686 68038.437500
1046.491211 40743.562500
1047.485840 19113.037109
1056.494995 27283.767578
1057.494019 91524.242188
1058.502075 57717.746094
1059.511353 31518.396484
1061.512329 10153.620117
1068.563721 41338.105469
1069.538940 32251.363281
1070.006226 9868.956055
1071.545654 39647.671875
1072.540649 21280.615234
1074.486572 145265.218750
1075.491699 81807.859375
1076.503784 31772.484375
1077.521240 9329.769531
1078.523926 27424.099609
1085.511963 9545.113281
1086.567505 513908.593750
1087.569214 309787.406250
1088.568726 100270.679688
1089.555786 12641.826172
1098.526245 28775.447266
1099.528442 21689.371094
1101.504639 10179.592773
1102.496582 9415.498047
1109.556396 11176.945313
1110.552734 10904.219727
1111.552368 21446.828125
1116.534912 27757.759766
1117.541138 22708.222656
1126.520386 22598.951172
1127.529663 25821.699219
1128.543213 23240.384766
1129.553589 20602.005859
1137.556274 11993.052734
1138.563232 21812.808594
1144.525024 57359.507813
1145.550659 63499.132813
1146.550293 48597.019531
1155.571167 123024.609375
1156.579468 86255.054688
1157.570557 32458.230469
1171.574951 19889.582031
1173.585327 1571883.750000
1174.588501 946495.500000
1175.587646 300987.687500
1176.575439 62282.062500
1190.590698 9506.073242
1197.559692 36075.523438
1198.546875 36608.210938
1199.561768 45989.121094
1200.582031 24678.789063
1215.577026 31893.919922
1216.566772 10024.403320
1225.567749 9646.595703
1226.613403 60536.171875
1227.072021 9731.592773
1227.611816 27177.783203
1229.613770 23822.566406
1230.607178 21778.406250
1236.619873 11249.469727
1244.634277 573148.375000
1245.636108 322439.937500
1246.635864 118617.296875
1247.640747 21533.722656
1254.614136 77911.382813
1255.609497 43918.554688
1256.614868 22136.136719
1257.617065 11504.914063
1269.599854 12112.032227
1272.621948 458126.625000
1273.623291 298968.343750
1274.624512 116371.101563
1275.621826 33924.761719
1283.605591 10997.834961
1286.628540 73407.992188
1287.619995 50665.093750
1288.619751 21153.056641
1296.625000 12619.776367
1298.632324 30253.380859
1299.639771 12457.392578
1313.628906 22566.804688
1314.630127 35004.308594
1315.622925 11374.789063
1323.147339 10216.244141
1323.650635 25058.441406
1324.635864 32222.216797
1325.644897 22286.660156
1340.663452 40863.105469
1341.656616 108117.750000
1342.660400 63594.968750
1343.666748 39987.730469
1344.672485 20081.056641
1357.687500 26899.410156
1358.680786 576054.062500
1359.682373 399218.687500
1360.684937 171283.781250
1361.689819 36678.121094
1367.706055 37148.589844
1368.684326 22458.197266
1369.673706 40348.582031
1384.657959 11655.484375
1385.705444 283576.281250
1386.704590 219479.015625
1387.705322 100134.796875
1388.712646 21669.857422
1394.711426 14297.381836
1400.667358 31881.775391
1401.661499 20789.089844
1402.692871 21367.416016
1411.708008 62942.339844
1412.698853 125299.757813
1413.695435 80616.992188
1414.705322 26944.474609
1415.695190 21212.769531
1429.718750 514706.187500
1430.715454 366902.687500
1431.717285 164963.484375
1432.732422 44338.605469
1440.701294 26554.222656
1441.675293 23169.380859
1443.705566 12528.763672
1454.665771 12010.682617
1465.720459 22398.609375
1471.690063 52659.792969
1472.688721 50025.742188
1482.736572 32969.027344
1483.732178 53020.093750
1484.707642 43647.421875
1499.750488 125030.617188
1500.751221 262009.765625
1501.757202 182894.218750
1502.749023 80433.132813
1569.770264 11573.169922
1570.762573 51264.339844
1571.773926 35145.898438
1586.796875 42597.960938
1587.790405 173190.093750
1588.784790 138044.328125
1589.789185 62201.222656
1590.808472 10654.095703
1639.803467 11848.007813
1640.805054 21241.646484
1657.824219 50985.511719
1658.819336 39525.023438
1659.815430 27369.033203
1667.781128 10762.351563
1683.811646 23447.171875
1684.808105 69500.210938
1685.811890 50811.546875
1686.798096 23612.830078
1701.831665 147827.046875
1702.831543 130087.671875
1703.822876 61941.722656
1704.828979 12555.162109
1711.830933 11556.490234
1712.796387 22414.990234
1728.871582 47288.148438
1729.869995 38732.558594
1730.838989 24674.062500
1798.887451 23000.779297
1814.915405 45204.625000
1815.933105 54945.718750
1816.908813 23501.902344
1914.939453 12714.897461
1915.934937 9285.228516
'''

rslt2 = string_of_spectrum.splitlines()
# print(rslt)
# print(len(rslt))
title2 = 'b1906_293T_proteinID_01A_QE3_122212.53744'
pep_mass2 = 1029.5142
pep_seq2 = 'VGGTKPAGGDFGEVLNSAANASATTTEPLPEK'


def make_spectrum_data(string_of_spectrum):
    spectrum_splitted_by_line = string_of_spectrum.splitlines()
    len_of_spectrum = len(spectrum_splitted_by_line)

    test_data = np.empty((0, 2), float)

    total = 0

    for i in range(0, len_of_spectrum):
        [x, y] = spectrum_splitted_by_line[i].split(' ')
        # print(x)
        # print(y)
        x = float(x)
        y = float(y)
        # print(type(x))
        # list = [x, y]
        total = total + y  # %로 바꾸기 위해 intensity의 합을 구한것.. 근데 매치되는 애들만 구해야하는 듯 하다..?!
        test_data = np.append(test_data, np.array([[x, y]]), axis=0)

    # print(test_data)

    return test_data


def return_data1():
    test_data = make_spectrum_data(string_of_spectrum)
    ms_data_list = [title, pep_mass, pep_seq, test_data]
    return ms_data_list


def return_data2():
    test_data2 = make_spectrum_data(string_of_spectrum2)
    ms_data_list = [title2, pep_mass2, pep_seq2, test_data2]
    return ms_data_list
