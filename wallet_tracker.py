
import sys
import argparse
import requests
import json
from datetime import datetime
trasfer_sig = '0xa9059cbb'

chain_name_url = {
    "ethereum":         "https://api.etherscan.io/api?chainid=1",
    "bnb":              "https://api.etherscan.io/api?chainid=56",
    "polygon":          "https://api.etherscan.io/api?chainid=137",
    "polygon_zk":       "https://api.etherscan.io/api?chainid=1101",
    "base":             "https://api.etherscan.io/api?chainid=8453",
    "arbitrum_one":     "https://api.etherscan.io/api?chainid=42161",
    "arbitrum_nova":    "https://api.etherscan.io/api?chainid=42170",
    "fantom":           "https://api.etherscan.io/api?chainid=250",
    "blast":            "https://api.etherscan.io/api?chainid=81457",
    "op":               "https://api.etherscan.io/api?chainid=10",
    "avalanche":        "https://api.etherscan.io/api?chainid=43114",
    "bittorrent":       "https://api.etherscan.io/api?chainid=199",
    "celo":             "https://api.etherscan.io/api?chainid=42220",
    "cronos":           "https://api.etherscan.io/api?chainid=25",
    "fraxtal":          "https://api.etherscan.io/api?chainid=252",
    "gnosis":           "https://api.etherscan.io/api?chainid=100",
    "kroma":            "https://api.etherscan.io/api?chainid=255",
    "mantle":           "https://api.etherscan.io/api?chainid=5000",
    "moonbeam":         "https://api.etherscan.io/api?chainid=1284",
    "moonriver":        "https://api.etherscan.io/api?chainid=1285",
    "opbnb":            "https://api.etherscan.io/api?chainid=204",
    "scroll":           "https://api.etherscan.io/api?chainid=534352",
    "taiko":            "https://api.etherscan.io/api?chainid=167000",
    "wemix":            "https://api.etherscan.io/api?chainid=1111",
    "zksync":           "https://api.etherscan.io/api?chainid=324",
    "xai":              "https://api.etherscan.io/api?chainid=660279",
    "xdc":              "https://api.etherscan.io/api?chainid=50",
    "ape":              "https://api.etherscan.io/api?chainid=33139",
    "world":            "https://api.etherscan.io/api?chainid=480",
    "sophon":           "https://api.etherscan.io/api?chainid=50104",
    "sonic":            "https://api.etherscan.io/api?chainid=146",
    "uni":              "https://api.etherscan.io/api?chainid=130",
    "abstract":         "https://api.etherscan.io/api?chainid=2741",
    "bera":             "https://api.etherscan.io/api?chainid=80094",
    "swell":            "https://api.etherscan.io/api?chainid=1923",
}

native_asset_name = {
    "ethereum":         "ETH",
    "bnb":              "BNB",
    "polygon":          "MATIC",
    "polygon_zk":       "ETH",
    "base":             "ETH",
    "arbitrum_one":     "ETH",
    "arbitrum_nova":    "ETH",
    "fantom":           "FTM",
    "blast":            "BLAST",
    "op":               "ETH",
    "avalanche":        "AVAX",
    "bittorrent":       "BTT",
    "celo":             "CELO",
    "cronos":           "CRO",
    "fraxtal":          "FRAX",
    "gnosis":           "xDAI",
    "kroma":            "KROMA",
    "mantle":           "MNTL",
    "moonbeam":         "GLMR",
    "moonriver":        "MOVR",
    "opbnb":            "BNB",
    "scroll":           "ETH",
    "taiko":            "ETH",
    "wemix":            "WEMIX",
    "zksync":           "ETH",
    "xai":              "XAI",
    "xdc":              "XDC",
    "ape":              "APE",
    "world":            "WORLD",
    "sophon":           "SOPHON",
    "sonic":            "SONIC",
    "uni":              "UNICH",
    "abstract":         "ABS",
    "bera":             "BRA",
    "swell":            "SWELL",
}

def get_base_url(chain_name: str) -> str:
    key = chain_name.strip().lower()
    if key not in chain_name_url:
        supported = ", ".join(sorted(chain_name_url.keys()))
        raise KeyError(f"unsupported chain name '{chain_name}'. supported: {supported}")
    return chain_name_url[key]

def fetch_transactions(address, api_key, startblock, endblock,page, offset, sort, internal, base_url):
    base = {
        'module':    'account',
        'address':   address,
        'startblock':startblock,
        'endblock':  endblock,
        'page':      page,
        'offset':    offset,
        'sort':      sort,
        'apikey':    api_key
    }
    
    # 일반 tx
    params = base.copy(); params['action'] = 'txlist'
    r = requests.get(base_url, params=params); r.raise_for_status()
    data = r.json()
    if data.get('status') != '1':
        raise ValueError(f"api error (txlist): {data.get('message')}")
    result = data.get('result') or []

    # internal tx
    if internal:
        params2 = base.copy(); params2['action'] = 'txlistinternal'
        r2 = requests.get(base_url, params=params2); r2.raise_for_status()
        d2 = r2.json()
        if d2.get('status') != '1':
            raise ValueError(f"api error (txlistinternal): {d2.get('message')}")
        result.extend(d2.get('result') or [])
    return result

