
from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator,Bip39MnemonicGenerator, Bip44, Bip44Coins, Bip44Changes,Bip32Secp256k1,Bip49Coins,Bip84Coins
from bip_utils.bip.conf.bip44 import Bip44Ethereum
from bip_utils import Bip49,Bip84
from bip_utils import WifDecoder, WifEncoder
from bip_utils import Bip44PublicKey, Bip44PrivateKey
import blocksmith

def generate_wallets_bip(mnemonic):
    #assert Bip39MnemonicValidator(mnemonic).Validate() #is_mnemonic(mnemonic=MNEMONIC, language=LANGUAGE)
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    bitcoin_result={}
    BITCOIN_TYPE={'bitcoin':Bip44Coins.BITCOIN}
    for coin in BITCOIN_TYPE:
        bitcoin_result[coin] = {}

        # Generate BIP44 master keys
        bip_obj_mst44 = Bip44.FromSeed(seed_bytes, BITCOIN_TYPE[coin])
        bip_obj_mst49 = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
        bip_obj_mst84 = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
        # Generate BIP44 account keys: m/44'/0'/0'
        for acc in range(5):
            bip_obj_acc44 = bip_obj_mst44.Purpose().Coin().Account(acc)
            bip_obj_acc49 = bip_obj_mst49.Purpose().Coin().Account(acc)
            bip_obj_acc84 = bip_obj_mst84.Purpose().Coin().Account(acc)
            # Generate BIP44 chain keys: m/44'/0'/0'/0
            bip_obj_chain44 = bip_obj_acc44.Change(Bip44Changes.CHAIN_EXT)
            bip_obj_chain49 = bip_obj_acc49.Change(Bip44Changes.CHAIN_EXT)
            bip_obj_chain84 = bip_obj_acc84.Change(Bip44Changes.CHAIN_EXT)
            # Generate the address pool (first 20 addresses): m/44'/0'/0'/0/i
            bitcoin_result[coin][acc]=[]
            for i in range(10):
                bip_obj_addr44 = bip_obj_chain44.AddressIndex(i)
                bip_obj_addr49 = bip_obj_chain49.AddressIndex(i)
                bip_obj_addr84 = bip_obj_chain84.AddressIndex(i)
                item={'p2pkh':bip_obj_addr44.PublicKey().ToAddress(),  #P2PKH.ToAddress(pub_key_bytes),
                     'p2sh':bip_obj_addr49.PublicKey().ToAddress(),  #P2SH.ToAddress(pub_key_bytes),
                     'p2wkh':bip_obj_addr84.PublicKey().ToAddress(),  #P2WPKH.ToAddress(pub_key_bytes),
                     'wif_p2pkh':bip_obj_addr44.PrivateKey().ToWif(), #private_key.ToWif()
                     'wif_p2sh':bip_obj_addr49.PrivateKey().ToWif(), #private_key.ToWif()
                     'wif_p2wkh':bip_obj_addr84.PrivateKey().ToWif() #private_key.ToWif()
                      }
                bitcoin_result[coin][acc].append(item)

    BITCOIN_TYPE={'litecoin':Bip44Coins.LITECOIN}
    for coin in BITCOIN_TYPE:
        bitcoin_result[coin] = {}
        # Generate BIP44 master keys
        bip_obj_mst44 = Bip44.FromSeed(seed_bytes, BITCOIN_TYPE[coin])
        bip_obj_mst49 = Bip49.FromSeed(seed_bytes, Bip49Coins.LITECOIN)
        bip_obj_mst84 = Bip84.FromSeed(seed_bytes, Bip84Coins.LITECOIN)
        # Print master key
        # Generate BIP44 account keys: m/44'/0'/0'
        for acc in range(3):
            bip_obj_acc44 = bip_obj_mst44.Purpose().Coin().Account(acc)
            bip_obj_acc49 = bip_obj_mst49.Purpose().Coin().Account(acc)
            bip_obj_acc84 = bip_obj_mst84.Purpose().Coin().Account(acc)
            # Generate BIP44 chain keys: m/44'/0'/0'/0
            bip_obj_chain44 = bip_obj_acc44.Change(Bip44Changes.CHAIN_EXT)
            bip_obj_chain49 = bip_obj_acc49.Change(Bip44Changes.CHAIN_EXT)
            bip_obj_chain84 = bip_obj_acc84.Change(Bip44Changes.CHAIN_EXT)
            # Generate the address pool (first 20 addresses): m/44'/0'/0'/0/i
            bitcoin_result[coin][acc]=[]
            for i in range(5):
                bip_obj_addr44 = bip_obj_chain44.AddressIndex(i)
                bip_obj_addr49 = bip_obj_chain49.AddressIndex(i)
                bip_obj_addr84 = bip_obj_chain84.AddressIndex(i)
                item={'p2pkh':bip_obj_addr44.PublicKey().ToAddress(),#P2PKH.ToAddress(pub_key_bytes),
                     'p2sh':bip_obj_addr49.PublicKey().ToAddress(),#P2SH.ToAddress(pub_key_bytes),
                     'p2wkh':bip_obj_addr84.PublicKey().ToAddress(),#P2WPKH.ToAddress(pub_key_bytes),
                     'wif_p2pkh':bip_obj_addr44.PrivateKey().ToWif(), #private_key.ToWif()
                     'wif_p2sh':bip_obj_addr49.PrivateKey().ToWif(), #private_key.ToWif()
                     'wif_p2wkh':bip_obj_addr84.PrivateKey().ToWif() #private_key.ToWif()
                }
                bitcoin_result[coin][acc].append(item)

    BITCOIN_TYPE={'bitcoin_cash':Bip44Coins.BITCOIN_CASH,
                  'bitcoin_sv':Bip44Coins.BITCOIN_SV,
                  'binance_chain': Bip44Coins.BINANCE_CHAIN}
    altcoin_result={}
    for coin in BITCOIN_TYPE:
        altcoin_result[coin] = {}
        bip_obj_mst44 = Bip44.FromSeed(seed_bytes, BITCOIN_TYPE[coin])
        for acc in range(3):
            bip_obj_acc44 = bip_obj_mst44.Purpose().Coin().Account(acc)
            bip_obj_chain44 = bip_obj_acc44.Change(Bip44Changes.CHAIN_EXT)
            altcoin_result[coin][acc]=[]
            for i in range(3):
                bip_obj_addr44 = bip_obj_chain44.AddressIndex(i)
                pub_key=bip_obj_addr44.PublicKey().ToAddress()
                pub_key=pub_key.replace('bitcoincash:','')
                if coin=='binance_chain':
                    pk=bip_obj_addr44.PrivateKey().Raw().ToHex()
                else:
                    pk=bip_obj_addr44.PrivateKey().ToWif()

                item={'p2pkh':pub_key,#P2PKH.ToAddress(pub_key_bytes),
                     'wif':pk#bip_obj_addr44.PrivateKey().ToWif()#private_key.ToWif()
                }
                altcoin_result[coin][acc].append(item)


    altcoin2_result={}
    ALTCOIN_TYPE={'algorand':Bip44Coins.ALGORAND,
                  'cosmos':Bip44Coins.COSMOS,
                  'dogecoin':Bip44Coins.DOGECOIN,
                  'dash':Bip44Coins.DASH,
                  'zcash':Bip44Coins.ZCASH,
                  'ethereum_classic':Bip44Coins.ETHEREUM_CLASSIC,
                  'tron':Bip44Coins.TRON,
                  'nano':Bip44Coins.NANO,
                  'neo':Bip44Coins.NEO,
                  'polkadot':Bip44Coins.POLKADOT_ED25519_SLIP,
                  'polygon':Bip44Coins.POLYGON,
                  'ripple':Bip44Coins.RIPPLE,
                  'stellar':Bip44Coins.STELLAR,
                  'solana':Bip44Coins.SOLANA,
                  'tezos':Bip44Coins.TEZOS,
                  'terra':Bip44Coins.TERRA,
                  'vechain':Bip44Coins.VECHAIN,
                  'filecoin':Bip44Coins.FILECOIN,
                  'theta':Bip44Coins.THETA,
                  'avalanche_C_chain':Bip44Coins.AVAX_C_CHAIN,
                  #'avalanche_P_chain': Bip44Coins.AVAX_P_CHAIN,
                  'avalanche_X_chain': Bip44Coins.AVAX_X_CHAIN,
                  'eos':Bip44Coins.EOS}

    for coin in ALTCOIN_TYPE:
        bip_obj_mst = Bip44.FromSeed(seed_bytes, ALTCOIN_TYPE[coin])
        bip_obj_acc = bip_obj_mst.Purpose().Coin().Account(0)
        bip_obj_chain = bip_obj_acc.Change(Bip44Changes.CHAIN_EXT)
        altcoin2_result[coin]=[]
        for i in range(10):
            if (i>2) and (coin!='ethereum_classic'):
                continue
            bip_obj_addr = bip_obj_chain.AddressIndex(i)
            if coin=='ethereum_classic' or coin=='tron':
                private_key=bip_obj_addr.PrivateKey().Raw().ToHex()
            else:
                private_key=bip_obj_addr.PrivateKey().Raw().ToHex()#ToWif()

            item={'p2pkh':bip_obj_addr.PublicKey().ToAddress(),
                 'wif':private_key}

            altcoin2_result[coin].append(item)

    eth_result={}
    derive_path="Ethereum m/44'/60'/0'/0"
    bip_obj_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    eth_result[derive_path]={}
    for acc in range(5):
        bip_obj_acc = bip_obj_mst.Purpose().Coin().Account(acc)
        bip_obj_chain = bip_obj_acc.Change(Bip44Changes.CHAIN_EXT)
        eth_result[derive_path][acc]=[]
        for i in range(10):
            bip_obj_addr = bip_obj_chain.AddressIndex(i)
            item={'EthAddr':bip_obj_addr.PublicKey().ToAddress(),
                 'private_key':bip_obj_addr.PrivateKey().Raw().ToHex()}

            eth_result[derive_path][acc].append(item)

    derive_path="Ethereum m/44'/60'/0'"
    eth_result[derive_path]={}
    for acc in range(3):
        eth_result[derive_path][acc] = []

        for i in range(10):
            bip_obj_addr = Bip32Secp256k1.FromSeedAndPath(seed_bytes, f"m/44'/60'/{acc}'/{i}")

            public_key=Bip44PublicKey(bip_obj_addr.PublicKey(),Bip44Ethereum)#BipPublicKey(bip_obj_addr,Bip44Ethereum)
            private_key=Bip44PrivateKey(bip_obj_addr.PrivateKey(),Bip44Ethereum)#BipPublicKey(bip_obj_addr,Bip44Ethereum)

            item={'EthAddr':public_key.ToAddress(),
                 'private_key':private_key.Raw().ToHex()}

            eth_result[derive_path][acc].append(item)

    return bitcoin_result,eth_result,altcoin_result,altcoin2_result

