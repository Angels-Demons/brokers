from enum import Enum


class ChargeType(Enum):
    MOSTAGHIM = 1001
    DELKHAH = 1002
    FOGHOLAADE = 1003
    JAVANAN = 1004
    BANOVAN = 1005

    @staticmethod
    def farsi(value):
        if value == 1001:
            return "مستقیم"
        elif value == 1002:
            return "دلخواه"
        elif value == 1003:
            return "فوق العاده"
        elif value == 1004:
            return "جوانان"
        elif value == 1005:
            return "بانوان"


class Operator(Enum):
    MCI = 1
    MTN = 2
    RIGHTEL = 3
    TALIYA = 4

    @staticmethod
    def farsi(value):
        if value == 1:
            return "همراه اول"
        elif value == 2:
            return "ایرانسل"
        elif value == 3:
            return "رایتل"
        elif value == 4:
            return "تالیا"


class ResponseTypes(Enum):
    SUCCESS = 0
    REFERTODESC = -1
    INVALIBROKER = -1001
    DEAVTIVEBROKER = -1002
    INVALIDAMOUNT = -1003
    EMPTYCHARGE = -1004
    DAILYLIMIREACHED = -1005
    MONTHLYLIMITREACHED = -1006
    TOTALLIMITREACHED = -1007
    INVALINUMBER = -1008
    EMPTYBANKTRANSACTION = -1009
    REPEATEDTRANSACTIONID = -1010
    INSTATUSERROR = -1011
    BLACLIST = -1012
    DEACTIVESUBSCRIBER = -1013
    SUBSCHARGELIMIT = -1014
    CHARGEISINACCESABLE = -1015
    BUSYCHARGINGGW = -1016
    UNGOINGTRANSACTIONID = -1017
    BROKERCHARGETYPEDENIEDACCESS = -1018
    NOTENOUGHBROKERBALANCE = -1019
    WRONGCHARGETYPE = -1021
    NORESULTFORBROKERREPORT = -1022
    INVALIDJAVANCHARGE = -1023
    REPEATEDBROKERNAME = -1024
    REPEATEDFACTORNUMBER = -1025
    BANOVANCHARGEISINACCESSABLE = -1027
    LOYALCHARGEISINACCESSABLE = -1028
    INVALIDCHARGE = -1029
    PACKAGEISINACCESSABLE = -1030
    NOPACKAGEFOUND = -1031
    PACKAGEINACCESSABLE = -1032
    INVALIDPACKAGETYPE = -1033
    INVALIPACKAGEAMOUNT = -1034
    POSTPAIDCHARGEINACCESSABLE = -1035
    PACKAGEERROR = -1036
    BANOVANINVALIDAMOUNT = -1037
    CHANGERESERVEPACKAGEERROR = -1038
    ACTIVEPAKAGEERROR = -1039
    ACTIVERESRVEERROR = -1040
    REPORTDENIEDACCESS = -1041
    DEACTIVEERROR = -1042
    LOSTERROR = -1043
    CHARGEERROR = -1044
    ERRORCHARGE = -1045
    PACKAGEACTIVATIONERROR = -1046
    ERRORDEACTIVATESUBSCRIBER = -1047
    EVACUATEDERROR = -1048
    POSTPAIDPACKAGE = -1049
    PREPAIDPACKAGE = -1050
    WRONGBANKCODE = -1051
    NEWSUBSCRIBERERROR = -1052
    TALIYAERROR = -1053
    INVALIDPERCENT = -1054
    REPEATEDUSER = -1055
    INVALIDUSERPERCENT = -1056
    ACCESSDENIED = -1057
    SUBUSERLIMITED = -1058
    STUDENTERROR = -1060
    SYSTEMERROR = -25228
    INVALIDINPUT = 19
    Error1 = 1264
    NOTMCI = 405610009

    @staticmethod
    def farsi(value):
        if value == 0:
            return "عملیات با موفقيت انجام گرديد."
        elif value == -1:
            return "به شرح خطاي اعلامي (درايه دوم آرايه برگشتي) رجوع گردد."
        elif value == -1001:
            return "کارگزار تعريف نشده است."
        elif value == -1002:
            return "کارگزار فعال نميباشد."
        elif value == -1003:
            return "مبلغ کارت شارژ ارسالي صحيح نميباشد."
        elif value == -1004:
            return "کارت شارژ تمام شده است."
        elif value == -1005:
            return "سهميه روزانه کارگزار تمام شده است."
        elif value == -1006:
            return "سهميه ماهانه کارگزار تمام شده است."
        elif value == -1007:
            return "سهميه کلي کارگزار تمام شده است."
        elif value == -1008:
            return "شماره تلفن مورد نظر وجود ندارد."
        elif value == -1009:
            return "شماره تراکنش بانکي خالي ميباشد."
        elif value == -1010:
            return "شماره تراکنش تکراري ميباشد."
        elif value == -1011:
            return "خطا از طرف سرور  INدر بازيابي وضعيت مشترک."
        elif value == -1012:
            return "تلفن در ليست سياه ميباشد."
        elif value == -1013:
            return "وضعيت مشترک فعال نميباشد."
        elif value == -1014:
            return "شارژ کنوني مشترک بيش از سقف تعيين شده است."
        elif value == -1015:
            return "در حال حاضر عمليات شارژ مقدور نميباشد."
        elif value == -1016:
            return "تمام درگاههاي شارژ مشغول است."
        elif value == -1017:
            return "با اين شماره تراکنش عمليات شارژ در حال اجرا است."
        elif value == -1018:
            return "کارگزار مجوز شروع اين نوع شارژ را ندارد."
        elif value == -1019:
            return "اعتبار کارگزار تمام شده است."
        elif value == -1021:
            return "نوع شارژ صحيح نيست."
        elif value == -1022:
            return "گزارش براي کارگزار در اين بازه زماني وجود ندارد."
        elif value == -1023:
            return "شارژ جوانان مختص مشترکين زير  25سال ميباشد."
        elif value == -1024:
            return "نام کارگزار تکراري است."
        elif value == -1025:
            return "شماره فاکتور تکراري است."
        elif value == -1027:
            return "مشترک مشمول طرح هديه شارژ بانوان نمي باشد."
        elif value == -1028:
            return "مشترک مشمول شارژ وفاداري نميباشد."
        elif value == -1029:
            return "شارژ با مشخصات ارسالي يافت نشد."
        elif value == -1030:
            return "کارگزار مجوز فروش اين نوع بسته را ندارد."
        elif value == -1031:
            return "بسته با مشخصات ارسالي يافت نشد."
        elif value == -1032:
            return "کارگزار مجوز فروش اين نوع بسته را ندارد."
        elif value == -1033:
            return "نوع بسته صحيح نميباشد."
        elif value == -1034:
            return "مبلغ بسته صحيح نميباشد."
        elif value == -1035:
            return "اعمال شارژ براي مشترکين دائمي امکانپذير نميباشد."
        elif value == -1036:
            return "خطا در فعالسازي بسته: متن خطا"
        elif value == -1037:
            return "امکان شارژ بانو با اين مبلغ وجود ندارد."
        elif value == -1038:
            return "امکان تغيير بسته رزرو وجود ندارد."
        elif value == -1039:
            return "به علت فعال بودن بسته اينترنت، امکان خريد بسته از اين درگاه براي شما فراهم نميباشد."
        elif value == -1040:
            return "امکان رزرو بسته درخواستي وجود ندارد، بسته رزرو ديگري براي شما فعال است."
        elif value == -1041:
            return "مجاز به ديدن اين گزارش نميباشيد."
        elif value == -1042:
            return "امکان ادامه فرآيند به دليل قطع خاص وجود ندارد."
        elif value == -1043:
            return "امکان ادامه فرآيند به دليل وضعيت مفقودي وجود ندارد."
        elif value == -1044:
            return "امکان شارژ اين مشترک وجود ندارد."
        elif value == -1045:
            return "امکان شارژ مشترک وجود ندارد."
        elif value == -1046:
            return "امکان فعالسازي بسته وجود ندارد."
        elif value == -1047:
            return "امکان ادامه فرآيند به دليل فعال نبودن وضعيت مشترک وجود ندارد."
        elif value == -1048:
            return "امکان ادامه فرآيند به دليل تخليه بودن وضعيت مشترک وجود ندارد."
        elif value == -1049:
            return "اين بسته مختص مشترکين دائمي است."
        elif value == -1050:
            return "اين بسته مختص مشترکين اعتباري است."
        elif value == -1051:
            return "کد بانک اشتباه است."
        elif value == -1052:
            return "اين بسته مختص مشترکين جديد ميباشد."
        elif value == -1053:
            return "امکان شارژ مشترکين تاليا از اين درگاه وجود ندارد."
        elif value == -1054:
            return "درصد وارد شده نامعتبر ميباشد."
        elif value == -1055:
            return "نام کاربر يا کارگزار تکراري است."
        elif value == -1056:
            return "کارگزار قابليت تعريف درصد ندارد."
        elif value == -1057:
            return "کاربر تعريف نشده است."
        elif value == -1058:
            return "کاربر از مجوز لازم برخوردار نيست."
        elif value == -1059:
            return "مجموع درصد کاربران زير مجموع کارگزار از صد بيشتر خواهد شد."
        elif value == -1060:
            return "دانش آموز گرامي، شما مجاز به دريافت بسته نوترينو نميباشيد. جهت اطلاع از بسته هاي انارستان کد *100*622# را شماره گیری نمایید."
        elif value == -25228:
            return "خطاي سيستمي، لطفا مجددا تلاش نماييد."
        elif value == 19:
            return "پارامتر ورودي اشتباه است."
        elif value == 1264:
            return "error"
        elif value == 405610009:
            return "شماره ارسالی در شبکه همراه اول وجود ندارد."



