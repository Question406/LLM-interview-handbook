---
id: code-attention
section: coding
order: 1
level: S
title: 手写 Multi-Head Attention：shape、mask、数值稳定性怎么处理？
quick: "将 [B,T,d_model] 投影并 reshape 成 [B,H,T,d_head]，计算经过缩放的 $QK^\\top$，在 softmax 前加上因果和 padding mask，再乘 V，并合并各头的输出。还要说明 mask 如何广播到分数矩阵，以及 fp16/bf16 下怎样保持数值稳定。"
tags:
  - PyTorch
  - Attention
  - KV Cache
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-09-28'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>将 [B,T,d_model] 投影并 reshape 成 [B,H,T,d_head]，计算经过缩放的 $QK^\top$，在 softmax 前加上因果和 padding mask，再乘 V，并合并各头的输出。还要说明 mask 如何广播到分数矩阵，以及 fp16/bf16 下怎样保持数值稳定。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><span class="math display"><mjx-container class="MathJax" jax="SVG" display="true"><svg style="vertical-align: -2.308ex;" xmlns="http://www.w3.org/2000/svg" width="46.313ex" height="5.727ex" role="img" focusable="false" viewBox="0 -1511.3 20470.1 2531.3"><g stroke="currentColor" fill="currentColor" stroke-width="0" transform="scale(1,-1)"><g data-mml-node="math"><g data-mml-node="TeXAtom" data-mjx-texclass="ORD"><g data-mml-node="mi"><path data-c="41" d="M255 0Q240 3 140 3Q48 3 39 0H32V46H47Q119 49 139 88Q140 91 192 245T295 553T348 708Q351 716 366 716H376Q396 715 400 709Q402 707 508 390L617 67Q624 54 636 51T687 46H717V0H708Q699 3 581 3Q458 3 437 0H427V46H440Q510 46 510 64Q510 66 486 138L462 209H229L209 150Q189 91 189 85Q189 72 209 59T259 46H264V0H255ZM447 255L345 557L244 256Q244 255 345 255H447Z"></path><path data-c="74" d="M27 422Q80 426 109 478T141 600V615H181V431H316V385H181V241Q182 116 182 100T189 68Q203 29 238 29Q282 29 292 100Q293 108 293 146V181H333V146V134Q333 57 291 17Q264 -10 221 -10Q187 -10 162 2T124 33T105 68T98 100Q97 107 97 248V385H18V422H27Z" transform="translate(750,0)"></path><path data-c="74" d="M27 422Q80 426 109 478T141 600V615H181V431H316V385H181V241Q182 116 182 100T189 68Q203 29 238 29Q282 29 292 100Q293 108 293 146V181H333V146V134Q333 57 291 17Q264 -10 221 -10Q187 -10 162 2T124 33T105 68T98 100Q97 107 97 248V385H18V422H27Z" transform="translate(1139,0)"></path><path data-c="65" d="M28 218Q28 273 48 318T98 391T163 433T229 448Q282 448 320 430T378 380T406 316T415 245Q415 238 408 231H126V216Q126 68 226 36Q246 30 270 30Q312 30 342 62Q359 79 369 104L379 128Q382 131 395 131H398Q415 131 415 121Q415 117 412 108Q393 53 349 21T250 -11Q155 -11 92 58T28 218ZM333 275Q322 403 238 411H236Q228 411 220 410T195 402T166 381T143 340T127 274V267H333V275Z" transform="translate(1528,0)"></path><path data-c="6E" d="M41 46H55Q94 46 102 60V68Q102 77 102 91T102 122T103 161T103 203Q103 234 103 269T102 328V351Q99 370 88 376T43 385H25V408Q25 431 27 431L37 432Q47 433 65 434T102 436Q119 437 138 438T167 441T178 442H181V402Q181 364 182 364T187 369T199 384T218 402T247 421T285 437Q305 442 336 442Q450 438 463 329Q464 322 464 190V104Q464 66 466 59T477 49Q498 46 526 46H542V0H534L510 1Q487 2 460 2T422 3Q319 3 310 0H302V46H318Q379 46 379 62Q380 64 380 200Q379 335 378 343Q372 371 358 385T334 402T308 404Q263 404 229 370Q202 343 195 315T187 232V168V108Q187 78 188 68T191 55T200 49Q221 46 249 46H265V0H257L234 1Q210 2 183 2T145 3Q42 3 33 0H25V46H41Z" transform="translate(1972,0)"></path><path data-c="74" d="M27 422Q80 426 109 478T141 600V615H181V431H316V385H181V241Q182 116 182 100T189 68Q203 29 238 29Q282 29 292 100Q293 108 293 146V181H333V146V134Q333 57 291 17Q264 -10 221 -10Q187 -10 162 2T124 33T105 68T98 100Q97 107 97 248V385H18V422H27Z" transform="translate(2528,0)"></path><path data-c="69" d="M69 609Q69 637 87 653T131 669Q154 667 171 652T188 609Q188 579 171 564T129 549Q104 549 87 564T69 609ZM247 0Q232 3 143 3Q132 3 106 3T56 1L34 0H26V46H42Q70 46 91 49Q100 53 102 60T104 102V205V293Q104 345 102 359T88 378Q74 385 41 385H30V408Q30 431 32 431L42 432Q52 433 70 434T106 436Q123 437 142 438T171 441T182 442H185V62Q190 52 197 50T232 46H255V0H247Z" transform="translate(2917,0)"></path><path data-c="6F" d="M28 214Q28 309 93 378T250 448Q340 448 405 380T471 215Q471 120 407 55T250 -10Q153 -10 91 57T28 214ZM250 30Q372 30 372 193V225V250Q372 272 371 288T364 326T348 362T317 390T268 410Q263 411 252 411Q222 411 195 399Q152 377 139 338T126 246V226Q126 130 145 91Q177 30 250 30Z" transform="translate(3195,0)"></path><path data-c="6E" d="M41 46H55Q94 46 102 60V68Q102 77 102 91T102 122T103 161T103 203Q103 234 103 269T102 328V351Q99 370 88 376T43 385H25V408Q25 431 27 431L37 432Q47 433 65 434T102 436Q119 437 138 438T167 441T178 442H181V402Q181 364 182 364T187 369T199 384T218 402T247 421T285 437Q305 442 336 442Q450 438 463 329Q464 322 464 190V104Q464 66 466 59T477 49Q498 46 526 46H542V0H534L510 1Q487 2 460 2T422 3Q319 3 310 0H302V46H318Q379 46 379 62Q380 64 380 200Q379 335 378 343Q372 371 358 385T334 402T308 404Q263 404 229 370Q202 343 195 315T187 232V168V108Q187 78 188 68T191 55T200 49Q221 46 249 46H265V0H257L234 1Q210 2 183 2T145 3Q42 3 33 0H25V46H41Z" transform="translate(3695,0)"></path></g></g><g data-mml-node="mo" transform="translate(4251,0)"><path data-c="28" d="M94 250Q94 319 104 381T127 488T164 576T202 643T244 695T277 729T302 750H315H319Q333 750 333 741Q333 738 316 720T275 667T226 581T184 443T167 250T184 58T225 -81T274 -167T316 -220T333 -241Q333 -250 318 -250H315H302L274 -226Q180 -141 137 -14T94 250Z"></path></g><g data-mml-node="mi" transform="translate(4640,0)"><path data-c="1D444" d="M399 -80Q399 -47 400 -30T402 -11V-7L387 -11Q341 -22 303 -22Q208 -22 138 35T51 201Q50 209 50 244Q50 346 98 438T227 601Q351 704 476 704Q514 704 524 703Q621 689 680 617T740 435Q740 255 592 107Q529 47 461 16L444 8V3Q444 2 449 -24T470 -66T516 -82Q551 -82 583 -60T625 -3Q631 11 638 11Q647 11 649 2Q649 -6 639 -34T611 -100T557 -165T481 -194Q399 -194 399 -87V-80ZM636 468Q636 523 621 564T580 625T530 655T477 665Q429 665 379 640Q277 591 215 464T153 216Q153 110 207 59Q231 38 236 38V46Q236 86 269 120T347 155Q372 155 390 144T417 114T429 82T435 55L448 64Q512 108 557 185T619 334T636 468ZM314 18Q362 18 404 39L403 49Q399 104 366 115Q354 117 347 117Q344 117 341 117T337 118Q317 118 296 98T274 52Q274 18 314 18Z"></path></g><g data-mml-node="mo" transform="translate(5431,0)"><path data-c="2C" d="M78 35T78 60T94 103T137 121Q165 121 187 96T210 8Q210 -27 201 -60T180 -117T154 -158T130 -185T117 -194Q113 -194 104 -185T95 -172Q95 -168 106 -156T131 -126T157 -76T173 -3V9L172 8Q170 7 167 6T161 3T152 1T140 0Q113 0 96 17Z"></path></g><g data-mml-node="mi" transform="translate(5875.7,0)"><path data-c="1D43E" d="M285 628Q285 635 228 637Q205 637 198 638T191 647Q191 649 193 661Q199 681 203 682Q205 683 214 683H219Q260 681 355 681Q389 681 418 681T463 682T483 682Q500 682 500 674Q500 669 497 660Q496 658 496 654T495 648T493 644T490 641T486 639T479 638T470 637T456 637Q416 636 405 634T387 623L306 305Q307 305 490 449T678 597Q692 611 692 620Q692 635 667 637Q651 637 651 648Q651 650 654 662T659 677Q662 682 676 682Q680 682 711 681T791 680Q814 680 839 681T869 682Q889 682 889 672Q889 650 881 642Q878 637 862 637Q787 632 726 586Q710 576 656 534T556 455L509 418L518 396Q527 374 546 329T581 244Q656 67 661 61Q663 59 666 57Q680 47 717 46H738Q744 38 744 37T741 19Q737 6 731 0H720Q680 3 625 3Q503 3 488 0H478Q472 6 472 9T474 27Q478 40 480 43T491 46H494Q544 46 544 71Q544 75 517 141T485 216L427 354L359 301L291 248L268 155Q245 63 245 58Q245 51 253 49T303 46H334Q340 37 340 35Q340 19 333 5Q328 0 317 0Q314 0 280 1T180 2Q118 2 85 2T49 1Q31 1 31 11Q31 13 34 25Q38 41 42 43T65 46Q92 46 125 49Q139 52 144 61Q147 65 216 339T285 628Z"></path></g><g data-mml-node="mo" transform="translate(6764.7,0)"><path data-c="2C" d="M78 35T78 60T94 103T137 121Q165 121 187 96T210 8Q210 -27 201 -60T180 -117T154 -158T130 -185T117 -194Q113 -194 104 -185T95 -172Q95 -168 106 -156T131 -126T157 -76T173 -3V9L172 8Q170 7 167 6T161 3T152 1T140 0Q113 0 96 17Z"></path></g><g data-mml-node="mi" transform="translate(7209.3,0)"><path data-c="1D449" d="M52 648Q52 670 65 683H76Q118 680 181 680Q299 680 320 683H330Q336 677 336 674T334 656Q329 641 325 637H304Q282 635 274 635Q245 630 242 620Q242 618 271 369T301 118L374 235Q447 352 520 471T595 594Q599 601 599 609Q599 633 555 637Q537 637 537 648Q537 649 539 661Q542 675 545 679T558 683Q560 683 570 683T604 682T668 681Q737 681 755 683H762Q769 676 769 672Q769 655 760 640Q757 637 743 637Q730 636 719 635T698 630T682 623T670 615T660 608T652 599T645 592L452 282Q272 -9 266 -16Q263 -18 259 -21L241 -22H234Q216 -22 216 -15Q213 -9 177 305Q139 623 138 626Q133 637 76 637H59Q52 642 52 648Z"></path></g><g data-mml-node="mo" transform="translate(7978.3,0)"><path data-c="29" d="M60 749L64 750Q69 750 74 750H86L114 726Q208 641 251 514T294 250Q294 182 284 119T261 12T224 -76T186 -143T145 -194T113 -227T90 -246Q87 -249 86 -250H74Q66 -250 63 -250T58 -247T55 -238Q56 -237 66 -225Q221 -64 221 250T66 725Q56 737 55 738Q55 746 60 749Z"></path></g><g data-mml-node="mo" transform="translate(8645.1,0)"><path data-c="3D" d="M56 347Q56 360 70 367H707Q722 359 722 347Q722 336 708 328L390 327H72Q56 332 56 347ZM56 153Q56 168 72 173H708Q722 163 722 153Q722 140 707 133H70Q56 140 56 153Z"></path></g><g data-mml-node="TeXAtom" data-mjx-texclass="ORD" transform="translate(9700.9,0)"><g data-mml-node="mi"><path data-c="73" d="M295 316Q295 356 268 385T190 414Q154 414 128 401Q98 382 98 349Q97 344 98 336T114 312T157 287Q175 282 201 278T245 269T277 256Q294 248 310 236T342 195T359 133Q359 71 321 31T198 -10H190Q138 -10 94 26L86 19L77 10Q71 4 65 -1L54 -11H46H42Q39 -11 33 -5V74V132Q33 153 35 157T45 162H54Q66 162 70 158T75 146T82 119T101 77Q136 26 198 26Q295 26 295 104Q295 133 277 151Q257 175 194 187T111 210Q75 227 54 256T33 318Q33 357 50 384T93 424T143 442T187 447H198Q238 447 268 432L283 424L292 431Q302 440 314 448H322H326Q329 448 335 442V310L329 304H301Q295 310 295 316Z"></path><path data-c="6F" d="M28 214Q28 309 93 378T250 448Q340 448 405 380T471 215Q471 120 407 55T250 -10Q153 -10 91 57T28 214ZM250 30Q372 30 372 193V225V250Q372 272 371 288T364 326T348 362T317 390T268 410Q263 411 252 411Q222 411 195 399Q152 377 139 338T126 246V226Q126 130 145 91Q177 30 250 30Z" transform="translate(394,0)"></path><path data-c="66" d="M273 0Q255 3 146 3Q43 3 34 0H26V46H42Q70 46 91 49Q99 52 103 60Q104 62 104 224V385H33V431H104V497L105 564L107 574Q126 639 171 668T266 704Q267 704 275 704T289 705Q330 702 351 679T372 627Q372 604 358 590T321 576T284 590T270 627Q270 647 288 667H284Q280 668 273 668Q245 668 223 647T189 592Q183 572 182 497V431H293V385H185V225Q185 63 186 61T189 57T194 54T199 51T206 49T213 48T222 47T231 47T241 46T251 46H282V0H273Z" transform="translate(894,0)"></path><path data-c="74" d="M27 422Q80 426 109 478T141 600V615H181V431H316V385H181V241Q182 116 182 100T189 68Q203 29 238 29Q282 29 292 100Q293 108 293 146V181H333V146V134Q333 57 291 17Q264 -10 221 -10Q187 -10 162 2T124 33T105 68T98 100Q97 107 97 248V385H18V422H27Z" transform="translate(1200,0)"></path><path data-c="6D" d="M41 46H55Q94 46 102 60V68Q102 77 102 91T102 122T103 161T103 203Q103 234 103 269T102 328V351Q99 370 88 376T43 385H25V408Q25 431 27 431L37 432Q47 433 65 434T102 436Q119 437 138 438T167 441T178 442H181V402Q181 364 182 364T187 369T199 384T218 402T247 421T285 437Q305 442 336 442Q351 442 364 440T387 434T406 426T421 417T432 406T441 395T448 384T452 374T455 366L457 361L460 365Q463 369 466 373T475 384T488 397T503 410T523 422T546 432T572 439T603 442Q729 442 740 329Q741 322 741 190V104Q741 66 743 59T754 49Q775 46 803 46H819V0H811L788 1Q764 2 737 2T699 3Q596 3 587 0H579V46H595Q656 46 656 62Q657 64 657 200Q656 335 655 343Q649 371 635 385T611 402T585 404Q540 404 506 370Q479 343 472 315T464 232V168V108Q464 78 465 68T468 55T477 49Q498 46 526 46H542V0H534L510 1Q487 2 460 2T422 3Q319 3 310 0H302V46H318Q379 46 379 62Q380 64 380 200Q379 335 378 343Q372 371 358 385T334 402T308 404Q263 404 229 370Q202 343 195 315T187 232V168V108Q187 78 188 68T191 55T200 49Q221 46 249 46H265V0H257L234 1Q210 2 183 2T145 3Q42 3 33 0H25V46H41Z" transform="translate(1589,0)"></path><path data-c="61" d="M137 305T115 305T78 320T63 359Q63 394 97 421T218 448Q291 448 336 416T396 340Q401 326 401 309T402 194V124Q402 76 407 58T428 40Q443 40 448 56T453 109V145H493V106Q492 66 490 59Q481 29 455 12T400 -6T353 12T329 54V58L327 55Q325 52 322 49T314 40T302 29T287 17T269 6T247 -2T221 -8T190 -11Q130 -11 82 20T34 107Q34 128 41 147T68 188T116 225T194 253T304 268H318V290Q318 324 312 340Q290 411 215 411Q197 411 181 410T156 406T148 403Q170 388 170 359Q170 334 154 320ZM126 106Q126 75 150 51T209 26Q247 26 276 49T315 109Q317 116 318 175Q318 233 317 233Q309 233 296 232T251 223T193 203T147 166T126 106Z" transform="translate(2422,0)"></path><path data-c="78" d="M201 0Q189 3 102 3Q26 3 17 0H11V46H25Q48 47 67 52T96 61T121 78T139 96T160 122T180 150L226 210L168 288Q159 301 149 315T133 336T122 351T113 363T107 370T100 376T94 379T88 381T80 383Q74 383 44 385H16V431H23Q59 429 126 429Q219 429 229 431H237V385Q201 381 201 369Q201 367 211 353T239 315T268 274L272 270L297 304Q329 345 329 358Q329 364 327 369T322 376T317 380T310 384L307 385H302V431H309Q324 428 408 428Q487 428 493 431H499V385H492Q443 385 411 368Q394 360 377 341T312 257L296 236L358 151Q424 61 429 57T446 50Q464 46 499 46H516V0H510H502Q494 1 482 1T457 2T432 2T414 3Q403 3 377 3T327 1L304 0H295V46H298Q309 46 320 51T331 63Q331 65 291 120L250 175Q249 174 219 133T185 88Q181 83 181 74Q181 63 188 55T206 46Q208 46 208 23V0H201Z" transform="translate(2922,0)"></path></g></g><g data-mml-node="mstyle" transform="translate(13150.9,0)"><g data-mml-node="mspace"></g></g><g data-mml-node="mrow" transform="translate(13150.6,0)"><g data-mml-node="mo" transform="translate(0 -0.5)"><path data-c="28" d="M701 -940Q701 -943 695 -949H664Q662 -947 636 -922T591 -879T537 -818T475 -737T412 -636T350 -511T295 -362T250 -186T221 17T209 251Q209 962 573 1361Q596 1386 616 1405T649 1437T664 1450H695Q701 1444 701 1441Q701 1436 681 1415T629 1356T557 1261T476 1118T400 927T340 675T308 359Q306 321 306 250Q306 -139 400 -430T690 -924Q701 -936 701 -940Z"></path></g><g data-mml-node="mfrac" transform="translate(736,0)"><g data-mml-node="mrow" transform="translate(220,676)"><g data-mml-node="mi"><path data-c="1D444" d="M399 -80Q399 -47 400 -30T402 -11V-7L387 -11Q341 -22 303 -22Q208 -22 138 35T51 201Q50 209 50 244Q50 346 98 438T227 601Q351 704 476 704Q514 704 524 703Q621 689 680 617T740 435Q740 255 592 107Q529 47 461 16L444 8V3Q444 2 449 -24T470 -66T516 -82Q551 -82 583 -60T625 -3Q631 11 638 11Q647 11 649 2Q649 -6 639 -34T611 -100T557 -165T481 -194Q399 -194 399 -87V-80ZM636 468Q636 523 621 564T580 625T530 655T477 665Q429 665 379 640Q277 591 215 464T153 216Q153 110 207 59Q231 38 236 38V46Q236 86 269 120T347 155Q372 155 390 144T417 114T429 82T435 55L448 64Q512 108 557 185T619 334T636 468ZM314 18Q362 18 404 39L403 49Q399 104 366 115Q354 117 347 117Q344 117 341 117T337 118Q317 118 296 98T274 52Q274 18 314 18Z"></path></g><g data-mml-node="msup" transform="translate(791,0)"><g data-mml-node="mi"><path data-c="1D43E" d="M285 628Q285 635 228 637Q205 637 198 638T191 647Q191 649 193 661Q199 681 203 682Q205 683 214 683H219Q260 681 355 681Q389 681 418 681T463 682T483 682Q500 682 500 674Q500 669 497 660Q496 658 496 654T495 648T493 644T490 641T486 639T479 638T470 637T456 637Q416 636 405 634T387 623L306 305Q307 305 490 449T678 597Q692 611 692 620Q692 635 667 637Q651 637 651 648Q651 650 654 662T659 677Q662 682 676 682Q680 682 711 681T791 680Q814 680 839 681T869 682Q889 682 889 672Q889 650 881 642Q878 637 862 637Q787 632 726 586Q710 576 656 534T556 455L509 418L518 396Q527 374 546 329T581 244Q656 67 661 61Q663 59 666 57Q680 47 717 46H738Q744 38 744 37T741 19Q737 6 731 0H720Q680 3 625 3Q503 3 488 0H478Q472 6 472 9T474 27Q478 40 480 43T491 46H494Q544 46 544 71Q544 75 517 141T485 216L427 354L359 301L291 248L268 155Q245 63 245 58Q245 51 253 49T303 46H334Q340 37 340 35Q340 19 333 5Q328 0 317 0Q314 0 280 1T180 2Q118 2 85 2T49 1Q31 1 31 11Q31 13 34 25Q38 41 42 43T65 46Q92 46 125 49Q139 52 144 61Q147 65 216 339T285 628Z"></path></g><g data-mml-node="mi" transform="translate(974,363) scale(0.707)"><path data-c="22A4" d="M55 642T55 648T59 659T66 666T71 668H708Q723 660 723 648T708 628H409V15Q402 2 391 0Q387 0 384 1T379 3T375 6T373 9T371 13T369 16V628H71Q70 628 67 630T59 637Z"></path></g></g></g><g data-mml-node="msqrt" transform="translate(470.9,-855.6)"><g transform="translate(853,0)"><g data-mml-node="msub"><g data-mml-node="mi"><path data-c="1D451" d="M366 683Q367 683 438 688T511 694Q523 694 523 686Q523 679 450 384T375 83T374 68Q374 26 402 26Q411 27 422 35Q443 55 463 131Q469 151 473 152Q475 153 483 153H487H491Q506 153 506 145Q506 140 503 129Q490 79 473 48T445 8T417 -8Q409 -10 393 -10Q359 -10 336 5T306 36L300 51Q299 52 296 50Q294 48 292 46Q233 -10 172 -10Q117 -10 75 30T33 157Q33 205 53 255T101 341Q148 398 195 420T280 442Q336 442 364 400Q369 394 369 396Q370 400 396 505T424 616Q424 629 417 632T378 637H357Q351 643 351 645T353 664Q358 683 366 683ZM352 326Q329 405 277 405Q242 405 210 374T160 293Q131 214 119 129Q119 126 119 118T118 106Q118 61 136 44T179 26Q233 26 290 98L298 109L352 326Z"></path></g><g data-mml-node="mi" transform="translate(553,-150) scale(0.707)"><path data-c="210E" d="M137 683Q138 683 209 688T282 694Q294 694 294 685Q294 674 258 534Q220 386 220 383Q220 381 227 388Q288 442 357 442Q411 442 444 415T478 336Q478 285 440 178T402 50Q403 36 407 31T422 26Q450 26 474 56T513 138Q516 149 519 151T535 153Q555 153 555 145Q555 144 551 130Q535 71 500 33Q466 -10 419 -10H414Q367 -10 346 17T325 74Q325 90 361 192T398 345Q398 404 354 404H349Q266 404 205 306L198 293L164 158Q132 28 127 16Q114 -11 83 -11Q69 -11 59 -2T48 16Q48 30 121 320L195 616Q195 629 188 632T149 637H128Q122 643 122 645T124 664Q129 683 137 683Z"></path></g></g></g><g data-mml-node="mo" transform="translate(0,35.6)"><path data-c="221A" d="M95 178Q89 178 81 186T72 200T103 230T169 280T207 309Q209 311 212 311H213Q219 311 227 294T281 177Q300 134 312 108L397 -77Q398 -77 501 136T707 565T814 786Q820 800 834 800Q841 800 846 794T853 782V776L620 293L385 -193Q381 -200 366 -200Q357 -200 354 -197Q352 -195 256 15L160 225L144 214Q129 202 113 190T95 178Z"></path></g><rect width="1010.3" height="60" x="853" y="775.6"></rect></g><rect width="2565.1" height="60" x="120" y="220"></rect></g><g data-mml-node="mo" transform="translate(3763.4,0)"><path data-c="2B" d="M56 237T56 250T70 270H369V420L370 570Q380 583 389 583Q402 583 409 568V270H707Q722 262 722 250T707 230H409V-68Q401 -82 391 -82H389H387Q375 -82 369 -68V230H70Q56 237 56 250Z"></path></g><g data-mml-node="mi" transform="translate(4763.6,0)"><path data-c="1D440" d="M289 629Q289 635 232 637Q208 637 201 638T194 648Q194 649 196 659Q197 662 198 666T199 671T201 676T203 679T207 681T212 683T220 683T232 684Q238 684 262 684T307 683Q386 683 398 683T414 678Q415 674 451 396L487 117L510 154Q534 190 574 254T662 394Q837 673 839 675Q840 676 842 678T846 681L852 683H948Q965 683 988 683T1017 684Q1051 684 1051 673Q1051 668 1048 656T1045 643Q1041 637 1008 637Q968 636 957 634T939 623Q936 618 867 340T797 59Q797 55 798 54T805 50T822 48T855 46H886Q892 37 892 35Q892 19 885 5Q880 0 869 0Q864 0 828 1T736 2Q675 2 644 2T609 1Q592 1 592 11Q592 13 594 25Q598 41 602 43T625 46Q652 46 685 49Q699 52 704 61Q706 65 742 207T813 490T848 631L654 322Q458 10 453 5Q451 4 449 3Q444 0 433 0Q418 0 415 7Q413 11 374 317L335 624L267 354Q200 88 200 79Q206 46 272 46H282Q288 41 289 37T286 19Q282 3 278 1Q274 0 267 0Q265 0 255 0T221 1T157 2Q127 2 95 1T58 0Q43 0 39 2T35 11Q35 13 38 25T43 40Q45 46 65 46Q135 46 154 86Q158 92 223 354T289 629Z"></path></g><g data-mml-node="mo" transform="translate(5814.6,0) translate(0 -0.5)"><path data-c="29" d="M34 1438Q34 1446 37 1448T50 1450H56H71Q73 1448 99 1423T144 1380T198 1319T260 1238T323 1137T385 1013T440 864T485 688T514 485T526 251Q526 134 519 53Q472 -519 162 -860Q139 -885 119 -904T86 -936T71 -949H56Q43 -949 39 -947T34 -937Q88 -883 140 -813Q428 -430 428 251Q428 453 402 628T338 922T245 1146T145 1309T46 1425Q44 1427 42 1429T39 1433T36 1436L34 1438Z"></path></g></g><g data-mml-node="mi" transform="translate(19701.1,0)"><path data-c="1D449" d="M52 648Q52 670 65 683H76Q118 680 181 680Q299 680 320 683H330Q336 677 336 674T334 656Q329 641 325 637H304Q282 635 274 635Q245 630 242 620Q242 618 271 369T301 118L374 235Q447 352 520 471T595 594Q599 601 599 609Q599 633 555 637Q537 637 537 648Q537 649 539 661Q542 675 545 679T558 683Q560 683 570 683T604 682T668 681Q737 681 755 683H762Q769 676 769 672Q769 655 760 640Q757 637 743 637Q730 636 719 635T698 630T682 623T670 615T660 608T652 599T645 592L452 282Q272 -9 266 -16Q263 -18 259 -21L241 -22H234Q216 -22 216 -15Q213 -9 177 305Q139 623 138 626Q133 637 76 637H59Q52 642 52 648Z"></path></g></g></g></svg></mjx-container></span><pre><code data-lang="python">import math
import torch
import torch.nn as nn

