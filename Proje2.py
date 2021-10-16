import math
import locale

locale.setlocale(locale.LC_ALL, "tr_TR.utf8")

TAM_PAUN = 1
YARIM_PUAN = 0.5
PUAN_YOK = 0


def baslangic_siralama_tablosu_yazdir(oyuncu_bilgileri):  # oyuncular ilk bilgiler ile sıralanır ve her birine bir bsno verilir
    oyuncu_bilgileri.sort(key=lambda lno: lno[0])
    oyuncu_bilgileri.sort(key=lambda ad: ad[1])
    oyuncu_bilgileri.sort(key=lambda ukd: ukd[3], reverse=True)
    oyuncu_bilgileri.sort(key=lambda elo: elo[2], reverse=True)
    oyuncu_bilgileri.sort(key=lambda puan: puan[4], reverse=True)

    sirali_liste = oyuncu_bilgileri

    bsno_sozluk = {}

    for bsno in range(len(oyuncu_bilgileri)):  # sıralanmış oyunculara bsno verilir
        bsno_sozluk.setdefault(bsno + 1, sirali_liste[bsno])

    print("Başlangıç Sıralama Listesi")
    print()
    print("BSNo   LNo               Ad-Soyad                ELO      UKD")
    print("----  -----   ------------------------------   -------  -------")

    for sira_no, bilgiler in bsno_sozluk.items():
        print(format(sira_no, "4d"), end="   ")
        print(format(bilgiler[0], "4d"), end="   ")
        print(bilgiler[1].ljust(30), end="   ")
        print(format(bilgiler[2], "7d"), end="   ")
        print(format(bilgiler[3], "6d"))

    return bsno_sozluk


def siralama_yap(bsno_sozluk, tek, oyuncu_sayisi):  # 1. tur hariç eşletirmeler yapılmadan önce oyuncular siralanir
    sno_liste = bsno_sozluk.values()

    sno_liste = sorted(sno_liste, key=lambda lnoo: lnoo[0])
    sno_liste = sorted(sno_liste, key=lambda ad: ad[1])
    sno_liste = sorted(sno_liste, key=lambda ukd: ukd[3], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda elo: elo[2], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda puan: puan[4], reverse=True)

    sno_liste = tur_atlat(sno_liste, tek)  # oyuncu sayisi tek ise sondaki oyuncu bye geçer
    sno_sozluk = {}

    for sno in range(oyuncu_sayisi):  # oyuncular bsno sira numaraları ile sıralamaya göre sözlüğe eklenir
        lno = sno_liste[sno][0]
        kisi = 1
        bulundu = False
        while kisi <= oyuncu_sayisi and not bulundu:
            if lno == bsno_sozluk[kisi][0]:   # oyuncunun bsno'su bulunur
                sno_sozluk.setdefault(kisi, sno_liste[sno])
                bulundu = True
            else:
                bulundu = False
                kisi += 1

    return sno_sozluk


def oyuncu_sayisi_tek_cift_mi(oyuncu_sayisi):  # oyuncu sayisi tek mi çift mi belirlenir
    if oyuncu_sayisi % 2 == 1:
        tek = True
    else:
        tek = False
    return tek


def ilk_tur_eslesme(renk_sozlugu, bsno_sozluk, msno_sozluk, oyuncu_sayisi, eslesme_sozlugu, tek):  # bütün oyuncular sırayla ikili olarak eşleştirilirler
    if tek:  # oyuncu sayisi tek ise sondaki oyuncuya bye atanır
        son_oyuncu = bsno_sozluk.get(oyuncu_sayisi)
        son_oyuncu[5] = "BYE"
        eslesme_sozlugu[oyuncu_sayisi][0][0] = "-"  # ilk tur rakibi - olarak girilir, yoktur
        eslesme_sozlugu[oyuncu_sayisi][0][1] = "-"  # ilk tur rengi - olarak girilir, yoktur
        eslesme_sozlugu[oyuncu_sayisi][0][2] = TAM_PAUN  # bye geçen oyuncu 1 puan alır

    sayi = 1
    msno = 1
    if tek:   # oyuncu sayisi tek ise son oyuncu eşleştirmeye dahil olmaz
        while sayi < oyuncu_sayisi:
            oyuncu = renk_sozlugu.get(sayi)  # oyuncuların rengi ilk oyuncunun rengine göre belirlendi
            if oyuncu[0] == "b":
                msno_sozluk.setdefault(msno, [sayi, sayi + 1])  # beyaz siyah şeklinde sıralamak için
            else:
                msno_sozluk.setdefault(msno, [sayi + 1, sayi])

            sayi += 2
            msno += 1
        msno_sozluk.setdefault(msno, [oyuncu_sayisi, "BYE"])  # son masaya bye geçen oyuncu yerleştirilir

    else:   # oyuncu sayisi çift ise bütün oyuncular eşleştirilir
        while sayi <= oyuncu_sayisi:
            oyuncu = renk_sozlugu.get(sayi)
            if oyuncu[0] == "b":
                msno_sozluk.setdefault(msno, [sayi, sayi + 1])  # beyaz siyah şeklinde sıralamak için
            else:
                msno_sozluk.setdefault(msno, [sayi + 1, sayi])

            sayi += 2
            msno += 1

    return msno_sozluk


def rakip_kontrol(eslesme_sozlugu, oyuncu, rakip, tur):  # eslesmeler yapılırken oyuncunun o rakiple daha önce eşleşip eşleşmediği kontrol edilir
    var = False
    tur_index = 0
    while tur-1 > tur_index and not var:
        if eslesme_sozlugu[oyuncu][tur_index][0] == rakip:
            var = True
        else:
            var = False
            tur_index += 1
    return var


