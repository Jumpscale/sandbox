from js9 import j
import threading
import re
from pssh.exceptions import ConnectionErrorException
import requests
import time
import os
import json


"""
# On tft node
root@abdelrahman-ThinkPad-T530:~# bitcoin-cli getnewaddress "" legacy
n18MobJVWMLkWDTf8cku9DRAMTa86itr6D

# run on the btc node using the updated btcatomicswap binary (allow publish flag)
root@ubuntu-xenial:~# btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 --publish initiate n18MobJVWMLkWDTf8cku9DRAMTa86itr6D 0.01234
Secret:      58febdffd0dd5c141d27c45d8fb1a962e2e9a4eb991fac2da0bca56bd99736ca
Secret hash: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8

Contract fee: 0.00000166 BTC (0.00000672 BTC/kB)
Refund fee:   0.00000297 BTC (0.00001017 BTC/kB)

Contract (2NFBadefP7PrqDWyyjfJZbvpJrs1Tx8BSke):
6382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888ac

Contract transaction (a37d954d2cfc03526ebb0624e68389f9140f05ac19e5df03a58593204a1c2fd8):
0200000000010156901f407052d8c5185a54246e764d8304574aae13847c71ea5a2afb73d9e8e80000000017160014253584f1f207ff244c2d9dd10f2508b265f31395feffffff028a1be8020000000017a9144a0de4a6e8e5a52c7c249890a00c8bafa217510b8750d412000000000017a914f0a2561a9fd9de1ce4ee98f70de86ae3312f4873870247304402202761c014d6a3c69584d437153e0eb75f12e21f06ea267818bb7eca933ed892ef02201fd5ed6e24ae6fb684386a58cfcbbfde0ae1e16260bc52d3ce7e79a5e9ab98d80121031be3ad72917139bda0c3b4c3aa0e405772bb1b10168104604b4140eb7bf6338200000000

Refund transaction (bda4c504b8ce4df6ac50e4914d16421c50ba4defb916e1142b5bcad25efede97):
0200000001d82f1c4a209385a503dfe519ac050f14f98983e62406bb6e5203fc2c4d957da301000000cf483045022100c367297bef6e53b5de7522c396979eac70e7d9eb62adf727083cf3ef777192c402201f799215dd284f2d3d3a6fd10453b83b28ac01e43e6e5a1ef5ef39b97b35c0cf0121028d69b6cdc4c6ed23170c0918388a6c9b27811372db9954d898affbcd40ede697004c616382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888ac000000000127d31200000000001976a914063f138942d2b2af935c678c2a99ae9470d8908e88acab0d045b

Published contract transaction (a37d954d2cfc03526ebb0624e68389f9140f05ac19e5df03a58593204a1c2fd8)

# run on the btc node to decode the contract
curl --user user:pass --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "decodescript", "params": ["6382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888ac"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
{"result":{"asm":"OP_IF OP_SIZE 32 OP_EQUALVERIFY OP_SHA256 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8 OP_EQUALVERIFY OP_DUP OP_HASH160 d71c92b78069af7047d0a6c367be634aeb5ad6ac OP_ELSE 1526992299 OP_CHECKLOCKTIMEVERIFY OP_DROP OP_DUP OP_HASH160 99c51785eb8ed83a06e495aee769f687616cdd4f OP_ENDIF OP_EQUALVERIFY OP_CHECKSIG","type":"nonstandard","p2sh":"2NFBadefP7PrqDWyyjfJZbvpJrs1Tx8BSke"},"error":null,"id":"curltest"}


# run on the tft node autdit transaction
root@abdelrahman-ThinkPad-T530:~# btcatomicswap --testnet -s localhost:8332 auditcontract 6382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888ac 0200000000010156901f407052d8c5185a54246e764d8304574aae13847c71ea5a2afb73d9e8e80000000017160014253584f1f207ff244c2d9dd10f2508b265f31395feffffff028a1be8020000000017a9144a0de4a6e8e5a52c7c249890a00c8bafa217510b8750d412000000000017a914f0a2561a9fd9de1ce4ee98f70de86ae3312f4873870247304402202761c014d6a3c69584d437153e0eb75f12e21f06ea267818bb7eca933ed892ef02201fd5ed6e24ae6fb684386a58cfcbbfde0ae1e16260bc52d3ce7e79a5e9ab98d80121031be3ad72917139bda0c3b4c3aa0e405772bb1b10168104604b4140eb7bf6338200000000
Contract address:        2NFBadefP7PrqDWyyjfJZbvpJrs1Tx8BSke
Contract value:          0.01234 BTC
Recipient address:       n18MobJVWMLkWDTf8cku9DRAMTa86itr6D
Author's refund address: muY1nb5swhfijRUovauF6uukbDLCyih1WY

Secret hash: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8

Locktime: 2018-05-22 12:31:39 +0000 UTC
Locktime reached in 45h18m42s


# generate tft address on btc node
# primary seed of tfchain wallet: pipe pyramid damp pistol tray actress hungry alcohol main this impulse emotion clown foam sure basic mammal elephant predict caught list save mule mistake
#2 agree ranch raise happy patch apple cover above grab nurse depart leaf require clog oyster grape reform toddler borrow neutral avocado elder loan media
# adddress from tfchain: 014aba1cf55b4c8d1c815ffa8791245c69f65f01461be5e83625a2684e4815982e2647ff1e2c2a

# seed: valley virus vital depend nest toilet when huge rather popular include also delay hurt tobacco elbow accuse flee cream mouse rose idle oyster exotic
# address: 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d

# run on the tft node
root@abdelrahman-ThinkPad-T530:~# tfchainc atomicswap participate 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d .5 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8
Contract address: 028761224dfb7fd4a34ed29e65852500ada0e2b54e017200cd97d1626af2c4544bb055199553a5
Contract value: 0.5 TFT
Recipient address: 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d
Refund address: 015a88c1bffaf989e10d9b9dd4262090a1185b8a1c159e93101be09a86ccab988b0b7a43c61320

Hashed Secret: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8

Locktime: 1526917093 (2018-05-21 17:38:13 +0200 CEST)
Locktime reached in: 23h59m59.241241198s

Publish atomic swap (participation) transaction? [Y/N] y
published contract transaction
OutputID: dafed64af281bccf03fda2da4814281251d13d9bfb3aea95f3e505b160b6efe5

# run on the brc node
root@ubuntu-xenial:~# tfchainc atomicswap audit 028761224dfb7fd4a34ed29e65852500ada0e2b54e017200cd97d1626af2c4544bb055199553a5 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d 015a88c1bffaf989e10d9b9dd4262090a1185b8a1c159e93101be09a86ccab988b0b7a43c61320 1526917093 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8 .5
Given unlock hash matches the given contract information :)

Contract address: 028761224dfb7fd4a34ed29e65852500ada0e2b54e017200cd97d1626af2c4544bb055199553a5
Recipient address: 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d
Refund address: 015a88c1bffaf989e10d9b9dd4262090a1185b8a1c159e93101be09a86ccab988b0b7a43c61320

Hashed Secret: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8

Locktime: 1526917093 (2018-05-21 15:38:13 +0000 UTC)
Locktime reached in: 23h22m31.925443992s

This was a quick check only, whether it has been spend already or not is unclear.
You can do a complete/thorough check when auditing using the output ID instead.


# run the claim on the btc node
root@ubuntu-xenial:~# tfchainc atomicswap claim dafed64af281bccf03fda2da4814281251d13d9bfb3aea95f3e505b160b6efe5 58febdffd0dd5c141d27c45d8fb1a962e2e9a4eb991fac2da0bca56bd99736ca .5
An unspend atomic swap contract could be found for the given outputID,
and the given contract information matches the found contract's information, all good! :)

Contract address: 028761224dfb7fd4a34ed29e65852500ada0e2b54e017200cd97d1626af2c4544bb055199553a5
Recipient address: 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d
Refund address: 015a88c1bffaf989e10d9b9dd4262090a1185b8a1c159e93101be09a86ccab988b0b7a43c61320

Hashed Secret: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8

Locktime: 1526917093 (2018-05-21 15:38:13 +0000 UTC)
Locktime reached in: 22h17m17.217868994s

Publish atomic swap claim transaction? [Y/N] y

Published atomic swap claim transaction!
Transaction ID: e506a3e3b7883c79df52f751bb3cd4a0b1bed9a670a1eb9e612fee891bb58ac6
>   NOTE that this does NOT mean for 100% you'll have the money!
> Due to potential forks, double spending, and any other possible issues your
> claim might be declined by the network. Please check the network
> (e.g. using a public explorer node or your own full node) to ensure
> your payment went through. If not, try to audit the contract (again).


# run on the tft node
root@abdelrahman-ThinkPad-T530:~# btcatomicswap --testnet -s localhost:8332 -rpcuser=user --rpcpass=pass --publish redeem 6382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888ac 0200000000010156901f407052d8c5185a54246e764d8304574aae13847c71ea5a2afb73d9e8e80000000017160014253584f1f207ff244c2d9dd10f2508b265f31395feffffff028a1be8020000000017a9144a0de4a6e8e5a52c7c249890a00c8bafa217510b8750d412000000000017a914f0a2561a9fd9de1ce4ee98f70de86ae3312f4873870247304402202761c014d6a3c69584d437153e0eb75f12e21f06ea267818bb7eca933ed892ef02201fd5ed6e24ae6fb684386a58cfcbbfde0ae1e16260bc52d3ce7e79a5e9ab98d80121031be3ad72917139bda0c3b4c3aa0e405772bb1b10168104604b4140eb7bf6338200000000 58febdffd0dd5c141d27c45d8fb1a962e2e9a4eb991fac2da0bca56bd99736ca
Redeem fee: 0.0000033 BTC (0.00001019 BTC/kB)

Redeem transaction (ddd1040fd2f255a82aba54255d39b7c8ccc43393f99fa2871c1557da216bf802):
0200000001d82f1c4a209385a503dfe519ac050f14f98983e62406bb6e5203fc2c4d957da301000000ef473044022079e824f3accd97fc3ba2f67a7a02caf60a6edc3678397b1f8f9d6dc624edeca60220156d9cfba11f220cbe133a63ad5c5b1c06582c169ee8a91da6d94ee38ef2d409012103a7e0010af3def18b827d45ddafcbbffea1f49ce468bb1d91f043e8feb8daa72c2058febdffd0dd5c141d27c45d8fb1a962e2e9a4eb991fac2da0bca56bd99736ca514c616382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888acffffffff0106d31200000000001976a914754aea4184341fe1779faac5557b16879709bdcd88acab0d045b

Published redeem transaction (ddd1040fd2f255a82aba54255d39b7c8ccc43393f99fa2871c1557da216bf802)


"""