class CardTypes(Enum):
    NATIONALCODE = 0
    PASSPORT = 1
    AMAYESH = 2
    PANAHANDEGHI = 3
    HOVIAT = 4
    IRANICOMPANY = 5
    NONIRANICOMPANY = 6
    SHABA = 7
    BANKCARD = 8
    TELEPHONENUMBER = 9

    @staticmethod
    def farsi(value):
        if value == 0:
            return "کد ملي افراد ايراني"
        elif value == 1:
            return "شماره گذرنامه اتباع"
        elif value == 2:
            return "شماره کارت آمايش"
        elif value == 3:
            return "شماره کارت پناهندگي"
        elif value == 4:
            return "شماره کارت هويت"
        elif value == 5:
            return "شناسه ملي شرکتهاي حقوقي ايراني"
        elif value == 6:
            return "شناسه ملي شرکت حقوقي خارجي"
        elif value == 7:
            return "شماره شباي حساب بانکي"
        elif value == 8:
            return "شماره کارت بانکي"
        elif value == 9:
            return "شماره تلفن"


class BankCodes(Enum):
    MARKAZI = 0
    MELLI = 1
    SEPAH = 2
    TEJARAT = 3
    MELLAT = 4
    SADERAT = 5
    MASKAN = 6
    KESHAVARZI = 7
    REFAH = 8
    TOSEE = 9
    EGHTESAD = 10
    SANAT = 11
    UNKNOWN = 12
    OSTAN = 13
    KARAFARIN = 14
    POSTBANK = 15
    PARSIAN = 16
    SAMAN = 17
    EGHTESADNOVIN = 19
    PASARGHAD = 20
    SARMAYE = 21
    SINA = 22
    JIRING = 23
    ANSAR = 24
    AYANDE = 25
    SHAHR = 26
    HEKMAT = 27
    DEY = 28
    KHAVARMIANE = 29

    @staticmethod
    def farsi(value):
        if value == 0:
            return "بانک مرکزي جمهوري اسلامي ايران"
        elif value == 1:
            return "بانک ملي ايران"
        elif value == 2:
            return "بانک سپه"
        elif value == 3:
            return "بانک تجارت"
        elif value == 4:
            return "بانک ملت"
        elif value == 5:
            return "بانک صادرات ايران"
        elif value == 6:
            return "بانک مسکن"
        elif value == 7:
            return "بانک کشاورزي"
        elif value == 8:
            return "بانک رفاه کارگران"
        elif value == 9:
            return "بانک توسعه صادرات ايران"
        elif value == 10:
            return "بانک اقتصاد"
        elif value == 11:
            return "بانک صنعت و معدن"
        elif value == 12:
            return "نامشخص"
        elif value == 13:
            return "بانک استان"
        elif value == 14:
            return "بانک کارآفرين"
        elif value == 15:
            return "پست بانک"
        elif value == 16:
            return "بانک پارسيان"
        elif value == 17:
            return "بانک سامان"
        elif value == 19:
            return "بانک اقتصاد نوين"
        elif value == 20:
            return "بانک پاسارگاد"
        elif value == 21:
            return "بانک سرمايه"
        elif value == 22:
            return "بانک سينا"
        elif value == 23:
            return "جيرينگ"
        elif value == 24:
            return "بانک انصار"
        elif value == 25:
            return "بانک آينده"
        elif value == 26:
            return "بانک شهر"
        elif value == 27:
            return "بانک حکمت ايرانيان"
        elif value == 28:
            return "بانک دي"
        elif value == 29:
            return "بانک خاورميانه"