def fetch_token_metadata(contract_address, api_key, base_url):
    params = {
        'module':'account','action':'tokentx','contractaddress':contract_address,
        'page':1,'offset':1,'startblock':0,'endblock':99999999,'sort':'asc','apikey':api_key
    }
    try:
        r = requests.get(base_url, params=params); r.raise_for_status()
        txs = r.json().get('result') or []
        if txs:
            first = txs[0]
            return first.get('tokenSymbol'), int(first.get('tokenDecimal',18))
    except Exception as e:
        print(f"fetch failed: {e}", file=sys.stderr)
    return None, 18

def parse_erc20_transfer(tx, api_key, base_url):
    data = tx.get('input','')
    if not data.startswith(trasfer_sig) or len(data)<10+64*2:
        return None
    sym, dec = fetch_token_metadata(tx['to'], api_key, base_url)
    payload = data[10:]
    recipient = '0x'+payload[24:64]
    val = int(payload[64:],16)
    if val<=0: return None
    amt = val/(10**dec)
    ts = int(tx.get('timeStamp',0))
    dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'from':tx['from'],'to':recipient,'asset':sym or 'UNKNOWN',
        'value':amt,'timestamp':dt,'tokenTransfer':True,'hash':tx.get('hash')
    }

def process_transactions(tx_list, api_key, base_url, native_asset):
    processed = []
    for tx in tx_list:
        if tx.get('methodId') == trasfer_sig:
            rec = parse_erc20_transfer(tx, api_key, base_url)
            if rec: processed.append(rec)
        else:
            val = int(tx.get('value',0)) / 10**18
            if val>0:
                ts = int(tx.get('timeStamp',0))
                dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                processed.append({
                    'from':tx['from'],'to':tx['to'],
                    'asset':native_asset,'value':val,
                    'timestamp':dt,'tokenTransfer':False,
                    'hash':tx.get('hash')
                })
    return processed

def summarize_by_asset(address, processed):
    addr = address.lower()
    summary = {}
    for tx in processed:
        a = tx['asset']
        if a not in summary:
            summary[a] = {'incoming_total':0.0,'outgoing_total':0.0,
                          'incoming_addresses':set(),'outgoing_addresses':set()}
        e = summary[a]
        if tx['to'].lower()==addr:
            e['incoming_total'] += tx['value']; e['incoming_addresses'].add(tx['from'])
        if tx['from'].lower()==addr:
            e['outgoing_total'] += tx['value']; e['outgoing_addresses'].add(tx['to'])
    for e in summary.values():
        e['incoming_addresses']=sorted(e['incoming_addresses'])
        e['outgoing_addresses']=sorted(e['outgoing_addresses'])
    return summary

def main():
    p = argparse.ArgumentParser(description='Per-chain wallet tracker')
    p.add_argument('--address',   required=True, help='address to track')
    p.add_argument('--api-key',   required=True, help='etherscan api key')
    p.add_argument('--chain-name',required=True, help='ex) ethereum, polygon')
    p.add_argument('--start-block',type=int, default=0, help='start blocknumber')
    p.add_argument('--end-block',  type=int, default=99999999, help='end blocknumber')
    p.add_argument('--page',       type=int, default=1, help='scanner page number')
    p.add_argument('--offset',     type=int, default=100, help='0 ~ 10000')
    p.add_argument('--sort',       choices=['asc','desc'], default='asc', help='asc or desc')
    p.add_argument('--internal',   action='store_true', help='include internal tx')
    p.add_argument('--json',       action='store_true', help='save transaction data to a jsonfile')
    args = p.parse_args()

    key = args.chain_name.strip().lower()
    try:
        base_url = get_base_url(args.chain_name)
    except KeyError as e:
        print(f"error {e}", file=sys.stderr); sys.exit(1)

    native_asset = native_asset_name.get(key, "?")

    txs = fetch_transactions(
        args.address, args.api_key,
        args.start_block, args.end_block,
        args.page, args.offset, args.sort,
        args.internal, base_url
    )
    processed = process_transactions(txs, args.api_key, base_url, native_asset)
    summary   = summarize_by_asset(args.address, processed)

    if args.json:
        with open('output.json','w',encoding='utf-8') as f:
            json.dump({'transactions':processed}, f, ensure_ascii=False, indent=4)
        print("saved detailed transactions to output.json")

    print("=== Asset Summary ===")
    for asset, data in summary.items():
        print(f"Asset: {asset}")
        print(f"  Incoming total: {data['incoming_total']}")
        print(f"  Outgoing total: {data['outgoing_total']}")
        print("  Incoming addresse : ")
        for inc in data['incoming_addresses']:
            print(f"    - {inc}")
        print("  Outgoing addresses : ")
        for out in data['outgoing_addresses']:
            print(f"    - {out}")

if __name__ == '__main__':
    main()
