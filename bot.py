import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = os.environ["GROUP_CHAT_ID"]
HISTORY_CHAT_ID = os.environ["HISTORY_CHAT_ID"]
HISTORY_THREAD_ID = int(os.environ.get("HISTORY_THREAD_ID", 0))
ORDER_THREAD_ID = int(os.environ.get("ORDER_THREAD_ID", 0))

(REGISTER_LAST_NAME, REGISTER_FIRST_NAME, WAITING_STICKER_PHOTO, CHOOSE_CATEGORY,
 CHOOSE_IPHONE_MODEL, CHOOSE_IPHONE_PARTS, FREE_TEXT_PARTS, CONFIRM_ORDER,
 OTHER_PART_TEXT, CUSTOM_MODEL_TEXT) = range(10)

(HISTORY_PHOTO, HISTORY_TEXT) = range(10, 12)
(UNBIND_PHOTO, UNBIND_PART_REMOVE, UNBIND_PART_ADD) = range(12, 15)

IPHONE_MODELS_ROWS = [
    [("iphone_xr", "iPhone XR"), ("iphone_x", "iPhone X"), ("iphone_xs", "iPhone XS")],
    [("iphone_xs_max", "iPhone XS Max")],
    [("iphone_11", "iPhone 11"), ("iphone_11_pro", "iPhone 11 Pro"), ("iphone_11_pro_max", "iPhone 11 Pro Max")],
    [("iphone_12_mini", "iPhone 12 Mini"), ("iphone_12", "iPhone 12"), ("iphone_12_pro", "iPhone 12 Pro")],
    [("iphone_12_pro_max", "iPhone 12 Pro Max")],
    [("iphone_13_mini", "iPhone 13 Mini"), ("iphone_13", "iPhone 13"), ("iphone_13_pro", "iPhone 13 Pro")],
    [("iphone_13_pro_max", "iPhone 13 Pro Max")],
    [("iphone_14", "iPhone 14"), ("iphone_14_plus", "iPhone 14 Plus"), ("iphone_14_pro", "iPhone 14 Pro")],
    [("iphone_14_pro_max", "iPhone 14 Pro Max")],
    [("iphone_15", "iPhone 15"), ("iphone_15_plus", "iPhone 15 Plus"), ("iphone_15_pro", "iPhone 15 Pro")],
    [("iphone_15_pro_max", "iPhone 15 Pro Max")],
    [("iphone_16", "iPhone 16"), ("iphone_16_plus", "iPhone 16 Plus"), ("iphone_16_pro", "iPhone 16 Pro")],
    [("iphone_16_pro_max", "iPhone 16 Pro Max")],
    [("iphone_17", "iPhone 17"), ("iphone_17_air", "iPhone 17 Air"), ("iphone_17_pro", "iPhone 17 Pro")],
    [("iphone_17_pro_max", "iPhone 17 Pro Max")],
    [("iphone_custom", "❓ Моєї моделі тут немає")],
]

IPHONE_MODELS_DICT = {key: name for row in IPHONE_MODELS_ROWS for key, name in row}