class RecordState(Enum):
    INITIAL = 1
    INITIAL_ERROR = 7
    CALLED = 2
    CALL_ERROR = 3
    EXE_REQ = 4
    EXECUTED = 5
    EXECUTE_ERROR = 6

    # @staticmethod
    # def farsi(value):
    #     if value == 1:
    #         return "مستقیم"
    #     elif value == 2:
    #         return "دلخواه"


class CreditType(Enum):
    GENERAL = 1
    TOP_UP = 2
    PACKAGE = 3

    @staticmethod
    def farsi(value):
        if value == CreditType.GENERAL.value:
            return "عمومی"
        elif value == CreditType.TOP_UP.value:
            return "شارژ"
        elif value == CreditType.PACKAGE.value:
            return "بسته"


class Choices:
    credit_types = (
        (CreditType.GENERAL.value, CreditType.farsi(CreditType.GENERAL.value)),
        (CreditType.TOP_UP.value, CreditType.farsi(CreditType.TOP_UP.value)),
        (CreditType.PACKAGE.value, CreditType.farsi(CreditType.PACKAGE.value)),
    )

    charge_type_choices = (
        (ChargeType.MOSTAGHIM.value, ChargeType.farsi(ChargeType.MOSTAGHIM.value)),
        (ChargeType.DELKHAH.value, ChargeType.farsi(ChargeType.DELKHAH.value)),
        (ChargeType.FOGHOLAADE.value, ChargeType.farsi(ChargeType.FOGHOLAADE.value)),
        (ChargeType.JAVANAN.value, ChargeType.farsi(ChargeType.JAVANAN.value)),
        (ChargeType.BANOVAN.value, ChargeType.farsi(ChargeType.BANOVAN.value)),
    )

    record_states = (
        (RecordState.INITIAL.value, RecordState.INITIAL.name),
        (RecordState.INITIAL_ERROR.value, RecordState.INITIAL_ERROR.name),
        (RecordState.CALLED.value, RecordState.CALLED.name),
        (RecordState.CALL_ERROR.value, RecordState.CALL_ERROR.name),
        (RecordState.EXE_REQ.value, RecordState.EXE_REQ.name),
        (RecordState.EXECUTED.value, RecordState.EXECUTED.name),
        (RecordState.EXECUTE_ERROR.value, RecordState.EXECUTE_ERROR.name),
    )

    operators = (
        (Operator.MCI.value, Operator.farsi(Operator.MCI.value)),
        (Operator.MTN.value, Operator.farsi(Operator.MTN.value)),
        (Operator.RIGHTEL.value, Operator.farsi(Operator.RIGHTEL.value)),
        (Operator.TALIYA.value, Operator.farsi(Operator.TALIYA.value)),
    )

    bank_codes = (
        (BankCodes.MARKAZI.value, BankCodes.farsi(BankCodes.MARKAZI.value)),
        (BankCodes.MELLI.value, BankCodes.farsi(BankCodes.MELLI.value)),
        (BankCodes.SEPAH.value, BankCodes.farsi(BankCodes.SEPAH.value)),
        (BankCodes.TEJARAT.value, BankCodes.farsi(BankCodes.TEJARAT.value)),
        (BankCodes.MELLAT.value, BankCodes.farsi(BankCodes.MELLAT.value)),
        (BankCodes.SADERAT.value, BankCodes.farsi(BankCodes.SADERAT.value)),
        (BankCodes.MASKAN.value, BankCodes.farsi(BankCodes.MASKAN.value)),
        (BankCodes.KESHAVARZI.value, BankCodes.farsi(BankCodes.KESHAVARZI.value)),
        (BankCodes.REFAH.value, BankCodes.farsi(BankCodes.REFAH.value)),
        (BankCodes.TOSEE.value, BankCodes.farsi(BankCodes.TOSEE.value)),
        (BankCodes.EGHTESAD.value, BankCodes.farsi(BankCodes.EGHTESAD.value)),
        (BankCodes.SANAT.value, BankCodes.farsi(BankCodes.SANAT.value)),
        (BankCodes.KHAVARMIANE.value, BankCodes.farsi(BankCodes.KHAVARMIANE.value)),
        (BankCodes.DEY.value, BankCodes.farsi(BankCodes.DEY.value)),
        (BankCodes.HEKMAT.value, BankCodes.farsi(BankCodes.HEKMAT.value)),
        (BankCodes.SHAHR.value, BankCodes.farsi(BankCodes.SHAHR.value)),
        (BankCodes.AYANDE.value, BankCodes.farsi(BankCodes.AYANDE.value)),
        (BankCodes.ANSAR.value, BankCodes.farsi(BankCodes.ANSAR.value)),
        (BankCodes.JIRING.value, BankCodes.farsi(BankCodes.JIRING.value)),
        (BankCodes.SINA.value, BankCodes.farsi(BankCodes.SINA.value)),
        (BankCodes.SARMAYE.value, BankCodes.farsi(BankCodes.SARMAYE.value)),
        (BankCodes.PASARGHAD.value, BankCodes.farsi(BankCodes.PASARGHAD.value)),
        (BankCodes.EGHTESADNOVIN.value, BankCodes.farsi(BankCodes.EGHTESADNOVIN.value)),
        (BankCodes.SAMAN.value, BankCodes.farsi(BankCodes.SAMAN.value)),
        (BankCodes.PARSIAN.value, BankCodes.farsi(BankCodes.PARSIAN.value)),
        (BankCodes.POSTBANK.value, BankCodes.farsi(BankCodes.POSTBANK.value)),
        (BankCodes.KARAFARIN.value, BankCodes.farsi(BankCodes.KARAFARIN.value)),
        (BankCodes.OSTAN.value, BankCodes.farsi(BankCodes.OSTAN.value)),
        (BankCodes.UNKNOWN.value, BankCodes.farsi(BankCodes.UNKNOWN.value))

    )

    card_types = (
        (CardTypes.NATIONALCODE.value, BankCodes.farsi(CardTypes.NATIONALCODE.value)),
        (CardTypes.PASSPORT.value, BankCodes.farsi(CardTypes.PASSPORT.value)),
        (CardTypes.AMAYESH.value, BankCodes.farsi(CardTypes.AMAYESH.value)),
        (CardTypes.PANAHANDEGHI.value, BankCodes.farsi(CardTypes.PANAHANDEGHI.value)),
        (CardTypes.HOVIAT.value, BankCodes.farsi(CardTypes.HOVIAT.value)),
        (CardTypes.IRANICOMPANY.value, BankCodes.farsi(CardTypes.IRANICOMPANY.value)),
        (CardTypes.NONIRANICOMPANY.value, BankCodes.farsi(CardTypes.NONIRANICOMPANY.value)),
        (CardTypes.SHABA.value, BankCodes.farsi(CardTypes.SHABA.value)),
        (CardTypes.BANKCARD.value, BankCodes.farsi(CardTypes.BANKCARD.value)),
        (CardTypes.TELEPHONENUMBER.value, BankCodes.farsi(CardTypes.TELEPHONENUMBER.value))
    )

    response_types_choices = (
        (ResponseTypes.SUCCESS.value, ResponseTypes.farsi(ResponseTypes.SUCCESS.value)),
        (ResponseTypes.REFERTODESC.value, ResponseTypes.farsi(ResponseTypes.REFERTODESC.value)),
        (ResponseTypes.INVALIBROKER.value, ResponseTypes.farsi(ResponseTypes.INVALIBROKER.value)),
        (ResponseTypes.DEAVTIVEBROKER.value, ResponseTypes.farsi(ResponseTypes.DEAVTIVEBROKER.value)),
        (ResponseTypes.INVALIDAMOUNT.value, ResponseTypes.farsi(ResponseTypes.INVALIDAMOUNT.value)),
        (ResponseTypes.EMPTYCHARGE.value, ResponseTypes.farsi(ResponseTypes.EMPTYCHARGE.value)),
        (ResponseTypes.DAILYLIMIREACHED.value, ResponseTypes.farsi(ResponseTypes.DAILYLIMIREACHED.value)),
        (ResponseTypes.MONTHLYLIMITREACHED.value, ResponseTypes.farsi(ResponseTypes.MONTHLYLIMITREACHED.value)),
        (ResponseTypes.TOTALLIMITREACHED.value, ResponseTypes.farsi(ResponseTypes.TOTALLIMITREACHED.value)),
        (ResponseTypes.INVALINUMBER.value, ResponseTypes.farsi(ResponseTypes.INVALINUMBER.value)),
        (ResponseTypes.EMPTYBANKTRANSACTION.value, ResponseTypes.farsi(ResponseTypes.EMPTYBANKTRANSACTION.value)),
        (ResponseTypes.REPEATEDTRANSACTIONID.value, ResponseTypes.farsi(ResponseTypes.REPEATEDTRANSACTIONID.value)),
        (ResponseTypes.INSTATUSERROR.value, ResponseTypes.farsi(ResponseTypes.INSTATUSERROR.value)),
        (ResponseTypes.BLACLIST.value, ResponseTypes.farsi(ResponseTypes.BLACLIST.value)),
        (ResponseTypes.DEACTIVESUBSCRIBER.value, ResponseTypes.farsi(ResponseTypes.DEACTIVESUBSCRIBER.value)),
        (ResponseTypes.SUBSCHARGELIMIT.value, ResponseTypes.farsi(ResponseTypes.SUBSCHARGELIMIT.value)),
        (ResponseTypes.CHARGEISINACCESABLE.value, ResponseTypes.farsi(ResponseTypes.CHARGEISINACCESABLE.value)),
        (ResponseTypes.BUSYCHARGINGGW.value, ResponseTypes.farsi(ResponseTypes.BUSYCHARGINGGW.value)),
        (ResponseTypes.INVALIDINPUT.value, ResponseTypes.farsi(ResponseTypes.INVALIDINPUT.value)),
        (ResponseTypes.SYSTEMERROR.value, ResponseTypes.farsi(ResponseTypes.SYSTEMERROR.value)),
        (ResponseTypes.STUDENTERROR.value, ResponseTypes.farsi(ResponseTypes.STUDENTERROR.value)),
        (ResponseTypes.SUBUSERLIMITED.value, ResponseTypes.farsi(ResponseTypes.SUBUSERLIMITED.value)),
        (ResponseTypes.ACCESSDENIED.value, ResponseTypes.farsi(ResponseTypes.ACCESSDENIED.value)),
        (ResponseTypes.INVALIDUSERPERCENT.value, ResponseTypes.farsi(ResponseTypes.INVALIDUSERPERCENT.value)),
        (ResponseTypes.REPEATEDUSER.value, ResponseTypes.farsi(ResponseTypes.REPEATEDUSER.value)),
        (ResponseTypes.UNGOINGTRANSACTIONID.value, ResponseTypes.farsi(ResponseTypes.UNGOINGTRANSACTIONID.value)),
        (ResponseTypes.BROKERCHARGETYPEDENIEDACCESS.value,
         ResponseTypes.farsi(ResponseTypes.BROKERCHARGETYPEDENIEDACCESS.value)),
        (ResponseTypes.NOTENOUGHBROKERBALANCE.value, ResponseTypes.farsi(ResponseTypes.NOTENOUGHBROKERBALANCE.value)),
        (ResponseTypes.WRONGCHARGETYPE.value, ResponseTypes.farsi(ResponseTypes.WRONGCHARGETYPE.value)),
        (ResponseTypes.NORESULTFORBROKERREPORT.value, ResponseTypes.farsi(ResponseTypes.NORESULTFORBROKERREPORT.value)),
        (ResponseTypes.INVALIDJAVANCHARGE.value, ResponseTypes.farsi(ResponseTypes.INVALIDJAVANCHARGE.value)),
        (ResponseTypes.REPEATEDBROKERNAME.value, ResponseTypes.farsi(ResponseTypes.REPEATEDBROKERNAME.value)),
        (ResponseTypes.REPEATEDFACTORNUMBER.value, ResponseTypes.farsi(ResponseTypes.REPEATEDFACTORNUMBER.value)),
        (ResponseTypes.BANOVANCHARGEISINACCESSABLE.value,
         ResponseTypes.farsi(ResponseTypes.BANOVANCHARGEISINACCESSABLE.value)),
        (ResponseTypes.LOYALCHARGEISINACCESSABLE.value,
         ResponseTypes.farsi(ResponseTypes.LOYALCHARGEISINACCESSABLE.value)),
        (ResponseTypes.INVALIDCHARGE.value, ResponseTypes.farsi(ResponseTypes.INVALIDCHARGE.value)),
        (ResponseTypes.PACKAGEISINACCESSABLE.value, ResponseTypes.farsi(ResponseTypes.PACKAGEISINACCESSABLE.value)),
        (ResponseTypes.NOPACKAGEFOUND.value, ResponseTypes.farsi(ResponseTypes.NOPACKAGEFOUND.value)),
        (ResponseTypes.PACKAGEINACCESSABLE.value, ResponseTypes.farsi(ResponseTypes.PACKAGEINACCESSABLE.value)),
        (ResponseTypes.INVALIDPERCENT.value, ResponseTypes.farsi(ResponseTypes.INVALIDPERCENT.value)),
        (ResponseTypes.TALIYAERROR.value, ResponseTypes.farsi(ResponseTypes.TALIYAERROR.value)),
        (ResponseTypes.NEWSUBSCRIBERERROR.value, ResponseTypes.farsi(ResponseTypes.NEWSUBSCRIBERERROR.value)),
        (ResponseTypes.WRONGBANKCODE.value, ResponseTypes.farsi(ResponseTypes.WRONGBANKCODE.value)),
        (ResponseTypes.PREPAIDPACKAGE.value, ResponseTypes.farsi(ResponseTypes.PREPAIDPACKAGE.value)),
        (ResponseTypes.POSTPAIDPACKAGE.value, ResponseTypes.farsi(ResponseTypes.POSTPAIDPACKAGE.value)),
        (ResponseTypes.EVACUATEDERROR.value, ResponseTypes.farsi(ResponseTypes.EVACUATEDERROR.value)),
        (ResponseTypes.ERRORDEACTIVATESUBSCRIBER.value,
         ResponseTypes.farsi(ResponseTypes.ERRORDEACTIVATESUBSCRIBER.value)),
        (ResponseTypes.PACKAGEACTIVATIONERROR.value, ResponseTypes.farsi(ResponseTypes.PACKAGEACTIVATIONERROR.value)),
        (ResponseTypes.ERRORCHARGE.value, ResponseTypes.farsi(ResponseTypes.ERRORCHARGE.value)),
        (ResponseTypes.CHARGEERROR.value, ResponseTypes.farsi(ResponseTypes.CHARGEERROR.value)),
        (ResponseTypes.LOSTERROR.value, ResponseTypes.farsi(ResponseTypes.LOSTERROR.value)),
        (ResponseTypes.DEACTIVEERROR.value, ResponseTypes.farsi(ResponseTypes.DEACTIVEERROR.value)),
        (ResponseTypes.REPORTDENIEDACCESS.value, ResponseTypes.farsi(ResponseTypes.REPORTDENIEDACCESS.value)),
        (ResponseTypes.ACTIVERESRVEERROR.value, ResponseTypes.farsi(ResponseTypes.ACTIVERESRVEERROR.value)),
        (ResponseTypes.ACTIVEPAKAGEERROR.value, ResponseTypes.farsi(ResponseTypes.ACTIVEPAKAGEERROR.value)),
        (ResponseTypes.CHANGERESERVEPACKAGEERROR.value,
         ResponseTypes.farsi(ResponseTypes.CHANGERESERVEPACKAGEERROR.value)),
        (ResponseTypes.BANOVANINVALIDAMOUNT.value, ResponseTypes.farsi(ResponseTypes.BANOVANINVALIDAMOUNT.value)),
        (ResponseTypes.PACKAGEERROR.value, ResponseTypes.farsi(ResponseTypes.PACKAGEERROR.value)),
        (ResponseTypes.POSTPAIDCHARGEINACCESSABLE.value,
         ResponseTypes.farsi(ResponseTypes.POSTPAIDCHARGEINACCESSABLE.value)),
        (ResponseTypes.INVALIPACKAGEAMOUNT.value, ResponseTypes.farsi(ResponseTypes.INVALIPACKAGEAMOUNT.value)),
        (ResponseTypes.INVALIDPACKAGETYPE.value, ResponseTypes.farsi(ResponseTypes.INVALIDPACKAGETYPE.value)),
        (ResponseTypes.Error1.value, ResponseTypes.farsi(ResponseTypes.Error1.value)),
        (ResponseTypes.NOTMCI.value,ResponseTypes.farsi(ResponseTypes.NOTMCI.value))

    )


class ResponceCodeTypes:
    successful = 0
    invalid_parameter = -10
    provider_error = -11
    insufficient_balance = -12
    inactive_broker = -13
    invalid_access = -14
    invalid_package_access = -15
    invalid_charge_access = -16