def print_wallets_bip(phrase):
    bitcoin_result, eth_result, altcoin_result, altcoin2_result=generate_wallets_bip(phrase)
    full_res=''
    coin_log={}
    for coin in bitcoin_result:
        #print(coin.upper())
        coin_log[coin] = []
        full_res += coin.upper() + f'\n'
        for acc in bitcoin_result[coin]:
            full_res += f'ACC={acc}\n'
            p2pkh_res = ''
            p2sh_res = ''
            p2wkh_res = ''

            for item in bitcoin_result[coin][acc]:
                p2pkh_res+=f"{coin}_address:{item['p2pkh']}\n"
                p2sh_res += f"{coin}_address:{item['p2sh']}\n"
                p2wkh_res+=f"{coin}_address:{item['p2wkh']}\n"
                #wif=item['wif']
                coin_log[coin].extend([f"{item['p2pkh']}:p2pkh:{item['wif_p2pkh']}",
                                       f"{item['p2sh']}:p2wpkh-p2sh:{item['wif_p2sh']}",
                                       f"{item['p2wkh']}:p2wpkh:{item['wif_p2wkh']}"
                                       ])

            full_res+=f'P2PKH:\n{p2pkh_res}\n' \
                      f'P2SH:\n{p2sh_res}\n' \
                      f'P2WKH:\n{p2wkh_res}\n{"-"*24}\n'


    coin_log['eth_pk']=[]
    coin_log['addr']=[]

    for coin in eth_result:
        #print(coin)
        #t=coin.replace('/','_')
        #coin_log[t]=[]
        full_res+=coin+'\n'
        for acc in eth_result[coin]:
            full_res += f'ACC={acc}\n'
            p2pkh_res=''
            for item in eth_result[coin][acc]:
                p2pkh_res+=f"{coin}_address:{item['EthAddr']}\n"
                #coin_log[t].append(item['EthAddr'])
                coin_log['eth_pk'].append(item['private_key'])
                coin_log['addr'].append(item['EthAddr']+':'+item['private_key'])
            #print(p2pkh_res)
            #print('\n')
            full_res+=f'{p2pkh_res}\n{"-"*24}\n'


    for coin in altcoin_result:
        #print(coin.upper())
        coin_log[coin]=[]
        full_res+=coin.upper()+'\n'
        for acc in altcoin_result[coin]:
            full_res += f'ACC={acc}\n'
            p2pkh_res=''
            for item in altcoin_result[coin][acc]:
                wif=item['wif']
                p2pkh_res+=f"{coin}_address:{item['p2pkh']}\n"
                coin_log[coin].append(f"{item['p2pkh']}:{wif}")

            full_res+=f'{p2pkh_res}\n{"-"*24}\n'

    for coin in altcoin2_result:
        #print(coin.upper())
        if coin != 'ethereum_classic':
            coin_log[coin]=[]
        full_res+=coin.upper()+'\n'
        p2pkh_res=''
        for item in altcoin2_result[coin]:
            p2pkh_res += f"{coin}_address:{item['p2pkh']}\n"
            #p2pkh_res+=f"{coin}_address:{item['p2pkh']}\n"
            if coin=='ethereum_classic':
                coin_log['eth_pk'].append(item['wif'])
                coin_log['addr'].append(item['p2pkh']+':'+item['wif'])
            else:
                coin_log[coin].append(item['p2pkh']+':'+item['wif'])

        #print(p2pkh_res)
        #print('\n')
        full_res+=f'{p2pkh_res}\n{"-"*24}\n'
    return full_res,coin_log


def get_eth_addr(pk):
    address = blocksmith.EthereumWallet.generate_address(pk)
    return address