IPHONE_PARTS = {
    "iphone_x": [
        ("Вібро", "77345"), ("Слуховий динамік", "80383"), ("Шлейф слухового динаміка", "819336"),
        ("Екран iPhone X ref/orig", "65101"), ("Шлейф JCID слухового динаміка з датчиками", "826812"),
        ("Корпус iPhone X", "43347"), ("Скло камери", "78091"), ("Фронтальна камера", "77344"),
        ("Шлейф антени Wi-Fi", "815588"), ("Шлейф кнопок звуку", "784688"), ("Шлейф кнопки Power", "64352"),
        ("Шлейф антени NFC/Bluetooth", "790181"), ("Шлейф Face iD без пайки", "807262"),
        ("Шлейф антени GSM", "791339"), ("Безпровідна зарядка", "817646"), ("Шлейф зарядки", "72831"),
        ("Основна камера", "77343"), ("Поліфонічний динамік", "77346"), ("Акумулятор (Battery)", "77342"),
    ],
    "iphone_xr": [
        ("Вібро", "83735"), ("Слуховий динамік", "83737"), ("Шлейф слухового динаміка", "819234"),
        ("Роз'єм для sim карти", "795371"), ("Екран iPhone XR ref/orig", "779764"),
        ("Шлейф JCID слухового динаміка з датчиками", "815283"), ("Корпус iPhone XR", "83705"),
        ("Скло камери", "779837"), ("Фронтальна камера", "83732"), ("Шлейф антени Wi-Fi", "817629"),
        ("Шлейф кнопок звуку", "811745"), ("Шлейф кнопки Power", "83708"),
        ("Шлейф антени NFC/Bluetooth", "790855"), ("Шлейф антени GSM", "817628"),
        ("Шлейф Face iD для пайки", "786736"), ("Безпровідна зарядка", "817645"),
        ("Шлейф зарядки", "83706"), ("Основна камера", "83731"), ("Поліфонічний динамік", "83740"),
        ("Акумулятор з шлейфом", "83736"), ("Акумулятор банка", "820513"),
    ],
    "iphone_xs": [
        ("Вібро", "78678"), ("Слуховий динамік", "784871"), ("Шлейф слухового динаміка", "819233"),
        ("Екран iPhone XS ref/orig", "86094"), ("Шлейф JCID слухового динаміка з датчиками", "826825"),
        ("Корпус iPhone XS", "78676"), ("Скло камери", "12938"), ("Фронтальна камера", "83478"),
        ("Шлейф антени Wi-Fi", "815589"), ("Шлейф кнопок звуку", "789743"),
        ("Шлейф кнопки Power", "817618"), ("Шлейф антени NFC/Bluetooth", "797393"),
        ("Шлейф антені GSM", "789805"), ("Безпровідна зарядка", "817644"),
        ("Шлейф зарядки", "83481"), ("Основна камера", "27024"), ("Поліфонічний динамік", "83483"),
        ("Акумулятор з шлейфом", "78677"), ("Акумулятор банка", "820514"),
    ],
    "iphone_xs_max": [
        ("Вібро", "84263"), ("Слуховий динамік", "786396"), ("Шлейф слухового динаміка", "819186"),
        ("Екран iPhone XS Max ref/orig", "778929"), ("Шлейф JCID слухового динаміка з датчиками", "826882"),
        ("Корпус iPhone XS Max", "84261"), ("Скло камери", "42955"), ("Фронтальна камера", "84264"),
        ("Шлейф антени Wi-Fi", "817623"), ("Шлейф кнопок звуку", "788173"),
        ("Шлейф кнопки Power", "84267"), ("Шлейф антені NFC/Bluetooth", "811600"),
        ("Шлейф антені GSM", "817625"), ("Безпровідна зарядка", "817643"),
        ("Шлейф зарядки", "84266"), ("Основна камера", "89263"), ("Поліфонічний динамік", "84265"),
        ("Акумулятор з шлейфом", "84262"), ("Акумулятор банка", "820515"),
    ],
    "iphone_11": [
        ("Вібро", "11335"), ("Слуховий динамік", "784621"), ("Шлейф слухового динаміка", "819235"),
        ("Роз'єм для sim карти", "794590"), ("Екран iPhone 11 ref/orig", "781829"),
        ("Шлейф JCID слухового динаміка з датчиками", "812491"), ("Корпус iPhone 11", "781213"),
        ("Скло камери", "817631"), ("Фронтальна камера", "784614"), ("Шлейф антени Wi-Fi", "816082"),
        ("Шлейф кнопок звуку", "789424"), ("Шлейф кнопки Power", "784537"),
        ("Шлейф антені NFC/Bluetooth", "790854"), ("Безпровідна зарядка", "817642"),
        ("Шлейф зарядки", "783656"), ("Основна камера", "781214"), ("Поліфонічний динамік", "29082"),
        ("Акумулятор з шлейфом", "781215"), ("Акумулятор банка", "820516"),
    ],
    "iphone_11_pro": [
        ("Вібро", "789800"), ("Слуховий динамік", "788172"), ("Шлейф слухового динаміка", "819236"),
        ("Екран iPhone 11 Pro ref/orig", "782490"), ("Шлейф JCID слухового динаміка з датчиками", "826883"),
        ("Корпус iPhone 11 Pro", "781217"), ("Скло камери", "782891"), ("Фронтальна камера", "790390"),
        ("Шлейф антені Wi-Fi", "817636"), ("Шлейф кнопок звуку", "792030"),
        ("Шлейф кнопки Power", "786353"), ("Шлейф антені NFC/Bluetooth", "800291"),
        ("Безпровідна зарядка", "817641"), ("Шлейф зарядки", "785517"),
        ("Основна камера", "781218"), ("Поліфонічний динамік", "788778"),
        ("Акумулятор з шлейфом", "781219"), ("Акумулятор банка", "820646"),
    ],
    "iphone_11_pro_max": [
        ("Вібро", "789802"), ("Слуховий динамік", "789495"), ("Шлейф слухового динаміка", "819237"),
        ("Екран iPhone 11 Pro Max ref/orig", "783416"), ("Шлейф JCID слухового динаміка з датчиками", "826884"),
        ("Корпус iPhone 11 Pro Max", "74426"), ("Скло камери", "817639"), ("Фронтальна камера", "788494"),
        ("Шлейф антені Wi-Fi", "813454"), ("Шлейф кнопок звуку", "791650"),
        ("Шлейф кнопки Power", "12247"), ("Шлейф антені NFC/Bluetooth", "791966"),
        ("Безпровідна зарядка", "817640"), ("Шлейф зарядки", "783905"),
        ("Основна камера", "781218"), ("Поліфонічний динамік", "789803"),
        ("Акумулятор з шлейфом", "781671"), ("Акумулятор банка", "820647"),
    ],
    "iphone_12_mini": [
        ("Вібро", "23365"), ("Слуховий динамік", "797622"),
        ("Шлейф слухового динаміка + датчик наближення", "819238"),
        ("Екран iPhone 12 mini ref/orig", "786852"), ("Шлейф JCID слухового динаміка з датчиками", "826918"),
        ("Корпус iPhone 12 mini", "787628"), ("Скло камери", "788630"), ("Фронтальна камера", "817658"),
        ("Шлейф антені Wi-Fi", "812864"), ("Шлейф кнопки power + кнопок гучності", "800030"),
        ("Шлейф антені NFC/Bluetooth", "817657"), ("Шлейф спалаху", "817654"),
        ("Шлейф зарядки", "787788"), ("Камера основна", "787629"), ("Поліфонічний динамік", "800676"),
        ("Акумулятор з шлейфом", "787787"), ("Акумулятор з привязкою", "859004"),
        ("Акумулятор банка", "820648"),
    ],
    "iphone_12": [
        ("Вібро", "817424"), ("Слуховий динамік", "790630"),
        ("Шлейф слухового динаміка + датчик наближення", "815310"),
        ("Екран iPhone 12/12 Pro ref/orig", "788319"), ("Шлейф JCID слухового динаміка з датчиками", "826919"),
        ("Скло камери", "788630"), ("Корпус iPhone 12", "786849"), ("Шлейф антені Wi-Fi", "809637"),
        ("Шлейф кнопки power + звуку", "796737"), ("Шлейф антені NFC/Bluetooth", "809638"),
        ("Безпровідна зарядка", "817651"), ("Шлейф спалаху", "816436"), ("Шлейф зарядки", "787556"),
        ("Камера основна", "786851"), ("Шлейф JC основної камери без пайки", "812150"),
        ("Поліфонічний динамік", "791447"), ("Акумулятор з шлейфом", "787555"),
        ("Акумулятор з привязкою", "859005"), ("Акумулятор банка", "820649"),
    ],
    "iphone_12_pro": [
        ("Вібро", "817424"), ("Слуховий динамік", "790630"),
        ("Шлейф слухового динаміка + датчик наближення", "815310"),
        ("Екран iPhone 12/12 Pro ref/orig", "788319"), ("Шлейф JCID слухового динаміка з датчиками", "826919"),
        ("Корпус iPhone 12 Pro", "787553"), ("Фронтальна камера", "801267"), ("Скло камери", "788630"),
        ("Шлейф антені Wi-Fi", "809637"), ("Шлейф кнопки power + звуку", "806693"),
        ("Шлейф антені NFC/Bluetooth", "809638"), ("Шлейф Lidar", "809264"),
        ("Безпровідна зарядка", "817651"), ("Шлейф спалаху", "816234"), ("Шлейф зарядки", "787556"),
        ("Камера основна", "787557"), ("Шлейф JC основної камери без пайки", "813343"),
        ("Поліфонічний динамік", "791447"), ("Акумулятор з шлейфом", "787555"),
        ("Акумулятор з привязкою", "859005"), ("Акумулятор банка", "820649"),
    ],
    "iphone_12_pro_max": [
        ("Вібро", "789152"), ("Слуховий динамік", "790949"),
        ("Шлейф слухового динаміка + датчик наближення", "815541"),
        ("Шлейф JCID слухового динаміка з датчиками", "826920"), ("Роз'єм для sim карти", "792377"),
        ("Екран iPhone 12 Pro Max ref/orig", "787527"), ("Корпус iPhone 12 Pro Max with 5G", "817686"),
        ("Корпус iPhone 12 Pro Max", "787935"), ("Скло камери", "788630"), ("Фронтальна камера", "789154"),
        ("Шлейф антені Wi-Fi", "817648"), ("Шлейф кнопки power + звуку", "789155"),
        ("Шлейф антені NFC/Bluetooth", "810450"), ("Шлейф Lidar", "817649"),
        ("Безпровідна зарядка", "813133"), ("Шлейф JC основної камери без пайки", "812151"),
        ("Шлейф спалаху", "816235"), ("Шлейф зарядки", "787934"), ("Камера основна", "787933"),
        ("Поліфонічний динамік", "789153"), ("Акумулятор з шлейфом", "787932"),
        ("Акумулятор з привязкою", "859007"), ("Акумулятор банка", "820650"),
    ],
    "iphone_13_mini": [
        ("Вібро", "817672"), ("Слуховий динамік", "817673"),
        ("Шлейф слухового динаміка + датчик наближення", "810950"),
        ("Шлейф JCID слухового динаміка з датчиками", "826921"),
        ("Екран iPhone 13 mini ref/orig", "817671"), ("Корпус iPhone 13 mini with 5G", "817683"),
        ("Корпус iPhone 13 mini", "809866"), ("Скло камери", "796785"), ("Фронтальна камера", "814778"),
        ("Шлейф антені Wi-Fi", "817675"), ("Шлейф кнопки power + кнопок гучності", "807049"),
        ("Шлейф антені NFC/Bluetooth", "817676"), ("Безпровідна зарядка", "817679"),
        ("Шлейф спалаху", "817680"), ("Шлейф зарядки", "803218"), ("Камера основна", "793514"),
        ("Шлейф JC основної камери без пайки", "812153"), ("Поліфонічний динамік", "813170"),
        ("Акумулятор з шлейфом", "797702"), ("Акумулятор з привязкою", "859008"),
        ("Акумулятор банка", "820651"),
    ],
    "iphone_13": [
        ("Вібро", "809360"), ("Слуховий динамік", "798250"),
        ("Шлейф слухового динаміка + датчик наближення", "815928"), ("Роз'єм для sim карти", "818485"),
        ("Екран iPhone 13 ref/orig", "817701"),
        ("Шлейф датчику освітлення та наближення з мікрофоном", "826922"),
        ("Корпус iPhone 13 with 5G", "817704"), ("Корпус iPhone 13", "793513"),
        ("Скло камери", "794663"), ("Фронтальна камера", "804006"), ("Шлейф антені Wi-Fi", "817707"),
        ("Шлейф кнопки power + кнопок гучності", "800266"), ("Шлейф антені NFC/Bluetooth", "807374"),
        ("Шлейф антені GPS", "817705"), ("Безпровідна зарядка", "817708"), ("Шлейф спалаху", "807048"),
        ("Шлейф зарядки", "805626"), ("Камера основна", "793514"),
        ("Шлейф JC основної камери без пайки", "812152"), ("Поліфонічний динамік", "800786"),
        ("Акумулятор з шлейфом", "793515"), ("Акумулятор з привязкою", "859009"),
        ("Акумулятор банка", "820652"),
    ],
    "iphone_13_pro": [
        ("Вібро", "806662"), ("Слуховий динамік", "800170"), ("Екран iPhone 13 Pro ref/orig", "799412"),
        ("Шлейф JC датчика освітлення та наближення з мікрофоном", "826923"),
        ("Корпус iPhone 13 Pro with 5G", "817714"), ("Корпус iPhone 13 Pro", "817713"),
        ("Скло камери", "794664"), ("Фронтальна камера", "809276"), ("Шлейф антені Wi-Fi", "817715"),
        ("Шлейф кнопки power + кнопок гучності", "807257"), ("Шлейф антені NFC/Bluetooth", "815650"),
        ("Шлейф антені GPS", "817717"), ("Безпровідна зарядка", "817719"), ("Шлейф спалаху", "817718"),
        ("Шлейф зарядки", "799413"), ("Камера основна", "793210"),
        ("Шлейф JC основної камери без пайки", "812153"), ("Поліфонічний динамік", "809261"),
        ("Акумулятор з шлейфом", "793209"), ("Акумулятор з привязкою", "859010"),
        ("Акумулятор банка", "820653"),
    ],
    "iphone_13_pro_max": [
        ("Вібро", "809359"), ("Слуховий динамік", "798754"),
        ("Шлейф слухового динаміка + датчик наближення", "819224"),
        ("Екран iPhone 13 Pro Max ref/orig", "817721"),
        ("Шлейф JC датчику освітлення та наближення з мікрофоном", "826924"),
        ("Корпус 13 Pro Max with 5G", "817723"), ("Корпус 13 Pro Max", "793206"),
        ("Скло камери", "794665"), ("Фронтальна камера", "802983"), ("Шлейф антені Wi-Fi", "817726"),
        ("Шлейф кнопки power + кнопок гучності", "804590"), ("Шлейф антені NFC/Bluetooth", "817727"),
        ("Шлейф Lidar", "817728"), ("Шлейф антені GPS", "817737"), ("Безпровідна зарядка", "817736"),
        ("Шлейф спалаху", "817735"), ("Шлейф зарядки", "796212"), ("Поліфонічний динамік", "805636"),
        ("Камера основна", "793210"), ("Шлейф JC основної камери без пайки", "812153"),
        ("Акумулятор з шлейфом", "793208"), ("Акумулятор з привязкою", "859011"),
        ("Акумулятор банка", "820654"),
    ],
    "iphone_14": [
        ("Вібро", "817744"), ("Слуховий динамік", "809503"),
        ("Шлейф слухового динаміка + датчик наближення", "817745"),
        ("Екран iPhone 14 ref/orig", "817742"),
        ("Шлейф JC датчику освітлення та наближення з мікрофоном", "826925"),
        ("Корпус iPhone 14 global", "817761"), ("Корпус iPhone 14 e-sim", "817760"),
        ("Скло камери", "802886"), ("Фронтальна камера", "813137"), ("Шлейф антені Wi-Fi", "817752"),
        ("Шлейф кнопки Power", "817753"), ("Шлейф антені NFC/Bluetooth", "817751"),
        ("Шлейф антені GPS", "817749"), ("Безпровідна зарядка", "817747"),
        ("Шлейф JC основної камери без пайки", "812155"), ("Шлейф спалаху", "817740"),
        ("Шлейф зарядки", "810557"), ("Камера основна", "809287"), ("Поліфонічний динамік", "810364"),
        ("Акумулятор з шлейфом", "801740"), ("Акумулятор з привязкою", "859012"),
        ("Акумулятор банка", "820655"), ("Задня кришка", "812840"),
    ],
    "iphone_14_plus": [
        ("Вібро", "817767"), ("Слуховий динамік", "817768"),
        ("Шлейф слухового динаміка + датчик наближення", "817769"),
        ("Екран iPhone 14 Plus ref/orig", "817771"),
        ("Шлейф JC датчику освітлення та наближення з мікрофоном", "826927"),
        ("Корпус 14 Plus global", "817766"), ("Корпус 14 Plus e-sim", "817765"),
        ("Фронтальна камера", "817774"), ("Шлейф антені Wi-Fi", "817775"),
        ("Шлейф кнопки power + кнопок гучності", "817776"), ("Шлейф антені NFC/Bluetooth", "817777"),
        ("Шлейф антені GPS", "817781"), ("Безпровідна зарядка", "817779"),
        ("Шлейф JC основної камери без пайки", "817778"), ("Шлейф спалаху", "817763"),
        ("Шлейф зарядки", "806062"), ("Камера основна", "805200"), ("Поліфонічний динамік", "817762"),
        ("Акумулятор з шлейфом", "801741"), ("Акумулятор з привязкою", "859013"),
        ("Акумулятор банка", "820656"), ("Задня кришка", "810521"),
    ],
    "iphone_14_pro": [
        ("Вібро", "817785"), ("Слуховий динамік", "810362"),
        ("Шлейф слухового динаміка + датчик наближення", "817787"),
        ("Екран iPhone 14 Pro ref/orig", "817788"),
        ("Шлейф JC датчику освітлення та наближення з мікрофоном", "826928"),
        ("Корпус 14 Pro global", "817793"), ("Корпус 14 Pro e-sim", "817792"),
        ("Скло камери", "802885"), ("Фронтальна камера", "810104"), ("Шлейф антені Wi-Fi", "817790"),
        ("Шлейф кнопки power + кнопок гучності", "817791"), ("Шлейф антені NFC/Bluetooth", "815887"),
        ("Шлейф Lidar", "817755"), ("Шлейф антені GPS", "817795"), ("Безпровідна зарядка", "817786"),
        ("Шлейф JC основної камери без пайки", "812154"), ("Шлейф основної камери для пайки", "836790"),
        ("Шлейф спалаху", "817784"), ("Шлейф зарядки", "810558"), ("Камера основна", "801756"),
        ("Поліфонічний динамік", "810365"), ("Акумулятор з шлейфом", "801742"),
        ("Акумулятор з привязкою", "859021"), ("Акумулятор банка", "820715"),
    ],
    "iphone_14_pro_max": [
        ("Вібро", "817797"), ("Слуховий динамік", "810363"),
        ("Шлейф слухового динаміка + датчик наближення", "812252"),
        ("Екран iPhone 14 Pro Max ref/orig", "817798"),
        ("Шлейф JC датчика освітлення та наближення з мікрофоном", "826929"),
        ("Корпус 14 Pro Max global", "804420"), ("Корпус 14 Pro Max e-sim", "817801"),
        ("Скло камери", "817800"), ("Фронтальна камера", "810129"), ("Шлейф антені Wi-Fi", "817802"),
        ("Шлейф кнопки power + кнопок гучності", "817463"), ("Шлейф антені NFC/Bluetooth", "817803"),
        ("Шлейф Lidar", "817804"), ("Шлейф антені GPS", "817808"), ("Безпровідна зарядка", "817806"),
        ("Шлейф JC основної камери без пайки", "812156"), ("Шлейф спалаху", "817807"),
        ("Шлейф зарядки", "808593"), ("Камера основна", "805072"), ("Поліфонічний динамік", "810366"),
        ("Акумулятор з шлейфом", "801743"), ("Акумулятор з привязкою", "859022"),
        ("Акумулятор банка", "820718"),
    ],
    "iphone_15": [
        ("Вібро", "817584"), ("Слуховий динамік", "817578"),
        ("Шлейф слухового динаміка + датчик наближення", "817585"), ("Роз'єм для sim карти", "880547"),
        ("Екран iPhone 15 ref/orig", "817577"), ("Шлейф JCID слухового динаміка з датчиками", "844590"),
        ("Корпус iPhone 15 global", "817575"), ("Корпус iPhone 15 e-sim", "817586"),
        ("Скло камери", "817573"), ("Фронтальна камера", "817572"), ("Шлейф антені Wi-Fi", "817589"),
        ("Шлейф кнопок звуку", "856621"), ("Шлейф кнопки Power", "817590"),
        ("Шлейф антені NFC/Bluetooth", "817583"), ("Шлейф антені GPS", "817582"),
        ("Безпровідна зарядка", "817859"), ("Шлейф JC основної камери без пайки", "817580"),
        ("Шлейф спалаху", "817860"), ("Шлейф зарядки", "817571"), ("Камера основна", "817570"),
        ("Поліфонічний динамік", "817569"), ("Акумулятор з шлейфом", "817568"),
        ("Акумулятор з привязкою", "858919"), ("Акумулятор банка", "820717"),
        ("Задня кришка", "817579"),
    ],
    "iphone_15_plus": [
        ("Вібро", "817892"), ("Слуховий динамік", "817891"),
        ("Шлейф слухового динаміка + датчик наближення", "817890"),
        ("Екран iPhone 15 Plus ref/orig", "817888"),
        ("Корпус iPhone 15 Plus global", "817883"), ("Корпус iPhone 15 Plus e-sim", "817882"),
        ("Скло камери", "817880"), ("Фронтальна камера", "817879"), ("Шлейф антені Wi-Fi", "817878"),
        ("Шлейф кнопки Power", "817877"), ("Шлейф антені NFC/Bluetooth", "817876"),
        ("Шлейф антені GPS", "817873"), ("Безпровідна зарядка", "817871"), ("Шлейф спалаху", "817869"),
        ("Шлейф зарядки", "817868"), ("Камера основна", "817867"), ("Поліфонічний динамік", "817866"),
        ("Акумулятор з шлейфом", "817865"), ("Акумулятор з привязкою", "859131"),
        ("Акумулятор банка", "820719"), ("Задня кришка", "817862"),
    ],
    "iphone_15_pro": [
        ("Вібро", "817915"), ("Слуховий динамік", "817914"),
        ("Шлейф слухового динаміка + датчик наближення", "817913"),
        ("Екран iPhone 15 Pro ref/orig", "817911"),
        ("Шлейф JC слухового динаміка + датчик наближення", "829949"),
        ("Корпус iPhone 15 Pro global", "817271"), ("Корпус iPhone 15 Pro e-sim", "817270"),
        ("Скло камери", "817907"), ("Фронтальна камера", "817906"), ("Шлейф антені Wi-Fi", "817905"),
        ("Шлейф кнопок звуку", "844950"), ("Шлейф кнопки Power", "817904"),
        ("Шлейф антені NFC/Bluetooth", "817903"), ("Шлейф Lidar", "817902"),
        ("Шлейф антені GPS", "817900"), ("Безпровідна зарядка", "817898"),
        ("Шлейф JC основної камери без пайки", "817897"), ("Шлейф спалаху", "817896"),
        ("Шлейф зарядки", "817268"), ("Камера основна", "817267"), ("Поліфонічний динамік", "817895"),
        ("Акумулятор з шлейфом", "817894"), ("Акумулятор з привязкою", "859132"),
        ("Акумулятор банка", "820720"), ("Задня кришка", "817893"),
    ],
    "iphone_15_pro_max": [
        ("Вібро", "817939"), ("Слуховий динамік", "817938"),
        ("Шлейф слухового динаміка + датчик наближення", "817937"),
        ("Екран iPhone 15 Pro Max ref/orig", "817918"),
        ("Шлейф JC датчика освітлення та наближення", "830864"),
        ("Корпус iPhone 15 Pro Max global", "817234"), ("Корпус iPhone 15 Pro Max e-sim", "817233"),
        ("Скло камери", "817935"), ("Фронтальна камера", "817934"), ("Шлейф антені Wi-Fi", "817933"),
        ("Шлейф кнопок звуку", "844270"), ("Шлейф кнопки Power", "817932"),
        ("Шлейф антені NFC/Bluetooth", "817931"), ("Шлейф Lidar", "817930"),
        ("Шлейф антені GPS", "817928"), ("Безпровідна зарядка", "817926"),
        ("Шлейф JC основної камери без пайки", "817925"), ("Шлейф спалаху", "817924"),
        ("Шлейф зарядки", "817237"), ("Камера основна", "817236"), ("Поліфонічний динамік", "817923"),
        ("Акумулятор з шлейфом", "817922"), ("Акумулятор з привязкою", "859133"),
        ("Акумулятор банка", "820721"), ("Задня кришка", "817921"),
    ],
    "iphone_16": [
        ("Слуховий динамік", "862405"), ("Шлейф датчику наближення", "869562"),
        ("Шлейф мікрофону та барометру", "868011"), ("Екран iPhone 16 ref/orig", "836731"),
        ("Корпус iPhone 16 global", "852393"), ("Корпус 16 e-sim", "852392"),
        ("Скло камери", "844650"), ("Фронтальна камера", "854293"), ("Шлейф кнопки Power", "880113"),
        ("Шлейф антені NFC/Bluetooth", "879026"), ("Безпровідна зарядка", "861216"),
        ("Шлейф JC основної камери без пайки", "857013"), ("Шлейф зарядки", "847982"),
        ("Камера основна", "854059"), ("Поліфонічний динамік", "842144"),
        ("Акумулятор з шлейфом", "852396"), ("Акумулятор з привязкою", "880336"),
        ("Акумулятор банка", "852395"), ("Задня кришка", "840248"),
    ],
    "iphone_16_plus": [
        ("Екран iPhone 16 Plus ref/orig", "849710"), ("Корпус iPhone 16 Plus global", "849450"),
        ("Корпус iPhone 16 Plus e-sim", "849420"), ("Скло камери", "845093"),
        ("Безпровідна зарядка", "856734"), ("Шлейф зарядки", "856733"),
        ("Камера основна", "849766"), ("Акумулятор з шлейфом", "867951"),
        ("Акумулятор банка", "867952"), ("Задня кришка", "856317"),
    ],
    "iphone_16_pro": [
        ("Вібро", "838529"), ("Слуховий динамік", "860579"), ("Шлейф нижнього мікрофона", "870860"),
        ("Екран iPhone 16 Pro ref/orig", "837509"),
        ("Шлейф JC датчику освітлення та наближення", "875495"),
        ("Корпус iPhone 16 Pro global", "839685"), ("Корпус iPhone 16 Pro e-sim", "838522"),
        ("Скло камери", "841363"), ("Фронтальна камера", "850472"), ("Шлейф кнопок звуку", "851024"),
        ("Шлейф кнопки Power", "859313"), ("Шлейф антені NFC/Bluetooth", "860026"),
        ("Безпровідна зарядка", "860817"), ("Шлейф JC основної камери без пайки", "856440"),
        ("Шлейф зарядки", "838526"), ("Шлейф кнопки камери", "859019"),
        ("Камера основна", "838524"), ("Поліфонічний динамік", "870872"),
        ("Акумулятор з шлейфом", "838523"), ("Акумулятор з привязкою", "868408"),
        ("Задня кришка", "838521"),
    ],
    "iphone_16_pro_max": [
        ("Вібро", "838535"), ("Слуховий динамік", "860578"), ("Шлейф нижнього мікрофона", "856344"),
        ("Шлейф основної антени сигналу", "860071"), ("Екран iPhone 16 Pro Max ref/orig", "837510"),
        ("Шлейф JC датчику освітлення та наближення", "861910"),
        ("Корпус iPhone 16 Pro Max global", "839676"), ("Корпус iPhone 16 Pro Max e-sim", "838534"),
        ("Скло камери", "842111"), ("Фронтальна камера", "849706"), ("Шлейф кнопок звуку", "878415"),
        ("Шлейф кнопки Power", "860849"), ("Шлейф антені NFC/Bluetooth", "855198"),
        ("Безпровідна зарядка", "860608"), ("Шлейф JC основної камери без пайки", "859370"),
        ("Шлейф зарядки", "838533"), ("Шлейф кнопки камери", "859018"),
        ("Камера основна", "838532"), ("Поліфонічний динамік", "856345"),
        ("Акумулятор з шлейфом", "838531"), ("Акумулятор з привязкою", "868406"),
        ("Акумулятор банка", "848703"), ("Задня кришка", "837977"),
    ],
    "iphone_17": [
        ("Слуховий динамік", "867986"), ("Екран iPhone 17 ref/orig", "867983"),
        ("Корпус iPhone 17 global", "867979"), ("Корпус iPhone 17 e-sim", "867980"),
        ("Скло камери", "869340"), ("Шлейф зарядки", "867985"), ("Камера основна", "867984"),
        ("Поліфонічний динамік", "867987"), ("Акумулятор з шлейфом", "867982"),
        ("Акумулятор банка", "867981"), ("Задня кришка", "867978"),
    ],
    "iphone_17_air": [
        ("Слуховий динамік", "868003"), ("Екран iPhone 17 Air ref/orig", "861286"),
        ("Корпус iPhone 17 Air", "861282"), ("Скло камери", "869339"),
        ("Шлейф зарядки", "868002"), ("Камера основна", "861288"),
        ("Акумулятор з шлейфом", "861287"), ("Задня кришка", "861284"),
    ],
    "iphone_17_pro": [
        ("Слуховий динамік", "867956"), ("Екран iPhone 17 Pro ref/orig", "859363"),
        ("Корпус iPhone 17 Pro global", "861101"), ("Корпус iPhone 17 Pro e-sim", "867994"),
        ("Скло камери", "868012"), ("Фронтальна камера", "880330"),
        ("Шлейф зарядки", "867993"), ("Камера основна", "867977"),
        ("Поліфонічний динамік", "867995"), ("Акумулятор з шлейфом", "867992"),
        ("Задня кришка", "867991"),
    ],
    "iphone_17_pro_max": [
        ("Слуховий динамік", "868001"), ("Екран iPhone 17 Pro Max ref/orig", "859282"),
        ("Корпус iPhone 17 Pro Max global", "859283"), ("Корпус iPhone 17 Pro Max e-sim", "865536"),
        ("Скло камери", "871411"), ("Фронтальна камера", "880329"),
        ("Шлейф кнопок звуку", "875377"), ("Шлейф кнопки Power", "875376"),
        ("Шлейф зарядки", "867997"), ("Камера основна", "867996"),
        ("Поліфонічний динамік", "868000"), ("Акумулятор з шлейфом", "859552"),
        ("Задня кришка", "867999"),
    ],
}