DEFAULT_SSHKEY_NAME = 'id_rsa'
DEFAULT_BITCOIN_DIR = '/root/.bitcoin'
DEFAULT_BITCOIN_CONT_DIR = '/.bitcoin'
DEFAULT_BITCOIN_CONFIG = """
rpcuser=user
rpcpassword=pass
testnet=1
rpcport=18332
rpcallowip=127.0.0.1
prune=550
server=1
"""
DEFAULT_BITCOIN_CONFIG_PATH = '{}/bitcoin.conf'.format(DEFAULT_BITCOIN_DIR)
DEFAULT_BITCOIN_CONT_CONFIG_PATH = '{}/bitcoin.conf'.format(DEFAULT_BITCOIN_CONT_DIR)
DEFAULT_TFT_WALLET_PASSPHRASE = 'pass'

atomic_exchange_repo = 'https://github.com/JimberSoftware/AtomicExchange.git'
bitcoind_config_path = '{}/cryptoDocker/bitcoin.conf'
bitcoind_cmd = 'bitcoind -conf={} --daemon'
tfchaind_data_dir = '/opt/var/data/tfchaind'
tfchaind_cmd = 'cd {};/opt/go_proj/bin/tfchaind --network testnet -M gctwe &'.format(tfchaind_data_dir)
bitcoinswap_bin_path = '{}/cryptoDocker/btcatomicswap'