def eslestirme_yap(sno_sozluk, msno_sozluk, renk_sozlugu, eslesme_sozlugu, tur, tek, oyuncu_sayisi, bsno_sozluk, masa_sayisi):  # 1. tur hariç eşleştirmeler yapılır
    eslesti_listesi = []  # eşleşmesi yapılan oyuncular burada tutulur

    puan_gruplari = puan_gruplari_olustur(bsno_sozluk, sno_sozluk)  # puan grupları sözlüğü
    tur_atlayan = None
    if tek:  # oyuncu sayisi tekise bye geçen oyuncunun tur bilgileri eslesme sozlüğüne eklenir
        sno_liste = []
        for oyuncu in sno_sozluk.keys():
            sno_liste.append(oyuncu)
        tur_atlayan = sno_liste[oyuncu_sayisi - 1]
        eslesti_listesi.append(tur_atlayan)
        eslesme_sozlugu[tur_atlayan][tur-1][0] = "-"
        eslesme_sozlugu[tur_atlayan][tur - 1][1] = "-"
        eslesme_sozlugu[tur_atlayan][tur - 1][2] = TAM_PAUN

    for masa in range(1, masa_sayisi):  # her masa için eşleştime yapılır
        for oyuncu in sno_sozluk.keys():  # eşleştirilmemiş her oyuncu için eşleştirme yapılır
            diger_masa = False
            if oyuncu not in eslesti_listesi:  # oyuncunun daha önce eşleştirilip eşleştirilmediği kontrol edilir
                eslesti_listesi.append(oyuncu)  # oyuncu eşleşti listesine eklenir
                bulundu = False
                puan = sno_sozluk[oyuncu][4]

                for puan_araligi in puan_gruplari.keys():  # puan aralıklarında rakip aramasi yapılır

                    while puan >= puan_araligi and not bulundu:  # rakibin puanı oyuncuyla aynı olmalıdır, rakip bulunamazsa alt puan gruplarında arama yapılır

                        for rakip in puan_gruplari[puan_araligi]:  # arama yapılan puan aralığındaki rakip uygun mu diye kontrol edilir, değilse diğer rakibe geçilir

                            if rakip not in eslesti_listesi:  # rakip daha önce eşleştirilmiş mi diye kontrol edilir
                                var = rakip_kontrol(eslesme_sozlugu, oyuncu, rakip, tur)  # oyuncu ve rakip daha önce eşleşmiş mi diye kontrol edilir
                                if not var:
                                    uygun = True  # rakip uygun olmazsa diğer rakibe geçilmesini sağlar
                                    while not bulundu and uygun:
                                        oyuncu_renk = renk_sozlugu[oyuncu][tur - 2]  # oyuncunun önceki turdaki rengi

                                        if oyuncu_renk == "-":  # önceki turda rengi yoksa bir önceki turdaki rengine bakılır
                                            oyuncu_renk = renk_sozlugu[oyuncu][tur - 3]

                                        if oyuncu_renk == "s":  # oyuncuya önceki turda aldığı rengin karşıtı verilir
                                            oyuncu_renk = "b"
                                        else:
                                            oyuncu_renk = "s"

                                        rakip_renk = renk_sozlugu[rakip][tur - 2]  # rakibin önceki turdaki rengi

                                        if rakip_renk == "-":  # önceki turda rengi yoksa bir önceki turdaki rengine bakılır
                                            rakip_renk = renk_sozlugu[rakip][tur - 3]

                                        if rakip_renk == "s":  # rakibe önceki turda aldığı rengin karşıtı verilir
                                            rakip_renk = "b"
                                        elif rakip_renk == "b":
                                            rakip_renk = "s"

                                        if tur == 2 and rakip_renk == "-":  # ilk turda bye geçmiş rakibin herhangi bir rengi olmadığı için oyuncunun karşıt rengi verilir
                                            if oyuncu_renk == "b":
                                                rakip_renk = "s"
                                            else:
                                                rakip_renk = "b"

                                        if oyuncu_renk == rakip_renk:  # oyuncu ve rakp rengi aynı olursa diğer rakipe geçilir
                                            bulundu = False
                                            uygun = False
                                        else:  # renkler karşıt olursa eşleştirme yapılır
                                            bulundu = True
                                            renk_sozlugu[oyuncu][tur-1] = oyuncu_renk
                                            renk_sozlugu[rakip][tur - 1] = rakip_renk

                                            eslesti_listesi.append(rakip)  # rakip eşleşti listesine eklenir
                                            if oyuncu_renk == "b":  # oyuncular masaya beyaz-siyah şeklinde oturtulur
                                                msno_sozluk.setdefault(masa, [oyuncu, rakip])
                                            else:
                                                msno_sozluk.setdefault(masa, [rakip, oyuncu])

                        if not bulundu:  # yukarıdaki kuralda rakip bulunmazsa bu kurala geçilir
                            for rakip in puan_gruplari[puan_araligi]:   # arama yapılan puan aralığındaki rakip uygun mu diye kontrol edilir, değilse diğer rakibe geçilir
                                if rakip not in eslesti_listesi:  # rakip daha önce eşleştirilmiş mi diye kontrol edilir
                                    var = rakip_kontrol(eslesme_sozlugu, oyuncu, rakip, tur)  # oyuncu ve rakip daha önce eşleşmiş mi diye kontrol edilir
                                    if not var:
                                        uygun = True
                                        while not bulundu and uygun:
                                            oyuncu_renk = renk_sozlugu[oyuncu][tur - 2]    # oyuncunun önceki turdaki rengi

                                            if oyuncu_renk == "-":  # önceki turda rengi yoksa bir önceki turdaki rengine bakılır
                                                oyuncu_renk = renk_sozlugu[oyuncu][tur - 3]

                                            if oyuncu_renk == "s":  # oyuncuya önceki turda aldığı rengin karşıtı verilir
                                                oyuncu_renk = "b"
                                            else:
                                                oyuncu_renk = "s"

                                            rakip_renk = renk_sozlugu[rakip][tur - 2]  # rakibin önceki turdaki rengi
                                            if rakip_renk == "-":
                                                rakip_renk = renk_sozlugu[rakip][tur - 3]

                                            if rakip_renk == "s":  # rakibe önceki turda aldığı renk verilir
                                                rakip_renk = "s"
                                            else:
                                                rakip_renk = "b"

                                            renk_sayi_farki = renk_sozlugu[rakip].count("b") - renk_sozlugu[rakip].count("s")  # bir renk diğerinden en fazla 2 kez fazla elınabilir

                                            # aynı renk 3 kez arka arkaya alınamaz ve bir renk diğerinden sayıca 2 den fazla alınamaz, rakibe önceki turdaki rengini verebilmek için bu kontrol edilir
                                            if ((renk_sozlugu[rakip][tur - 2] == renk_sozlugu[rakip][tur - 3]) and (rakip_renk == renk_sozlugu[rakip][tur - 2])) or (renk_sayi_farki > 2 or renk_sayi_farki < -2):
                                                bulundu = False  # kurala uymazsa diğer rakibe geçilir
                                                uygun = False

                                            else:
                                                if oyuncu_renk == rakip_renk:  # oyuncu ve rakip rengi aynı olursa diğer rakibe geçilir
                                                    bulundu = False
                                                    uygun = False

                                                else:  # renkler karşıt ise eşleşme yapılır
                                                    bulundu = True
                                                    renk_sozlugu[oyuncu][tur - 1] = oyuncu_renk
                                                    renk_sozlugu[rakip][tur - 1] = rakip_renk

                                                    eslesti_listesi.append(rakip)  # rakip eşleşti listesine eklenir
                                                    if oyuncu_renk == "b":  # oyuncular beyaz-siyah şeklinde masaya yerleştirilir
                                                        msno_sozluk.setdefault(masa, [oyuncu, rakip])
                                                    else:
                                                        msno_sozluk.setdefault(masa, [rakip, oyuncu])
                        if not bulundu:  # yukarıdaki kuralda da rakip bulunmazsa bu kurala geçilir
                            for rakip in puan_gruplari[puan_araligi]: # arama yapılan puan aralığındaki rakip uygun mu diye kontrol edilir, değilse diğer rakibe geçilir
                                if rakip not in eslesti_listesi:  # rakip daha önce eşleştirilmiş mi diye kontrol edilir
                                    var = rakip_kontrol(eslesme_sozlugu, oyuncu, rakip, tur)  # oyuncu ve rakip daha önce eşleşmiş mi diye kontrol edilir
                                    if not var:
                                        uygun = True
                                        while not bulundu and uygun:
                                            oyuncu_renk = renk_sozlugu[oyuncu][tur - 2]  # oyuncunun önceki turdaki rengi

                                            if oyuncu_renk == "-":   # önceki turda rengi yoksa bir önceki turdaki rengine bakılır
                                                oyuncu_renk = renk_sozlugu[oyuncu][tur - 3]

                                            if oyuncu_renk == "s":  # oyuncuya önceki turda aldığı renk verilir
                                                oyuncu_renk = "s"
                                            else:
                                                oyuncu_renk = "b"

                                            renk_sayi_farki = renk_sozlugu[oyuncu].count("b") - renk_sozlugu[oyuncu].count("s")  # bir renk diğerinden en fazla 2 kez fazla elınabilir

                                            # aynı renk 3 kez arka arkaya alınamaz ve bir renk diğerinden sayıca 2 den fazla alınamaz, oyuncuya önceki turdaki rengini verebilmek için bu kontrol edilir
                                            if ((renk_sozlugu[oyuncu][tur - 2] == renk_sozlugu[oyuncu][tur - 3]) and (oyuncu_renk == renk_sozlugu[oyuncu][tur - 2])) or (renk_sayi_farki > 2 or renk_sayi_farki < -2):
                                                bulundu = False  # kurala uymazsa diğer rakibe geçilir
                                                uygun = False

                                            else:  # oyuncu renk kurallarına uyuyorsa rakibin rengi kontrol edilir
                                                rakip_renk = renk_sozlugu[rakip][tur - 2]  # rakibin önceki turdaki rengi
                                                if rakip_renk == "-":  # önceki turda rengi yoksa bir önceki turdaki rengine bakılır
                                                    rakip_renk = renk_sozlugu[rakip][tur - 3]

                                                if rakip_renk == "s":  # rakibe önceki turda aldığı rengin karşıtı verilir
                                                    rakip_renk = "b"
                                                else:
                                                    rakip_renk = "s"

                                                if oyuncu_renk == rakip_renk:  # oyuncu ve rakip rengi aynı olursa diğer rakibe geçilir
                                                    bulundu = False
                                                    uygun = False

                                                else:  # renkler karşıt olursa eşleştirme yapılır
                                                    bulundu = True
                                                    renk_sozlugu[oyuncu][tur - 1] = oyuncu_renk
                                                    renk_sozlugu[rakip][tur - 1] = rakip_renk
                                                    eslesti_listesi.append(rakip)  # rakip eşleşti listesine eklenir
                                                    if oyuncu_renk == "b":  # oyuncular beyaz-siyah şeklinde masaya oturtulurlar
                                                        msno_sozluk.setdefault(masa, [oyuncu, rakip])

                                                    else:
                                                        msno_sozluk.setdefault(masa, [rakip, oyuncu])
                            else:
                                break

                    if bulundu:  # rakip bulunduysa bir alt puan araığına geçilmez
                        diger_masa = True
                        break

            if diger_masa:  # rakip bulunduysa diğer masaya geçilir
                break

    if tek:  # bye geçen oyuncu son masaya oturtulup karşısına bye yazılır
        msno_sozluk.setdefault(len(msno_sozluk) + 1, [tur_atlayan, "BYE"])

    return msno_sozluk