CATEGORIES = {
    "cat_iphone": "📱 Запчастини iPhone",
    "cat_ipad": "📟 Запчастини iPad",
    "cat_macbook": "💻 Запчастини MacBook",
    "cat_watch": "⌚️ Запчастини Apple Watch",
    "cat_android": "🤖 Андроїди",
    "cat_other": "📦 Інше",
}


def get_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🛒 Замовити запчастину")],
        [KeyboardButton("📋 Історія заміни запчастин")],
        [KeyboardButton("🔄 Відвязка запчастини")],
    ], resize_keyboard=True)


def build_models_keyboard():
    keyboard = []
    for row in IPHONE_MODELS_ROWS:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"model_{key}") for key, name in row])
    return InlineKeyboardMarkup(keyboard)


def build_parts_keyboard(model_key, selected):
    parts = IPHONE_PARTS.get(model_key, [])
    keyboard = []
    for i, (part_name, art) in enumerate(parts):
        part_id = f"p{i}"
        mark = "✅ " if part_id in selected else ""
        keyboard.append([InlineKeyboardButton(f"{mark}{part_name} (Арт. {art})", callback_data=f"toggle_{part_id}")])
    keyboard.append([InlineKeyboardButton("📝 Інше", callback_data="other_part")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад до вибору моделі", callback_data="back_to_models")])
    keyboard.append([InlineKeyboardButton("✔️ Підтвердити замовлення", callback_data="confirm_parts")])
    return InlineKeyboardMarkup(keyboard)


def build_order_summary(data):
    parts = data.get("parts_list", [])
    parts_text = "\n".join(f"  • {p}" for p in parts)
    model_line = f"📱 *Модель:* {data.get('iphone_model', '')}\n" if data.get("iphone_model") else ""
    return (
        "📋 *Перевірте ваше замовлення:*\n\n"
        f"👤 *Працівник:* {data.get('employee_name', '')}\n"
        f"🗂 *Категорія:* {data.get('category', '')}\n"
        f"{model_line}"
        f"🔧 *Запчастини:*\n{parts_text}\n\nВсе вірно?"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = context.bot_data.get("users", {})
    if user_id in users:
        await update.message.reply_text(f"👋 З поверненням, {users[user_id]}!", reply_markup=get_main_menu())
        return ConversationHandler.END
    await update.message.reply_text("👋 Вітаємо!\n\nВведіть ваше *прізвище*:", parse_mode="Markdown")
    return REGISTER_LAST_NAME


async def register_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_name"] = update.message.text.strip()
    await update.message.reply_text("Тепер введіть ваше *ім'я*:", parse_mode="Markdown")
    return REGISTER_FIRST_NAME


async def register_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.text.strip()
    last_name = context.user_data.get("last_name", "")
    full_name = f"{last_name} {first_name}"
    if "users" not in context.bot_data:
        context.bot_data["users"] = {}
    context.bot_data["users"][str(update.effective_user.id)] = full_name
    await update.message.reply_text(f"✅ Зареєстровано як *{full_name}*!", parse_mode="Markdown", reply_markup=get_main_menu())
    return ConversationHandler.END


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = context.bot_data.get("users", {})
    if user_id not in users:
        await update.message.reply_text("⚠️ Спочатку введіть /start")
        return ConversationHandler.END
    context.user_data.clear()
    context.user_data["employee_name"] = users[user_id]
    context.user_data["selected_parts"] = []
    await update.message.reply_text("📸 Надішліть фото стікера з IMEI або серійним номером:")
    return WAITING_STICKER_PHOTO


async def receive_sticker_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Надішліть саме фото стікера.")
        return WAITING_STICKER_PHOTO
    context.user_data["sticker_photo_id"] = update.message.photo[-1].file_id
    keyboard = [[InlineKeyboardButton(label, callback_data=key)] for key, label in CATEGORIES.items()]
    await update.message.reply_text("✅ Фото отримано!\n\nОберіть категорію:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_CATEGORY


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_key = query.data
    context.user_data["category"] = CATEGORIES[category_key]
    context.user_data["iphone_model"] = None
    if category_key == "cat_iphone":
        await query.edit_message_text("Оберіть модель iPhone:", reply_markup=build_models_keyboard())
        return CHOOSE_IPHONE_MODEL
    await query.edit_message_text(
        f"Категорія: *{CATEGORIES[category_key]}*\n\nОпишіть потрібні запчастини:",
        parse_mode="Markdown"
    )
    return FREE_TEXT_PARTS


async def choose_iphone_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_key = query.data.replace("model_", "")

    if model_key == "iphone_custom":
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад до вибору моделі", callback_data="back_to_models")]
        ])
        await query.edit_message_text(
            "Введіть модель iPhone та запчастину яка потрібна:",
            reply_markup=back_keyboard
        )
        return CUSTOM_MODEL_TEXT

    model_name = IPHONE_MODELS_DICT.get(model_key, model_key)
    context.user_data["iphone_model"] = model_name
    context.user_data["iphone_model_key"] = model_key
    context.user_data["selected_parts"] = []
    await query.edit_message_text(
        f"Модель: *{model_name}*\n\nОберіть запчастини (можна декілька):",
        parse_mode="Markdown",
        reply_markup=build_parts_keyboard(model_key, [])
    )
    return CHOOSE_IPHONE_PARTS


async def custom_model_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    custom_text = update.message.text.strip()
    context.user_data["parts_list"] = [custom_text]
    context.user_data["iphone_model"] = "Інша модель"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
    ])
    await update.message.reply_text(build_order_summary(context.user_data), parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM_ORDER


async def toggle_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_key = context.user_data.get("iphone_model_key", "")

    if query.data == "back_to_models":
        await query.edit_message_text("Оберіть модель iPhone:", reply_markup=build_models_keyboard())
        return CHOOSE_IPHONE_MODEL

    if query.data == "other_part":
        await query.edit_message_text("📝 Напишіть що саме потрібно замовити (назва, артикул, або опис):")
        return OTHER_PART_TEXT

    if query.data == "confirm_parts":
        selected = context.user_data.get("selected_parts", [])
        if not selected:
            await query.answer("⚠️ Оберіть хоча б одну запчастину!", show_alert=True)
            return CHOOSE_IPHONE_PARTS
        parts = IPHONE_PARTS.get(model_key, [])
        context.user_data["parts_list"] = [
            f"{parts[int(pid[1:])][0]} (Арт. {parts[int(pid[1:])][1]})"
            for pid in selected if pid[1:].isdigit() and int(pid[1:]) < len(parts)
        ]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
            [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
        ])
        await query.edit_message_text(build_order_summary(context.user_data), parse_mode="Markdown", reply_markup=keyboard)
        return CONFIRM_ORDER

    part_id = query.data.replace("toggle_", "")
    selected = context.user_data.get("selected_parts", [])
    if part_id in selected:
        selected.remove(part_id)
    else:
        selected.append(part_id)
    context.user_data["selected_parts"] = selected
    await query.edit_message_text(
        f"Модель: *{context.user_data.get('iphone_model', '')}*\n\nОберіть запчастини:",
        parse_mode="Markdown",
        reply_markup=build_parts_keyboard(model_key, selected)
    )
    return CHOOSE_IPHONE_PARTS