def tft_wallet_unlock(prefab, passphrase):
    """
    Unlock a tft wallet

    @param passphrase: Phasephrase to unlock the wallet
    """
    cmd = 'curl -A "Rivine-Agent" "localhost:23110/wallet"'
    rc, out, err = prefab.core.run(cmd, die=False, showout=False)
    if rc:
        raise RuntimeError('Failed to unlock tft wallet. Error {}'.format(err))
    json_out = json.loads(out)
    if json_out.get('unlocked') is False and json_out.get('encrypted') is True:
        cmd = 'curl -A "Rivine-Agent" --data "passphrase={}" "localhost:23110/wallet/unlock"'.format(passphrase)
        _, out, _ = prefab.core.run(cmd, showout=False)
        if out:
            stdout_error = json.loads(out).get('message')
            if stdout_error:
                raise RuntimeError('Failed to unlock wallet. Error {}'.format(stdout_error))


def tft_wallet_init(prefab, passphrase, recovery_seed=None):
    """
    Initialize tft wallet using the passphrase and recovery seed if provided
    If the wallet is unlocked then nothing will happen
    """

    cmd = 'curl -A "Rivine-Agent" "localhost:23110/wallet"'
    rc, out, err = prefab.core.run(cmd, die=False, showout=False)
    if rc:
        raise RuntimeError('Failed to unlock tft wallet. Error {}'.format(err))
    json_out = json.loads(out)
    cmd_data = '--data "passphrase={}"'
    if json_out.get('unlocked') is False and json_out.get('encrypted') is False:
        if recovery_seed:
            entropy = entropy = j.data.encryption.mnemonic.to_entropy(recovery_seed)
            cmd_data = '--data "passphrase={}&seed={}"'.format(passphrase, entropy.hex())
        else:
            cmd_data = '--data "passphrase={}"'.format(passphrase)
        cmd = 'curl -A "Rivine-Agent" {} "localhost:23110/wallet/init"'.format(cmd_data)
        rc, out, err = prefab.core.run(cmd, die=False, showout=False)
        if rc:
            raise RuntimeError('Failed to initialize tft wallet. Error {}'.format(err))