def buchhloz_sonneborn_hesapla(eslesme_sozlugu, bsno_sozluk, tur_sayisi, esitlik_bozucu_sozluk):  # eşitlik bozma puanlari hesaplanir
    siralama_icin_puan_sozlugu = {}  # oyuncuların oynayamadıkları maçlar için hesaplanan punanları tutulur
    sb_icin_puan_sozlugu = {}  # oyuncuların bye geçtikleri ya da rakiplerinin gelmedikleri maçlar için hesaplanan puanlar tutulur
    for oyuncu in eslesme_sozlugu.keys():
        tur = 0
        atlama_puani = []  # oyuncunun oynayamadığı maçlar için hesaplanan punanları tutulur
        sb_icin_puan = []  # oyuncunun bye geçtiği ya da rakiplerinin gelmedikleri maçlar için hesaplanan puanlar tutulur
        atlamaya_kadarki_puan = 0  # oynanmayan maçların puanını heesaplamak için kullanılır

        while tur <= tur_sayisi - 1:  # her tur için veriler kontrol edilir
            if eslesme_sozlugu[oyuncu][tur][0] == "-":   # bye geçme durumu
                kalan_tur = tur_sayisi - tur - 1
                atlama_puani.append(atlamaya_kadarki_puan + (kalan_tur*YARIM_PUAN))
                sb_icin_puan.append(atlamaya_kadarki_puan + (kalan_tur*YARIM_PUAN))
                atlamaya_kadarki_puan += TAM_PAUN

                tur += 1
            elif eslesme_sozlugu[oyuncu][tur][2] == "+":   # rakibi gelmedi
                kalan_tur = tur_sayisi - tur - 1
                atlama_puani.append(atlamaya_kadarki_puan + (kalan_tur*YARIM_PUAN))
                sb_icin_puan.append(atlamaya_kadarki_puan + (kalan_tur * YARIM_PUAN))
                atlamaya_kadarki_puan += TAM_PAUN

                tur += 1
            elif eslesme_sozlugu[oyuncu][tur][2] == "-":   # oyuncunun kendisi gelmedi
                kalan_tur = tur_sayisi - tur - 1
                atlama_puani.append(atlamaya_kadarki_puan + (kalan_tur*YARIM_PUAN))
                tur += 1

            else:

                if eslesme_sozlugu[oyuncu][tur][2] == "½":
                    atlamaya_kadarki_puan += YARIM_PUAN
                elif eslesme_sozlugu[oyuncu][tur][2] == TAM_PAUN:
                    atlamaya_kadarki_puan += TAM_PAUN
                tur += 1

        siralama_icin_puan_sozlugu.setdefault(oyuncu, atlama_puani)
        sb_icin_puan_sozlugu.setdefault(oyuncu, sb_icin_puan)

    oyuncunun_rakiplerinin_puanlari = {}  # oynanan maçlar için oyuncuların rakiplerinin puanları tutulur

    for oyuncu in eslesme_sozlugu.keys():
        rakip_puanlari = []   # oynanan maçlar için oyuncunun rakiplerinin puanları tutulur
        sb_rakip_puanlari = []  # oyuncun yendiği rakiplerin puanları ve berabere kaldığı rakiplerin puanlarının yarısı tutulur

        for tur in range(tur_sayisi):
            rakip = eslesme_sozlugu[oyuncu][tur][0]
            if rakip != "-":   # bye geçilmediyse
                if eslesme_sozlugu[oyuncu][tur][2] not in ["+", "-"]:  # maç oynandıysa
                    rakip_puanlari.append(bsno_sozluk[rakip][4])
                    sonuc = eslesme_sozlugu[oyuncu][tur][2]
                    if sonuc == 1:
                        sb_rakip_puanlari.append(bsno_sozluk[rakip][4])
                    elif sonuc == "½":
                        sb_rakip_puanlari.append(bsno_sozluk[rakip][4]/2)

        for atlama in siralama_icin_puan_sozlugu[oyuncu]:
            rakip_puanlari.append(atlama)

        for sb in sb_icin_puan_sozlugu[oyuncu]:
            sb_rakip_puanlari.append(sb)

        esitlik_bozucu_sozluk[oyuncu][2] = sum(sb_rakip_puanlari)  # ssb puanı esitlik_bozucu_sozluk teki yerine eklenir

        rakip_puanlari.sort(reverse=True)  # puanlar büyükten küçüğe sıralanır
        oyuncunun_rakiplerinin_puanlari.setdefault(oyuncu, rakip_puanlari)

    for oyuncu, rakipler in oyuncunun_rakiplerinin_puanlari.items():  # bh1 hesabı için sondaki en küçük puan hariç tüm puanlar toplanır
        bh1 = 0
        for rakip in range(len(rakipler)-1):
            bh1 += rakipler[rakip]

        esitlik_bozucu_sozluk[oyuncu][0] = bh1  # bh1 puanı esitlik_bozucu_sozluk teki yerine eklenir

    for oyuncu, rakipler in oyuncunun_rakiplerinin_puanlari.items():  # bh2 hesabı için sondaki en küçük 2 puan hariç tüm puanlar toplanır
        bh2 = 0
        for rakip in range(len(rakipler)-2):
            bh2 += rakipler[rakip]

        esitlik_bozucu_sozluk[oyuncu][1] = bh2  # bh2 puanı esitlik_bozucu_sozluk teki yerine eklenir

    return esitlik_bozucu_sozluk


