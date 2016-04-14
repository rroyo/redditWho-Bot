import utils, praw, re

subreddits = ['1te2ni','1te3fe','1te6tf','1te88n','1te97f','1teair','1telse','1tesuq','1tf6wg','1tftok','1tg3gd','1tghd1','1tghvs','1tgkyw','1tgn67','1tgte5','1th3i3','1th42m','1thp0l','1thunp','1thw9b','1thwvk','1tiebr','1tit5u','1tiwkh','1tiz5w','1tj003','1tj302','1tj3or','1tjgyq','1tjjeu','1tjk8j','1tjlnb','1tjycv','1tjz26','1tk4bu','1tkymq','1tl06s','1tl26r','1tl845','1tlmtn','1tlst5','1tlszv','1tly77','1tlynp','1tm16c','1tm209','1tm67a','1tmbyc','1tmp5e','1tmqh0','1tmtjr','1tn074','1tn56j','1tnyd9','1to5jo','1to60b','1tockm','1toct6','1toed2','1tolxk','1tomvu','1tomxf','1toq0u','1tp2nx','1tp8lz','1tppj3','1tq459','1tqgkv','1tqicr','1tqjs5','1tqjti','1tqyzd','1tr0pe','1traox','1trc4c','1trjt8','1trvet','1tsfyd','1tsvqi','1tsyph','1tszsy','1tt08z','1tt8ls','1ttbas','1ttkon','1ttsg4','1tttip','1tty61','1tufy8','1tugsw','1tumdu','1tv2gz','1tv7ht','1tvkdh','1tvlo0','1tvn2i','1tvq11','1tvr5f','1tvvbe','1tw6ov','1twj6i','1twult','1tx0yx','1tx3i7','1txnnb','1txu62','1txvh3','1txwxp','1txzez','1ty1j3','1ty1mh','1ty59u','1ty5au','1tyeyh','1tyv44','1tyxmg','1tz33j','1tzc82','1tztvi','1u0bgv','1u0kjc','1u0kku','1u0nex','1u0syq','1u0wwy','1u0zal','1u1pyt','1u1s41','1u27ld','1u2cfg','1u2e6x','1u2kke','1u38mr','1u3a2w','1u3g87','1u3g91','1u3st4','1u3u1f','1u4amt','1u4sz2','1u4z4g','1u561j','1u5fw3','1u5n6k','1u5phn','1u5qut','1u5s9q','1u65za','1u6eqe','1u6j7d','1u6kg2','1u6lpx','1u6xar','1u6z6h','1u829s','1u83wz','1u848u','1u86l7','1u87y8','1u88l2','1u8eqk','1u8iw4','1u8rz6','1u98g1','1u9k6x','1u9ovd','1u9tv0','1ua5m2','1uac3m','1ub3iy','1ub3q4','1ube12','1ubyw0','1uc545','1uc9is','1uc9rj','1uce74','1ud9tl','1uda2h','1udamk','1udcmg','1uddi7','1udls5','1udwd1','1ue1ku','1ue2qf','1uebo6','1uedls','1uefd9','1ueg04','1uff1f','1ufo17','1ufpu3','1ufrrq','1ugctj','1uggjn','1ugix3','1uglyg','1ugt84','1ugtkn','1uh2bw','1uh8lc','1uhr0b','1uiafz','1uixb1','1uj4lx','1ujbw7','1ujdk6','1ujn41','1ujnf8','1ujqs4','1ujr1l','1ukmjf','1ukori','1ukza3','1ul2xx','1ul8ac','1uljf6','1umaqn','1umcux','1umdez','1umniy','1umukz','1umwza','1umz1w','1un2ta','1unchy','1unid1','1unm9k','1uoard','1upbz3','1upel3','1upflb','1upkn0','1upleh','1upmim','1upmk2','1upoxc','1upvhz','1uq5co','1uqdtz','1uqhs4','1ur1jo','1urbfk','1urrdg','1ursuy','1urvjz','1usk64','1uslir','1uslpk','1usry1','1ustwi','1ut65r','1ut6xc','1utyul','1uug8z','1uuikw','1uupzk','1uus6f','1uvj2h','1uvopo','1uvp3i','1uvp6a','1uvs7g','1uvv9r','1uw0aa','1uw77h','1uw876','1uwd9h','1uwhyu','1ux4wc','1uxaeq','1uxqe7','1uxvso','1uxysi','1uxz93','1uyi8w','1uyjpi','1uyovc','1uyr8c','1uz43n','1uzenx','1uzf9p','1uzmkc','1uzt83','1v03pr','1v0hfh','1v0mdy','1v127f','1v1m1g','1v1p7t','1v1t93','1v1zes','1v286y','1v2adi','1v2tee','1v2zmk','1v36z9','1v370x','1v3plm','1v3ttl','1v3w5i','1v3x7d','1v3yzm','1v40kl','1v415d','1v41y3','1v487x','1v48gw','1v4k0w','1v4o40','1v5vo3','1v5zt2','1v6pp9','1v6t0v','1v6u3o','1v701x','1v718v','1v71vd','1v7fos','1v7jgi','1v7sla','1v7sn7','1v7ubs','1v8oko','1v8qsc','1v9lg7','1v9nf1','1v9oo0','1v9prj','1v9ptb','1vabko','1vaj6y','1vaofl','1vau0f','1vax4g','1vbjcq','1vbozt','1vbvh1','1vc6b0','1vcpy7','1vctwp','1vd80b','1vd9lj','1vdb5p','1vdlch','1vdr8o','1vdyrd','1veeqi','1ver43','1vetuy','1vfpbt','1vftrr','1vfwwh','1vfzt0','1vg0ue','1vg4zn','1vgl09','1vgrfq','1vgrsq','1vhbbq','1vhtuq','1vi37d','1vildm','1virg3','1vis3s','1viwcy','1viwh5','1viz28','1vjf0e','1vjuqo','1vjyrk','1vk3x8','1vkbxd','1vkgvg','1vkzbz','1vl4eb','1vl9hl','1vlaph','1vlell','1vlg83','1vlhoq','1vlkyt','1vm3uv','1vmg6o','1vmti3','1vn56s','1vn6e5','1vnzph','1vo51v','1vo53q','1voaj1','1vooq6','1vp7xf','1vpr9r','1vqy81','1vqzrd','1vr6c4','1vr7sh','1vraso','1vre0r','1vre14','1vrivy','1vrsyi','1vrw66','1vskw5','1vtlja','1vtxov','1vu9gk','1vuf8d','1vug9e','1vuhvg','1vuoip','1vuw50','1vuwpu','1vv7sl','1vveam','1vwg7l','1vwrom','1vxh76','1vxo78','1vxp74','1vxycp','1vybt5','1vydbu','1vye4s','1vyg6l','1vzaiz','1vzw8f','1w02lw','1w0amr','1w0wr2','1w0zat','1w0ztw','1w105k','1w12af','1w12mp','1w14wy','1w16ir','1w18p4','1w282b','1w28fw','1w2yz9','1w3uqv','1w3x7c','1w3xbx','1w3xv2','1w47tp','1w4fun','1w4n7l','1w50uu','1w5t8x','1w634a','1w6r44','1w6szo','1w70we','1w715h','1w7buj','1w7lcj','1w7yqg','1w8bwh','1w8qf1','1w8vhz','1w91pv','1w9afv','1w9vh6','1wa02m','1wa360','1wa69j','1wadvq','1wao86','1wapy2','1wb3id','1wd5wh','1wd6vk','1wda9o','1wdam0','1wdd04','1web8d','1weknp','1wesao','1wgibu','1wgj3r','1wgtqk','1wh86m','1whceh','1whvqf','1wi6ie','1wjkm6','1wjrdg','1wjurf','1wjvsf','1wjy5y','1wk0oa','1wk1ll','1wkbcf','1wkh04','1wli9c','1wlvbp','1wlvwk','1wmy8c','1wmz4e','1wn1f9','1wn55t','1wn68x','1wn9b2','1wnb0i','1wnbzc','1wntee','1wnzda','1wpq83','1wq3oc','1wq481','1wqess','1wqivi','1wr3oc','1wr7oh','1wrbt5','1wruf3','1wsvyz','1wszp1','1wt0m7','1wt18z','1wtcka','1wtks7','1wtnwd','1wuk9v','1wuqb6','1wuwbg','1wv20f','1wvruf','1wvs80','1ww09m','1ww0ku','1ww3e2','1wwjbs','1wwmb7','1wwo1i','1wwqzs','1wwu6d','1wwvt4','1wwvwp','1wx8ux','1wxzfa','1wydet','1wykrq','1wz79s','1wz92v','1wz9pl','1wzen4','1wzhyc','1wzw39','1x05ha','1x08ve','1x0my4','1x1mml','1x1pdm','1x2sjv','1x2tkf','1x2umf','1x34t4','1x36c2','1x3bn9','1x3dhm','1x3gt1','1x40oc','1x493d','1x49n8','1x56ss','1x5e9c','1x5jog','1x63tz','1x64f2','1x66cp','1x67nt','1x6fhn','1x6i6r','1x6kvc','1x6lem','1x6o56','1x6su0','1x7cfa','1x8h9x','1x9gqt','1x9h2n','1x9ipj','1x9kqq','1x9rh0','1xa2sr','1xa6vx','1xafq0','1xau8p','1xb0a2','1xb356','1xbrp1','1xbux3','1xbwlk','1xcak4','1xcfqm','1xch3y','1xcj9o','1xcle9','1xcx44','1xd75z','1xds5a','1xdzwr','1xe5og','1xe9zu','1xenn8','1xev23','1xf4u4','1xfdnd','1xfhpk','1xfi1c','1xfi5d','1xfws7','1xfz8h','1xg0sz','1xh0mf','1xh4qg','1xh5uv','1xhfq7','1xhftx','1xifdy','1xj01o','1xj2ll','1xj35c','1xj3iv','1xj5d9','1xj8z4','1xjc7y','1xjhqq','1xjptn','1xjrb3','1xjv73','1xls4i','1xlsrf','1xlxk3','1xlxmx','1xlzkn','1xm5jx','1xmma6','1xmtnl','1xnaq6','1xnas2','1xotoe','1xoyh3','1xp1sr','1xp749','1xp9w1','1xpkvl','1xpq6g','1xptjx','1xpxsc','1xqa8n','1xqg6n','1xqpzz','1xrbux','1xs68x','1xsapq','1xsg5b','1xsqs4','1xsv19','1xtll4','1xtort','1xtypn','1xuu52','1xvcuh','1xw2jo','1xw3av','1xwf13','1xwsrz','1xwveg','1xwxdd','1xx37q','1xx5ic','1xxzew','1xyeuk','1xyktq','1xyn79','1xzbeb','1xze31','1xzfgz','1xzfkq','1xzgsa','1xzkbr','1y02w5','1y0pm4','1y0sex','1y1m1v','1y2255','1y23gf','1y23j5','1y26b3','1y26fn','1y2c53','1y2sz9','1y2tq6','1y2wy8','1y316k','1y31k8','1y3a5b','1y3k6q','1y3mzk','1y4vr4','1y4wdp','1y52yc','1y54or','1y5aee','1y5cqj','1y5d09','1y5f2a','1y5h01','1y64i7','1y67re','1y68v3','1y7cnl','1y7qco','1y8kre','1y8l41','1y8ld5','1y8r1u','1y8t59','1y8vyo','1y8xi6','1y96ag','1y9mjf','1y9wq8','1yb8b8','1ybgte','1yc1lw','1yc2ae','1yc79u','1yc8ts','1ycbcz','1ycg5o','1ych87','1ycpg1','1ycw8w','1yd4yw','1yd7hd','1ydjke','1ydkhz','1ydx45','1yei3p','1yeurr','1yfju4','1yfq9z','1yfsaz','1yfu3u','1yfxgd','1yg7n4','1ygg2t','1ygqwa','1ygz9p','1yhuxj','1yhz9u','1yi164','1yiaiw','1yiofo','1yirbn','1yj6lr','1yjbbm','1yjbsa','1yjbxo','1yjg30','1yjhik','1yjv87','1yjzwy','1ykf77','1ykr28','1yla94','1ylbex','1ym7ox','1ymee3','1ymf2v','1ymgo1','1ymhkt','1ymyp5','1ynj29','1ynj2o','1yns4f','1yom7g','1yomu8','1yp0ok','1yp5je','1yp65f','1yp75p','1ypgkb','1yphbi','1ypnxr','1yq3py','1yqndd','1yr1r1','1yraz9','1yrb1g','1yrobw','1ys9sy','1ysdez','1ysgvf','1ysl1s','1yspgd','1ysq9o','1yszno','1yszoi','1ytrl5','1yu534','1yupav','1yvli5','1yvp42','1yvw36','1yvybv','1yvzbn','1yw26m','1yw2zx','1yw417','1yw6eq','1ywcsc','1ywf63','1ywk1y','1ywukg','1yxheu','1yxtaf','1yy9k2','1yzc3f','1yzd55','1yzl05','1yzlaa','1yzpxk','1z01ro','1z0boq','1z0eqo','1z0fv1','1z0q3v','1z0v0j','1z1muz','1z2s2c','1z2wsj','1z30h4','1z30xm','1z311f','1z37uu','1z3lo3','1z3s1g','1z3yom','1z4kyq','1z62du','1z66oa','1z6a8g','1z6ar0','1z6azb','1z6dqw','1z6fx3','1z71pa','1z779q','1z8eg3','1z8gqg','1z8ps0','1z96sw','1z9clw','1z9j2y','1z9m3p','1z9zlo','1zauo9','1zb4ad','1zccef','1zcee8','1zcf9x','1zcgmy','1zcir3','1zcizf','1zcpbi','1zcu48','1zdj4b','1zdrc2','1zdz6m','1zepkj','1zf0t6','1zf5j9','1zfci0','1zfgll','1zfhio','1zfm3h','1zfy6m','1zg0rx','1zg5gl','1zgbzk','1zh5b5','1zhasz','1zinku','1zir1w','1zizks','1zj277','1zj66x','1zjjdk','1zju4j','1zksek','1zkzlb','1zlxow','1zmash','1zmb91','1zmdk3','1zn0h8','1znio4','1znlhm','1znlz4','1znpz5','1zns5n','1znuk7','1znxvz','1zpn5e','1zpo1u','1zprfw','1zprtb','1zpvno','1zq46b','1zqpoq','1zqxqr','1zr7s8','1zrg8d','1zsp95','1zsrub','1zsw6n','1zswat','1zswmz','1zt51h','1zt5sb','1ztcdf','1ztebw','1ztg7w','1zufl6','1zutdp','1zv36h','1zvrxf','1zvv1s','1zwe7h','1zwkrq','1zwycl','1zxbhl','1zxzc8','1zymqp','1zyn3x','1zyvh4','1zz501','1zz6an','1zzc44','1zzoss','1zzpfw','200j7w','201ar7','201ca0','201hc9','201kdh','201ncm','201nxj','201rgv','20236g','2029x3','202d56','202i0b','202loi','202mn5','203gjx','204asc','204i28','204myk','204pu1','204tjr','204zh3','20501c','2055xt','205ay1','205ipj','205un6','206re4','207gs8','207zhn','207zzc','2081up','20842t','2084k3','2085wv','208c7d','208p9e','208x40','2095a7','2096pd','20a8ez','20b6o9','20b8md','20bdp1','20berx','20bjbr','20bm4o','20bswl','20c0k5','20ckj6','20d6x3','20d7al','20dmui','20e79g','20e7xd','20ebc6','20ednf','20eg33','20eguy','20ej8w','20eo26','20eq9h','20fd5e','20fkwt','20fmd0','20g4v0','20gv2z','20gynl','20hac6','20hc6m','20hrb2','20hudy','20i03n','20jdpw','20jje6','20jqhf','20jsvn','20jz9a','20k3nx','20k6l5','20ku08','20l37e','20lcpf','20lhlc','20m035','20meby','20mga2','20mi40','20mi4a','20mkxl','20mnrw','20muuq','20nt4v','20ocj8','20oge2','20oh4n','20oycb','20plnn','20ppr7','20ppua','20pyat','20q6vk','20qa1v','20qi7t','20qxz5','20r1eq','20rt58','20rw0e','20szx7','20szy5','20t3nv','20tdof','20tj4y','20tse5','20u04o','20ugvt','20uvh2','20v5kt','20vfcz','20vwuw','20w7dt','20wb50','20wkwg','20wton','20x4rx','20x586','20xbia','20xhre','20xuzu','20xybl','20yo2t','20yrk8','20zeb2','20zp83','20zq3c','20zrph','20zs13','20zur1','20zvc6','210142','210k8h','211mci','211q0r','212gjl','212gt9','212jy7','2136cx','2136jg','213g02','214273','2155n2','2156vc','2158ky','2159sw','2159wp','215gzb','215nw5','2168g6','216b9x','216d7r','216jxr','216kfh','2173oq','217bvm','217tqr','21818p','2181ry','2182s7','2186ii','21879i','218bzh','218ge9','218n0a','218tso','2198v0','219d5e','219to7','21b51o','21basj','21betx','21bf6p','21bf77','21bfp7','21bklf','21bu8p','21bwur','21bxjs','21cdyc','21cgwf','21ckyq','21dkd8','21dnf3','21dv9v','21dyrq','21enm7','21enqf','21ets7','21evf3','21ex52','21f9n2','21g8yb','21h9t5','21hb93','21hqu2','21ht25','21htr7','21hzjw','21i2cr','21i4dm','21i52z','21i53s','21i59f','21ioj4','21is2f','21j7hu','21jkst','21jzxa','21k56t','21l164','21l2rs','21l2y5','21l3i9','21l4mz','21l5aa','21laha','21lbmu','21lgfi','21mehx','21ml9a','21npfj','21nq38','21ny0m','21nyw3','21o26r','21o30l','21o4nm','21o5dy','21o6rm','21od2n','21olom','21p1lw','21paoi','21pbil','21pcol','21pmg9','21pp44','21pvzt','21qcl0','21qjuw','21qp08','21qpwk','21qy6x','21r033','21r52c','21ro18','21rr9h','21rtiu','21sk3e','21tcdr','21thv3','21tmn0','21tydh','21u7p3','21u88w','21u9z0','21uk3u','21ut84','21vjtt','21vmb9','21vnws','21x1rp','21x3eu','21x84o','21x8m7','21xaqs','21xgkr','21xgmj','21xi12','21xllk','21xnrs','21xnte','21xqrm','21xuub','21xx9p','21xy50','21y16n','21y5cw','21y9ro','21ygdi','21yifs','21z96s','21zc4w','2205za','2208r6','220a3x','220eo1','220hfn','220t6u','220trw','220wq7','221apr','221lgz','2229wf','222pu0','2239bx','223d05','223ied','223je2','223uur','223zhq','224a2g','224jq5','224kf9','225e27','226f8f','226jj5','226qw4','226uui','226ywo','227hzo','227nqz','227pfi','228177','22825v','228vpq','229g6p','229hle','229t5d','229zmb','22a1pe','22a5yj','22ak9o','22bgst','22c7mu','22c9oq','22cf3s','22ci5g','22cmvi','22cxe5','22cxsm','22db0k','22dmgw','22dt8i','22evx4','22ezyh','22f1qu','22f1v9','22f305','22f8nb','22fbc8','22fvit','22g8m9','22gr0y','22h3vp','22hdvu','22ic95','22idea','22idmj','22ihk0','22ir9l','22isih','22jac7','22jcqz','22k59y','22khxy','22kxki','22lg25','22lk6n','22lkqw','22loe7','22ltuv','22lv6c','22mmbw','22muin','22nlra','22ois9','22oiur','22ol9m','22ooxm','22oqbf','22p23z','22p8c8','22peus','22phm1','22psqi','22qqfk','22qv7n','22r0e6','22r6s1','22riyb','22rqbc','22rqs7','22rxic','22sbli','22so4p','22srua','22t4rq','22ty2r','22u8yf','22uccj','22uekc','22uo82','22urz1','22v6j7','22v9p5','22vkqk','22w988','22wkv1','22wnpy','22x8xo','22x91f','22xd60','22xdv7','22xgnc','22xsoo','22y9f7','22ye91','22yf3p','22ylpy','22yvrj','22zs9w','22zspk','22ztio','22zvio','2301kq','2303bo','23040o','23075i','230dk4','230lkx','230ys4','231ps6','232n3x','233008','233159','2333rd','2338m3','2339io','233ewl','233lxd','233upw','233ven','2340xa','23430f','234bum','23587v','235ceg','236455','2368rz','236ba4','236wp3','2373p0','2377j2','2379bm','237i39','239abq','239gug','239h7w','239inj','239irp','239lyl','239ss0','239zyy','23ah4z','23asg1','23bpvm','23ci7l','23cjxu','23cmo9','23crdm','23crja','23d1tl','23d211','23d3fo','23df1b','23dqsk','23e7yh','23enhz','23falw','23fdlr','23fdz8','23feul','23ffup','23fjp0','23fptf','23fqlw','23ft4a','23gkvg','23gtya','23h8sh','23hbp5','23hh1h','23hlav','23ibbn','23ibio','23ictp','23ie12','23if14','23ijmc','23j4gs','23je1i','23jjka','23jnil','23jrhx','23ktjw','23kwlp','23kx2b','23kzb5','23l9ay','23l9b6','23le5f','23lezh','23lgxz','23llu9','23moi9','23mrl2','23mu77','23nrjk','23nyhd','23o280','23o2cw','23o4t3','23o5kc','23o8gz','23o9l4','23oa67','23ocxx','23oeql','23ol7l','23otzz','23ox7g','23pfxs','23pxjq','23q2n1','23qmks','23qnlt','23ra1l','23raxk','23rbi9','23rdsn','23rh6n','23ris8','23rryp','23rsap','23rw2j','23ssfm','23sx31','23t2l8','23t9rs','23tp3i','23ub61','23ue42','23uj2n','23uk7i','23ulai','23unqp','23urvu','23v1r6','23vefd','23vh9n','23vn4i','23vslm','23w3xu','23whkk','23wjvd','23wzh7','23x0g9','23xev4','23xtxd','23xuqh','23xzwb','23y5v3','23yh4o','23yi69','23z6hw','2401sc','2403mf','2408y5','240l6k','240xfj','240xpy','2410rf','2416yp','241aza','241e9j','241h28','241htv','241rbw','242fil','242mk5','243dqw','243gyq','243ihb','243ilk','243itz','243mb1','243smc','243y0o','24409d','2444y9','244am7','244b1e','244d2k','244hne','244rg5','244xap','246a0x','246f4b','246gr8','246guk','246i3n','246l5h','246li9','24773d','247itg','2483m2','2493g3','249ecs','249jne','249nex','249r2l','249rd9','249sx4','24a00w','24agtm','24amul','24aq7f','24b5kz','24bepp','24bzz2','24cr2a','24cr5i','24cwui','24cyzu','24d10y','24d211','24dbbb','24dfu4','24du74','24e4sf','24eb0j','24fnfr','24fsrd','24fz2x','24g14c','24g3e3','24g526','24g5yb','24g67z','24gbii','24gko6','24hj49','24hlu7','24hn6t','24j3an','24j4yy','24j6sh','24j73q','24j7k0','24jad9','24ji82','24jt91','24k13m','24kg4i','24ksbx','24l1v6','24m2xd','24m68i','24m722','24m7ip','24m89u','24mdaz','24mwzs','24n2gn','24n942','24nh03','24nq3v','24nvo8','24nweq','24oog3','24oqce','24oruy','24otva','24owfa','24oypq','24pdwt','24pmhw','24psfk','24qrzp','24r8cf','24ripd','24rjrv','24rq1r','24rr89','24s1y0','24s6zh','24sn7x','24spz6','24syx3','24t0n6','24tj99','24u8c9','24ukfb','24ukwr','24umzd','24uqup','24uxyk','24v1aj','24vbbl','24vcvf','24vzgl','24w2oh','24wqfq','24xkof','24xt5y','24xv1u','24xvvl','24xzjs','24y0hr','24yjv1','24z70t','24zl5s','24zt3f','2501ok','250b03','2517xc','251f3v','251fm7','251g8z','251gv7','251llc','251mek','251odl','252868','2529rb','2536qu','253o4k','254c25','254dfp','254ehg','254elb','254fp4','254ktu','254vjb','2553kr','255cti','255gio','255vna','256tc2','2575b2','2575p5','257bd4','257etv','257psc','257r5l','257so1','258pl8','258w8s','2594wu','259qrh','259uu2','25a0jv','25a1nj','25a1t5','25a3k7','25a740','25a914','25ad4w','25ajfk','25awa6','25axfr','25b6rn','25bq4m','25bq6f','25bzas','25cjo2','25cmcc','25crfu','25cs2q','25cur9','25cxju','25d197','25d61b','25d8zb','25demd','25dgal','25dpgr','25dptb','25dtbh','25e4mu','25enkh','25fuex','25fvj5','25fxww','25g245','25g2rh','25g8tz','25h2jk','25h2ud','25h2v2','25hjp5','25i53z','25i7fr','25ii3b','25izjv','25j1b6','25j1v0','25j9s6','25ja0t','25jbes','25jch9','25jfbc','25jhbv','25jhjc','25jl29','25jqr6','25kesk','25klg9','25kx9u','25lb69','25lzcg','25m3ac','25m81x','25mdpc','25n7qi','25n9tq','25nal9','25nveg','25o5i9','25p8p1','25pbwq','25pd6a','25pgoj','25pict','25pnb1','25q1iq','25qcs3','25qtsb','25rjfa','25s8oi','25sdit','25segk','25sfr0','25sib4','25slbl','25t672','25tgwa','25tjgt','25tzd4','25u323','25u522','25u8u3','25urlf','25uswh','25uu2d','25v56j','25v5ml','25vcvi','25viel','25vv7i','25vvjq','25w55z','25weoz','25wkb9','25xhq2','25xka3','25xlwc','25xmzc','25xq5y','25xrsp','25xuds','25ygxb','25yjjq','25ys4m','25ysr1','25z7dq','25zjhz','25zn42','25zv6j','260l3h','260qbt','260ro3','260ugk','260xzi','26187f','261lid','2626ka','262h0b','262qez','263iti','263vcc','263vss','263y1p','2644e2','264c9e','264isc','264oxe','264t5v','264x6d','265627','2676wn','267b38','267crq','267ilh','267pwl','267yrc','268a0s','268jl2','268nzp','268wjk','26a0uw','26a97b','26a9l5','26acgp','26afon','26ajsl','26al5a','26axeo','26b9kj','26bcvm','26bor0','26by28','26cdc8','26cmzg','26d5jk','26d975','26damv','26dcl1','26do81','26dr1u','26e6g4','26ebig','26ejpg','26fs7e','26fteb','26fwlw','26fzqd','26gcdp','26gwv3','26h0hl','26h9rc','26hbup','26hpdd','26hv99','26ifwv','26ikoi','26im07','26ip5q','26irrc','26irxa','26jgw5','26jmv2','26jwl9','26kd1k','26kkqc','26kmc4','26kn1k','26kwwh','26lcrc','26loyj','26lpzg','26ltvj','26m0co','26m53n','26m62y','26mhbl','26mkm1','26n1by','26n4xq','26nbio','26nxjr','26ol3m','26omjr','26oms1','26op1q','26ou21','26out6','26ovgn','26ovud','26ozyk','26p22y','26pdzc','26phhg','26qil5','26qj4p','26qpcq','26rh0e','26rrby','26rx97','26s5o7','26s983','26sfuh','26siz8','26sjmt','26sqlj','26t60c','26tcsa','26thig','26u7v1','26u9kp','26v7bn','26v8rf','26vai7','26ve9p','26vewg','26vqvb','26vsxl','26vw6q','26wbl1','26wk9p','26x6yw','26xoz2','26y2r5','26y9f5','26yc5e','26ye6w','26yo2t','26yyl3','26z9hl','26zcx3','26zhip','26zo1v','2709jd','270t0o','270ucm','270ugc','270wm0','2710sd','271bpl','271jfk','271lkw','271urx','271z25','272i9d','272pu5','273l41','273r05','273rgr','273tia','273w4l','273wpf','273xgr','2741gc','27456z','274sri','2751bz','2755pl','2759c0','275e4z','275tim','2762at','276w8i','276zze','277evx','277lty','277y9p','277z4l','2783zj','278u0s','278yyb','279lzz','27a0qa','27a1y2','27aetm','27amxf','27apsd','27axwi','27b8wz','27bh4q','27ca78','27cclw','27cddz','27de53','27dhjd','27dktc','27dl6g','27dlsh','27dodr','27ds90','27e1a7','27eov8','27epqr','27eugk','27euu9','27fns4','27gn7x','27goxo','27h3fc','27h6xs','27hr7p','27i5vn','27ib91','27iokb','27j6rd','27jbpo','27jjnk','27jkbx','27jq7z','27jrb4','27k1e8','27kg4e','27kye5','27ld8t','27lsvb','27ly0q','27ly5d','27m3s4','27m5jt','27mcr4','27mhxg','27mulj','27mvw5','27n64n','27nimd','27nmzw','27nqll','27ofrn','27oqmd','27ou1f','27ow1h','27oyg8','27p6z3','27p73f','27ps4p','27q35j','27qdsj','27r0ia','27r214','27rb8s','27rc7r','27rihw','27rtjz','27s1af','27s3jh','27s680','27sda6','27smba','27t68n','27teed','27tg6h','27tuoz','27tv99','27u9yz','27uh22','27uig6','27vbvn','27vl5y','27vluj','27vmif','27vq36','27vrrj','27wjrx','27wkww','27x6mp','27xayw','27xo4z','27y3yp','27yijh','27yjqb','27ym25','27yugi','27yxko','27yy1w','27z336','27z6ch','27zs0w','27zyhh','28099r','280di2','280xi8','281hw7','281jgc','281knp','281pkz','281ru8','281rzw','2826pl','282oor','282ujs','283ps9','283ykf','284lo9','284o1g','284p5x','28503q','2852fw','2853su','285bzf','285h2r','285mma','285ri8','285vji','285y2u','285yl2','2866sv','286yyo','2873us','287bnn','287cen','287k1e','287zfu','2880i2','2880tt','2889w3','288a3l','288i38','288la4','288sa8','289p0s','289q8l','289ro2','289tqc','289uwp','289v5i','289wmn','28a2xb','28a33z','28a6ax','28a6cu','28a7ml','28afyf','28akjv','28b64x','28bkqf','28ccmc','28cgfq','28chkm','28chrj','28crg5','28d0cr','28d1db','28d8jd','28d9go','28dax9','28dzwm','28e1w4','28ebdj','28f1g0','28g983','28ga0x','28gc68','28gf6d','28gfnd','28ghrt','28gk1a','28gkl2','28gw3o','28h0ql','28h59w','28hh4g','28hjqm','28htuu','28ic40','28il5s','28iqgk','28jggh','28jkub','28jnf4','28jo7s','28juwx','28jw78','28jz2y','28kfi9','28khvu','28l255','28lbgr','28lqig','28mjrm','28mr7t','28msj5','28mv4n','28n4u2','28n7tt','28n8qd','28ny43','28nzfw','28o3kt','28obnl','28pp3z','28pq8b','28ps1p','28pto4','28puqk','28pweh','28q1eo','28qcj9','28qg7s','28qkzq','28qtqj','28quw7','28qwt6','28r4fs','28rh8v','28rmkg','28rr8u','28rsn1','28s37j','28s8hf','28s9bg','28sjh6','28sm0n','28sof0','28svdn','28tior','28tr45','28uudr','28v2ym','28vb8p','28vcc8','28vdfh','28vevv','28vqeh','28w1dg','28wc7w','28wdzi','28wffk','28y6uh','28ycx9','28yfdb','28yfwf','28yi8o','28yqzr','28zhxy','28zorw','28zv3k','29041r','2907wg','290u0d','2917na','291mf9','291ow1','291r4a','291sqi','291tw9','291vse','2925dc','2929m0','292lfv','292ms0','2934ec','293afs','293b7j','293d4e','293jya','293v61','2953k3','2956aq','2957co','295c83','295ln2','295o3b','295r33','295vii','2961s5','296ff3','297k03','297sjd','2980zh','298enr','298i80','298iqj','298lqg','298mvs','298nhy','298v5b','298w8s','299aa8','29a4ha','29aexw','29ahaz','29aiuu','29an0o','29asdh','29b7yf','29bc3i','29bf3b','29bfrt','29bjfp','29br5z','29c4r5','29cgy3','29cj30','29cmuv','29cnd3','29cvdl','29donf','29duv0','29dvwj','29e0iw','29eagr','29ecm6','29ecxs','29esnx','29ezm1','29fhoh','29frnk','29fydx','29g080','29gjj7','29glos','29go83','29gr27','29gs7e','29gw6c','29hgzt','29hn7u','29hne2','29hwb1','29i91s','29ic2j','29ik8g','29jui3','29k20u','29k27p','29k3px','29k6hk','29k6iv','29kcxm','29kxo5','29l6ji','29lqjm','29lwnf','29muzt','29n87n','29ncqv','29nl0t','29nm70','29nwui','29ois4','29oykm','29qbxl','29qjo6','29qlpl','29qluw','29qnno','29r90d','29ra3s','29rfit','29rraz','29scaq','29shbr','29stga','29t8bc','29tc1u','29tj5y','29trj2','29ttmp','29tudp','29ubdp','29uo38','29urm5','29usyt','29vm0h','29vmtw','29voxy','29w1cj','29w2b5','29w8ya','29wc1e','29wgul','29woe2','29wruq','29xc2o','29xd5q','29xggk','29xhub','29ynnr','29yvcq','29ywsi','29yy0t','29yyli','29z7za','29zgxz','29zh5a','29zmvc','29zrt2','2a0bzt','2a0ejf','2a0l20','2a0nfq','2a1h7j','2a1ioc','2a1q8w','2a1qac','2a1ubh','2a22e2','2a2c00','2a2snl','2a2zf2','2a38ib','2a4kbc','2a4qpr','2a4tm0','2a4x2y','2a579i','2a58d4','2a5jfb','2a5jhy','2a5oi0','2a5q90']
idint = 4594374
subredditSubmissions = 0