async def other_part_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    other_text = update.message.text.strip()
    model_key = context.user_data.get("iphone_model_key", "")
    selected = context.user_data.get("selected_parts", [])
    parts = IPHONE_PARTS.get(model_key, [])
    parts_list = [
        f"{parts[int(pid[1:])][0]} (Арт. {parts[int(pid[1:])][1]})"
        for pid in selected if pid[1:].isdigit() and int(pid[1:]) < len(parts)
    ]
    parts_list.append(f"📝 Інше: {other_text}")
    context.user_data["parts_list"] = parts_list
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
    ])
    await update.message.reply_text(build_order_summary(context.user_data), parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM_ORDER


async def back_to_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(label, callback_data=key)] for key, label in CATEGORIES.items()]
    await query.edit_message_text("Оберіть категорію:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_CATEGORY


async def free_text_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["parts_list"] = [update.message.text.strip()]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
    ])
    await update.message.reply_text(build_order_summary(context.user_data), parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM_ORDER


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel_order":
        await query.edit_message_text("❌ Замовлення скасовано.")
        return ConversationHandler.END

    data = context.user_data
    parts_text = "\n".join(f"  • {p}" for p in data.get("parts_list", []))
    model_line = f"Модель: {data.get('iphone_model', '')}\n" if data.get("iphone_model") else ""
    group_message = (
        "НОВЕ ЗАМОВЛЕННЯ ЗАПЧАСТИН\n\n"
        f"Працівник: {data.get('employee_name', '')}\n"
        f"Категорія: {data.get('category', '')}\n"
        f"{model_line}"
        f"Запчастини:\n{parts_text}"
    )
    try:
        user_id = update.effective_user.id
        done_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Замовлення зроблено", callback_data=f"order_done_{user_id}")]
        ])
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=ORDER_THREAD_ID if ORDER_THREAD_ID else None,
            photo=data.get("sticker_photo_id"),
            caption=group_message,
            reply_markup=done_keyboard
        )
        await query.edit_message_text("Замовлення відправлено!")
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.edit_message_text("Помилка при відправці. Зверніться до адміністратора.")
    return ConversationHandler.END


