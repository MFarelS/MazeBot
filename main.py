from bot          import Bot, JustAnException
from user         import User
from checkoutdata import PaymentInfo, PaymentChannel, PaymentChannelOptionInfo
from colorama     import Fore, init
from time         import sleep
from datetime     import datetime
import os

init()
INFO = Fore.LIGHTBLUE_EX + "[*]" + Fore.BLUE
INPUT = Fore.LIGHTGREEN_EX + "[?]" + Fore.GREEN
PROMPT = Fore.LIGHTRED_EX + "[!]" + Fore.RED
ERROR = Fore.LIGHTRED_EX + "[!]" + Fore.RED


def int_input(prompt_: str, max_: int = -1, min_: int = 1) -> int:
    input_: str
    while True:
        input_ = input(f"{INPUT} {prompt_}")
        if input_.isdigit():
            input_int = int(input_)
            if max_ == -1:
                return input_int
            elif min_ <= input_int <= max_:
                return input_int
            elif input_int > max_:
                print(PROMPT, "Angka terlalu banyak!")
                continue
            elif input_int < min_:
                print(PROMPT, "Angka terlalu sedikit!")
                continue
        print(PROMPT, "Masukkan angka!")


if os.name.lower() == "nt":
    os.system("cls")
else:
    os.system("clear")