def smartinsert(con, cur, subreddits, idint, MIN_SCORE):
    ''' La funció original ha estat modificada, per adaptar-la a les
        necessitats del projecte.

        Insereix els valors passats a la base de dades
        Si ja existeixen, actualitza el nombre de vots i de comentaris

        :param con: pymysql.connections.Connection object
        :param cur: pymysql.cursors.Cursor object
        :param results: una llista d'objectes praw.objects.Submission
        :param idint: id del subreddit en base 10
        :param MIN_SCORE: puntuació mínima de la publicació per ser inclosa a la BBDD
        :param subredditSubmissions: nombre total de publicacions al subreddit

        :return: el nombre de publicacions noves afegides i les acualitzades
        :rtype: int, int
    '''
    newposts = 0                        # Comptabilitzen pubs noves i actualitzades
    updates = 0
    global subredditSubmissions

    for idpubstr in subreddits:
        o = r.get_submission(submission_id=idpubstr)

        print ('Capturant pub {0}'.format(o.id))     
        cur.execute("SELECT * FROM posts WHERE idstr='{0}' LIMIT 1".format(o.id))             

        if not cur.fetchone():          # Nova publicació a la BBDD            
            # Reddit té un bug, en que si l'autor d'una publicació s'ha esborrat,
            # es produeix una excepció al intentar recuperar-ne el nom.
            try:                
                o.authorx = o.author.name
            except AttributeError:
                o.authorx = '[DELETED]'            

            if (isinstance(o, praw.objects.Submission) and (o.score >= MIN_SCORE)):
                if o.is_self:
                    o.url = 'None'

                postdata = {
                    'idstr': o.id,
                    'idsub': idint,
                    'title': re.escape(o.title),
                    'author': o.authorx,
                    'subreddit': o.subreddit.display_name,
                    'score': o.score,
                    'ups': o.ups,
                    'downs': o.downs,
                    'num_comments': o.num_comments,
                    'is_self': o.is_self,
                    'domain': utils.getDomain(o.url),
                    'url': con.escape_string(o.url),
                    'created_utc': int(o.created_utc),
                    'over18': o.over_18
                }
            
                try:
                    newposts += 1
                    query = """INSERT INTO posts (idstr, idsub, title, author, subreddit, score, ups, downs,
                               num_comments, is_self, domain, url, created_utc, over18)
                               VALUES('{idstr}', {idsub}, '{title}', '{author}', '{subreddit}', {score}, {ups},
                               {downs}, {num_comments},{is_self}, '{domain}', '{url}', {created_utc}, {over18})
                            """.format(**postdata)
                    cur.execute(query)                    
                    con.commit()   
                except pymysql.MySQLError as e:
                    text = 'smartinsert:Insert. ID: {2}\nEXCEPCIÓ: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), o.id)
                    storeExcept(text, cur, con)
                    pass
            #Fi if (isinstance(o, praw.objects.Submission)...

            subredditSubmissions += 1   # Nombre total de publicacions al subreddit

        #Fi if not cur.fetchone()

        else:                           # Actualització d'una entrada existent
            updates += 1
            if isinstance(o, praw.objects.Submission):
                postdata = {
                    'idstr': o.id,
                    'score': o.score,
                    'num_comments': o.num_comments 
                }
                try:
                    query = "UPDATE posts SET score = {score}, num_comments = {num_comments} WHERE idstr = '{idstr}' LIMIT 1".format(**postdata)
                    cur.execute(query)
                    con.commit()   
                except pymysql.MySQLError as e:
                    text = 'smartinsert:Update. ID: {2}\nEXCEPCIÓ: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), o.id)
                    storeExcept(text, cur, con)
                    pass
            #Fi if (isinstance(o, praw.objects.Submission)...
        #Fi else -> if not cur.fetchone()

    #Fi bucle for o in results

        



(r, db) = utils.rwlogin()
smartinsert(db.con, db.cur, subreddits, idint, 500)
print(subredditSubmissions)