def puan_gruplari_olustur(bsno_sozluk, sno_sozluk):  # eşleştirmeleri yapabilmek için hangi puan grubunda hangi oyuncuların olduğu belirlenir
    puan_gruplari = {}
    for oyuncu in sno_sozluk.keys():
        puan = bsno_sozluk[oyuncu][4]
        if puan not in puan_gruplari.keys():  # hangi puan gruplarının olduğu bulunur ve key olarak eklenir
            puan_gruplari.setdefault(puan, [])

    for puan in puan_gruplari.keys():
        for rakip in sno_sozluk.keys():
            if bsno_sozluk[rakip][4] == puan:  # oyuncu hangi puan grubundaysa oraya eklenir
                puan_gruplari.get(puan).append(rakip)

    return puan_gruplari


def eslestirme_tablosunu_yazdir(msno_sozluk, bsno_sozluk, bye_kontrol, masa_sayisi, tur):  # eşleştirme tablosu yazdırılır
    print()
    print("{}. Tur Eşleştirme Listesi:".format(tur))
    print()
    print("             Beyazlar                       Siyahlar")
    print("MNo    BSNo     LNo     Puan    -    Puan     LNo     BSNo")
    print("---    ----    -----    ----         ----    -----    ----")
    for masa_no in range(1, masa_sayisi):
        bsno1 = msno_sozluk[masa_no][0]
        bsno2 = msno_sozluk[masa_no][1]

        print(format(masa_no, "3d"), end="    ")

        print(format(bsno1, "4d"), end="    ")  # bsno
        print(format(bsno_sozluk[bsno1][0], "5d"), end="    ")  # lno
        print(format(bsno_sozluk[bsno1][4], "4.2f"), end="    ")  # puan
        print("-", end="    ")
        print(format(bsno_sozluk[bsno2][4], "4.2f"), end="    ")  # puan
        print(format(bsno_sozluk[bsno2][0], "5d"), end="    ")  # lno
        print(format(bsno2, "4d"))  # bsno

    if bye_kontrol:
        bsno1 = msno_sozluk[masa_sayisi][0]

        print(format(masa_sayisi, "3d"), end="    ")
        print(format(bsno1, "4d"), end="    ")  # bsno
        print(format(bsno_sozluk[bsno1][0], "5d"), end="    ")  # lno
        print(format(bsno_sozluk[bsno1][4], "4.2f"), end="    ")  # puan
        print("-", end="    ")
        print(bsno_sozluk[bsno1][5].ljust(6))