async def order_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.replace("order_done_", ""))
    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👌 Вже зроблено", callback_data="already_done")]
        ])
    )
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="Ваше замовлення опрацьовано! Менеджер підтвердив виконання."
        )
    except Exception as e:
        logger.error(f"Error notifying user: {e}")


async def history_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = context.bot_data.get("users", {})
    if user_id not in users:
        await update.message.reply_text("⚠️ Спочатку введіть /start")
        return ConversationHandler.END
    context.user_data.clear()
    context.user_data["employee_name"] = users[user_id]
    await update.message.reply_text("📸 Надішліть фото штрихкоду з IMEI або серійним номером пристрою:")
    return HISTORY_PHOTO


async def history_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Надішліть саме фото штрихкоду.")
        return HISTORY_PHOTO
    context.user_data["history_photo_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ Фото отримано!\n\nЩо саме потрібно перевірити? Напишіть текстом:")
    return HISTORY_TEXT


async def history_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    check_text = update.message.text.strip()
    data = context.user_data
    group_message = (
        "ЗАПИТ НА ІСТОРІЮ ЗАМІНИ ЗАПЧАСТИН\n\n"
        f"Працівник: {data.get('employee_name', '')}\n"
        f"Що перевірити: {check_text}"
    )
    try:
        await context.bot.send_photo(
            chat_id=HISTORY_CHAT_ID,
            message_thread_id=HISTORY_THREAD_ID if HISTORY_THREAD_ID else None,
            photo=data.get("history_photo_id"),
            caption=group_message
        )
        await update.message.reply_text("✅ Запит відправлено!", reply_markup=get_main_menu())
    except Exception as e:
        logger.error(f"History error: {e}")
        await update.message.reply_text("⚠️ Помилка при відправці. Зверніться до адміністратора.")
    return ConversationHandler.END