def check_tfchain_synced(prefab, height_threeshold=10):
    """
    Check if the tfchain daemon is synced with the offical testnet
    @param prefab: prefab of the TFT node
    @param height_threeshold: The max difference between the testnet explorer and the local node to be considered in sync
    """
    testnet_explorer = 'https://explorer.testnet.threefoldtoken.com/explorer'
    res = requests.get(testnet_explorer)
    if res.status_code == 200:
        expected_height = res.json()['height']
        _, out, err = prefab.core.run(cmd='tfchainc', showout=False)
        out = '{}\n{}'.format(out, err)
        match = re.search('^Synced:\s+(?P<synced>\w+)\n*.*\n*Height:\s*(?P<height>\d+)', out)
        if match:
            match_info = match.groupdict()
            if match_info['synced'] == 'Yes' and expected_height - int(match_info['height']) <= height_threeshold:
                return True
    return False

def check_btc_synced(prefab, height_threeshold=10):
    """
    Check if the BTC node is synced with the offical testnet3
    @param prefab: prefab of the BTC node
    @param height_threeshold: The max difference between the testnet and the local node to be considered in sync
    """
    testnet_url = 'https://api.blockcypher.com/v1/btc/test3'
    res = requests.get(testnet_url)
    if res.status_code == 200:
        expected_height = res.json()['height']
        _, out, _ = prefab.core.run(cmd='bitcoin-cli -getinfo', showout=False)
        current_height = json.loads(out)['blocks']
        if expected_height - current_height <= height_threeshold:
            return True
    return False