try:
    print(INFO, "Mengambil informasi user...", end='\r')
    cookie = open("cookie.txt", 'r')
    user = User.login(cookie.read())
    cookie.close()
    print(INFO, "Welcome", Fore.GREEN, user.name, ' ' * 10)
    print()

    print(INFO, "Masukan url barang yang akan dibeli")
    bot = Bot(user)
    item = bot.fetch_item_from_url(input(INPUT + " url: " + Fore.RESET))

    print(Fore.RESET, "-" * 32)
    print(Fore.LIGHTBLUE_EX, "Nama:", Fore.GREEN, item.name)
    print(Fore.LIGHTBLUE_EX, "Harga:", Fore.GREEN, item.get_price(item.price))
    print(Fore.LIGHTBLUE_EX, "Brand:", Fore.GREEN, item.brand)
    print(Fore.LIGHTBLUE_EX, "Stok:", Fore.GREEN, item.stock)
    print(Fore.LIGHTBLUE_EX, "Lokasi Toko:", Fore.GREEN, item.shop_location)
    print(Fore.RESET, "-" * 32)
    print()

    selected_model = 0
    if len(item.models) > 1:
        print(INFO, "Pilih model/variasi")
        print(Fore.RESET, "-" * 32)
        for index, model in enumerate(item.models):
            print(Fore.GREEN + '[' + str(index+1) + ']' + Fore.BLUE, model.name)
            print('\t', Fore.LIGHTBLUE_EX, "Harga:", Fore.GREEN, item.get_price(model.price))
            print('\t', Fore.LIGHTBLUE_EX, "Stok:", Fore.GREEN, model.stock)
            print('\t', Fore.LIGHTBLUE_EX, "ID Model:", Fore.GREEN, model.model_id)
            print(Fore.RESET, "-" * 32)
        print()
        selected_model = int_input("Pilihan: ", len(item.models))-1
        print()

    print(INFO, "Pilih metode pembayaran")
    payment_channels = dict(enumerate(PaymentChannel))
    for index, channel in payment_channels.items():
        print(Fore.GREEN + '[' + str(index+1) + ']' + Fore.BLUE, {
                PaymentChannel.ALFAMART           : "Alfamart",
                PaymentChannel.INDOMART_ISAKU     : "Indomart iSaku",
                PaymentChannel.AKULAKU            : "Akulaku",
                PaymentChannel.TRANSFER_BANK      : "Transfer Bank",
                PaymentChannel.COD_BAYAR_DI_TEMPAT: "COD (Bayar di tempat)",
                PaymentChannel.SHOPEE_PAY         : "ShopeePay"
            }[channel])
    print()
    selected_payment_channel = payment_channels[int_input("Pilihan: ", len(payment_channels))-1]
    print()

    selected_option_info = PaymentChannelOptionInfo.NONE
    if selected_payment_channel is PaymentChannel.TRANSFER_BANK or \
            selected_payment_channel is PaymentChannel.AKULAKU:
        options_info = dict(enumerate(list(PaymentChannelOptionInfo)[1 if selected_payment_channel is
                            PaymentChannel.TRANSFER_BANK else 7:None if selected_payment_channel is
                            PaymentChannel.AKULAKU else 7]))
        for index, option_info in options_info.items():
            print(Fore.GREEN + '[' + str(index+1) + ']' + Fore.BLUE, {
                    PaymentChannelOptionInfo.TRANSFER_BANK_BCA_AUTO: "Transfer Bank BCA (Dicek Otomatis)",
                    PaymentChannelOptionInfo.TRANSFER_BANK_BNI_AUTO: "Transfer Bank BNI (Dicek Otomatis)",
                    PaymentChannelOptionInfo.TRANSFER_BANK_BRI_AUTO: "Transfer Bank BRI (Dicek Otomatis)",
                    PaymentChannelOptionInfo.TRANSFER_BANK_PERMATA_AUTO: "Transfer Bank Permata (Dicek Otomatis)",
                    PaymentChannelOptionInfo.TRANSFER_BANK_SYARIAH_AUTO: "Transfer Bank Syariah (Dicek Otomatis)",
                    PaymentChannelOptionInfo.TRANSFER_BANK_MANDIRI_AUTO: "Transfer Bank Mandiri (Dicek Otomatis)",
                    PaymentChannelOptionInfo.AKULAKU_CICILAN_1X: "Akulaku Cicilan 1X",
                    PaymentChannelOptionInfo.AKULAKU_CICILAN_2X: "Akulaku Cicilan 2X",
                    PaymentChannelOptionInfo.AKULAKU_CICILAN_3X: "Akulaku Cicilan 3X",
                    PaymentChannelOptionInfo.AKULAKU_CICILAN_6X: "Akulaku Cicilan 6X",
                    PaymentChannelOptionInfo.AKULAKU_CICILAN_9X: "Akulaku Cicilan 9X",
                    PaymentChannelOptionInfo.AKULAKU_CICILAN_12X: "Akulaku Cicilan 12X"
                }[option_info])
        print()
        selected_option_info = options_info[int_input("Pilihan: ", len(options_info))-1]

    if not item.is_flash_sale:
        if item.upcoming_flash_sale is not None:
            flash_sale_start = datetime.fromtimestamp(item.upcoming_flash_sale.start_time)
            print(INFO, "Waktu Flash Sale: ", flash_sale_start.strftime("%H:%M:%S"))
            print(INFO, "Menunggu Flash Sale...", end='\r')
            sleep((datetime.fromtimestamp(item.upcoming_flash_sale.start_time) - datetime.now())
                  .total_seconds() - 2)
            print(INFO, "Bersiap siap...", end='\r')
            while not item.is_flash_sale:
                item = bot.fetch_item(item.item_id, item.shop_id)
        else:
            print(PROMPT, "Flash Sale telah Lewat!")
            exit(1)

    print(INFO, "Flash Sale telah tiba")
    start = datetime.now()
    print(INFO, "Menambah item ke cart...")
    cart_item = bot.add_to_cart(item, selected_model)
    print(INFO, "Checkout item...")
    bot.checkout(PaymentInfo(
        channel=selected_payment_channel,
        option_info=selected_option_info
    ), cart_item)
    end = datetime.now() - start
    print(INFO, "Item berhasil dibeli dalam waktu", Fore.YELLOW, end.seconds, "detik", end.microseconds // 1000,
          "milis")
    print(Fore.GREEN + "[*]", "Sukses")
except JustAnException as e:
    print(ERROR, {
        0x90b109: "url tidak cocok",
        0x69    : "item tidak ditemukan",
        0x2323  : "stok habis",
        0xb612  : "gagal menambah item ke cart",
        0x1111  : "gagal mengambil info checkout",
        0xaaaa  : "gagal checkout",
        0xaeee  : "respon tidak diterima, mungkin item sudah habis (anda telat)",
        0xbacc  : "gagal checkout, respon tidak ok",
        0x2232  : "gagal menghapus item dari cart"
    }.get(e.code(), f"Error tidak diketahui, code: {e.code()}"))
    exit(1)
except Exception:
    print(ERROR, "gagal login, cookie tidak valid, silahkan login ulang")
    exit(1)