async def handle_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.reply_to_message:
        return
    if not message.reply_to_message.from_user.is_bot:
        return
    original = message.reply_to_message
    caption = original.caption or original.text or ""
    reply_text = message.text or message.caption or ""
    manager_name = message.from_user.first_name or "Менеджер"

    # Check if this is unbind transfer number reply
    if "worker_id:" in caption:
        for line in caption.split("\n"):
            if "worker_id:" in line:
                try:
                    worker_id = int(line.replace("worker_id:", "").strip())
                    await context.bot.send_message(
                        chat_id=worker_id,
                        text=f"Номер переміщення: {reply_text}"
                    )
                except Exception as e:
                    logger.error(f"Error sending transfer number: {e}")
        return

    # Regular reply — find worker by name
    worker_name = None
    for line in caption.split("\n"):
        if "Працівник:" in line:
            worker_name = line.replace("Працівник:", "").strip()
            break
    if not worker_name:
        return
    users = context.bot_data.get("users", {})
    worker_id = None
    for uid, name in users.items():
        if name == worker_name:
            worker_id = int(uid)
            break
    if not worker_id:
        return
    try:
        await context.bot.send_message(
            chat_id=worker_id,
            text=f"Відповідь від менеджера ({manager_name}):\n\n{reply_text}"
        )
    except Exception as e:
        logger.error(f"Error sending reply to worker: {e}")