def start_blockchains(prefab, node_name):
    """
    Start blockchains daemons on a node
    """
    # a bit unrelated but make sure that curl is installed
    prefab.core.run('apt-get update; apt-get install -y curl', die=False, showout=False)
    print("Starting tfchaind daemon on {}".format(node_name))
    tfchaind_cmd = 'tfchaind --network testnet -M gctwe'
    tfchaind_cmd_check = 'ps fax | grep "{}" | grep -v grep'.format(tfchaind_cmd)
    rc, _, _ = prefab.core.run(cmd=tfchaind_cmd_check, die=False, showout=False)
    if rc:
        prefab.core.run('{} >/dev/null 2>&1 &'.format(tfchaind_cmd), showout=False)

    # start bitcoind
    print("Starting btcoind daemon on {}".format(node_name))
    prefab.core.dir_ensure(DEFAULT_BITCOIN_DIR)
    prefab.core.file_write(location=DEFAULT_BITCOIN_CONFIG_PATH,
                                    content=DEFAULT_BITCOIN_CONFIG)
    btc_cmd = 'bitcoind -daemon'
    btc_cmd_check = 'ps fax | grep "{}" | grep -v grep'.format(btc_cmd)
    rc, _, _ = prefab.core.run(cmd=btc_cmd_check, die=False, showout=False)
    if rc:
        prefab.core.run(cmd=btc_cmd, showout=False)