class MHA(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.h = n_heads
        self.dh = d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.out = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x, padding_mask=None):
        B, T, D = x.shape
        qkv = self.qkv(x).view(B, T, 3, self.h, self.dh)
        q, k, v = qkv.unbind(dim=2)
        q = q.transpose(1, 2)   # [B,H,T,Dh]
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        scores = q @ k.transpose(-1, -2) / math.sqrt(self.dh)

        causal = torch.triu(
            torch.ones(T, T, dtype=torch.bool, device=x.device), diagonal=1
        )
        scores = scores.masked_fill(causal, float(&#x27;-inf&#x27;))
        if padding_mask is not None:      # [B,T], True=valid
            scores = scores.masked_fill(~padding_mask[:, None, None, :], float(&#x27;-inf&#x27;))

        attn = torch.softmax(scores.float(), dim=-1).to(q.dtype)
        y = attn @ v
        y = y.transpose(1, 2).contiguous().view(B, T, D)
        return self.out(y)</code></pre><p>实际框架常用 fused SDPA 或 FlashAttention。白板题考的是数学和 shape，不是去复刻最高性能 kernel。Softmax 放到 fp32 里算是常见的稳定做法。若某个 query 的所有 key 都被 mask 掉，要避免全是 -∞ 算出 NaN。</p><h3>进阶：KV cache、输入预填充（prefill，即处理输入并建立缓存） 与 逐 token 生成（decode）</h3><p>自回归生成第 t 步时，新 query 要和前面所有 token 的 K/V 做 attention，而这些 K/V 在前几步已经算过。KV cache 把每层的 K/V 存下来，推理于是拆成两个阶段：</p><ul><li>Prefill：对整段输入提示（prompt）做一次前向计算，$T$ 等于 prompt 长度，把每层 K/V 写进 cache，只拿最后一个位置的 logits 采样第一个新 token。这一步主要受计算能力限制（compute-bound），影响首个 token 的等待时间（TTFT）。</li><li>Decode：每步只输入 1 个新 token，q 是 $[B,H,1,d_h]$，和 cache 里的 $[B,H,S,d_h]$ 做 attention，单步 attention 开销从 $O(S^2)$ 降到 $O(S)$。这一步主要受内存带宽限制（memory-bound），每步都要读取权重和整份 cache，因此影响每个输出 token 的耗时（TPOT）和吞吐。</li></ul><p>和上面的基础版相比，改动主要有三处。一是 K/V 先 append 进 cache，再和历史拼成长度 $S=\text{past}+T$。二是 causal mask 要带 offset：绝对位置为 past+i 的 query 只能看 $k\_pos \le \text{past}+i$ 的 key。past=0 时就退化成原来的 triu，decode 时 $T=1$，mask 全为 False。三是 cache 可以复用：同一个 system prompt 或 few-shot 前缀只 prefill 一次，fork 给多条请求，每条只需要 prefill 自己的后缀。</p><pre><code data-lang="python">class KVCache:
    """预分配 [B,H,max_len,Dh]，len 是已写入的 token 数（batch 内对齐）。"""
    def __init__(self, B, H, max_len, dh, device=None, dtype=torch.float32):
        self.k = torch.zeros(B, H, max_len, dh, device=device, dtype=dtype)
        self.v = torch.zeros_like(self.k)
        self.len = 0

    def append(self, k, v):                      # k, v: [B,H,T_new,Dh]
        t = k.size(2)
        assert self.len + t &lt;= self.k.size(2), "KV cache overflow"
        self.k[:, :, self.len:self.len + t] = k
        self.v[:, :, self.len:self.len + t] = v
        self.len += t
        return self.k[:, :, :self.len], self.v[:, :, :self.len]

    def fork(self, n):
        """把 batch=1 的前缀 cache 复制给 n 条请求，前缀不用重算。"""
        new = KVCache.__new__(KVCache)
        new.k = self.k.expand(n, -1, -1, -1).clone()
        new.v = self.v.expand(n, -1, -1, -1).clone()
        new.len = self.len
        return new


class CachedMHA(MHA):
    def forward(self, x, cache=None, key_valid=None):
        # x: [B,T,D]；prefill 时 T=prompt 长度，decode 时 T=1
        # key_valid: [B, past+T]，True=有效 key（左 padding 时用）
        B, T, D = x.shape
        q, k, v = self.qkv(x).view(B, T, 3, self.h, self.dh).unbind(dim=2)
        q, k, v = (t.transpose(1, 2) for t in (q, k, v))   # [B,H,T,Dh]

        past = 0
        if cache is not None:
            past = cache.len
            k, v = cache.append(k, v)            # [B,H,past+T,Dh]
        S = k.size(2)

        scores = q @ k.transpose(-1, -2) / math.sqrt(self.dh)   # [B,H,T,S]
        q_pos = torch.arange(past, past + T, device=x.device)[:, None]
        k_pos = torch.arange(S, device=x.device)[None, :]
        scores = scores.masked_fill(k_pos &gt; q_pos, float(&#x27;-inf&#x27;))  # 带 offset 的 causal
        if key_valid is not None:
            scores = scores.masked_fill(~key_valid[:, None, None, :], float(&#x27;-inf&#x27;))

        attn = torch.softmax(scores.float(), dim=-1).nan_to_num(0.0).to(q.dtype)
        y = (attn @ v).transpose(1, 2).contiguous().view(B, T, D)
        return self.out(y)


class TinyLM(nn.Module):
    def __init__(self, vocab, d_model, n_heads, n_layers):
        super().__init__()
        self.emb = nn.Embedding(vocab, d_model)
        self.layers = nn.ModuleList(CachedMHA(d_model, n_heads) for _ in range(n_layers))
        self.head = nn.Linear(d_model, vocab, bias=False)

    def new_caches(self, B, max_len):
        p = self.head.weight
        l0 = self.layers[0]
        return [KVCache(B, l0.h, max_len, l0.dh, p.device, p.dtype) for _ in self.layers]

    def forward(self, ids, caches=None, key_valid=None):
        x = self.emb(ids)
        for i, layer in enumerate(self.layers):
            x = x + layer(x, None if caches is None else caches[i], key_valid)
        return self.head(x)                      # [B,T,V]


@torch.no_grad()
def prefill(model, ids, caches, key_valid=None):
    """一次性把整段 prompt 写进 cache，只返回最后一个位置的 logits。"""
    return model(ids, caches, key_valid)[:, -1]  # [B,V]


@torch.no_grad()
def decode_step(model, next_id, caches, key_valid=None):
    """每步只喂 1 个新 token，K/V 从 cache 里读。"""
    return model(next_id[:, None], caches, key_valid)[:, -1]


@torch.no_grad()
def generate(model, prompt_ids, max_new_tokens, caches=None, prompt_valid=None):
    # prompt_valid: [B,T]，左 padding 时 pad 位置为 False
    B, T = prompt_ids.shape
    if caches is None:
        caches = model.new_caches(B, T + max_new_tokens)
    valid = prompt_valid
    logits = prefill(model, prompt_ids, caches, valid)
    out = []
    for _ in range(max_new_tokens):
        nxt = logits.argmax(-1)                  # greedy
        out.append(nxt)
        if valid is not None:
            valid = torch.cat([valid, valid.new_ones(B, 1)], dim=1)
        logits = decode_step(model, nxt, caches, valid)
    return torch.stack(out, dim=1)               # [B,max_new_tokens]</code></pre><p>用法：前缀复用时先 <code>sys_caches = model.new_caches(1, max_len)</code>，调用 <code>prefill(model, sys_ids, sys_caches)</code>，再用 <code>[c.fork(n) for c in sys_caches]</code> 得到每条请求的 cache，把它传给 <code>generate(model, user_ids, ...)</code>。这样前缀那段不会重算。这份代码验证过四件事：prefill 加逐 token decode 的 logits 和整段全量 forward 一致；greedy 生成结果和不带 cache 的朴素实现一致；前缀复用和从头 prefill 一致；左 padding 的 batch 生成和逐条生成一致。</p><p>有两处细节容易漏。<code>fork</code> 这里用 clone 是为了好懂；vLLM 的 prefix caching 和 SGLang 的 RadixAttention 按 block 引用共享，写时才复制。左 padding 时，pad 位置的 query 看不到任何有效 key，整行都是 -∞，softmax 会得到 NaN。这个 NaN 会经过 residual 流进下一层的 V，而 0×NaN 仍是 NaN，所以要 <code>nan_to_num(0.0)</code>。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Causal mask 和 padding mask 谁先加？</summary><div class="follow-answer"><p>只要两者最终合成同一个被屏蔽位置集合，先后顺序无所谓。需要保证广播后的形状正确：causal 常常是 [T,T]，padding key mask 常常是 [B,1,1,T]。</p></div></details><details class="followup"><summary>为什么 mask 在 softmax 前而不是之后？</summary><div class="follow-answer"><p>softmax 后再置零会破坏概率归一化，除非重新归一化。前面加 -∞，被屏蔽位置的概率才严格是 0。</p></div></details><details class="followup"><summary>GQA 怎么改这段代码？</summary><div class="follow-answer"><p>Q 仍有 Hq 个 heads，K/V 只有 Hkv 个。计算前按 group 让若干 Q heads 共享同一 KV head。避免物理 repeat，可以由专门 kernel 来做。</p></div></details><details class="followup"><summary>KV cache 占多少显存？GQA 省在哪？</summary><div class="follow-answer"><p>大小是 $2 \times L \times B \times H_{kv} \times S \times d_h \times \text{bytes}$，其中 2 对应 K 和 V。以 Llama-2-7B 为例（32 层、32 头、$d_h=128$、fp16），每个 token 约 0.5 MB，4k 上下文单条序列约 2 GB，很快就比权重还大。GQA/MQA 把 $H_{kv}$ 从 $H$ 降到几个甚至 1 个，cache 缩小 $H/H_{kv}$ 倍；MLA 更进一步，只缓存低秩潜在表示。</p></div></details><details class="followup"><summary>为什么 prefill 是 compute-bound，decode 是 memory-bound？</summary><div class="follow-answer"><p>Prefill 一次处理 T 个 token，投影是 $[T,d]\times[d,d]$ 的大矩阵乘，每读一次权重能做很多 FLOPs。Decode 每步只有 1 个 token，却要把全部权重和整份 KV cache 从 HBM 读一遍，算术强度很低。所以 decode 靠加大 batch 摊薄读权重的成本；chunked prefill 和 PD 分离是为了不让长 prompt 的 prefill 卡住正在 decode 的请求。</p></div></details><details class="followup"><summary>加了 RoPE 以后 cache 怎么处理？</summary><div class="follow-answer"><p>新 token 的位置要用绝对位置 past+i，不能从 0 重新数。cache 里存的是旋转之后的 K，decode 时只给新 token 的 q/k 做旋转，历史 K 不动。前缀复用成立的前提是前缀位置完全相同；左 padding 时每条样本的 position id 要按有效长度算，不能直接用列下标。</p></div></details><details class="followup"><summary>Batch 里 prompt 长度不同怎么办？</summary><div class="follow-answer"><p>白板写法是左 padding 加 key_valid mask，这样所有序列的新 token 都落在同一列，cache.len 能对齐，代码里就是这么做的。代价是 pad 位置也占 cache。生产系统一般不 padding，而是每条序列记自己的长度，用 PagedAttention 按 block 管理 cache，再配合 continuous batching，让序列随时加入和退出 batch。</p></div></details></div>