def eslesme_sozlugune_ekle(eslesme_sozluk, renk_sozlugu, oyuncu, rakip, puan1, puan2, tur):  # her maç sonucu alındığında sonuçlar eşleşme sözüğüne eklenir
    renk1 = renk_sozlugu[oyuncu][tur-1]
    renk2 = renk_sozlugu[rakip][tur-1]

    eslesme_sozluk[oyuncu][tur-1][2] = puan1  # oyuncu puan
    eslesme_sozluk[oyuncu][tur-1][1] = renk1  # oyuncu renk
    eslesme_sozluk[oyuncu][tur-1][0] = rakip  # rakip bsno

    if rakip != "BYE":
        eslesme_sozluk[rakip][tur-1][2] = puan2  # rakip puan
        eslesme_sozluk[rakip][tur-1][1] = renk2  # rakip renk
        eslesme_sozluk[rakip][tur-1][0] = oyuncu  # oyuncu bsno

    else:
        eslesme_sozluk[oyuncu][tur-1][2] = TAM_PAUN  # oyuncu puan
        eslesme_sozluk[oyuncu][tur-1][1] = "-"  # oyuncu renk
        eslesme_sozluk[oyuncu][tur-1][0] = "-"  # rakip  bsno


def bye_kontrol_yap(msno_sozluk):  # son masada bye durumu var mı diye bakılır ve sonuç alınacak masa sayisi belirlenir
    bye_kontrol = msno_sozluk[len(msno_sozluk)][1]

    if bye_kontrol == "BYE":
        bye_kontrol = True
        masa_sayisi = len(msno_sozluk)
    else:
        bye_kontrol = False
        masa_sayisi = len(msno_sozluk) + 1

    return bye_kontrol, masa_sayisi


def mac_sonucunu_al(masa, tur):  # maç sonucu alınır
    sonuc = 0
    sonuc_hatali = True
    while sonuc_hatali:
        try:
            sonuc = int(input("{}. turda {}. masada oynanan macin sonucunu giriniz (0-5):".format(tur, masa)))
            while sonuc < 0 or sonuc > 5:
                sonuc = int(input("1. turda {}. masada oynanan macin sonucunu giriniz (0-5):".format(masa)))
            sonuc_hatali = False
        except ValueError:
            print("Geçersiz Sayı")
            sonuc_hatali = True
            continue

    puan1, puan2 = sonuclarin_puan_karsiligi(sonuc)  # sonuçların karşılığı alınır

    return puan1, puan2


def bsno_sozluk_puan_ekle(puan1, puan2, bsno_sozluk, oyuncu, rakip):  # maç sonucu alındıktan sonra puanlar bsno_sozluk e eklenir
    if puan1 == "½":
        puan1 = YARIM_PUAN

    if puan2 == "½":
        puan2 = YARIM_PUAN

    if puan1 in [PUAN_YOK, TAM_PAUN, YARIM_PUAN]:
        bsno_sozluk[oyuncu][4] += puan1
    elif puan1 == "+":
        bsno_sozluk[oyuncu][4] += TAM_PAUN
        if bsno_sozluk[oyuncu][5] != "BYE":
            bsno_sozluk[oyuncu][5] = "-"  # rakip gelmediği için tur atladı

    if puan2 in [PUAN_YOK, TAM_PAUN, YARIM_PUAN]:
        bsno_sozluk[rakip][4] += puan2

    elif puan2 == "+":
        bsno_sozluk[rakip][4] += TAM_PAUN
        if bsno_sozluk[rakip][5] != "BYE":
            bsno_sozluk[rakip][5] = "-"  # rakip gelmediği için tur atladı