def create_blockchain_zos_vms(zos_node_name='main', sshkeyname=None):
    """
    Create 2 ZOS vms each running the crypto flist that cointains the blockchains binaries

    @param zos_node_name: Name of the Zero os client instance where the vms will be created
    @param sshkeyname: Name of the sshkey to use to authorize access to the created nodes
    """
    sshkey = j.clients.sshkey.get(sshkeyname)
    # zos_cl = j.clients.zero_os.get(zos_node_name)
    zrobot_cl = j.clients.zrobot.robots[zos_node_name]
    tft_node_data = {
    'name': 'tft_node',
    'flist': 'https://hub.gig.tech/abdelrahman_hussein_1/ubuntucryptoexchange.flist',
    'memory': 1024 * 14,
    'cpu': 2,
    'nics':[{'type': 'default', 'name': 'nic01'}],
    'ports':[{'name': 'ssh', 'source': 2250, 'target':22}],
    'configs': [{'path': '/root/.ssh/authorized_keys', 'content': sshkey.pubkey,
                 'name': 'sshauthorizedkeys'}],
    }
    print("Creating TFT node vm")
    tft_node_srv = zrobot_cl.services.find_or_create('github.com/zero-os/0-templates/vm/0.0.1', tft_node_data['name'], tft_node_data)
    task = tft_node_srv.schedule_action('install')
    task.wait()
    if task.state != 'ok':
        raise RuntimeError('Failed to create a VM for TFT')

    timeout = 5 * 60
    tft_node_prefab = None
    while timeout > 0:
        try:
            tft_node_prefab = j.tools.prefab.getFromSSH(addr=zos_node_name, port=tft_node_data['ports'][0]['source'])
            break
        except ConnectionErrorException as ex:
            time.sleep(30)
            timeout -= 30

    if tft_node_prefab is None:
        raise RuntimeError("Failed to establish a connection to {} port: {}".format(zos_node_name, tft_node_data['ports'][0]['source']))

    # add /opt/bin to the path
    tft_node_prefab.core.run('echo "export PATH=/opt/bin:$PATH" >> /root/.bash_profile', profile=False, showout=False)

    start_blockchains(tft_node_prefab, tft_node_data['name'])
    print('Initializing TFT wallet')
    passphrase = os.environ.get('TFT_WALLET_PASSPHRASE', DEFAULT_TFT_WALLET_PASSPHRASE)
    recovery_seed = os.environ.get('TFT_WALLET_RECOVERY_SEED')
    tft_wallet_init(prefab=tft_node_prefab,
                    passphrase=passphrase,
                    recovery_seed=recovery_seed)
    print('Unlocking TFT wallet')
    tft_wallet_unlock(prefab=tft_node_prefab,
                      passphrase=passphrase)

    btc_node_data = {
    'name': 'btc_node',
    'flist': 'https://hub.gig.tech/abdelrahman_hussein_1/ubuntucryptoexchange.flist',
    'memory': 1024 * 14,
    'cpu': 2,
    'nics':[{'type': 'default', 'name': 'nic01'}],
    'ports':[{'name': 'ssh', 'source': 2350, 'target':22}],
    'configs': [{'path': '/root/.ssh/authorized_keys', 'content': sshkey.pubkey,
                 'name': 'sshauthorizedkeys'}],
    }
    print("Creating BTC node vm")
    btc_node_srv = zrobot_cl.services.find_or_create('github.com/zero-os/0-templates/vm/0.0.1', btc_node_data['name'], btc_node_data)
    task = btc_node_srv.schedule_action('install')
    task.wait()
    if task.state != 'ok':
        raise RuntimeError('Failed to create a VM for BTC')

    timeout = 5 * 60
    btc_node_prefab = None
    while timeout > 0:
        try:
            btc_node_prefab = j.tools.prefab.getFromSSH(addr=zos_node_name, port=btc_node_data['ports'][0]['source'])
            break
        except ConnectionErrorException as ex:
            time.sleep(30)
            timeout -= 30

    if btc_node_prefab is None:
        raise RuntimeError("Failed to establish a connection to {} port: {}".format(zos_node_name, btc_node_data['ports'][0]['source']))

    # add /opt/bin to the path
    btc_node_prefab.core.run('echo "export PATH=/opt/bin:$PATH" >> /root/.bash_profile', profile=False, showout=False)

    start_blockchains(btc_node_prefab, btc_node_data['name'])

    print("Wait until TFT node is synced")
    while True:
        if check_tfchain_synced(tft_node_prefab):
            break
        time.sleep(20)

    print("Wait until BTC node is synced")
    while True:
        if check_btc_synced(btc_node_prefab):
            break
        time.sleep(20)


def create_packet_machines(sshkeyname=None):
    """
    This will create 4 nodes each running all the blockchains

    @param sshkeyname: Name of the sshkey to use to authorize access to the created nodes

    @returns: A dictionary with in the form {"btc": <prefab_obj>, "tft": <prefab_obj>, "eth": <prefab_obj>, "xrp": <prefab_obj>}
    """
    packet_cl = j.clients.packetnet.get()
    sshkeyname = sshkeyname or (j.clients.sshkey.listnames()[0] if j.clients.sshkey.listnames() else DEFAULT_SSHKEY_NAME)
    print("Creating packet machine for Bitcoin node")
    btc_node = packet_cl.startDevice(hostname='hussein.btc', os='ubuntu_16_04', remove=False, sshkey=sshkeyname)
    install_blockchains(prefab=btc_node.prefab)

    # start bitcoind
    btc_node.prefab.core.dir_ensure(DEFAULT_BITCOIN_DIR)
    btc_node.prefab.core.file_write(location=DEFAULT_BITCOIN_CONFIG_PATH,
                                    content=DEFAULT_BITCOIN_CONFIG)

    start_blockchains(prefab=btc_node.prefab, node_name='hussein.btc')

    print("Creating packet machine for TFTChain node")
    tft_node = packet_cl.startDevice(hostname='hussein.tft', os='ubuntu_16_04', remove=False, sshkey=sshkeyname)
    install_blockchains(prefab=tft_node.prefab)

    start_blockchains(prefab=tft_node.prefab, node_name='hussein.tft')

    return {
    'btc': btc_node.prefab,
    'tft': tft_node.prefab,
    'eth': None,
    'xrp': None,
    }