async def unbind_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = context.bot_data.get("users", {})
    if user_id not in users:
        await update.message.reply_text("Спочатку введіть /start")
        return ConversationHandler.END
    context.user_data.clear()
    context.user_data["employee_name"] = users[user_id]
    await update.message.reply_text("📸 Надішліть фото стікера з IMEI або серійним номером:")
    return UNBIND_PHOTO


async def unbind_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Надішліть саме фото стікера.")
        return UNBIND_PHOTO
    context.user_data["unbind_photo_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("Яку запчастину потрібно відвязати? Напишіть текстом:")
    return UNBIND_PART_REMOVE


async def unbind_part_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["unbind_remove"] = update.message.text.strip()
    await update.message.reply_text("Яку запчастину потрібно привязати? Напишіть текстом:")
    return UNBIND_PART_ADD


async def unbind_part_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["unbind_add"] = update.message.text.strip()
    data = context.user_data
    group_message = (
        "ЗАПИТ НА ВІДВЯЗКУ ЗАПЧАСТИНИ\n\n"
        f"Працівник: {data.get('employee_name', '')}\n"
        f"Відвязати: {data.get('unbind_remove', '')}\n"
        f"Привязати: {data.get('unbind_add', '')}"
    )
    try:
        user_id = update.effective_user.id
        unbind_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Відвязати запчастину", callback_data=f"unbind_done_{user_id}")]
        ])
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=ORDER_THREAD_ID if ORDER_THREAD_ID else None,
            photo=data.get("unbind_photo_id"),
            caption=group_message,
            reply_markup=unbind_keyboard
        )
        await update.message.reply_text("Запит відправлено!", reply_markup=get_main_menu())
    except Exception as e:
        logger.error(f"Unbind error: {e}")
        await update.message.reply_text("Помилка при відправці. Зверніться до адміністратора.")
    return ConversationHandler.END