def bye_puan_ekle(bye_kontrol, msno_sozluk, bsno_sozluk):  # bye geçen oyuncuya 1 puan eklenir
    if bye_kontrol:
        masa_sayisi = len(msno_sozluk)
        eslesme = msno_sozluk[masa_sayisi]
        kisi = eslesme[0]
        bsno_sozluk[kisi][4] += TAM_PAUN


def tur_atlat(sno_liste, tek):  # oyuncu sayısı sıralanmış listede kurallara uyan son oyuncuya tur atlat
    if tek:
        bulundu = False
        kisi = len(sno_liste) - 1
        while kisi > 0 and not bulundu:
            if sno_liste[kisi][5] == "-" or sno_liste[kisi][5] == "BYE":  # "-" rakip gelmedi anlamındadır
                kisi -= 1
            else:
                sno_liste[kisi][5] = "BYE"

                bulundu = True
                sno_liste = insertion_sort(sno_liste, kisi)  # bye geçen listenin sonuna atılır ve diğer oyuncular birer adım yukarı kaydırılır
    return sno_liste


def insertion_sort(sno_liste, kisi):  # bye olanı sona atar ve diğer oyuncuları bir basamak yukarı kaydırır
    konum = len(sno_liste) - 1
    bilgi1 = sno_liste[konum]
    sno_liste[konum] = sno_liste[kisi]

    while konum > kisi:
        bilgi2 = sno_liste[konum - 1]
        sno_liste[konum - 1] = bilgi1
        bilgi1 = bilgi2
        konum -= 1

    return sno_liste


def tur_verilerini_sozluklere_ekle(msno_sozluk, bsno_sozluk, eslesme_sozlugu, renk_sozlugu, esitlik_bozucu_sozluk,bye_kontrol, masa_sayisi, tur):

    bye_puan_ekle(bye_kontrol, msno_sozluk, bsno_sozluk)  # bye geçen oyuncu varsa 1 puan aklenir

    for masa in range(1, masa_sayisi):
        puan1, puan2 = mac_sonucunu_al(masa, tur)

        oyuncu = msno_sozluk[masa][0]
        rakip = msno_sozluk[masa][1]

        eslesme_sozlugune_ekle(eslesme_sozlugu, renk_sozlugu, oyuncu, rakip, puan1, puan2, tur)  # eslesme sozluğüne maç sonuçları eklenir
        esitlik_bozucu_sozluge_galibiyet_sayisi_ekle(esitlik_bozucu_sozluk, puan1, puan2, oyuncu, rakip)  # kazanan ya da rakibi gelmeyen oyuncu için galibiyet sayısı eklenir
        bsno_sozluk_puan_ekle(puan1, puan2, bsno_sozluk, oyuncu, rakip) # oyuncuların puanları bsno_sozluk e eklenir


def sonuclarin_puan_karsiligi(sonuc):  # maç sonuçlarını karşılıklarına dönüştürülür
    if sonuc == 0:
        return "½", "½"
    elif sonuc == 1:
        return TAM_PAUN, PUAN_YOK
    elif sonuc == 2:
        return PUAN_YOK, TAM_PAUN
    elif sonuc == 3:
        return "+", "-"
    elif sonuc == 4:
        return "-", "+"
    else:
        return "-", "-"


def eslesme_sozlugu_olustur(tur_sayisi, oyuncu_sayisi):  # tur sayısına göre eşleşme sözlüğü oluşturulur
    eslesme_sozlugu = {}
    for oyuncu in range(1, oyuncu_sayisi + 1):
        kisi = []
        for tur in range(tur_sayisi):
            kisi.append([0, 0, 0])
        eslesme_sozlugu.setdefault(oyuncu, kisi)
    return eslesme_sozlugu