def install_blockchains(prefab):
    """
    Install TFT, BTC, ETH and XRP blockchains
    """
    print("Installing blockchains")
    prefab.system.base.install(upgrade=True)
    prefab.blockchain.tfchain.build()
    prefab.blockchain.tfchain.install()
    prefab.blockchain.bitcoin.build()
    prefab.blockchain.bitcoin.install()
    prefab.blockchain.atomicswap.build()
    prefab.blockchain.atomicswap.install()
    # prefab.blockchain.ethereum.install()



def create_packet_zos(sshkeyname=None, zt_netid="", zt_client_instance='main', packet_client_instance='main', hostname='atomicswap.test'):
    """
    Creates a zos node on packet.net

    @param sshkeyname: Name of the sshkey to use to authorize access to the created node
    @param zt_netid: Zerotier network id
    @param zt_client_instance: Name of the zerotier client instance
    """
    zt_api_token = j.clients.zerotier.get(zt_client_instance).config.data['token_']
    packet_cl = j.clients.packetnet.get(packet_client_instance)
    sshkeyname = sshkeyname or (j.clients.sshkey.listnames()[0] if j.clients.sshkey.listnames() else DEFAULT_SSHKEY_NAME)
    zos_packet_cl, packet_node, ipaddr  = packet_cl.startZeroOS(hostname=hostname, zerotierId=zt_netid,
                                                                plan='baremetal_1', zerotierAPI=zt_api_token,
                                                                branch='development', params=['development', 'console=ttyS1,115200'])
                                                                # branch='development', params=['development'])
    zos_node_name = ipaddr
    zrobot_data = {
    'url': 'http://{}:6600'.format(zos_node_name)
    }
    # the get call to create the client instance and then we get a more usefull robot instance
    zrobot_cl = j.clients.zrobot.get(zos_node_name, data=zrobot_data)
    zrobot_cl = j.clients.zrobot.robots[zos_node_name]
    # wait for 0-node reobot to be reachable services can be listed
    timeout = 5 * 60
    print("Waiting for 0-node robot to be ready")
    while timeout > 0:
        try:
            zrobot_cl.services.names
        except Exception:
            timeout -= 30
            time.sleep(30)
        else:
            break

    if not timeout:
        raise RuntimeError("Z-node robot is not accessible")

    try:
        create_blockchain_zos_vms(zos_node_name=zos_node_name, sshkeyname=sshkeyname)
    except Exception:
        import IPython
        IPython.embed()
    return zos_node_name


def main():
    """
    Deploys the blockchains
    """
    print("Preparing blockchains environments")
    if not j.clients.sshkey.sshagent_available():
        j.clients.sshkey.sshagent_start()
    zt_netid_envvar = 'ZT_NET_ID'
    zt_netid = os.environ.get(zt_netid_envvar)
    if zt_netid is None:
        raise RuntimeError('Environtment variable {} is not set'.format(zt_netid_envvar))
    sshkeyname = os.environ.get('SSHKEY_NAME')
    zt_client_instance = os.environ.get('ZT_CLIENT_INSTANCE', 'main')
    packet_client_instance = os.environ.get('PACKET_CLIENT_INSTANCE', 'main')
    zos_node_hostname = os.environ.get('ZOS_NODE_NAME', 'atomicswap.test')
    zos_node_name = create_packet_zos(zt_netid=zt_netid, sshkeyname=sshkeyname,
                                      zt_client_instance=zt_client_instance,
                                      packet_client_instance=packet_client_instance,
                                      hostname=zos_node_hostname
                                      )

    print("ZOS node ip address is: {}".format(zos_node_name))


if __name__ == '__main__':
    main()
    # import IPython
    # IPython.embed()