async def unbind_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.replace("unbind_done_", ""))

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Готово — введіть номер переміщення", callback_data="unbind_already_done")]
        ])
    )

    # Ask manager for transfer number
    context.user_data[f"unbind_worker_{query.message.message_id}"] = user_id
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        message_thread_id=query.message.message_thread_id,
        text=f"Введіть номер переміщення (reply на це повідомлення):\nworker_id:{user_id}"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Скасовано.", reply_markup=get_main_menu())
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    reg_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_last_name)],
            REGISTER_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_first_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="registration", persistent=False,
    )

    order_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("Замовити запчастину"), order_start)],
        states={
            WAITING_STICKER_PHOTO: [MessageHandler(filters.PHOTO, receive_sticker_photo)],
            CHOOSE_CATEGORY: [CallbackQueryHandler(choose_category, pattern="^cat_")],
            CHOOSE_IPHONE_MODEL: [CallbackQueryHandler(choose_iphone_model, pattern="^model_")],
            CHOOSE_IPHONE_PARTS: [CallbackQueryHandler(toggle_part, pattern="^(toggle_|confirm_parts|other_part|back_to_models)")],
            OTHER_PART_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, other_part_text)],
            CUSTOM_MODEL_TEXT: [
                CallbackQueryHandler(choose_iphone_model, pattern="^model_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, custom_model_text),
            ],
            FREE_TEXT_PARTS: [
                CallbackQueryHandler(back_to_categories, pattern="^back_to_categories$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, free_text_parts),
            ],
            CONFIRM_ORDER: [CallbackQueryHandler(confirm_order, pattern="^(send_order|cancel_order)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="order", persistent=False, allow_reentry=True,
    )

    history_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("Історія заміни запчастин"), history_start)],
        states={
            HISTORY_PHOTO: [MessageHandler(filters.PHOTO, history_photo)],
            HISTORY_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, history_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="history", persistent=False, allow_reentry=True,
    )

    app.add_handler(reg_conv)
    app.add_handler(order_conv)
    app.add_handler(history_conv)
    app.add_handler(CallbackQueryHandler(order_done, pattern="^order_done_"))
    app.add_handler(CallbackQueryHandler(unbind_done, pattern="^unbind_done_"))

    unbind_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("Відвязка запчастини"), unbind_start)],
        states={
            UNBIND_PHOTO: [MessageHandler(filters.PHOTO, unbind_photo)],
            UNBIND_PART_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, unbind_part_remove)],
            UNBIND_PART_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, unbind_part_add)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="unbind", persistent=False, allow_reentry=True,
    )
    app.add_handler(unbind_conv)
    app.add_handler(MessageHandler(
        filters.Chat([int(GROUP_CHAT_ID), int(HISTORY_CHAT_ID)]) & filters.REPLY,
        handle_group_reply
    ))

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