def main():
    oyuncu_bilgileri = []

    lno_hatali = True
    lno = 1
    while lno_hatali and lno > 0:
        try:
            lno = int(input(
                "Lisans Numarası (0'dan büyük tam sayı olmalıdır. Başka oyunca yoksa 0 ya da negatif bir sayı giriniz):"))  # lisans numarası
            lno_hatali = False
        except ValueError:
            print("Geçersiz sayı")
            lno_hatali = True
            continue

    while lno > 0:
        oyuncu = [0, 0, 0, 0, 0, 0]
        lno = lisans_no_kontrol(lno, oyuncu_bilgileri)
        oyuncu[0] = lno

        ad_soyad = input("Ad Soyad:").replace("i", "İ").upper()
        while ad_soyad == "":
            ad_soyad = input("Ad Soyad:").replace("i", "İ").upper()

        oyuncu[1] = ad_soyad

        elo_hata = True
        elo = 0
        while elo_hata:
            try:
                elo = int(
                    input("Uluslararası Kuvvet Puanını Giriniz(en az 1000, yoksa 0):"))  # uluslararası kuvvet puanı
                while elo < 1000 and elo != 0:
                    elo = int(input("Hatalı giriş, tekrar giriniz:"))
                elo_hata = False
            except ValueError:
                print("Geçersiz sayı")
                elo_hata = True
                continue

        oyuncu[2] = elo

        ukd_hata = True
        ukd = 0
        while ukd_hata:
            try:
                ukd = int(input("Ulusal kuvvet Puanını Giriniz(en az 1000, yoksa 0):"))  # ulusal kuvvet puanı
                while ukd < 1000 and ukd != 0:
                    ukd = int(input("Hatalı giriş, tekrar giriniz:"))
                ukd_hata = False
            except ValueError:
                print("Geçersiz sayı")
                ukd_hata = True
                continue
        oyuncu[3] = ukd

        oyuncu_bilgileri.append(oyuncu)

        hatali = True
        while hatali:
            try:
                lno = int(input(
                    "Lisans Numarası (0'dan büyük tam sayı olmalıdır. Başka oyunca yoksa 0 ya da negatif bir sayı giriniz):"))  # lisans numarası
                hatali = False
            except ValueError:
                print("Geçersiz sayı")
                hatali = True
                continue

    try:

        bsno_sozluk = baslangic_siralama_tablosu_yazdir(oyuncu_bilgileri)

        oyuncu_sayisi = len(bsno_sozluk)

        tur_sayisi = int(math.log(oyuncu_sayisi, 2).__ceil__())

        tur = 0
        tur_hatali = True
        while tur_hatali:
            try:
                tur = int(input("Turnuvadaki tur sayisini giriniz:"))
                while tur < tur_sayisi or tur > oyuncu_sayisi - 1:
                    tur = int(input("Turnuvadaki tur sayisini giriniz:"))
                tur_hatali = False
            except ValueError:
                print("Geçersiz Sayı")
                tur_hatali = True
                continue

        tek = oyuncu_sayisi_tek_cift_mi(oyuncu_sayisi)
        renk_sozlugu = renk_sozlugu_olustur(tur, oyuncu_sayisi)
        renk_sozlugu = ilk_renk_atama(renk_sozlugu, tek, oyuncu_sayisi)

        eslesme_sozlugu = eslesme_sozlugu_olustur(tur, oyuncu_sayisi)

        msno_sozluk = {}
        msno_sozluk = ilk_tur_eslesme(renk_sozlugu, bsno_sozluk, msno_sozluk, oyuncu_sayisi, eslesme_sozlugu, tek)

        esitlik_bozucu_sozluk = esitlik_bozucu_sozluk_olustur(oyuncu_sayisi)

        bye_kontrol, masa_sayisi = bye_kontrol_yap(msno_sozluk)
        eslestirme_tablosunu_yazdir(msno_sozluk, bsno_sozluk, bye_kontrol, masa_sayisi, tur=1)
        tur_verilerini_sozluklere_ekle(msno_sozluk, bsno_sozluk, eslesme_sozlugu, renk_sozlugu, esitlik_bozucu_sozluk,
                                       bye_kontrol, masa_sayisi, tur=1)

        for turr in range(2, tur + 1):
            msno_sozluk = {}
            sno_sozluk = siralama_yap(bsno_sozluk, bye_kontrol, oyuncu_sayisi)
            eslestirme_yap(sno_sozluk, msno_sozluk, renk_sozlugu, eslesme_sozlugu, turr, tek, oyuncu_sayisi, bsno_sozluk, masa_sayisi)
            eslestirme_tablosunu_yazdir(msno_sozluk, bsno_sozluk, bye_kontrol, masa_sayisi, turr)
            tur_verilerini_sozluklere_ekle(msno_sozluk, bsno_sozluk, eslesme_sozlugu, renk_sozlugu, esitlik_bozucu_sozluk,
                                           bye_kontrol, masa_sayisi, turr)

        esitlik_bozucu_sozluk = buchhloz_sonneborn_hesapla(eslesme_sozlugu, bsno_sozluk, tur, esitlik_bozucu_sozluk)
        nihai_liste = nihai_siralama_listesi_yazdir(esitlik_bozucu_sozluk, bsno_sozluk, oyuncu_sayisi)
        capraz_tablo_yazdir(nihai_liste, eslesme_sozlugu, oyuncu_sayisi, tur)
    except ValueError:
        print("Oyuncu girişi olmadığı için program sonlandırıldı.")
    except IndexError:
        print("Tek oyuncu olduğu için eşleştirme yapılamıyor, program sonlandırıldı.")


def nihai_siralama_listesi_yazdir(esitlik_bozucu_sozluk, bsno_sozluk, oyuncu_sayisi):  # oyuncular eşitlik bozma ölçütleriyle beraber sıralayıp tablo olarak yazdırır
    for oyuncu, bilgiler in bsno_sozluk.items():
        for puanlar in range(4):
            bilgiler.append(esitlik_bozucu_sozluk[oyuncu][puanlar])
        bilgiler.append(oyuncu)

    sno_liste = bsno_sozluk.values()

    sno_liste = sorted(sno_liste, key=lambda lnoo: lnoo[0])
    sno_liste = sorted(sno_liste, key=lambda ad: ad[1])
    sno_liste = sorted(sno_liste, key=lambda ukd: ukd[3], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda elo: elo[2], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda gs: gs[9], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda sb: sb[8], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda bh2: bh2[7], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda bh1: bh1[6], reverse=True)
    sno_liste = sorted(sno_liste, key=lambda puan: puan[4], reverse=True)

    for sira in range(oyuncu_sayisi):
        sno_liste[sira].append(sira+1)

    print()
    print("Nihai Sıralama Listesi:")
    print()
    print(" SNo      BSNo      LNo                Ad-Soyad                ELO        UKD      Puan      BH-1      BH-2       SB       GS")
    print("-----    ------    -----    ------------------------------    ------    ------    ------    ------    ------    ------    ----")

    for oyuncu in range(oyuncu_sayisi):
        print(format(sno_liste[oyuncu][11], "5d"), end="    ")
        print(format(sno_liste[oyuncu][10], "6d"), end="    ")
        print(format(sno_liste[oyuncu][0], "5d"), end="    ")
        print(sno_liste[oyuncu][1].ljust(30), end="    ")
        print(format(sno_liste[oyuncu][2], "6d"), end="    ")
        print(format(sno_liste[oyuncu][3], "6d"), end="    ")
        print(format(sno_liste[oyuncu][4], "6.2f"), end="    ")
        print(format(sno_liste[oyuncu][6], "6.2f"), end="    ")
        print(format(sno_liste[oyuncu][7], "6.2f"), end="    ")
        print(format(sno_liste[oyuncu][8], "6.2f"), end="    ")
        print(format(sno_liste[oyuncu][9], "4d"))

    return sno_liste


def capraz_tablo_yazdir(nihai_liste, eslesme_sozlugu, oyuncu_sayisi, tur_sayisi):  # oyuncuları bsno larına göre sıralayıp tablo olarak yazdırır
    bsno_liste = sorted(nihai_liste, key=lambda bsno: bsno[10])

    print()
    print("Çapraz Tablo:")
    print()
    print(" BSNo     SNo       LNo                Ad-Soyad                 ELO       UKD", end="     ")

    for tur in range(1, tur_sayisi+1):
        print("{}. Tur".format(tur), end="     ")

    print(" Puan      BH-1      BH-2       SB       GS")

    print("-----    ------    -----    ------------------------------    ------    ------", end="    ")

    for tur in range(tur_sayisi):
        print("-------", end="    ")

    print("------    ------    ------    ------    ----")

    for oyuncu in range(oyuncu_sayisi):
        print(format(bsno_liste[oyuncu][10], "5d"), end="    ")
        print(format(bsno_liste[oyuncu][11], "6d"), end="    ")
        print(format(bsno_liste[oyuncu][0], "5d"), end="    ")
        print(bsno_liste[oyuncu][1].ljust(30), end="    ")
        print(format(bsno_liste[oyuncu][2], "6d"), end="    ")
        print(format(bsno_liste[oyuncu][3], "6d"), end="    ")

        for tur in range(tur_sayisi):
            for bilgi in range(3):
                print(format(str(eslesme_sozlugu[oyuncu+1][tur][bilgi]), "2"), end=" ")
            print(end="  ")

        print(format(bsno_liste[oyuncu][4], "6.2f"), end="    ")
        print(format(bsno_liste[oyuncu][6], "6.2f"), end="    ")
        print(format(bsno_liste[oyuncu][7], "6.2f"), end="    ")
        print(format(bsno_liste[oyuncu][8], "6.2f"), end="    ")
        print(format(bsno_liste[oyuncu][9], "4d"))


def esitlik_bozucu_sozluk_olustur(oyuncu_sayisi):  # eşitlik bozucu puuanların tutulması için sözlük oluşturulur
    esitlik_bozucu_sozluk = {}
    for oyuncu in range(1, oyuncu_sayisi + 1):
        esitlik_bozucu_sozluk.setdefault(oyuncu, [0, 0, 0, 0])
    return esitlik_bozucu_sozluk


def esitlik_bozucu_sozluge_galibiyet_sayisi_ekle(esitlik_bozucu_sozluk, puan1, puan2, oyuncu, rakip):
    if puan1 == TAM_PAUN or puan1 == "+":
        esitlik_bozucu_sozluk[oyuncu][3] += 1  # galibiyet sayısı
    if puan2 == TAM_PAUN or puan2 == "+":
        esitlik_bozucu_sozluk[rakip][3] += 1  # galibiyet sayısı


def ilk_renk_atama(renk_sozlugu, tek, oyuncu_sayisi):  # ik oyuncunun rengi alınır ve diğer oyuncuların renkleri ona göre belirlenir
    renk = input("Baslangic siralamasina gore ilk oyuncunun ilk turdaki rengini giriniz (b/s):")
    while renk not in ["b", "s"]:
        renk = input("Baslangic siralamasina gore ilk oyuncunun ilk turdaki rengini giriniz (b/s):")

    birincinin_bilgisi = renk_sozlugu.get(1)
    birincinin_bilgisi[0] = renk

    if tek:
        sayi = oyuncu_sayisi
        secim = renk_sozlugu.get(oyuncu_sayisi)
        secim[0] = "-"
    else:
        sayi = oyuncu_sayisi+1

    for sira in range(2, sayi):  # numarası tek olan oyunculara ilk oyuncun rengi çift olanlara karşıt rengi verilir
        secim = renk_sozlugu.get(sira)
        if sira % 2 != 0:
            if renk == "b":
                secim[0] = "b"
            else:
                secim[0] = "s"
        else:
            if renk == "b":
                secim[0] = "s"
            else:
                secim[0] = "b"

    return renk_sozlugu


def renk_sozlugu_olustur(tur_sayisi, oyuncu_sayisi):  # her oyuncu için tur sayısı kadar renk tutabilecek sözlük oluşturulur
    renk_sozlugu = {}
    for oyuncu in range(1, oyuncu_sayisi + 1):
        kisi = []
        for tur in range(tur_sayisi):
            kisi.append("-")
        renk_sozlugu.setdefault(oyuncu, kisi)
    return renk_sozlugu


def lisans_no_kontrol(lisans_no, oyuncu_bilgileri):  # girilen lisans numarası daha önce alınmış mı diye kontrol edilir
    bulundu = True

    while bulundu:
        bulundu = False
        for bilgi in range(len(oyuncu_bilgileri)):
            if lisans_no in oyuncu_bilgileri[bilgi]:
                hatali = True
                while hatali:
                    try:
                        lisans_no = int(input(
                            "Lisans Numarası (0'dan büyük tam sayı olmalıdır. Başka oyunca yoksa 0 ya da negatif bir sayı giriniz):"))  # lisans numarası
                        hatali = False
                    except ValueError:
                        print("Geçersiz sayı")
                        hatali = True
                        continue

                bulundu = True

    return lisans_no


main()
